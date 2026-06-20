# backend/app/services/user_profile_service.py
from sqlalchemy.orm import Session
from datetime import datetime
from app.models.user import User
from app.services.auth_service import get_password_hash, verify_password

class UserProfileService:
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_by_id(self, user_id: int) -> User:  # Changed to int
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def update_profile(self, user_id: int, profile_data: dict) -> User:  # Changed to int
        """Update user profile"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None
        
        # Allowed fields for update
        updatable_fields = ['full_name', 'phone', 'company', 'job_title', 
                           'timezone', 'language', 'bio', 'avatar']
        
        for field in updatable_fields:
            if field in profile_data and profile_data[field] is not None:
                setattr(user, field, profile_data[field])
        
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        
        return user
    
    def change_password(self, user_id: int, current_password: str, new_password: str):  # Changed to int
        """Change user password"""
        user = self.get_user_by_id(user_id)
        if not user:
            return None, "User not found"
        
        if not verify_password(current_password, user.password_hash):
            return None, "Current password is incorrect"
        
        user.password_hash = get_password_hash(new_password)
        user.updated_at = datetime.utcnow()
        self.db.commit()
        
        return user, None 