// src/components/message/MessageThread.jsx
import React, { useState, useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchThreadMessages, sendMessage } from '../../store/slices/messageSlice';
import MessageItem from './MessageItem';
import Modal from '../common/Modal';
import Button from '../common/Button';
import LoadingSpinner from '../common/LoadingSpinner'
import { IoArrowBack } from 'react-icons/io5';
import { toast } from 'react-hot-toast'

function MessageThread({ parentMessage, onClose }) {
  const dispatch = useDispatch();
  const { threads, loading } = useSelector((state) => state.messages);
  const threadMessages = threads[parentMessage?.id] || [];
  const [replyContent, setReplyContent] = useState('');

  useEffect(() => {
    if (parentMessage) {
      dispatch(fetchThreadMessages(parentMessage.id));
    }
  }, [dispatch, parentMessage]);

  const handleSendReply = async () => {
    if (!replyContent.trim() || !parentMessage) return;
    
    try {
      await dispatch(sendMessage({
        channelId: parentMessage.channel_id,
        content: replyContent,
        replyToId: parentMessage.id
      })).unwrap();
      setReplyContent('');
      await dispatch(fetchThreadMessages(parentMessage.id));
    } catch (error) {
      toast.error('Failed to send reply');
    }
  };

  return (
    <Modal isOpen={true} onClose={onClose} title="Thread" size="lg">
      <div className="mb-4 pb-4 border-b border-[#202225]">
        <div className="flex items-center space-x-2 mb-2">
          <button onClick={onClose} className="text-[#b9bbbe] hover:text-white">
            <IoArrowBack size={20} />
          </button>
          <span className="text-[#b9bbbe] text-sm">Thread</span>
        </div>
        <MessageItem message={parentMessage} isThreadParent />
      </div>
      
      <div className="max-h-96 overflow-y-auto space-y-2 mb-4">
        {loading ? (
          <div className="flex justify-center py-4">
            <LoadingSpinner size="sm" />
          </div>
        ) : (
          threadMessages.map((message) => (
            <MessageItem key={message.id} message={message} />
          ))
        )}
      </div>
      
      <div className="border-t border-[#202225] pt-4">
        <div className="flex space-x-2">
          <input
            type="text"
            value={replyContent}
            onChange={(e) => setReplyContent(e.target.value)}
            placeholder={`Reply to ${parentMessage?.author_username}...`}
            className="flex-1 bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
            onKeyPress={(e) => e.key === 'Enter' && handleSendReply()}
          />
          <Button variant="primary" size="sm" onClick={handleSendReply}>
            Reply
          </Button>
        </div>
      </div>
    </Modal>
  );
}

export default MessageThread;