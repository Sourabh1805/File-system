# app/models/entities.py
from abc import ABC
from datetime import datetime
from typing import Dict, Optional, Union
from pydantic import BaseModel
from typing import List, Optional, Literal

class Entity(ABC):
    def __init__(self, name: str):
        self.name = name
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.parent: Optional['Container'] = None

    def path(self) -> str:
        path_parts = []
        current = self
        while current:
            path_parts.append(current.name)
            current = current.parent
        return '/' + '/'.join(reversed(path_parts))

class Container(Entity):
    def __init__(self, name: str):
        super().__init__(name)
        self.children: Dict[str, Union['Container', 'File']] = {}

    def add_child(self, child: Entity):
        if child.name in self.children:
            raise ValueError(f"Name '{child.name}' already exists")
        child.parent = self
        self.children[child.name] = child
        self.modified_at = datetime.now()

class Drive(Container):
    def path(self) -> str:
        return f"/{self.name}/"

class Folder(Container):
    pass

class File(Entity):
    def __init__(self, name: str, content: str = ""):
        super().__init__(name)
        self._content = content

    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str):
        self._content = value
        self.modified_at = datetime.now()

class EntityResponse(BaseModel):
    type: Literal["drive", "folder", "file"]
    name: str
    path: str
    created_at: str
    modified_at: str
    content: Optional[str] = None
    children: Optional[List['EntityResponse']] = None
