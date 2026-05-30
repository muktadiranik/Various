// src/components/message/MessageList.jsx
import React, { useEffect, useRef, useCallback, useMemo } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchMessages } from '../../store/slices/messageSlice';
import MessageItem from './MessageItem';
import TypingIndicator from '../presence/TypingIndicator';
import LoadingSpinner from '../common/LoadingSpinner';

function MessageList() {
  const dispatch = useDispatch();
  const { selectedChannel } = useSelector((state) => state.channels);
  const { messages, loading, hasMore } = useSelector((state) => state.messages);
  const { typingUsers } = useSelector((state) => state.presence);
  const messagesEndRef = useRef(null);
  const containerRef = useRef(null);
  const isLoadingMore = useRef(false);
  const channelIdRef = useRef(null);

  const channelMessages = useMemo(() => {
    return messages[selectedChannel?.id] || [];
  }, [messages, selectedChannel?.id]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (channelMessages.length > 0) {
      scrollToBottom();
    }
  }, [channelMessages.length]);

  // Initial load of messages when channel changes
  useEffect(() => {
    if (selectedChannel && selectedChannel.id !== channelIdRef.current) {
      channelIdRef.current = selectedChannel.id;
      dispatch(fetchMessages({ channelId: selectedChannel.id, limit: 50 }));
    }
  }, [selectedChannel, dispatch]);

  const handleScroll = useCallback(async () => {
    if (!containerRef.current || isLoadingMore.current || !hasMore || loading) return;
    
    const { scrollTop } = containerRef.current;
    if (scrollTop === 0) {
      isLoadingMore.current = true;
      const oldestMessage = channelMessages[channelMessages.length - 1];
      if (oldestMessage && selectedChannel) {
        await dispatch(fetchMessages({
          channelId: selectedChannel.id,
          limit: 50,
          before: oldestMessage.created_at
        }));
      }
      isLoadingMore.current = false;
    }
  }, [channelMessages, hasMore, loading, selectedChannel, dispatch]);

  const currentTypingUsers = useMemo(() => {
    return typingUsers[selectedChannel?.id] || [];
  }, [typingUsers, selectedChannel?.id]);

  if (!selectedChannel) {
    return (
      <div className="flex-1 flex items-center justify-center">
        <p className="text-[#b9bbbe]">Select a channel to start chatting</p>
      </div>
    );
  }

  return (
    <div
      ref={containerRef}
      onScroll={handleScroll}
      className="flex-1 overflow-y-auto p-4 space-y-2"
    >
      {loading && channelMessages.length === 0 && (
        <div className="flex justify-center py-8">
          <LoadingSpinner />
        </div>
      )}
      
      {channelMessages.map((message) => (
        <MessageItem key={message.id} message={message} />
      ))}
      
      {currentTypingUsers.length > 0 && (
        <TypingIndicator users={currentTypingUsers} />
      )}
      
      <div ref={messagesEndRef} />
    </div>
  );
}

export default MessageList;