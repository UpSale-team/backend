from typing import Dict, AnyStr, List
from pydantic import BaseModel, Field
from ..providers import user_db
from ..utils.utils import get_current_time
from ..utils.constants import PLACEHOLDER_IMAGE


class UserModel(BaseModel):
    id: str = Field(..., title="User ID")
    name: str = Field(..., title="User Name")
    email: str = Field(..., title="User Email")
    avatar: str = Field(..., title="User Avatar")
    projects: list[str] = Field(None, title="User Projects")
    created_at: str = Field(..., title="User Created At")


class UserMinimalModel(BaseModel):
    id: str = Field(..., title="User ID")
    name: str = Field(..., title="User Name")
    email: str = Field(..., title="User Email")
    avatar: str = Field(..., title="User Avatar")


class UserSchema:
    def __init__(
        self,
        uid: AnyStr = None,
        name: AnyStr = "",
        email: AnyStr = "",
        avatar: AnyStr = PLACEHOLDER_IMAGE,
        projects: List[AnyStr] = [],
        created_at: AnyStr = get_current_time(),
    ):
        self.id = uid
        self.name = name
        self.email = email
        self.avatar = avatar
        self.projects = projects
        self.created_at = created_at

    def to_dict(self, include_id=True, minimal=False):
        data_dict = {
            "name": self.name,
            "email": self.email,
            "avatar": self.avatar,
        }
        if not minimal:
            data_dict["projects"] = self.projects
            data_dict["created_at"] = self.created_at
        if include_id:
            data_dict["id"] = self.id
        return data_dict

    @staticmethod
    def from_dict(data: Dict):
        return UserSchema(
            uid=data.get("id"),
            name=data.get("name"),
            email=data.get("email"),
            avatar=data.get("avatar"),
            projects=data.get("projects"),
            created_at=data.get("created_at"),
        )

    @staticmethod
    def find_all():
        users = user_db.get_all()
        return [UserSchema.from_dict(user) for user in users]

    @staticmethod
    def find_by_email(email: AnyStr):
        queries = user_db.query_equal("email", email)
        if len(queries) == 0:
            return None
        return UserSchema.from_dict(queries[0])

    @staticmethod
    def find_by_id(uid: AnyStr):
        data = user_db.get_by_id(uid)
        if not data:
            return None
        return UserSchema.from_dict(data)

    @staticmethod
    def find_all_by_ids(uids: List[AnyStr]):
        users = user_db.get_all_by_ids(uids)
        return [UserSchema.from_dict(user) for user in users if user]

    @staticmethod
    def find_user_by_substring(substring: AnyStr):
        users = user_db.query_similar("email", substring)
        return [UserSchema.from_dict(user) for user in users]

    def create_user(self):
        user_id = user_db.create(self.to_dict(include_id=False))
        self.id = user_id
        return self

    def update_user_projects(self, project_id: AnyStr, is_add: bool, key: AnyStr = "projects"):
        if is_add:
            setattr(self, key, list(
                set(getattr(self, key)) | set([project_id])))
        else:
            setattr(self, key, list(
                set(getattr(self, key)) - set([project_id])))
        user_db.update(self.id, {f"{key}": getattr(self, key)})