// src/components/role/CreateRoleModal.jsx
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { createRole } from '../../store/slices/roleSlice';
import Modal from '../common/Modal';
import Button from '../common/Button';
import PermissionSelector from './PermissionSelector';
import toast from 'react-hot-toast';

function CreateRoleModal({ isOpen, onClose }) {
  const dispatch = useDispatch();
  const { selectedGuild } = useSelector((state) => state.guilds);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    permissions: 0,
    position: 0,
    is_mentionable: false,
    is_hoisted: false,
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handlePermissionChange = (permissions) => {
    setFormData({ ...formData, permissions });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedGuild) return;
    
    setLoading(true);
    try {
      await dispatch(createRole({ guildId: selectedGuild.id, roleData: formData })).unwrap();
      toast.success('Role created successfully!');
      onClose();
      setFormData({ name: '', permissions: 0, position: 0, is_mentionable: false, is_hoisted: false });
    } catch (error) {
      toast.error(error.message || 'Failed to create role');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Role" size="lg">
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
            Role Name
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
            required
            minLength={1}
            maxLength={100}
          />
        </div>

        <div className="mb-4">
          <label className="flex items-center cursor-pointer mb-2">
            <input
              type="checkbox"
              name="is_mentionable"
              checked={formData.is_mentionable}
              onChange={(e) => setFormData({ ...formData, is_mentionable: e.target.checked })}
              className="mr-2"
            />
            <span className="text-[#b9bbbe]">Allow anyone to @mention this role</span>
          </label>
        </div>

        <div className="mb-4">
          <label className="flex items-center cursor-pointer mb-2">
            <input
              type="checkbox"
              name="is_hoisted"
              checked={formData.is_hoisted}
              onChange={(e) => setFormData({ ...formData, is_hoisted: e.target.checked })}
              className="mr-2"
            />
            <span className="text-[#b9bbbe]">Display role members separately from online members</span>
          </label>
        </div>

        <div className="mb-6">
          <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
            Permissions
          </label>
          <PermissionSelector
            permissions={formData.permissions}
            onChange={handlePermissionChange}
          />
        </div>

        <div className="flex justify-end space-x-3">
          <Button variant="secondary" onClick={onClose} type="button">
            Cancel
          </Button>
          <Button variant="primary" type="submit" loading={loading}>
            Create Role
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default CreateRoleModal;