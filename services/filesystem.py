# app/services/filesystem.py
from typing import Dict, List
from api.models.entities import Drive, Folder, File, Container, Entity, EntityResponse
import logging

logger = logging.getLogger(__name__)

class FileSystemService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize only once
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if not self.__initialized:
            self.drives: Dict[str, Drive] = {}
            self.__initialized = True

    def create_drive(self, name: str) -> Drive:
        if name in self.drives:
            logger.warning("Drive already exsits")
            raise ValueError(f"Drive {name} already exists")
        drive = Drive(name)
        self.drives[name] = drive
        return drive


    def create_folder(self, name: str, parent: Container) -> Folder:
        if not isinstance(parent, Container):
            raise ValueError("Parent must be a container")
        folder = Folder(name)
        parent.add_child(folder)
        return folder

    def create_file(self, name: str, parent: Container) -> File:
        if not isinstance(parent, Container):
            raise ValueError("Parent must be a container")
        file = File(name)
        parent.add_child(file)
        return file

    def delete_entity(self, entity: Entity):
        if isinstance(entity, Drive):
            del self.drives[entity.name]
        elif entity.parent:
            del entity.parent.children[entity.name]
        else:
            raise ValueError("Cannot delete entity without parent")
    
    def move_entity(self, entity: Entity, new_parent: Container, new_name: str):
        # Existing checks
        if isinstance(entity, Drive):
            raise ValueError("Cannot move drives")
        if entity.parent is None:
            raise ValueError("Entity must have a parent to move")
        if new_name in new_parent.children:
            raise ValueError(f"Name '{new_name}' already exists in target")
    
        # Prevent moving into own subtree
        current = new_parent
        while current is not None:
            if current == entity:
                raise ValueError("Cannot move entity into its own subtree")
            current = current.parent
    
        # Remove from old parent and rename
        del entity.parent.children[entity.name]
        entity.name = new_name

        # Add to new parent
        new_parent.add_child(entity)
    
    
    def get_structure(self) -> List[EntityResponse]:
        return [self._entity_to_response(drive) for drive in self.drives.values()]

    def _entity_to_response(self, entity: Entity) -> EntityResponse:
        """Recursively convert entity hierarchy to response model"""
        response = EntityResponse(
            type=self._get_entity_type(entity),
            name=entity.name,
            path=entity.path(),
            created_at=entity.created_at.isoformat(),
            modified_at=entity.modified_at.isoformat(),
        )

        if isinstance(entity, Container):
            response.children = [
                self._entity_to_response(child)
                for child in entity.children.values()
            ]
        elif isinstance(entity, File):
            response.content = entity.content
            
        return response

    def _get_entity_type(self, entity: Entity) -> str:
        if isinstance(entity, Drive):
            return "drive"
        if isinstance(entity, Folder):
            return "folder"
        return "file"
    
    def resolve_path(self, path: str) -> Entity:
        """Resolve /C/Documents/file.txt to actual entity"""
        path = path.strip("/")
        parts = path.split("/")
        
        if not parts:
            raise ValueError("Invalid path")
            
        # Start from drive
        drive_name = parts[0]
        if drive_name not in self.drives:
            raise ValueError(f"Drive {drive_name} not found")
            
        current: Entity = self.drives[drive_name]
        
        for part in parts[1:]:
            if not isinstance(current, Container):
                raise ValueError(f"{current.name} is not a container")
                
            if part not in current.children:
                raise ValueError(f"Path segment {part} not found")
                
            current = current.children[part]
            
        return current
    
    def _resolve_path(self, path: str) -> Entity:
        path = path.strip("/")
        parts = path.split("/")
    
        if not parts:
            raise ValueError("Invalid path")
        
        drive_name = parts[0]
        if drive_name not in self.drives:
            raise ValueError(f"Drive {drive_name} not found")
        
        current: Entity = self.drives[drive_name]
    
        for part in parts[1:]:
            if not isinstance(current, Container):
                raise ValueError(f"{current.name} is not a container")
            
            if part not in current.children:
                raise ValueError(f"Path segment {part} not found")
            
            current = current.children[part]
        
        return current
    
# app/services/filesystem.py
