# app/api/v1/roles.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from app.dependencies import get_current_user, get_role_service, get_current_user_permissions
from app.services.role_service import RoleService
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, RoleAssign, RoleRemove

router = APIRouter(prefix="/roles", tags=["roles"])


@router.post("/", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    guild_id: int,
    role_data: RoleCreate,
    current_user: dict = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Create a new role in a guild"""
    try:
        role = await role_service.create_role(
            guild_id=guild_id,
            user_id=current_user["id"],
            user_permissions=user_permissions,
            role_data=role_data
        )
        return role
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/", response_model=List[RoleResponse])
async def get_guild_roles(
    guild_id: int,
    current_user: dict = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Get all roles in a guild"""
    try:
        roles = await role_service.get_guild_roles(
            guild_id=guild_id,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        return roles
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    current_user: dict = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Get role by ID"""
    try:
        roles = await role_service.get_guild_roles(0, current_user["id"], user_permissions)
        for role in roles:
            if role.id == role_id:
                return role
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.put("/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: int,
    role_data: RoleUpdate,
    current_user: dict = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Update a role"""
    try:
        role = await role_service.update_role(
            role_id=role_id,
            user_id=current_user["id"],
            user_permissions=user_permissions,
            role_data=role_data
        )
        if not role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
        return role
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: int,
    current_user: dict = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Delete a role"""
    try:
        success = await role_service.delete_role(
            role_id=role_id,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Role not found")
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/assign", response_model=dict)
async def assign_role(
    guild_id: int,
    assign_data: RoleAssign,
    current_user: dict = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Assign a role to a user"""
    try:
        success = await role_service.assign_role(
            guild_id=guild_id,
            target_user_id=assign_data.user_id,
            role_id=assign_data.role_id,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to assign role")
        return {"message": "Role assigned successfully"}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/remove", response_model=dict)
async def remove_role(
    guild_id: int,
    remove_data: RoleRemove,
    current_user: dict = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service),
    user_permissions: int = Depends(get_current_user_permissions)
):
    """Remove a role from a user"""
    try:
        success = await role_service.remove_role(
            guild_id=guild_id,
            target_user_id=remove_data.user_id,
            role_id=remove_data.role_id,
            user_id=current_user["id"],
            user_permissions=user_permissions
        )
        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to remove role")
        return {"message": "Role removed successfully"}
    except PermissionError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/user/{user_id}", response_model=List[RoleResponse])
async def get_user_roles(
    user_id: int,
    guild_id: int,
    current_user: dict = Depends(get_current_user),
    role_service: RoleService = Depends(get_role_service)
):
    """Get all roles of a user in a guild"""
    try:
        roles = await role_service.get_user_roles(guild_id, user_id)
        return roles
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))