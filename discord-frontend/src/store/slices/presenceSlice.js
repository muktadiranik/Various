// src/store/slices/presenceSlice.js
import { createSlice } from '@reduxjs/toolkit';

const presenceSlice = createSlice({
  name: 'presence',
  initialState: {
    onlineUsers: {},
    typingUsers: {},
  },
  reducers: {
    updateUserPresence: (state, action) => {
      const { userId, status, guildId } = action.payload;
      if (status === 'online') {
        state.onlineUsers[userId] = { status, guildId, lastSeen: new Date().toISOString() };
      } else {
        delete state.onlineUsers[userId];
      }
    },
    addTypingUser: (state, action) => {
      const { channelId, userId, username } = action.payload;
      if (!state.typingUsers[channelId]) {
        state.typingUsers[channelId] = [];
      }
      if (!state.typingUsers[channelId].find(u => u.userId === userId)) {
        state.typingUsers[channelId].push({ userId, username });
      }
    },
    removeTypingUser: (state, action) => {
      const { channelId, userId } = action.payload;
      if (state.typingUsers[channelId]) {
        state.typingUsers[channelId] = state.typingUsers[channelId].filter(u => u.userId !== userId);
        if (state.typingUsers[channelId].length === 0) {
          delete state.typingUsers[channelId];
        }
      }
    },
    clearTypingUsers: (state, action) => {
      const { channelId } = action.payload;
      delete state.typingUsers[channelId];
    },
  },
});

export const { updateUserPresence, addTypingUser, removeTypingUser, clearTypingUsers } = presenceSlice.actions;
export default presenceSlice.reducer;