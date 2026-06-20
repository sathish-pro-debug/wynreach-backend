import uuid
import secrets
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.team import TeamMember, Invitation


class TeamService:
    def __init__(self, db: Session):
        self.db = db

    async def get_team_members(self, workspace_id: str):
        members = self.db.query(TeamMember).filter(
            TeamMember.workspace_id == workspace_id
        ).all()
        return members

    async def invite_member(self, workspace_id: str, email: str, role: str,
                             invited_by: str, invited_by_name: str):
        try:
            existing = self.db.query(TeamMember).filter(
                TeamMember.workspace_id == workspace_id,
                TeamMember.email == email
            ).first()
            if existing:
                return None, "Member already exists in this workspace"
            member = TeamMember(
                id=str(uuid.uuid4()),
                workspace_id=workspace_id,
                email=email,
                role=role,
                status="pending",
                invited_by=invited_by
            )
            self.db.add(member)
            token = secrets.token_urlsafe(32)
            invitation = Invitation(
                id=str(uuid.uuid4()),
                email=email,
                workspace_id=workspace_id,
                role=role,
                invited_by=invited_by,
                invited_by_name=invited_by_name,
                token=token,
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            self.db.add(invitation)
            self.db.commit()
            self.db.refresh(member)
            return member, None
        except Exception as e:
            self.db.rollback()
            return None, str(e)

    async def accept_invitation(self, token: str, user_id: str, user_name: str):
        try:
            invitation = self.db.query(Invitation).filter(
                Invitation.token == token
            ).first()
            if not invitation:
                return None, "Invalid invitation token"
            if invitation.expires_at < datetime.utcnow():
                return None, "Invitation has expired"
            member = self.db.query(TeamMember).filter(
                TeamMember.workspace_id == invitation.workspace_id,
                TeamMember.email == invitation.email
            ).first()
            if member:
                member.user_id = user_id
                member.name = user_name
                member.status = "active"
                member.accepted_at = datetime.utcnow()
            self.db.delete(invitation)
            self.db.commit()
            return invitation.workspace_id, None
        except Exception as e:
            self.db.rollback()
            return None, str(e)

    async def update_role(self, member_id: str, new_role: str, workspace_id: str):
        try:
            member = self.db.query(TeamMember).filter(
                TeamMember.id == member_id,
                TeamMember.workspace_id == workspace_id
            ).first()
            if not member:
                return None, "Member not found"
            member.role = new_role
            self.db.commit()
            self.db.refresh(member)
            return member, None
        except Exception as e:
            self.db.rollback()
            return None, str(e)

    async def remove_member(self, member_id: str, workspace_id: str):
        try:
            member = self.db.query(TeamMember).filter(
                TeamMember.id == member_id,
                TeamMember.workspace_id == workspace_id
            ).first()
            if not member:
                return None, "Member not found"
            self.db.delete(member)
            self.db.commit()
            return member, None
        except Exception as e:
            self.db.rollback()
            return None, str(e)

    async def resend_invitation(self, email: str, workspace_id: str,
                                 invited_by: str, invited_by_name: str):
        try:
            old_inv = self.db.query(Invitation).filter(
                Invitation.email == email,
                Invitation.workspace_id == workspace_id
            ).first()
            if old_inv:
                self.db.delete(old_inv)
            token = secrets.token_urlsafe(32)
            invitation = Invitation(
                id=str(uuid.uuid4()),
                email=email,
                workspace_id=workspace_id,
                role="Viewer",
                invited_by=invited_by,
                invited_by_name=invited_by_name,
                token=token,
                expires_at=datetime.utcnow() + timedelta(days=7)
            )
            self.db.add(invitation)
            self.db.commit()
            self.db.refresh(invitation)
            return invitation, None
        except Exception as e:
            self.db.rollback()
            return None, str(e)