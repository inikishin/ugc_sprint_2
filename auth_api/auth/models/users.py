import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from werkzeug.security import generate_password_hash, check_password_hash

from auth.models import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    active = Column(Boolean, default=True)
    last_login_at = Column(DateTime, nullable=True)
    current_login_at = Column(DateTime, nullable=True)
    last_login_ip = Column(String, nullable=True)
    current_login_ip = Column(String, nullable=True)
    login_count = Column(Integer, nullable=True)

    login_history = relationship('UserLoginHistory', back_populates='user')
    refresh_token = relationship('RefreshToken', back_populates='user')
    oauth_refresh_tokens = relationship('UserOAuthRefreshToken', back_populates='user')
    roles = relationship('UserRole', back_populates='user')

    def __init__(self, password=None, **kwargs):
        super(User, self).__init__(**kwargs)

        if password is not None:
            self.set_password(password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def __repr__(self):
        return f'<User {self.email} (id: {self.id})>'


def create_partition(target, connection, **kw) -> None:
    """ creating partition by user_sign_in """
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_login_history_y2022" PARTITION OF "user_login_history" FOR VALUES FROM ('2022-01-01') TO ('2022-12-31')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_login_history_y2023" PARTITION OF "user_login_history" FOR VALUES FROM ('2023-01-01') TO ('2023-12-31')"""
    )
    connection.execute(
        """CREATE TABLE IF NOT EXISTS "user_login_history_y2024" PARTITION OF "user_login_history" FOR VALUES FROM ('2024-01-01') TO ('2024-12-31')"""
    )


class UserLoginHistory(Base):
    __tablename__ = 'user_login_history'
    __table_args__ = (
        {
            'postgresql_partition_by': 'RANGE (login_at)',
            'listeners': [('after_create', create_partition)],
        }
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='login_history')
    user_agent = Column(String, nullable=True)
    login_ip = Column(String, nullable=True)
    login_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'<UserLoginHistory: {self.id}>'


class UserOAuthRefreshToken(Base):
    __tablename__ = 'user_oauth_refresh_token'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    user = relationship('User', back_populates='oauth_refresh_tokens')
    provider = Column(String, nullable=True)
    refresh_token = Column(String, nullable=True)
    expires_in = Column(Integer, nullable=True)

    def __repr__(self):
        return f'<UserOAuthRefreshToken: {self.id}>'


class RefreshToken(Base):
    __tablename__ = 'refresh_tokens'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), unique=True,
                     nullable=False)
    user = relationship('User', back_populates='refresh_token')
    token = Column(String, nullable=True)
    expires_at = Column(DateTime, nullable=True)

    def __repr__(self):
        return f'<RefreshToken: {self.token}>'


class Role(Base):
    __tablename__ = 'roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    users = relationship('UserRole', back_populates='role')

    def __repr__(self):
        return f'<Role {self.name} (id: {self.id})>'


class UserRole(Base):
    __tablename__ = 'user_roles'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
                unique=True, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    role_id = Column(UUID(as_uuid=True), ForeignKey('roles.id'), nullable=False)
    user = relationship('User', back_populates='roles')
    role = relationship('Role', back_populates='users')
