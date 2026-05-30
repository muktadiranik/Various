// src/components/channel/ChannelSettings.jsx
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { updateChannel, deleteChannel, fetchChannels } from '../../store/slices/channelSlice';
import Modal from '../common/Modal';
import Button from '../common/Button';
import toast from 'react-hot-toast';

function ChannelSettings({ channelId, onClose }) {
  const dispatch = useDispatch();
  const { selectedGuild } = useSelector((state) => state.guilds);
  const { list: channels } = useSelector((state) => state.channels);
  const channel = channels.find(c => c.id === channelId);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    topic: '',
    is_private: false,
  });

  useEffect(() => {
    if (channel) {
      setFormData({
        name: channel.name || '',
        topic: channel.topic || '',
        is_private: channel.is_private || false,
      });
    }
  }, [channel]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedGuild || !channel) return;
    
    setLoading(true);
    try {
      await dispatch(updateChannel({ channelId: channel.id, channelData: formData })).unwrap();
      await dispatch(fetchChannels(selectedGuild.id));
      toast.success('Channel updated successfully!');
      onClose();
    } catch (error) {
      toast.error(error.message || 'Failed to update channel');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!selectedGuild || !channel) return;
    if (window.confirm(`Are you sure you want to delete #${channel.name}? This action cannot be undone.`)) {
      setLoading(true);
      try {
        await dispatch(deleteChannel(channel.id)).unwrap();
        await dispatch(fetchChannels(selectedGuild.id));
        toast.success('Channel deleted');
        onClose();
      } catch (error) {
        toast.error(error.message || 'Failed to delete channel');
      } finally {
        setLoading(false);
      }
    }
  };

  if (!channel) return null;

  return (
    <Modal isOpen={true} onClose={onClose} title="Channel Settings" size="md">
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
            Channel Name
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

        {channel.type === 'text' && (
          <div className="mb-4">
            <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
              Topic
            </label>
            <input
              type="text"
              name="topic"
              value={formData.topic}
              onChange={handleChange}
              className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
              maxLength={1024}
            />
          </div>
        )}

        <div className="mb-6">
          <label className="flex items-center cursor-pointer">
            <input
              type="checkbox"
              name="is_private"
              checked={formData.is_private}
              onChange={(e) => setFormData({ ...formData, is_private: e.target.checked })}
              className="mr-2"
            />
            <span className="text-[#b9bbbe]">Private Channel</span>
          </label>
        </div>

        <div className="flex justify-between">
          <Button variant="danger" onClick={handleDelete} type="button" loading={loading}>
            Delete Channel
          </Button>
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

export default ChannelSettings;