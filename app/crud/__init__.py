
# app/crud/__init__.py
from app.crud.user_crud import UserCRUD
from app.crud.ipdr_crud import IPDRLogCRUD

# Create singleton instances for dependency injection
user_crud = UserCRUD()
ipdr_crud = IPDRLogCRUD()

__all__ = ["user_crud", "ipdr_crud", "UserCRUD", "IPDRLogCRUD"]