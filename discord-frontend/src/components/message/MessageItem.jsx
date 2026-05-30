// src/components/message/MessageItem.jsx
import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { formatDistanceToNow } from 'date-fns';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { updateMessage, deleteMessage, addReaction, removeReaction, pinMessage, unpinMessage } from '../../store/slices/messageSlice';
import { IoMdAdd, IoMdTrash, IoMdCreate, IoMdPin } from 'react-icons/io';
import toast from 'react-hot-toast';

function MessageItem({ message }) {
  const dispatch = useDispatch();
  const { user } = useSelector((state) => state.auth);
  const isAuthor = message.author_id === user?.id;
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(message.content);
  const [showReactions, setShowReactions] = useState(false);

  const handleUpdate = async () => {
    if (editContent.trim() === message.content) {
      setIsEditing(false);
      return;
    }
    try {
      await dispatch(updateMessage({ messageId: message.id, content: editContent })).unwrap();
      setIsEditing(false);
      toast.success('Message updated');
    } catch (error) {
      toast.error('Failed to update message');
    }
  };

  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this message?')) {
      try {
        await dispatch(deleteMessage(message.id)).unwrap();
        toast.success('Message deleted');
      } catch (error) {
        toast.error('Failed to delete message');
      }
    }
  };

  const handleAddReaction = async (emoji) => {
    try {
      await dispatch(addReaction({ messageId: message.id, emoji })).unwrap();
    } catch (error) {
      toast.error('Failed to add reaction');
    }
    setShowReactions(false);
  };

  const handleRemoveReaction = async (emoji) => {
    try {
      await dispatch(removeReaction({ messageId: message.id, emoji })).unwrap();
    } catch (error) {
      toast.error('Failed to remove reaction');
    }
  };

  const handlePin = async () => {
    try {
      if (message.is_pinned) {
        await dispatch(unpinMessage(message.id)).unwrap();
        toast.success('Message unpinned');
      } else {
        await dispatch(pinMessage(message.id)).unwrap();
        toast.success('Message pinned');
      }
    } catch (error) {
      toast.error('Failed to pin/unpin message');
    }
  };

  const commonReactions = ['👍', '❤️', '😂', '🎉', '🔥', '👏'];

  // Group reactions by emoji
  const reactionGroups = message.reactions?.reduce((acc, r) => {
    if (!acc[r.emoji]) {
      acc[r.emoji] = { count: 0, users: [] };
    }
    acc[r.emoji].count++;
    acc[r.emoji].users.push(r.user_id);
    return acc;
  }, {}) || {};

  return (
    <div className="group flex hover:bg-[#4f545c] hover:bg-opacity-30 rounded p-2 transition-colors">
      <div className="flex-shrink-0 mr-4">
        <div className="w-10 h-10 rounded-full bg-[#5865f2] flex items-center justify-center text-white font-bold">
          {message.author_username?.[0]?.toUpperCase()}
        </div>
      </div>
      
      <div className="flex-1">
        <div className="flex items-baseline space-x-2">
          <span className="font-semibold text-white">{message.author_username}</span>
          <span className="text-xs text-[#72767d]">
            {formatDistanceToNow(new Date(message.created_at), { addSuffix: true })}
          </span>
          {message.is_edited && (
            <span className="text-xs text-[#72767d]">(edited)</span>
          )}
          {message.is_pinned && (
            <IoMdPin className="text-[#faa81a] text-sm" />
          )}
        </div>
        
        {isEditing ? (
          <div className="mt-1">
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              className="w-full bg-[#202225] text-white rounded p-2 focus:outline-none focus:ring-2 focus:ring-[#5865f2]"
              rows={3}
            />
            <div className="flex space-x-2 mt-2">
              <button
                onClick={handleUpdate}
                className="px-3 py-1 bg-[#5865f2] text-white rounded text-sm hover:bg-[#4752c4]"
              >
                Save
              </button>
              <button
                onClick={() => setIsEditing(false)}
                className="px-3 py-1 bg-[#4f545c] text-white rounded text-sm hover:bg-[#5d6269]"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <div className="text-[#dcddde] prose prose-invert max-w-none">
            {message.is_deleted ? (
              <em className="text-[#72767d]">Message deleted</em>
            ) : (
              <ReactMarkdown
                components={{
                  code({ node, inline, className, children, ...props }) {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <SyntaxHighlighter
                        style={vscDarkPlus}
                        language={match[1]}
                        PreTag="div"
                        {...props}
                      >
                        {String(children).replace(/\n$/, '')}
                      </SyntaxHighlighter>
                    ) : (
                      <code className={className} {...props}>
                        {children}
                      </code>
                    );
                  }
                }}
              >
                {message.content}
              </ReactMarkdown>
            )}
          </div>
        )}
        
        {/* Reactions */}
        {Object.keys(reactionGroups).length > 0 && (
          <div className="flex flex-wrap gap-1 mt-2">
            {Object.entries(reactionGroups).map(([emoji, data]) => (
              <button
                key={emoji}
                onClick={() => handleRemoveReaction(emoji)}
                className="px-2 py-0.5 bg-[#4f545c] rounded text-sm hover:bg-[#5d6269] transition-colors"
              >
                {emoji} {data.count}
              </button>
            ))}
          </div>
        )}
      </div>
      
      {/* Action Buttons */}
      {!message.is_deleted && (
        <div className="hidden group-hover:flex space-x-1">
          <div className="relative">
            <button
              onClick={() => setShowReactions(!showReactions)}
              className="p-1 rounded hover:bg-[#4f545c]"
            >
              <IoMdAdd className="text-[#b9bbbe]" />
            </button>
            
            {showReactions && (
              <div className="absolute bottom-full mb-2 left-0 bg-[#2f3136] rounded-lg shadow-lg p-2 flex space-x-2 z-10">
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
          
          {isAuthor && (
            <button
              onClick={() => setIsEditing(true)}
              className="p-1 rounded hover:bg-[#4f545c]"
            >
              <IoMdCreate className="text-[#b9bbbe]" />
            </button>
          )}
          
          <button
            onClick={handlePin}
            className="p-1 rounded hover:bg-[#4f545c]"
          >
            <IoMdPin className={`text-[#b9bbbe] ${message.is_pinned ? 'text-[#faa81a]' : ''}`} />
          </button>
          
          <button
            onClick={handleDelete}
            className="p-1 rounded hover:bg-[#ed4245]"
          >
            <IoMdTrash className="text-[#b9bbbe]" />
          </button>
        </div>
      )}
    </div>
  );
}

export default MessageItem;