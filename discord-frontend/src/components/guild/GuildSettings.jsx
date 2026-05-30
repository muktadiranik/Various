// src/components/guild/GuildSettings.jsx
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateGuild, deleteGuild } from '../../store/slices/guildSlice';
import Modal from '../common/Modal';
import Button from '../common/Button';
import toast from 'react-hot-toast';

function GuildSettings({ onClose }) {
  const dispatch = useDispatch();
  const { selectedGuild } = useSelector((state) => state.guilds);
  const { user } = useSelector((state) => state.auth);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_public: true,
    icon_url: '',
  });

  useEffect(() => {
    if (selectedGuild) {
      setFormData({
        name: selectedGuild.name || '',
        description: selectedGuild.description || '',
        is_public: selectedGuild.is_public ?? true,
        icon_url: selectedGuild.icon_url || '',
      });
    }
  }, [selectedGuild]);

  const isOwner = selectedGuild?.owner_id === user?.id;

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedGuild) return;
    
    setLoading(true);
    try {
      await dispatch(updateGuild({ guildId: selectedGuild.id, data: formData })).unwrap();
      toast.success('Server settings updated!');
      onClose();
    } catch (error) {
      toast.error(error.message || 'Failed to update server');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedGuild) return;
    if (window.confirm('Are you sure you want to delete this server? This action cannot be undone.')) {
      setLoading(true);
      try {
        await dispatch(deleteGuild(selectedGuild.id)).unwrap();
        toast.success('Server deleted');
        onClose();
      } catch (error) {
        toast.error(error.message || 'Failed to delete server');
      } finally {
        setLoading(false);
      }
    }
  };

  return (
    <Modal isOpen={true} onClose={onClose} title="Server Settings" size="lg">
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
            Server Name
          </label>
          <input
            type="text"
            name="name"
            value={formData.name}
            onChange={handleChange}
            className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
            required
            minLength={2}
            maxLength={100}
          />
        </div>

        <div className="mb-4">
          <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
            Description
          </label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
            rows={3}
            maxLength={500}
          />
        </div>

        <div className="mb-4">
          <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
            Server Icon URL
          </label>
          <input
            type="url"
            name="icon_url"
            value={formData.icon_url}
            onChange={handleChange}
            className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
            placeholder="https://example.com/icon.png"
          />
        </div>

        <div className="mb-6">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              name="is_public"
              checked={formData.is_public}
              onChange={(e) => setFormData({ ...formData, is_public: e.target.checked })}
              className="mr-2"
            />
            <span className="text-[#b9bbbe]">Public Server</span>
          </label>
          <p className="text-[#72767d] text-sm mt-1">
            Public servers can be discovered and joined by anyone.
          </p>
        </div>

        <div className="flex justify-between">
          {isOwner && (
            <Button variant="danger" onClick={handleDelete} type="button" loading={loading}>
              Delete Server
            </Button>
          )}
          <div className="flex space-x-3">
            <Button variant="secondary" onClick={onClose} type="button">
              Cancel
            </Button>
            <Button variant="primary" type="submit" loading={loading}>
              Save Changes
            </Button>
          </div>
        </div>
      </form>
    </Modal>
  );
}

export default GuildSettings;