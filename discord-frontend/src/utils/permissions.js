// src/utils/permissions.js
export const hasPermission = (permissions, required) => {
  return (permissions & required) === required;
};

export const hasAnyPermission = (permissions, requiredList) => {
  return requiredList.some(required => (permissions & required) === required);
};

export const addPermission = (permissions, toAdd) => {
  return permissions | toAdd;
};

export const removePermission = (permissions, toRemove) => {
  return permissions & ~toRemove;
};

export const getHighestRole = (roles) => {
  if (!roles || roles.length === 0) return null;
  return roles.reduce((highest, role) => role.position > highest.position ? role : highest, roles[0]);
};

export const canManageRole = (userHighestPosition, targetRolePosition, userPermissions) => {
  if (hasPermission(userPermissions, PERMISSIONS.ADMINISTRATOR)) return true;
  if (hasPermission(userPermissions, PERMISSIONS.MANAGE_ROLES)) {
    return userHighestPosition > targetRolePosition;
  }
  return false;
};