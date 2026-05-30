// src/components/guild/GuildList.jsx
import React from 'react';
import { useSelector } from 'react-redux';
import { motion } from 'framer-motion';

function GuildList({ onSelectGuild, selectedGuildId }) {
  const { list: guilds } = useSelector((state) => state.guilds);

  return (
    <div className="space-y-2">
      {guilds.map((guild, index) => (
        <motion.button
          key={guild.id}
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: index * 0.05 }}
          onClick={() => onSelectGuild(guild)}
          className={`w-12 h-12 rounded-full bg-[#2f3136] flex items-center justify-center text-white font-bold text-xl hover:rounded-2xl transition-all duration-200 ${
            selectedGuildId === guild.id ? 'rounded-2xl bg-[#5865f2]' : ''
          }`}
          title={guild.name}
        >
          {guild.name?.[0]?.toUpperCase()}
        </motion.button>
      ))}
    </div>
  );
}

export default GuildList;