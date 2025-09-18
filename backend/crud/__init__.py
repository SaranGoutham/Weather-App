# backend/crud/__init__.py
# keep this minimal to avoid import cycles / name mismatches
from . import user  # so you can do: from ..crud import user as user_crud
