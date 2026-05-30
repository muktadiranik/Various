// src/hooks/usePermissions.js
import { useSelector } from 'react-redux';
import { hasPermission as checkPermission } from '../utils/permissions';

function usePermissions() {
  const { selectedGuild } = useSelector((state) => state.guilds);
  const { user } = useSelector((state) => state.auth);
  const { roles } = useSelector((state) => state.roles);

  const isOwner = selectedGuild?.owner_id === user?.id;
  const userRoles = roles.filter(role => 
    role.members?.some(m => m.user_id === user?.id)
  );
  const highestRole = userRoles.length > 0 
    ? userRoles.reduce((max, role) => role.position > max.position ? role : max, userRoles[0])
    : null;

  const hasPermission = (permission) => {
    if (isOwner) return true;
    return userRoles.some(role => checkPermission(role.permissions, permission));
  };

  const hasAnyPermission = (permissions) => {
    if (isOwner) return true;
    return permissions.some(perm => hasPermission(perm));
  };

  const hasAllPermissions = (permissions) => {
    if (isOwner) return true;
    return permissions.every(perm => hasPermission(perm));
  };

  return {
    isOwner,
    userRoles,
    highestRole,
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
  };
}

export default usePermissions;