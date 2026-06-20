# app/models/__init__.py
# =====================================================
# USER MODELS
# =====================================================
from .user import (
    User,
    Workspace,
    RefreshToken,
)

# =====================================================
# SENDER IDENTITY MODELS
# =====================================================
from .sender_identity import (
    EmailDomain,
    EmailAddress,
    WhatsAppNumber
)

# =====================================================
# CONTACT & LIST MODELS
# =====================================================
from .contact import Contact
from .lists import (
    AudienceList,
    ListContact
)

# =====================================================
# SUPPRESSION MODEL
# =====================================================
from .suppression import Suppression

# =====================================================
# TEAM MODELS
# =====================================================
from .team import TeamMember, Invitation

# =====================================================
# AUTOMATION MODELS
# =====================================================
from .automation import (
    AutomationRule,
    RuleExecution,
    AutomationSequence,
    SequenceExecution
)
from .message_log import MessageLog
from .notification import Notification

from .automation import (
    AutomationRule,
    RuleExecution,
    AutomationSequence,
    SequenceExecution
)

# =====================================================
# EXPORTS
# =====================================================
__all__ = [
    # USERS
    'User',
    'Workspace',
    'RefreshToken',
    
    # SENDER IDENTITIES
    'EmailDomain',
    'EmailAddress',
    'WhatsAppNumber',
    
    # CONTACTS
    'Contact',
    
    # LISTS
    'AudienceList',
    'ListContact',
    
    # SUPPRESSION
    'Suppression',
    
    # TEAM
    'TeamMember',
    'Invitation',
    
    # AUTOMATIONS
    'AutomationRule',
    'RuleExecution',
    'AutomationSequence',
    'SequenceExecution',
    'Notification',
    'MessageLog',
]

