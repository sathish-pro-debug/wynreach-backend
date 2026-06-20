# app/routers/automation_rules.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_main_db
from app.models.automation_rule import AutomationRule
from pydantic import BaseModel
from typing import Optional, Dict, List
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/automation-rules", tags=["Automation Rules"])


class AutomationRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    campaign_id: str
    campaign_name: Optional[str] = None
    campaign_channel: str
    trigger_type: str
    trigger_config: Optional[Dict] = None
    condition_type: str = "always"
    condition_config: Optional[Dict] = None
    action_type: str
    action_config: Optional[Dict] = None


class AutomationRuleResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    campaign_id: str
    campaign_name: Optional[str]
    campaign_channel: str
    trigger_type: str
    trigger_config: Optional[Dict]
    condition_type: str
    condition_config: Optional[Dict]
    action_type: str
    action_config: Optional[Dict]
    is_active: bool
    execution_count: int
    created_at: datetime

    class Config:
        from_attributes = True


async def get_current_user():
    return {"id": "test_user_123"}


@router.post("/", response_model=AutomationRuleResponse)
async def create_rule(
    rule_data: AutomationRuleCreate,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Create a new automation rule"""
    
    try:
        new_rule = AutomationRule(
            id=str(uuid.uuid4()),
            # user_id=current_user["id"],  # ← Comment this out
            name=rule_data.name,
            description=rule_data.description,
            campaign_id=rule_data.campaign_id,
            campaign_name=rule_data.campaign_name,
            campaign_channel=rule_data.campaign_channel,
            trigger_type=rule_data.trigger_type,
            trigger_config=rule_data.trigger_config,
            condition_type=rule_data.condition_type,
            condition_config=rule_data.condition_config,
            action_type=rule_data.action_type,
            action_config=rule_data.action_config,
            is_active=True,
            execution_count=0
        )
        
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        
        return new_rule
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create rule: {str(e)}")


@router.get("/", response_model=List[AutomationRuleResponse])
async def get_rules(
    campaign_id: Optional[str] = None,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Get all automation rules"""
    
    query = db.query(AutomationRule)
    
    if campaign_id:
        query = query.filter(AutomationRule.campaign_id == campaign_id)
    
    return query.all()


@router.get("/{rule_id}", response_model=AutomationRuleResponse)
async def get_rule(
    rule_id: str,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Get a specific rule"""
    
    rule = db.query(AutomationRule).filter(
        AutomationRule.id == rule_id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    return rule


@router.patch("/{rule_id}/toggle")
async def toggle_rule(
    rule_id: str,
    is_active: bool,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Activate or deactivate a rule"""
    
    rule = db.query(AutomationRule).filter(
        AutomationRule.id == rule_id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule.is_active = is_active
    db.commit()
    
    return {"message": f"Rule {'activated' if is_active else 'deactivated'}"}


@router.delete("/{rule_id}")
async def delete_rule(
    rule_id: str,
    db: Session = Depends(get_main_db),
    current_user = Depends(get_current_user)
):
    """Delete a rule"""
    
    rule = db.query(AutomationRule).filter(
        AutomationRule.id == rule_id
    ).first()
    
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    db.delete(rule)
    db.commit()
    
    return {"message": "Rule deleted"}