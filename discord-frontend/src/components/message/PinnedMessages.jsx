// src/components/message/PinnedMessages.jsx
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchPinnedMessages, unpinMessage } from '../../store/slices/messageSlice';
import Modal from '../common/Modal';
import LoadingSpinner from '../common/LoadingSpinner'
import MessageItem from './MessageItem';
import { IoMdPin } from 'react-icons/io';
import toast from 'react-hot-toast';

function PinnedMessages({ channelId, onClose }) {
  const dispatch = useDispatch();
  const { pinnedMessagesList } = useSelector((state) => state.messages);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (channelId) {
      setLoading(true);
      dispatch(fetchPinnedMessages(channelId)).finally(() => setLoading(false));
    }
  }, [dispatch, channelId]);

  const handleUnpin = async (messageId) => {
    try {
      await dispatch(unpinMessage(messageId)).unwrap();
      toast.success('Message unpinned');
      await dispatch(fetchPinnedMessages(channelId));
    } catch (error) {
      toast.error('Failed to unpin message');
    }
  };

  return (
    <Modal isOpen={true} onClose={onClose} title="Pinned Messages" size="lg">
      {loading ? (
        <div className="flex justify-center py-8">
          <LoadingSpinner />
        </div>
      ) : pinnedMessagesList.length === 0 ? (
        <div className="text-center py-8">
          <IoMdPin className="text-[#4f545c] text-4xl mx-auto mb-2" />
          <p className="text-[#b9bbbe]">No pinned messages</p>
          <p className="text-[#72767d] text-sm">Pin important messages to keep them visible</p>
        </div>
      ) : (
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {pinnedMessagesList.map((message) => (
            <div key={message.id} className="relative group">
              <MessageItem message={message} />
              <button
                onClick={() => handleUnpin(message.id)}
                className="absolute top-2 right-2 hidden group-hover:block p-1 rounded hover:bg-[#4f545c]"
              >
                <IoMdPin className="text-[#faa81a]" />
              </button>
            </div>
          ))}
        </div>
      )}
    </Modal>
  );
}

export default PinnedMessages;