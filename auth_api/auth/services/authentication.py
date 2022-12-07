from datetime import datetime
import os
from typing import Optional

from flask_jwt_extended import create_access_token, create_refresh_token
from werkzeug.exceptions import BadRequest, Unauthorized

from auth.main import jwt_redis_blocklist
from auth.models.users import User, RefreshToken, UserLoginHistory
from auth.utils.opentelemetry_tracer import trace


class AuthService:
    def __init__(self, db):
        self.db = db

    def generate_tokens_for_user(self, user):
        additional_claims = {
            "last_name": user.last_name,
            "first_name": user.first_name,
            "email": user.email,
            'role_names': [role.role.name for role in user.roles],
        }

        access_token = create_access_token(identity=user.id,
                                           additional_claims=additional_claims)

        refresh_token = create_refresh_token(identity=user.id)

        db_refresh_token = self.db.query(RefreshToken) \
            .filter(RefreshToken.user_id == user.id) \
            .first()
        if db_refresh_token is None:
            db_refresh_token = RefreshToken()

        db_refresh_token.user_id = user.id
        db_refresh_token.token = refresh_token

        self.db.add(db_refresh_token)
        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    @trace(span_name='login service')
    def login(self, login: str, password: str, user_agent: str, ip: str) -> dict:
        login_user = self.db.query(User).filter_by(email=login).first()

        if login_user is None:
            raise BadRequest(f'User with login {login} not found')

        if not login_user.verify_password(password):
            raise BadRequest('Incorrect password')

        data = self.generate_tokens_for_user(login_user)

        login_user.last_login_at = datetime.now()
        login_user.last_seen_at = datetime.now()
        self.db.add(login_user)

        login_history = UserLoginHistory(
            user_id=login_user.id,
            user_agent=user_agent,
            login_ip=ip,
            login_at=datetime.now())
        self.db.add(login_history)

        self.db.commit()

        return data

    def refresh(self, user_id: str, refresh_token: str) -> Optional[dict]:
        db_refresh_token = self.db.query(RefreshToken)\
            .filter(RefreshToken.user_id == user_id)\
            .first()

        if db_refresh_token:
            if db_refresh_token.token == refresh_token:
                data = self.generate_tokens_for_user(db_refresh_token.user)

                return data

        raise Unauthorized

    def logout(self, user_id: str, jti: str) -> bool:
        db_refresh_token = self.db.query(RefreshToken) \
            .filter(RefreshToken.user_id == user_id) \
            .first()

        if db_refresh_token:
            self.db.delete(db_refresh_token)
            self.db.commit()

        jwt_redis_blocklist.set(jti,
                                "",
                                ex= os.getenv('JWT_ACCESS_TOKEN_EXPIRES', 60))

        return True
