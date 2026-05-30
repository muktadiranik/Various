// src/components/message/MessageReactions.jsx
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { addReaction, removeReaction } from '../../store/slices/messageSlice';
import { IoMdAdd } from 'react-icons/io';
import toast from 'react-hot-toast';

function MessageReactions({ messageId, reactions }) {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const [showPicker, setShowPicker] = useState(false);

  const commonReactions = ['👍', '❤️', '😂', '🎉', '🔥', '👏', '😮', '💯', '🙏', '👀'];

  const handleAddReaction = async (emoji) => {
    try {
      await dispatch(addReaction({ messageId, emoji })).unwrap();
    } catch (error) {
      toast.error('Failed to add reaction');
    }
    setShowPicker(false);
  };

  const handleRemoveReaction = async (emoji) => {
    try {
      await dispatch(removeReaction({ messageId, emoji })).unwrap();
    } catch (error) {
      toast.error('Failed to remove reaction');
    }
  };

  const hasReacted = (emoji) => {
    return reactions?.some(r => r.emoji === emoji && r.user_id === user?.id);
  };

  // Group reactions by emoji
  const reactionGroups = reactions?.reduce((acc, r) => {
    if (!acc[r.emoji]) {
      acc[r.emoji] = { count: 0, users: [] };
    }
    acc[r.emoji].count++;
    acc[r.emoji].users.push(r.user_id);
    return acc;
  }, {}) || {};

  if (Object.keys(reactionGroups).length === 0 && !showPicker) return null;

  return (
    <div className="flex flex-wrap gap-1 mt-2 items-center">
      {Object.entries(reactionGroups).map(([emoji, data]) => (
        <button
          key={emoji}
          onClick={() => handleRemoveReaction(emoji)}
          className={`px-2 py-0.5 rounded text-sm transition-colors ${
            hasReacted(emoji)
              ? 'bg-[#5865f2] text-white'
              : 'bg-[#4f545c] text-[#b9bbbe] hover:bg-[#5d6269]'
          }`}
        >
          {emoji} {data.count}
        </button>
      ))}
      
      <div className="relative">
        <button
          onClick={() => setShowPicker(!showPicker)}
          className="px-2 py-0.5 bg-[#4f545c] rounded text-sm text-[#b9bbbe] hover:bg-[#5d6269] transition-colors"
        >
          <IoMdAdd size={14} />
        </button>
        
        {showPicker && (
          <div className="absolute bottom-full mb-2 left-0 bg-[#2f3136] rounded-lg shadow-lg p-2 flex flex-wrap gap-1 z-10 max-w-xs">
            {commonReactions.map(emoji => (
              <button
                key={emoji}
                onClick={() => handleAddReaction(emoji)}
                className="text-xl hover:bg-[#4f545c] p-1 rounded transition-colors"
              >
                {emoji}
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default MessageReactions;