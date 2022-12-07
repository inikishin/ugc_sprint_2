"""Create auth tables

Revision ID: 6fcd9016f73a
Revises: 
Create Date: 2022-06-08 16:43:09.294845

"""
from alembic import op
import uuid
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '6fcd9016f73a'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  default=uuid.uuid4,
                  unique=True, nullable=False),
        sa.Column('email', sa.String, unique=True, nullable=False),
        sa.Column('password', sa.String, nullable=False),
        sa.Column('first_name', sa.String, nullable=True),
        sa.Column('last_name', sa.String, nullable=True),
        sa.Column('phone', sa.String, nullable=True),
        sa.Column('active', sa.Boolean, default=True),
        sa.Column('last_login_at', sa.DateTime, nullable=True),
        sa.Column('current_login_at', sa.DateTime, nullable=True),
        sa.Column('last_login_ip', sa.String, nullable=True),
        sa.Column('current_login_ip', sa.String, nullable=True),
        sa.Column('login_count', sa.Integer, nullable=True),
    )

    op.create_table(
        'roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  default=uuid.uuid4,
                  unique=True, nullable=False),
        sa.Column('name', sa.String, unique=True, nullable=False),
        sa.Column('description', sa.String),
    )

    op.create_table(
        'user_login_history',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4,
               unique=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id'),
               nullable=False),
        sa.Column('user_agent', sa.String, nullable=True),
        sa.Column('login_ip', sa.String, nullable=True),
        sa.Column('login_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'user_oauth_refresh_token',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  default=uuid.uuid4,
                  unique=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id'),
                  nullable=False),
        sa.Column('provider', sa.String, nullable=True),
        sa.Column('refresh_token', sa.String, nullable=True),
        sa.Column('expires_in', sa.Integer, nullable=True),
    )

    op.create_table(
        'refresh_tokens',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  default=uuid.uuid4,
                  unique=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id'), unique=True,
                  nullable=False),
        sa.Column('token', sa.String, nullable=True),
        sa.Column('expires_at', sa.DateTime, nullable=True),
    )

    op.create_table(
        'user_roles',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True,
                  default=uuid.uuid4,
                  unique=True, nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('users.id'),
                  nullable=False),
        sa.Column('role_id', postgresql.UUID(as_uuid=True),
                  sa.ForeignKey('roles.id'),
                  nullable=False),
    )


def downgrade() -> None:
    op.drop_table('user_oauth_refresh_token')
    op.drop_table('user_login_history')
    op.drop_table('refresh_tokens')
    op.drop_table('user_roles')
    op.drop_table('roles')
    op.drop_table('users')
