// src/components/guild/CreateGuildModal.jsx
import React, { useState } from 'react';
import { useDispatch } from 'react-redux';
import { createGuild } from '../../store/slices/guildSlice';
import Modal from '../common/Modal';
import Button from '../common/Button';
import toast from 'react-hot-toast';

function CreateGuildModal({ isOpen, onClose }) {
  const dispatch = useDispatch();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    is_public: true,
  });

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await dispatch(createGuild(formData)).unwrap();
      toast.success('Guild created successfully!');
      onClose();
      setFormData({ name: '', description: '', is_public: true });
    } catch (error) {
      toast.error(error.message || 'Failed to create guild');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create a Server">
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
            Description (Optional)
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
            Public servers can be joined by anyone. Private servers require an invite.
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

export default CreateGuildModal;