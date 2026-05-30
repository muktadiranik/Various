// src/store/slices/messageSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import messageService from '../../services/messageService';

export const fetchMessages = createAsyncThunk(
  'messages/fetch',
  async ({ channelId, limit = 50, offset = 0, before, after }, { rejectWithValue }) => {
    try {
      return await messageService.getChannelMessages(channelId, limit, offset, before, after);
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch messages');
    }
  }
);

export const sendMessage = createAsyncThunk(
  'messages/send',
  async ({ channelId, content, replyToId }, { rejectWithValue }) => {
    try {
      return await messageService.createMessage(channelId, { content, reply_to_id: replyToId });
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to send message');
    }
  }
);

export const updateMessage = createAsyncThunk(
  'messages/update',
  async ({ messageId, content }, { rejectWithValue }) => {
    try {
      return await messageService.updateMessage(messageId, { content });
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update message');
    }
  }
);

export const deleteMessage = createAsyncThunk(
  'messages/delete',
  async (messageId, { rejectWithValue }) => {
    try {
      await messageService.deleteMessage(messageId);
      return messageId;
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete message');
    }
  }
);

export const addReaction = createAsyncThunk(
  'messages/addReaction',
  async ({ messageId, emoji }, { rejectWithValue }) => {
    try {
      await messageService.addReaction(messageId, { emoji });
      return { messageId, emoji };
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to add reaction');
    }
  }
);

export const removeReaction = createAsyncThunk(
  'messages/removeReaction',
  async ({ messageId, emoji }, { rejectWithValue }) => {
    try {
      await messageService.removeReaction(messageId, emoji);
      return { messageId, emoji };
    } catch (error) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to remove reaction');
    }
  }
);

export const pinMessage = createAsyncThunk('messages/pin', async (messageId, { rejectWithValue }) => {
  try {
    return await messageService.pinMessage(messageId);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to pin message');
  }
});

export const unpinMessage = createAsyncThunk('messages/unpin', async (messageId, { rejectWithValue }) => {
  try {
    return await messageService.unpinMessage(messageId);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to unpin message');
  }
});

export const fetchPinnedMessages = createAsyncThunk('messages/fetchPinned', async (channelId, { rejectWithValue }) => {
  try {
    return await messageService.getPinnedMessages(channelId);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch pinned messages');
  }
});

export const searchMessages = createAsyncThunk('messages/search', async ({ channelId, query, limit }, { rejectWithValue }) => {
  try {
    return await messageService.searchMessages(channelId, query, limit);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to search messages');
  }
});

export const fetchThreadMessages = createAsyncThunk('messages/fetchThread', async (parentMessageId, { rejectWithValue }) => {
  try {
    return await messageService.getThreadMessages(parentMessageId);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch thread messages');
  }
});

const messageSlice = createSlice({
  name: 'messages',
  initialState: {
    messages: {},
    threads: {},
    pinnedMessagesList: [],
    searchResults: [],
    loading: false,
    hasMore: true,
    error: null,
  },
  reducers: {
    addNewMessage: (state, action) => {
      const { channelId, message } = action.payload;
      if (!state.messages[channelId]) state.messages[channelId] = [];
      state.messages[channelId].unshift(message);
    },
    updateMessageInList: (state, action) => {
      const { messageId, updates } = action.payload;
      for (const channelId in state.messages) {
        const index = state.messages[channelId].findIndex(m => m.id === messageId);
        if (index !== -1) {
          state.messages[channelId][index] = { ...state.messages[channelId][index], ...updates };
          break;
        }
      }
    },
    removeMessageFromList: (state, action) => {
      const messageId = action.payload;
      for (const channelId in state.messages) {
        state.messages[channelId] = state.messages[channelId].filter(m => m.id !== messageId);
      }
    },
    clearMessages: (state, action) => {
      state.messages[action.payload] = [];
      state.hasMore = true;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchMessages.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchMessages.fulfilled, (state, action) => {
        const { channel_id, messages, has_more } = action.payload;
        state.messages[channel_id] = messages;
        state.hasMore = has_more;
        state.loading = false;
      })
      .addCase(fetchMessages.rejected, (state, action) => {
        state.error = action.payload;
        state.loading = false;
      })
      .addCase(sendMessage.fulfilled, (state, action) => {
        const message = action.payload;
        if (!state.messages[message.channel_id]) state.messages[message.channel_id] = [];
        state.messages[message.channel_id].unshift(message);
      })
      .addCase(deleteMessage.fulfilled, (state, action) => {
        const messageId = action.payload;
        for (const channelId in state.messages) {
          state.messages[channelId] = state.messages[channelId].filter(m => m.id !== messageId);
        }
      })
      .addCase(pinMessage.fulfilled, (state, action) => {
        const message = action.payload;
        for (const channelId in state.messages) {
          const index = state.messages[channelId].findIndex(m => m.id === message.id);
          if (index !== -1) {
            state.messages[channelId][index].is_pinned = true;
            break;
          }
        }
      })
      .addCase(unpinMessage.fulfilled, (state, action) => {
        const message = action.payload;
        for (const channelId in state.messages) {
          const index = state.messages[channelId].findIndex(m => m.id === message.id);
          if (index !== -1) {
            state.messages[channelId][index].is_pinned = false;
            break;
          }
        }
      })
      .addCase(fetchPinnedMessages.fulfilled, (state, action) => {
        state.pinnedMessagesList = action.payload;
      })
      .addCase(fetchThreadMessages.fulfilled, (state, action) => {
        const { parent_message_id, messages } = action.payload;
        state.threads[parent_message_id] = messages;
      });
  },
});

export const { addNewMessage, updateMessageInList, removeMessageFromList, clearMessages, clearError } = messageSlice.actions;
export default messageSlice.reducer;