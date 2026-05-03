from fastapi import APIRouter
from .auth import router as auth
from .users import router as users
from .servers import router as servers
from .channels import router as channels
