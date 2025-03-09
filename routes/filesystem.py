# app/api/routes/filesystem.py
from fastapi import APIRouter, Depends, HTTPException
from api.services.filesystem import FileSystemService
from typing import List
from datetime import datetime
from api.models.entities import EntityResponse, Container
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

def get_filesystem_service() -> FileSystemService:
    return FileSystemService()

@router.post("/drives/{drive_name}")
def create_drive(drive_name: str, service: FileSystemService = Depends(get_filesystem_service)):
    try:
        drive = service.create_drive(drive_name)
        logger.info(f"Drive '{drive_name}' created successfully at {drive.path()}")
        return {"path": drive.path(), "created_at": drive.created_at}
    except ValueError as e:
        logger.warning(f"Failed to create drive '{drive_name}': {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/folders/{path:path}")
def create_folder(path: str, service: FileSystemService = Depends(get_filesystem_service)):
    path = path.strip('/')
    if not path:
        raise HTTPException(status_code=400, detail="Path is empty")
    parts = path.split('/')
    folder_name = parts[-1]
    parent_path = '/'.join(parts[:-1]) if len(parts) > 1 else ''
    
    if not parent_path:
        raise HTTPException(status_code=400, detail="Cannot create folder at root level. Use /drives endpoint to create a drive.")
    
    try:
        parent = service.resolve_path(parent_path)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    try:
        folder = service.create_folder(folder_name, parent)
        return {"path": folder.path(), "created_at": folder.created_at.isoformat()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    

@router.post("/files/{path:path}")
def create_file(
    path: str,
    service: FileSystemService = Depends(get_filesystem_service)
):
    """Create a new file at specified path"""
    path = path.strip('/')
    if not path:
        raise HTTPException(status_code=400, detail="Path cannot be empty")
    
    parts = path.split('/')
    if len(parts) < 2:
        raise HTTPException(
            status_code=400, 
            detail="File must be created within a drive or folder"
        )
    
    filename = parts[-1]
    parent_path = '/'.join(parts[:-1])
    
    try:
        parent = service.resolve_path(parent_path)
        #if not isinstance(parent, Container):
            #raise ValueError("Parent must be a drive or folder")
            
        file = service.create_file(filename, parent)
        return {
            "path": file.path(),
            "created_at": file.created_at.isoformat(),
            "content": file.content
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except KeyError as e:
        raise HTTPException(status_code=404, detail=f"Parent path not found: {parent_path}")


    



@router.get("/structure", response_model=List[EntityResponse])
def get_full_structure(service: FileSystemService = Depends(get_filesystem_service)):
    """Get complete file system hierarchy"""
    return service.get_structure()

@router.get("/entity/{path:path}", response_model=EntityResponse)
def get_entity(
    path: str,
    service: FileSystemService = Depends(get_filesystem_service)
):
    """Get specific entity by path"""
    try:
        entity = service._resolve_path(path)
        return service._entity_to_response(entity)
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))
    


@router.put("/entities/{old_path:path}/move/{new_path:path}")
def move_entity(
    old_path: str,
    new_path: str,
    service: FileSystemService = Depends(get_filesystem_service)
):
    try:
        # Resolve entity to move
        entity = service.resolve_path(old_path)
        
        # Split new path into parent path and new name
        new_path = new_path.strip('/')
        parts = new_path.split('/')
        if len(parts) < 1:
            raise ValueError("New path cannot be empty")
        if len(parts) == 1:
            raise ValueError("New path must include parent directory")
            
        parent_path = '/'.join(parts[:-1])
        new_name = parts[-1]

        # Resolve new parent
        new_parent = service.resolve_path(parent_path)
        if not isinstance(new_parent, Container):
            raise ValueError("Target parent must be a container (drive or folder)")

        # Perform the move
        service.move_entity(entity, new_parent, new_name)
        
        return {
            "status": "success",
            "new_path": entity.path(),
            "moved_at": datetime.now().isoformat()
        }
        
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error {str(e)}")
    

@router.delete("/entities/{path:path}")
def delete_entity(path: str, service: FileSystemService = Depends(get_filesystem_service)):
    try:
        entity = service._resolve_path(path)
        service.delete_entity(entity)
        return {"status": "success"}
    except (ValueError, KeyError) as e:
        raise HTTPException(status_code=404, detail=str(e))