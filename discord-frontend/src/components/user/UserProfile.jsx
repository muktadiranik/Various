// src/components/user/UserProfile.jsx
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateUser } from '../../store/slices/authSlice';
import Modal from '../common/Modal';
import Button from '../common/Button';
import toast from 'react-hot-toast';

function UserProfile({ onClose }) {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    avatar_url: '',
  });

  useEffect(() => {
    if (user) {
      setFormData({
        username: user.username || '',
        email: user.email || '',
        avatar_url: user.avatar_url || '',
      });
    }
  }, [user]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await dispatch(updateUser(formData)).unwrap();
      toast.success('Profile updated successfully!');
      onClose();
    } catch (error) {
      toast.error(error.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={true} onClose={onClose} title="User Profile" size="md">
      <form onSubmit={handleSubmit}>
        <div className="flex justify-center mb-6">
          <div className="w-24 h-24 rounded-full bg-[#5865f2] flex items-center justify-center text-white text-3xl font-bold">
            {formData.username?.[0]?.toUpperCase() || 'U'}
          </div>
        </div>

        <div className="mb-4">
          <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
            Username
          </label>
          <input
            type="text"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
            required
            minLength={2}
            maxLength={32}
          />
        </div>

        <div className="mb-4">
          <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
            Email
          </label>
          <input
            type="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
            required
          />
        </div>

        <div className="mb-6">
          <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
            Avatar URL (Optional)
          </label>
          <input
            type="url"
            name="avatar_url"
            value={formData.avatar_url}
            onChange={handleChange}
            className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
            placeholder="https://example.com/avatar.jpg"
          />
        </div>

        <div className="flex justify-end space-x-3">
          <Button variant="secondary" onClick={onClose} type="button">
            Cancel
          </Button>
          <Button variant="primary" type="submit" loading={loading}>
            Save Changes
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default UserProfile;