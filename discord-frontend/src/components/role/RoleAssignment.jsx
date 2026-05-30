// src/components/role/RoleAssignment.jsx
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchGuildMembers } from '../../store/slices/guildSlice';
import { assignRole, removeRole, fetchRoles } from '../../store/slices/roleSlice';
import Modal from '../common/Modal';
import LoadingSpinner from '../common/LoadingSpinner';
import { IoAdd, IoTrash } from 'react-icons/io5';
import toast from 'react-hot-toast';

function RoleAssignment({ role, isOpen, onClose }) {
  const dispatch = useDispatch();
  const { selectedGuild } = useSelector((state) => state.guilds);
  const { members, loading: membersLoading } = useSelector((state) => state.guilds);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [membersWithRole, setMembersWithRole] = useState([]);
  const [membersWithoutRole, setMembersWithoutRole] = useState([]);

  useEffect(() => {
    if (selectedGuild && isOpen) {
      dispatch(fetchGuildMembers(selectedGuild.id));
      dispatch(fetchRoles(selectedGuild.id));
    }
  }, [dispatch, selectedGuild, isOpen]);

  useEffect(() => {
    if (members.length > 0 && role) {
      const withRole = members.filter(m => 
        m.roles?.some(r => r.id === role.id)
      );
      const withoutRole = members.filter(m => 
        !m.roles?.some(r => r.id === role.id)
      );
      setMembersWithRole(withRole);
      setMembersWithoutRole(withoutRole);
    }
  }, [members, role]);

  const filteredMembersWithoutRole = membersWithoutRole.filter(m =>
    m.username.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (m.nickname && m.nickname.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  const handleAssign = async (userId) => {
    if (!selectedGuild || !role) return;
    setLoading(true);
    try {
      await dispatch(assignRole({ guildId: selectedGuild.id, userId, roleId: role.id })).unwrap();
      await dispatch(fetchGuildMembers(selectedGuild.id));
      toast.success(`Role assigned`);
    } catch (error) {
      toast.error('Failed to assign role');
    } finally {
      setLoading(false);
    }
  };

  const handleRemove = async (userId) => {
    if (!selectedGuild || !role) return;
    setLoading(true);
    try {
      await dispatch(removeRole({ guildId: selectedGuild.id, userId, roleId: role.id })).unwrap();
      await dispatch(fetchGuildMembers(selectedGuild.id));
      toast.success(`Role removed`);
    } catch (error) {
      toast.error('Failed to remove role');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Manage ${role?.name} Role`} size="lg">
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search members..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
        />
      </div>

      {membersLoading ? (
        <LoadingSpinner />
      ) : (
        <div className="grid grid-cols-2 gap-4">
          <div>
            <h4 className="text-[#b9bbbe] text-sm font-semibold mb-2">
              Members with role ({membersWithRole.length})
            </h4>
            <div className="space-y-1 max-h-96 overflow-y-auto">
              {membersWithRole.map((member) => (
                <div key={member.user_id} className="flex items-center justify-between p-2 bg-[#202225] rounded">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-[#5865f2] flex items-center justify-center text-white text-sm">
                      {member.username?.[0]?.toUpperCase()}
                    </div>
                    <span className="text-white text-sm truncate">
                      {member.nickname || member.username}
                    </span>
                  </div>
                  <button
                    onClick={() => handleRemove(member.user_id)}
                    disabled={loading}
                    className="p-1 text-[#b9bbbe] hover:text-[#ed4245] transition-colors"
                  >
                    <IoTrash size={16} />
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div>
            <h4 className="text-[#b9bbbe] text-sm font-semibold mb-2">
              Members without role ({filteredMembersWithoutRole.length})
            </h4>
            <div className="space-y-1 max-h-96 overflow-y-auto">
              {filteredMembersWithoutRole.map((member) => (
                <div key={member.user_id} className="flex items-center justify-between p-2 bg-[#202225] rounded">
                  <div className="flex items-center space-x-2">
                    <div className="w-8 h-8 rounded-full bg-[#5865f2] flex items-center justify-center text-white text-sm">
                      {member.username?.[0]?.toUpperCase()}
                    </div>
                    <span className="text-white text-sm truncate">
                      {member.nickname || member.username}
                    </span>
                  </div>
                  <button
                    onClick={() => handleAssign(member.user_id)}
                    disabled={loading}
                    className="p-1 text-[#b9bbbe] hover:text-[#3ba55d] transition-colors"
                  >
                    <IoAdd size={16} />
                  </button>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </Modal>
  );
}

export default RoleAssignment;