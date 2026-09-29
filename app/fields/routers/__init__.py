from fastapi import APIRouter

router = APIRouter(prefix="/fields", tags=["fields"])

# Order matters: the search router (/find-by-point) must be included before the CRUD
# router, otherwise "find-by-point" would be captured by /{field_id}.
