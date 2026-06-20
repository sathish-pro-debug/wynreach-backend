# backend/app/routers/__init__.py
from fastapi import APIRouter
from . import auth
from . import users
from . import campaigns
from . import lists
from . import team
from . import sender_identity
from . import automation  # ✅ Make sure this is imported

router = APIRouter()

# Include routers
router.include_router(auth.router, prefix="/api/auth", tags=["auth"])
router.include_router(users.router, prefix="/api/users", tags=["users"])
router.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
router.include_router(lists.router, prefix="/api/lists", tags=["lists"])
router.include_router(team.router, prefix="/api/team", tags=["team"])
router.include_router(sender_identity.router, prefix="/api/sender-identity", tags=["sender-identity"])
router.include_router(automation.router, prefix="/api/automation", tags=["automation"])  # ✅ This should be here