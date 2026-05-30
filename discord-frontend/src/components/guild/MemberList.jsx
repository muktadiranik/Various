// src/components/guild/MemberList.jsx
import React, { useEffect } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { fetchGuildMembers } from '../../store/slices/guildSlice';
import OnlineStatus from '../presence/OnlineStatus';

function MemberList() {
  const dispatch = useDispatch();
  const { selectedGuild, members } = useSelector((state) => state.guilds);
  const { onlineUsers } = useSelector((state) => state.presence);

  useEffect(() => {
    if (selectedGuild) {
      dispatch(fetchGuildMembers(selectedGuild.id));
    }
  }, [dispatch, selectedGuild]);

  const onlineMembers = members.filter(m => onlineUsers[m.user_id]);
  const offlineMembers = members.filter(m => !onlineUsers[m.user_id]);

  return (
    <div className="w-60 bg-[#2f3136] flex flex-col">
      <div className="h-12 flex items-center px-4 shadow-md">
        <h3 className="text-[#b9bbbe] text-xs font-semibold uppercase">Members — {members.length}</h3>
      </div>

      <div className="flex-1 overflow-y-auto p-2">
        <div className="mb-4">
          <h4 className="text-[#8e9297] text-xs font-semibold uppercase mb-2">Online — {onlineMembers.length}</h4>
          {onlineMembers.map((member) => (
            <div key={member.user_id} className="flex items-center px-2 py-1 rounded hover:bg-[#4f545c] cursor-pointer">
              <OnlineStatus userId={member.user_id} />
              <span className="ml-2 text-[#dcddde] text-sm truncate">
                {member.nickname || member.username}
              </span>
            </div>
          ))}
        </div>

        <div>
          <h4 className="text-[#8e9297] text-xs font-semibold uppercase mb-2">Offline — {offlineMembers.length}</h4>
          {offlineMembers.map((member) => (
            <div key={member.user_id} className="flex items-center px-2 py-1 rounded hover:bg-[#4f545c] cursor-pointer">
              <div className="w-2 h-2 rounded-full bg-[#747f8d]"></div>
              <span className="ml-2 text-[#dcddde] text-sm truncate">
                {member.nickname || member.username}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default MemberList;