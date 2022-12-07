from datetime import datetime
from typing import Optional, List
import uuid

from sqlalchemy.orm import Session
from werkzeug.exceptions import NotFound
from auth.models.users import User, UserLoginHistory, UserRole,\
    UserOAuthRefreshToken
from auth.services.roles import RoleService
from auth.utils.http_query_helper import decode_pagination


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def is_user_exists(self, user_email: str) -> bool:
        user = self.db.query(User).filter(User.email == user_email).first()
        return True if user else False

    def get_all_users(self) -> Optional[List[User]]:
        return self.db.query(User).all()

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        user = self.db.query(User).get(user_id)
        if user is None:
            raise NotFound(f'User with id {user_id} not found')

        return user

    def get_user_by_universal_email(self,
                                    email: Optional[str] = None):
        return self.db.query(User).filter(
            User.email == email).first()

    def get_user_login_history(
            self,
            user_id: str,
            page_number: int = 1,
            page_size: int = 50,
    ) -> Optional[List[UserLoginHistory]]:
        query = self.db.query(UserLoginHistory).filter(
            UserLoginHistory.user_id == user_id)

        start_index, end_index = decode_pagination(page_number, page_size)
        user_login_history = query.slice(start_index, end_index).all()

        return user_login_history

    def create_user(self,
                    email: str,
                    password: str,
                    first_name: str = None,
                    last_name: str = None,
                    phone: str = None) -> Optional[User]:
        new_user = User(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
        )
        self.db.add(new_user)
        self.db.commit()

        return new_user

    def update_user(self,
                    user_id: str,
                    user_data: dict) -> Optional[User]:
        user = self.db.query(User).get(user_id)
        user.email=user_data.get('email')
        user.first_name=user_data.get('first_name')
        user.last_name=user_data.get('last_name')
        user.phone=user_data.get('phone')

        self.db.add(user)
        self.db.commit()

        return user

    def deactivate_user(self, user_id: str) -> bool:
        user = self.db.query(User).get(user_id)
        user.active = False
        self.db.add(user)
        self.db.commit()

        return True

    def create_super_user(self, email: str, password: str, first_name: str,
                          last_name: str) -> User:
        user = self.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        self.db.add(user)
        self.db.flush()

        role_service = RoleService(self.db)
        role = role_service.get_role_by_name('admin')

        user_role_link = UserRole(user_id=user.id, role_id=role.id)
        self.db.add(user_role_link)

        self.db.commit()

        return user

    def get_user_roles(self, user_id: str):
        user = self.get_user_by_id(user_id)

        return [role.role for role in user.roles]

    def add_role_to_user(self, user_id: str, role_id: str):
        user = self.get_user_by_id(user_id)
        role_service = RoleService(self.db)
        role = role_service.get_role_by_id(role_id)

        user_role_link = self.db.query(UserRole)\
            .filter_by(user_id=user.id, role_id=role.id)\
            .first()

        if user_role_link is None:
            user_role_link = UserRole(user_id=user.id, role_id=role.id)
            self.db.add(user_role_link)
            self.db.commit()

        return user_role_link.id

    def remove_role_to_user(self, user_id: str, role_id: str):
        user_role_link = self.db.query(UserRole)\
            .filter_by(user_id=user_id, role_id=role_id)\
            .first()

        if user_role_link:
            self.db.delete(user_role_link)
            self.db.commit()

        return True

    def get_user_oauth_refresh_token(self, user_id: str, provider: str):
        token = (
            self.db.query(UserOAuthRefreshToken)
            .filter(UserOAuthRefreshToken.user_id == user_id,
                    UserOAuthRefreshToken.provider == provider)
            .first()
        )

        if token:
            return token.refresh_token
        else:
            return None

    def save_user_oauth_refresh_token(self,
                                      user_id: str,
                                      provider: str,
                                      refresh_token: str,
                                      expires_in: int):
        existing_tokens = (
            self.db.query(UserOAuthRefreshToken)
            .filter(UserOAuthRefreshToken.user_id == user_id)
            .all()
        )

        for existing_token in existing_tokens:
            self.db.delete(existing_token)

        new_token = UserOAuthRefreshToken(
            user_id=user_id,
            provider=provider,
            refresh_token=refresh_token,
            expires_in=expires_in,
        )

        self.db.add(new_token)
        self.db.commit()
