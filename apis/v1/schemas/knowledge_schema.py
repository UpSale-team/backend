from typing import AnyStr, Dict
import enum 
from pydantic import BaseModel, Field
from ..providers import storage_db, knowledge_db
from ..utils.utils import get_current_time


class KnowledgeModel(BaseModel):
    id: str = Field(None, title="Knowledge ID")
    name: str = Field("", title="Knowledge Name")
    path: str = Field("", title="Knowledge Path")
    url: str = Field("", title="Knowledge URL")
    content: str = Field("", title="Knowledge Content")
    upload_at: str = Field("", title="Knowledge Upload At")


class KnowledgeSchema:

    def __init__(self,
                 knowledge_id: AnyStr = None,
                 name: AnyStr = "",
                 path: AnyStr = "",
                 url: AnyStr = "",
                 content: AnyStr = "",
                 upload_at: AnyStr = get_current_time()):
        self.id = knowledge_id
        self.name = name
        self.path = path
        self.url = url
        self.content = content
        self.upload_at = upload_at


    def to_dict(self, include_id=True):
        data_dict = {
            "name": self.name,
            "path": self.path,
            "url": self.url,
            "content": self.content,
            "upload_at": self.upload_at
        }
        if include_id:
            data_dict["id"] = self.id
        return data_dict
    
    @staticmethod
    def from_dict(data: Dict):
        return KnowledgeSchema(
            cv_id=data.get("id"),
            name=data.get("name"),
            path=data.get("path"),
            url=data.get("url"),
            content=data.get("content"),
            upload_at=data.get("upload_at")
        )
    
        
    @staticmethod
    def find_by_ids(knowledge_ids: list[AnyStr]):
        return [KnowledgeSchema.from_dict(knowledge) for knowledge in knowledge_db.get_all_by_ids(knowledge_ids)
    
    ]


    @staticmethod
    def find_by_id(knowledge_id: AnyStr):
        data = knowledge_db.get_by_id(knowledge_id)
        if not data:
            return None
        return KnowledgeSchema.from_dict(data)
    
    def create_knowledge(self):
        knowledge_id = knowledge_db.create(self.to_dict(include_id=False))  # Tạo document trong database
        self.id = knowledge_id  # Lưu lại ID sau khi tạo
        return self  # Trả về đối tượng KnowledgeSchema

    def update_path_url(self, path: AnyStr, url: AnyStr):
        """Cập nhật đường dẫn và URL cho đối tượng Knowledge."""
        self.path = path  # Cập nhật đường dẫn mới
        self.url = url  # Cập nhật URL mới
        knowledge_db.update(self.id, {  # Cập nhật document trong database
            "path": path,
            "url": url
        })
    
    def download_content(self) -> AnyStr:
        """Tải nội dung của file đã upload."""
        try:
            return storage_db.download(self.path)
        except Exception as e:
            return None

    def delete_knowledge(self) -> bool:
        """Xóa file đã upload và document khỏi Firebase."""
        try:
            # Xóa document từ Firebase
            knowledge_db.delete(self.id)
            # Xóa file từ storage (nếu cần)
            storage_db.remove(self.path)  # Phương thức xóa file trong storage
            return True  # Trả về True nếu xóa thành công
        except Exception as e:
            return False  # Trả về False nếu có lỗi

    def update_knowledge(self, new_path: str, new_data: Dict) -> bool:
        """Cập nhật file đã upload và dữ liệu trong Firebase."""
        try:
            # Xóa file cũ
            self.delete_knowledge()
            # Upload file mới
            storage_db.upload(new_path)  # Giả sử bạn có phương thức upload trong storage
            # Cập nhật document trong Firebase
            storage_db.update(self.id, new_data)  # Cập nhật dữ liệu mới vào Firebase
            self.path = new_path  # Cập nhật đường dẫn file mới
            return True  # Trả về True nếu cập nhật thành công
        except Exception as e:
            return False  # Trả về False nếu có lỗi
        
    def update_content(self, content: AnyStr):
        self.content = content
        knowledge_db.update(self.id, {
            "content": content
        })