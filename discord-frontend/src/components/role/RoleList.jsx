// src/components/role/RoleList.jsx
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchRoles, deleteRole } from '../../store/slices/roleSlice';
import CreateRoleModal from './CreateRoleModal';
import RoleAssignment from './RoleAssignment';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner'
import { IoAdd, IoTrash, IoPencil } from 'react-icons/io5';
import toast from 'react-hot-toast';

function RoleList() {
  const dispatch = useDispatch();
  const { selectedGuild } = useSelector((state) => state.guilds);
  const { list: roles, loading } = useSelector((state) => state.roles);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState(null);
  const [showAssignment, setShowAssignment] = useState(false);

  useEffect(() => {
    if (selectedGuild) {
      dispatch(fetchRoles(selectedGuild.id));
    }
  }, [dispatch, selectedGuild]);

  const handleDeleteRole = async (roleId, roleName) => {
    if (roleName === '@everyone') {
      toast.error('Cannot delete the @everyone role');
      return;
    }
    if (window.confirm(`Are you sure you want to delete the ${roleName} role?`)) {
      try {
        await dispatch(deleteRole(roleId)).unwrap();
        toast.success('Role deleted');
      } catch (error) {
        toast.error('Failed to delete role');
      }
    }
  };

  if (!selectedGuild) return null;

  return (
    <div className="bg-[#2f3136] rounded-lg p-4">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-white font-semibold">Roles ({roles.length})</h3>
        <Button variant="primary" size="sm" onClick={() => setShowCreateModal(true)}>
          <IoAdd className="mr-1" /> Create Role
        </Button>
      </div>

      {loading ? (
        <LoadingSpinner />
      ) : (
        <div className="space-y-2">
          {roles.map((role) => (
            <div
              key={role.id}
              className="flex items-center justify-between p-3 bg-[#202225] rounded-lg hover:bg-[#1a1c1f] transition-colors"
            >
              <div className="flex items-center space-x-3">
                <div
                  className="w-4 h-4 rounded-full"
                  style={{ backgroundColor: `hsl(${role.id * 137 % 360}, 70%, 50%)` }}
                />
                <span className="text-white">{role.name}</span>
                <span className="text-[#72767d] text-sm">
                  {role.member_count || 0} members
                </span>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={() => {
                    setSelectedRole(role);
                    setShowAssignment(true);
                  }}
                  className="p-1 text-[#b9bbbe] hover:text-white transition-colors"
                >
                  <IoPencil size={18} />
                </button>
                {role.name !== '@everyone' && (
                  <button
                    onClick={() => handleDeleteRole(role.id, role.name)}
                    className="p-1 text-[#b9bbbe] hover:text-[#ed4245] transition-colors"
                  >
                    <IoTrash size={18} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <CreateRoleModal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} />
      
      {selectedRole && (
        <RoleAssignment
          role={selectedRole}
          isOpen={showAssignment}
          onClose={() => {
            setShowAssignment(false);
            setSelectedRole(null);
          }}
        />
      )}
    </div>
  );
}

export default RoleList;