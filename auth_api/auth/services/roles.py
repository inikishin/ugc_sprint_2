from typing import Optional, List
import uuid

from sqlalchemy.orm import Session
from werkzeug.exceptions import NotFound

from auth.models.users import Role


class RoleService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def is_role_exists(self, role_name: str) -> bool:
        role = self.db.query(Role).filter(Role.name == role_name).first()
        return True if role else False

    def get_all_roles(self) -> Optional[List[Role]]:
        return self.db.query(Role).all()

    def get_role_by_id(self, role_id: str) -> Optional[Role]:
        role = self.db.query(Role).get(role_id)
        if role is None:
            raise NotFound(f'Role with id {role_id} not found')
        return role

    def get_role_by_name(self, role_name: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.name == role_name).first()

    def create_role(self, role_name: str,
                    role_description: str = None) -> Optional[Role]:
        new_role = Role(
            name=role_name,
            description=role_description,
        )
        self.db.add(new_role)
        self.db.commit()

        return new_role

    def update_role(self, role_id: str, role_name: str,
                    role_description: str = None) -> Optional[Role]:
        role = self.db.query(Role).get(role_id)

        if role is None:
            raise NotFound(f'Role with id {role_id} not found')

        role.name = role_name
        role.description = role_description

        self.db.add(role)
        self.db.commit()

        return role

    def delete_role(self, role_id: uuid.UUID) -> bool:
        role = self.db.query(Role).get(role_id)

        for user_link in role.users:
            self.db.delete(user_link)

        self.db.delete(role)
        self.db.commit()

        return True
