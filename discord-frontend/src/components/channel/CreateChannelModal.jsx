// src/components/channel/CreateChannelModal.jsx
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { createChannel, fetchChannels } from '../../store/slices/channelSlice';
import Modal from '../common/Modal';
import Button from '../common/Button';
import toast from 'react-hot-toast';

function CreateChannelModal({ isOpen, onClose }) {
  const dispatch = useDispatch();
  const { selectedGuild } = useSelector((state) => state.guilds);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    type: 'text',
    topic: '',
    is_private: false,
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedGuild) {
      toast.error('No server selected');
      return;
    }

    setLoading(true);
    try {
      await dispatch(createChannel({ 
        guildId: selectedGuild.id, 
        channelData: formData 
      })).unwrap();
      await dispatch(fetchChannels(selectedGuild.id));
      toast.success('Channel created successfully!');
      onClose();
      setFormData({ name: '', type: 'text', topic: '', is_private: false });
    } catch (error) {
      toast.error(error.message || 'Failed to create channel');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Channel">
      <form onSubmit={handleSubmit}>
        <div className="mb-4">
          <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
            Channel Type
          </label>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="radio"
                name="type"
                value="text"
                checked={formData.type === 'text'}
                onChange={handleChange}
                className="mr-2"
              />
              <span className="text-white">Text</span>
            </label>
            <label className="flex items-center">
              <input
                type="radio"
                name="type"
                value="voice"
                checked={formData.type === 'voice'}
                onChange={handleChange}
                className="mr-2"
              />
              <span className="text-white">Voice</span>
            </label>
          </div>
        </div>

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

        {formData.type === 'text' && (
          <div className="mb-4">
            <label className="block text-[#b9bbbe] text-sm font-semibold mb-2">
              Topic (Optional)
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
          <p className="text-[#72767d] text-sm mt-1">
            Private channels are only visible to users with permission.
          </p>
        </div>

        <div className="flex justify-end space-x-3">
          <Button variant="secondary" onClick={onClose} type="button">
            Cancel
          </Button>
          <Button variant="primary" type="submit" loading={loading}>
            Create
          </Button>
        </div>
      </form>
    </Modal>
  );
}

export default CreateChannelModal;