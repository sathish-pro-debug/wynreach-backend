# backend/app/schemas/automation.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum

class RuleStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    DRAFT = "draft"

class TriggerType(str, Enum):
    CONTACT_ADDED_TO_LIST = "contact_added_to_list"
    TAG_APPLIED = "tag_applied"
    CAMPAIGN_LINK_CLICKED = "campaign_link_clicked"
    DATE_FIELD = "date_field"
    MESSAGE_SENT = "message_sent"
    MESSAGE_DELIVERED = "message_delivered"
    MESSAGE_READ = "message_read"
    MESSAGE_REPLIED = "message_replied"

class ConditionType(str, Enum):
    ALWAYS = "always"
    FIELD_EQUALS = "field_equals"
    TAG_EXISTS = "tag_exists"

class ActionType(str, Enum):
    SEND_EMAIL_CAMPAIGN = "send_email_campaign"
    SEND_WHATSAPP_MESSAGE = "send_whatsapp_message"
    ADD_TO_LIST = "add_to_list"
    REMOVE_FROM_LIST = "remove_from_list"
    ADD_TAG = "add_tag"
    REMOVE_TAG = "remove_tag"
    NOTIFY_TEAM = "notify_team"

# Trigger Configs
class ContactAddedToListConfig(BaseModel):
    list_name: str

class TagAppliedConfig(BaseModel):
    tag: str

class CampaignLinkClickedConfig(BaseModel):
    link: str

class DateFieldConfig(BaseModel):
    field: str
    value: str

class MessageEventConfig(BaseModel):
    message_id: Optional[str] = None
    contact_id: Optional[int] = None

# Condition Configs
class FieldEqualsConfig(BaseModel):
    field: str
    value: str

class TagExistsConfig(BaseModel):
    tag: str

# Action Configs
class SendEmailCampaignConfig(BaseModel):
    campaign_id: str
    campaign_name: str

class SendWhatsAppMessageConfig(BaseModel):
    template_name: str
    message: str

class AddToListConfig(BaseModel):
    list_name: str

class AddTagConfig(BaseModel):
    tag_name: str

class NotifyTeamConfig(BaseModel):
    message: str

# Main Rule Schema
class AutomationRuleCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_type: TriggerType
    trigger_config: Dict[str, Any]
    condition_type: ConditionType = ConditionType.ALWAYS
    condition_config: Dict[str, Any] = {}
    action_type: ActionType
    action_config: Dict[str, Any]

class AutomationRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[RuleStatus] = None
    trigger_type: Optional[TriggerType] = None
    trigger_config: Optional[Dict[str, Any]] = None
    condition_type: Optional[ConditionType] = None
    condition_config: Optional[Dict[str, Any]] = None
    action_type: Optional[ActionType] = None
    action_config: Optional[Dict[str, Any]] = None

class AutomationRuleResponse(BaseModel):
    id: str
    workspace_id: int
    name: str
    description: Optional[str]
    status: RuleStatus
    trigger_type: TriggerType
    trigger_config: Dict[str, Any]
    condition_type: ConditionType
    condition_config: Dict[str, Any]
    action_type: ActionType
    action_config: Dict[str, Any]
    total_triggered: int
    last_triggered_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

class RuleExecutionResponse(BaseModel):
    id: str
    rule_id: str
    contact_id: Optional[int]
    triggered_at: datetime
    status: str
    details: Dict[str, Any]

    # backend/app/schemas/automation.py

class AutomationSequenceResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    campaign_id: str
    campaign_name: Optional[str]
    campaign_channel: Optional[str]
    steps: TypingList[Dict]
    status: str
    total_triggered: int
    completed_count: int
    last_resume_at: Optional[str]
    created_at: str
    updated_at: str