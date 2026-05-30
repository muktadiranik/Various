// src/components/layout/MainLayout.jsx
import React, { useEffect, useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import GuildSidebar from '../guild/GuildSidebar';
import ChannelList from '../channel/ChannelList';
import ChannelHeader from '../channel/ChannelHeader';
import MessageList from '../message/MessageList';
import MessageInput from '../message/MessageInput';
import MemberList from '../guild/MemberList';
import GuildSettings from '../guild/GuildSettings';
import UserProfile from '../user/UserProfile';
import { fetchGuilds } from '../../store/slices/guildSlice';
import { fetchChannels } from '../../store/slices/channelSlice';
import websocketService from '../../services/websocketService';
import { addNewMessage, updateMessageInList, removeMessageFromList } from '../../store/slices/messageSlice';
import { updateUserPresence, addTypingUser, removeTypingUser } from '../../store/slices/presenceSlice';

function MainLayout() {
  const dispatch = useDispatch();
  const { selectedGuild } = useSelector((state) => state.guilds);
  const { selectedChannel } = useSelector((state) => state.channels);
  const [showGuildSettings, setShowGuildSettings] = useState(false);
  const [showUserProfile, setShowUserProfile] = useState(false);

  useEffect(() => {
    dispatch(fetchGuilds());
    
    const token = localStorage.getItem('token');
    if (token) {
      websocketService.connect(token);
      
      websocketService.on('new_message', (message) => {
        dispatch(addNewMessage({ channelId: message.channel_id, message }));
      });
      
      websocketService.on('message_updated', (data) => {
        dispatch(updateMessageInList({ messageId: data.message_id, updates: data.data }));
      });
      
      websocketService.on('message_deleted', (messageId) => {
        dispatch(removeMessageFromList(messageId));
      });
      
      websocketService.on('presence_update', (data) => {
        dispatch(updateUserPresence({ userId: data.user_id, status: data.status, guildId: data.guild_id }));
      });
      
      websocketService.on('user_typing', (data) => {
        if (data.action === 'start') {
          dispatch(addTypingUser({ channelId: data.channel_id, userId: data.user_id, username: data.username }));
          setTimeout(() => {
            dispatch(removeTypingUser({ channelId: data.channel_id, userId: data.user_id }));
          }, 3000);
        } else {
          dispatch(removeTypingUser({ channelId: data.channel_id, userId: data.user_id }));
        }
      });
    }
    
    return () => {
      websocketService.disconnect();
    };
  }, [dispatch]);

  useEffect(() => {
    if (selectedGuild) {
      dispatch(fetchChannels(selectedGuild.id));
      websocketService.joinGuild(selectedGuild.id);
    }
  }, [dispatch, selectedGuild]);

  useEffect(() => {
    if (selectedChannel) {
      websocketService.joinChannel(selectedChannel.id);
    }
  }, [selectedChannel]);

  return (
    <div className="flex h-screen bg-[#36393f]">
      <GuildSidebar onOpenUserProfile={() => setShowUserProfile(true)} />
      
      <div className="flex flex-1">
        <ChannelList />
        
        <div className="flex-1 flex flex-col">
          {selectedChannel ? (
            <>
              <ChannelHeader onOpenGuildSettings={() => setShowGuildSettings(true)} />
              <MessageList />
              <MessageInput />
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <h2 className="text-2xl font-bold text-white mb-2">Welcome to {selectedGuild?.name || 'Discord'}</h2>
                <p className="text-[#b9bbbe]">Select a channel to start chatting</p>
              </div>
            </div>
          )}
        </div>
        
        <MemberList />
      </div>
      
      {showGuildSettings && (
        <GuildSettings onClose={() => setShowGuildSettings(false)} />
      )}
      
      {showUserProfile && (
        <UserProfile onClose={() => setShowUserProfile(false)} />
      )}
    </div>
  );
}

export default MainLayout;