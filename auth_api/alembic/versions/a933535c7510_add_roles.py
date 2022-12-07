"""add roles

Revision ID: a933535c7510
Revises: 6fcd9016f73a
Create Date: 2022-06-14 11:49:11.174542

"""
from alembic import op
import sqlalchemy as sa

from auth.models import db
from auth.models.users import Role


# revision identifiers, used by Alembic.
revision = 'a933535c7510'
down_revision = '6fcd9016f73a'
branch_labels = None
depends_on = None


def upgrade() -> None:
    roles_list = [
        {'name': 'admin', 'description': 'Superuser role'},
        {'name': 'user', 'description': 'Common user'},
    ]

    for role in roles_list:
        db_role = db.query(Role).filter_by(name=role['name']).first()
        if db_role is None:
            db_role = Role(name=role['name'], description=role['description'])
            db.add(db_role)

    db.commit()


def downgrade() -> None:
    pass
