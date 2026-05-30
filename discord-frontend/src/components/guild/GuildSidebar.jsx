// src/components/guild/GuildSidebar.jsx
import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { selectGuild } from '../../store/slices/guildSlice';
import CreateGuildModal from './CreateGuildModal';
import { IoAdd } from 'react-icons/io5';

function GuildSidebar({ onOpenUserProfile }) {
  const dispatch = useDispatch();
  const { list: guilds, selectedGuild } = useSelector((state) => state.guilds);
  const { user } = useSelector((state) => state.auth);
  const [showCreateModal, setShowCreateModal] = useState(false);

  const handleSelectGuild = (guild) => {
    dispatch(selectGuild(guild));
  };

  return (
    <>
      <div className="w-20 bg-[#202225] flex flex-col items-center py-3 space-y-3">
        {/* User Avatar */}
        <button
          onClick={onOpenUserProfile}
          className="w-12 h-12 rounded-full bg-[#5865f2] flex items-center justify-center text-white font-bold text-xl hover:rounded-2xl transition-all duration-200"
        >
          {user?.username?.[0]?.toUpperCase()}
        </button>
        
        <div className="w-8 h-px bg-[#4f545c] my-2" />
        
        {/* Guild List */}
        <div className="flex-1 overflow-y-auto space-y-3">
          {guilds.map((guild) => (
            <button
              key={guild.id}
              onClick={() => handleSelectGuild(guild)}
              className={`w-12 h-12 rounded-full bg-[#2f3136] flex items-center justify-center text-white font-bold text-xl hover:rounded-2xl transition-all duration-200 ${
                selectedGuild?.id === guild.id ? 'rounded-2xl bg-[#5865f2]' : ''
              }`}
              title={guild.name}
            >
              {guild.name?.[0]?.toUpperCase()}
            </button>
          ))}
          
          {/* Add Guild Button */}
          <button
            onClick={() => setShowCreateModal(true)}
            className="w-12 h-12 rounded-full bg-[#2f3136] flex items-center justify-center text-[#3ba55d] text-2xl hover:rounded-2xl hover:bg-[#3ba55d] hover:text-white transition-all duration-200"
          >
            <IoAdd />
          </button>
        </div>
      </div>
      
      <CreateGuildModal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} />
    </>
  );
}

export default GuildSidebar;