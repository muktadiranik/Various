// src/components/message/MessageInput.jsx
import React, { useState, useRef, useEffect } from 'react';
import { useSelector } from 'react-redux';
import websocketService from '../../services/websocketService';
import Button from '../common/Button';
import toast from 'react-hot-toast';

function MessageInput() {
  const { selectedChannel } = useSelector((state) => state.channels);
  const { selectedGuild } = useSelector((state) => state.guilds);
  const [content, setContent] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const typingTimeoutRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [content]);

  const handleTyping = () => {
    if (!isTyping && selectedChannel && selectedGuild) {
      setIsTyping(true);
      websocketService.startTyping(selectedChannel.id, selectedGuild.id);
    }
    
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    
    typingTimeoutRef.current = setTimeout(() => {
      if (isTyping && selectedChannel) {
        setIsTyping(false);
        websocketService.stopTyping(selectedChannel.id);
      }
    }, 2000);
  };

  const handleSend = () => {
    if (!content.trim()) return;
    if (!selectedChannel) {
      toast.error('No channel selected');
      return;
    }
    
    websocketService.sendMessage(selectedChannel.id, content.trim());
    setContent('');
    
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current);
    }
    if (isTyping) {
      setIsTyping(false);
      websocketService.stopTyping(selectedChannel.id);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!selectedChannel) {
    return (
      <div className="h-24 bg-[#404249] p-4 rounded-lg mx-4 mb-4 flex items-center justify-center">
        <p className="text-[#b9bbbe]">Select a channel to start messaging</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="bg-[#404249] rounded-lg">
        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => {
            setContent(e.target.value);
            handleTyping();
          }}
          onKeyDown={handleKeyDown}
          placeholder={`Message #${selectedChannel.name}`}
          className="w-full bg-transparent text-white p-3 resize-none focus:outline-none"
          rows={1}
        />
        <div className="flex justify-end p-2">
          <Button
            variant="primary"
            size="sm"
            onClick={handleSend}
            disabled={!content.trim()}
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}

export default MessageInput;