# app/core/permissions.py
from typing import List, Optional, Tuple
from dataclasses import dataclass
from app.core.constants import Permission


@dataclass
class RoleData:
    """Role data structure for permission calculation"""
    id: int
    name: str
    permissions: int
    position: int


@dataclass
class PermissionOverrideData:
    """Permission override data structure"""
    allow: int
    deny: int


class PermissionCalculator:
    """Utility class for calculating effective permissions"""
    
    @staticmethod
    def calculate_role_permissions(roles: List[RoleData]) -> int:
        """
        Calculate combined permissions from multiple roles.
        Uses bitwise OR to combine all role permissions.
        
        Args:
            roles: List of roles with their permissions
            
        Returns:
            Combined permissions as bitmask
        """
        if not roles:
            return 0
        
        permissions = 0
        for role in roles:
            permissions |= role.permissions
        
        return permissions
    
    @staticmethod
    def calculate_channel_permissions(
        base_permissions: int,
        role_overrides: List[Tuple[int, int]],
        member_overrides: List[Tuple[int, int]]
    ) -> int:
        """
        Calculate effective channel permissions considering overrides.
        
        Permission resolution order:
        1. Start with base permissions (guild-level)
        2. Apply role overrides (allow, then deny for each role)
        3. Apply member-specific overrides (allow, then deny)
        
        Args:
            base_permissions: Base permissions from guild roles
            role_overrides: List of (allow, deny) tuples for roles
            member_overrides: List of (allow, deny) tuples for member
            
        Returns:
            Effective permissions for channel
        """
        if base_permissions & Permission.ADMINISTRATOR:
            return Permission.all_permissions()
        
        effective = base_permissions
        
        # Apply role overrides
        for allow, deny in role_overrides:
            effective = (effective | allow) & ~deny
        
        # Apply member-specific overrides
        for allow, deny in member_overrides:
            effective = (effective | allow) & ~deny
        
        return effective
    
    @staticmethod
    def has_permission(permissions: int, required: Permission) -> bool:
        """
        Check if a permission is present in the bitmask.
        
        Args:
            permissions: Bitmask to check
            required: Required permission
            
        Returns:
            True if permission is present
        """
        return bool(permissions & required)
    
    @staticmethod
    def has_any_permission(permissions: int, *required: Permission) -> bool:
        """
        Check if any of the required permissions are present.
        
        Args:
            permissions: Bitmask to check
            required: List of required permissions
            
        Returns:
            True if any permission is present
        """
        combined = 0
        for perm in required:
            combined |= perm
        return bool(permissions & combined)
    
    @staticmethod
    def has_all_permissions(permissions: int, *required: Permission) -> bool:
        """
        Check if all required permissions are present.
        
        Args:
            permissions: Bitmask to check
            required: List of required permissions
            
        Returns:
            True if all permissions are present
        """
        combined = 0
        for perm in required:
            combined |= perm
        return (permissions & combined) == combined
    
    @staticmethod
    def add_permission(permissions: int, to_add: Permission) -> int:
        """Add a permission to the bitmask"""
        return permissions | to_add
    
    @staticmethod
    def remove_permission(permissions: int, to_remove: Permission) -> int:
        """Remove a permission from the bitmask"""
        return permissions & ~to_remove
    
    @staticmethod
    def toggle_permission(permissions: int, to_toggle: Permission) -> int:
        """Toggle a permission in the bitmask"""
        return permissions ^ to_toggle
    
    @staticmethod
    def get_highest_role_position(roles: List[RoleData]) -> int:
        """
        Get the highest position from user's roles.
        
        Args:
            roles: List of user's roles
            
        Returns:
            Highest role position
        """
        if not roles:
            return -1
        
        return max(role.position for role in roles)
    
    @staticmethod
    def can_manage_role(
        user_highest_position: int,
        target_role_position: int,
        user_permissions: int
    ) -> bool:
        """
        Check if user can manage a target role.
        
        Args:
            user_highest_position: User's highest role position
            target_role_position: Target role's position
            user_permissions: User's effective permissions
            
        Returns:
            True if user can manage the role
        """
        if PermissionCalculator.has_permission(user_permissions, Permission.ADMINISTRATOR):
            return True
        
        if PermissionCalculator.has_permission(user_permissions, Permission.MANAGE_ROLES):
            return user_highest_position > target_role_position
        
        return False
    
    @staticmethod
    def get_permissions_list(permissions: int) -> List[str]:
        """
        Get list of permission names from bitmask.
        
        Args:
            permissions: Bitmask to parse
            
        Returns:
            List of permission names
        """
        return [perm.name for perm in Permission if permissions & perm]
    
    @staticmethod
    def create_permission_string(permissions: int) -> str:
        """
        Create human-readable permission string.
        
        Args:
            permissions: Bitmask to format
            
        Returns:
            Comma-separated permission names
        """
        return ", ".join(PermissionCalculator.get_permissions_list(permissions))


class PermissionValidator:
    """Validation utilities for permission operations"""
    
    @staticmethod
    def validate_role_hierarchy(
        user_roles: List[RoleData],
        target_roles: List[RoleData],
        user_permissions: int
    ) -> bool:
        """
        Validate if user can modify target roles based on hierarchy.
        
        Args:
            user_roles: User's roles
            target_roles: Target user's roles
            user_permissions: User's effective permissions
            
        Returns:
            True if operation is allowed
        """
        if PermissionCalculator.has_permission(user_permissions, Permission.ADMINISTRATOR):
            return True
        
        user_highest = PermissionCalculator.get_highest_role_position(user_roles)
        target_highest = PermissionCalculator.get_highest_role_position(target_roles)
        
        return user_highest > target_highest
    
    @staticmethod
    def validate_channel_permission(
        effective_permissions: int,
        required: Permission,
        error_message: str = None
    ) -> None:
        """
        Validate channel permission and raise exception if missing.
        
        Args:
            effective_permissions: User's effective permissions
            required: Required permission
            error_message: Custom error message
            
        Raises:
            PermissionError: If permission is missing
        """
        if not PermissionCalculator.has_permission(effective_permissions, required):
            if error_message is None:
                error_message = f"Missing required permission: {required.name}"
            raise PermissionError(error_message)
    
    @staticmethod
    def validate_guild_permission(
        user_permissions: int,
        guild_owner_id: int,
        user_id: int,
        required: Permission
    ) -> bool:
        """
        Validate guild-level permission considering ownership.
        
        Args:
            user_permissions: User's effective permissions
            guild_owner_id: Owner ID of the guild
            user_id: User ID to check
            required: Required permission
            
        Returns:
            True if user has permission or is owner
        """
        if user_id == guild_owner_id:
            return True
        
        return PermissionCalculator.has_permission(user_permissions, required)