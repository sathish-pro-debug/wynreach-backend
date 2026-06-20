from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_main_db
from app.models.team import TeamMember, Invitation
from sqlalchemy.orm import joinedload
from app.models.user import User
from app.services.auth_service import get_current_user, get_password_hash
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import secrets
import uuid
import boto3
from app.core.config import settings
from app.services.aws_ses_service import AWSSESService
aws_ses = AWSSESService()
router = APIRouter()

# =====================================================
# Email Sending Function
# =====================================================
def send_invite_email(to_email: str, temp_password: str, workspace_name: str, invited_by_name: str, invite_token: str):
    if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
        print("=" * 60)
        print(f"INVITATION (AWS not configured)")
        print(f"To: {to_email}")
        print(f"Temp Password: {temp_password}")
        print(f"Invite Link: http://localhost:5173/set-password/{invite_token}")
        print("=" * 60)
        return False
    try:
        client = boto3.client(
            'ses',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        accept_url = f"http://localhost:5173/set-password/{invite_token}"
        html_body = f"""
        <html>
        <body>
            <h2>Welcome to WYNReach!</h2>
            <p><strong>{invited_by_name}</strong> has invited you to join <strong>{workspace_name}</strong>.</p>
            <p><strong>Temporary Password:</strong> {temp_password}</p>
            <p><a href="{accept_url}">Accept Invitation</a></p>
            <p>This link expires in 7 days.</p>
        </body>
        </html>
        """
        client.send_email(
            Source=settings.SES_FROM_EMAIL,
            Destination={"ToAddresses": [to_email]},
            Message={
                "Subject": {"Data": f"Invitation to join {workspace_name}"},
                "Body": {"Html": {"Data": html_body}}
            }
        )
        print(f"Email sent to {to_email}")
        return True
    except Exception as e:
        print(f"Email failed: {e}")
        print(f"Invite link: http://localhost:5173/set-password/{invite_token}")
        print(f"Temp password: {temp_password}")
        return False

# =====================================================
# Pydantic Models
# =====================================================
class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: str = "Viewer"  # ✅ NO full_name here - owner doesn't need to know the member's name

class TeamMemberResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    role: str
    status: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class RemoveMemberRequest(BaseModel):
    member_id: str

class UpdateRoleRequest(BaseModel):
    member_id: str
    role: str

class AcceptInviteRequest(BaseModel):
    full_name: str  # ✅ The member provides their name when accepting
    password: str = None

# =====================================================
# Get Team Members
# =====================================================
@router.get("/members", response_model=List[TeamMemberResponse])
def get_team_members(
    db: Session = Depends(get_main_db),
    current_user: User = Depends(get_current_user)
):
    # Get the current user's role in THIS workspace
    current_member = db.query(TeamMember).filter(
        TeamMember.user_id == str(current_user.id),
        TeamMember.workspace_id == str(current_user.workspace_id),
        TeamMember.status == "active"
    ).first()
    
    if not current_member:
        raise HTTPException(status_code=403, detail="Not a member of this workspace")
    
    # Get all members from the current user's workspace
    members = db.query(TeamMember).filter(
        TeamMember.workspace_id == str(current_user.workspace_id),
        TeamMember.status == "active"
    ).all()
    
    return members

# =====================================================
# Invite Member (Owner sends email only)
# =====================================================
@router.post("/invite")
def invite_member(
    request: InviteMemberRequest,
    db: Session = Depends(get_main_db),
    current_user: User = Depends(get_current_user)
):
    # Only owner can invite
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only workspace owner can invite members")
    
    # Check for existing ACTIVE member
    existing_active = db.query(TeamMember).filter(
        TeamMember.workspace_id == str(current_user.workspace_id),
        TeamMember.email == request.email,
        TeamMember.status == "active"
    ).first()
    if existing_active:
        raise HTTPException(status_code=400, detail="User is already an active team member")
    
    # Check for DELETED member
    existing_deleted = db.query(TeamMember).filter(
        TeamMember.workspace_id == str(current_user.workspace_id),
        TeamMember.email == request.email,
        TeamMember.status == "deleted"
    ).first()
    
    invite_token = secrets.token_urlsafe(32)
    temp_password = secrets.token_urlsafe(10)
    hashed_password = get_password_hash(temp_password)
    
    # Create or get user (without full_name - will be set when accepting)
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        user = User(
            email=request.email,
            full_name="",  # Empty - will be set when user accepts
            password_hash=hashed_password,
            workspace_id=current_user.workspace_id,
            role="member",
            is_active=True
        )
        db.add(user)
        db.flush()
    
    if existing_deleted:
        # Reactivate deleted member
        existing_deleted.status = "pending"
        existing_deleted.role = request.role
        existing_deleted.full_name = ""  # Empty - will be set when accepting
        existing_deleted.invite_token = invite_token
        existing_deleted.invited_by_user_id = str(current_user.id)
        existing_deleted.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(existing_deleted)
        new_member = existing_deleted
    else:
        # Create new team member without full_name
        new_member = TeamMember(
            user_id=str(user.id),
            workspace_id=str(current_user.workspace_id),
            email=request.email,
            full_name="",  # Empty - will be set when accepting
            role=request.role,
            status="pending",
            invited_by_user_id=str(current_user.id),
            invite_token=invite_token
        )
        db.add(new_member)
        db.flush()
    
    # Delete old invitation
    existing_invitation = db.query(Invitation).filter(
        Invitation.email == request.email,
        Invitation.workspace_id == str(current_user.workspace_id)
    ).first()
    if existing_invitation:
        db.delete(existing_invitation)
    
    # Create new invitation
    invitation = Invitation(
        email=request.email,
        workspace_id=str(current_user.workspace_id),
        workspace_name=f"{current_user.full_name}'s Workspace",
        role=request.role,
        invited_by=str(current_user.id),
        invited_by_name=current_user.full_name,
        token=invite_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(invitation)
    db.commit()
    db.refresh(new_member)
    
    # Send email
    workspace_name = f"{current_user.full_name}'s Workspace"
    send_invite_email(
        to_email=request.email,
        temp_password=temp_password,
        workspace_name=workspace_name,
        invited_by_name=current_user.full_name,
        invite_token=invite_token
    )
    
    return {"message": "Invitation sent successfully", "member_id": new_member.id}

# =====================================================
# Remove Member
# =====================================================
@router.delete("/member")
def remove_member(
    member_id: Optional[str] = Query(None),
    request: Optional[RemoveMemberRequest] = None,
    db: Session = Depends(get_main_db),
    current_user: User = Depends(get_current_user)
):
    member_id_value = member_id or (request.member_id if request else None)
    if not member_id_value:
        raise HTTPException(status_code=400, detail="member_id is required")
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only owner can remove members")
    member = db.query(TeamMember).filter(
        TeamMember.id == int(member_id_value),
        TeamMember.workspace_id == str(current_user.workspace_id)
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    # Soft delete
    member.status = "deleted"
    db.commit()
    # Delete any pending invitations
    invitation = db.query(Invitation).filter(
        Invitation.email == member.email,
        Invitation.workspace_id == str(current_user.workspace_id)
    ).first()
    if invitation:
        db.delete(invitation)
        db.commit()
    return {"message": "Member removed successfully"}

# =====================================================
# Update Role
# =====================================================
@router.put("/role")
def update_role(
    request: UpdateRoleRequest,
    db: Session = Depends(get_main_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "owner":
        raise HTTPException(status_code=403, detail="Only owner can change roles")
    member = db.query(TeamMember).filter(
        TeamMember.id == int(request.member_id),
        TeamMember.workspace_id == str(current_user.workspace_id)
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    member.role = request.role
    db.commit()
    return {"message": f"Role updated to {request.role}"}

# =====================================================
# Accept Invite (Member provides their full name here)
# =====================================================
@router.post("/accept-invite")
def accept_invitation(
    token: str,
    request: AcceptInviteRequest,
    db: Session = Depends(get_main_db)
):
    print(f"🔐 Accepting invitation for token: {token}")
    print(f"📝 Request data: full_name={request.full_name}, password={'provided' if request.password else 'not provided'}")
    
    invitation = db.query(Invitation).filter(
        Invitation.token == token,
        Invitation.expires_at > datetime.utcnow()
    ).first()
    
    if not invitation:
        print(f"❌ Invalid or expired token: {token}")
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")
    
    print(f"✅ Found invitation for email: {invitation.email}")
    
    # Check if user exists
    user = db.query(User).filter(User.email == invitation.email).first()
    
    if not user:
        hashed_password = get_password_hash(request.password) if request.password else None
        user = User(
            email=invitation.email,
            full_name=request.full_name,  # ✅ Use full_name
            password_hash=hashed_password,
            workspace_id=int(invitation.workspace_id),
            is_active=True,
            role="member"
        )
        db.add(user)
        db.flush()
        print(f"✅ Created new user: {user.email} with name: {user.full_name}")
    else:
        # Update existing user
        user.full_name = request.full_name  # ✅ Use full_name
        if request.password:
            user.password_hash = get_password_hash(request.password)
        user.is_active = True
        db.flush()
        print(f"✅ Updated existing user: {user.email} with name: {user.full_name}")
    
    # Update team member
    member = db.query(TeamMember).filter(
        TeamMember.workspace_id == invitation.workspace_id,
        TeamMember.email == invitation.email
    ).first()
    
    if member:
        member.user_id = str(user.id)
        member.full_name = request.full_name  # ✅ Use full_name
        member.status = "active"
        member.invite_token = None
        print(f"✅ Updated team member: {member.email}")
    
    # Delete the invitation
    db.delete(invitation)
    db.commit()
    
    print(f"🎉 Invitation accepted successfully for {invitation.email}")
    
    return {"message": "Invitation accepted", "workspace_id": invitation.workspace_id}

# =====================================================
# Test Endpoints
# =====================================================
@router.get("/ping")
def ping():
    return {"message": "Team router is working"}

@router.get("/my-role")
def get_my_role(
    db: Session = Depends(get_main_db),
    current_user: User = Depends(get_current_user)
):
    # Get the user's role in their CURRENT workspace
    team_member = db.query(TeamMember).filter(
        TeamMember.user_id == str(current_user.id),
        TeamMember.workspace_id == str(current_user.workspace_id),
        TeamMember.status == "active"
    ).first()
    
    if not team_member:
        return {"role": None}
    
    return {"role": team_member.role}