// src/store/slices/channelSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import channelService from '../../services/channelService';

export const fetchChannels = createAsyncThunk('channels/fetch', async (guildId, { rejectWithValue }) => {
  try {
    return await channelService.getGuildChannels(guildId);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch channels');
  }
});

export const createChannel = createAsyncThunk('channels/create', async ({ guildId, channelData }, { rejectWithValue }) => {
  try {
    return await channelService.createChannel(guildId, channelData);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to create channel');
  }
});

export const updateChannel = createAsyncThunk('channels/update', async ({ channelId, channelData }, { rejectWithValue }) => {
  try {
    return await channelService.updateChannel(channelId, channelData);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to update channel');
  }
});

export const deleteChannel = createAsyncThunk('channels/delete', async (channelId, { rejectWithValue }) => {
  try {
    await channelService.deleteChannel(channelId);
    return channelId;
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to delete channel');
  }
});

const channelSlice = createSlice({
  name: 'channels',
  initialState: {
    list: [],
    selectedChannel: null,
    loading: false,
    error: null,
  },
  reducers: {
    selectChannel: (state, action) => {
      state.selectedChannel = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchChannels.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchChannels.fulfilled, (state, action) => {
        state.list = action.payload;
        state.loading = false;
      })
      .addCase(fetchChannels.rejected, (state, action) => {
        state.error = action.payload;
        state.loading = false;
      })
      .addCase(createChannel.fulfilled, (state, action) => {
        state.list.push(action.payload);
      })
      .addCase(updateChannel.fulfilled, (state, action) => {
        const index = state.list.findIndex(c => c.id === action.payload.id);
        if (index !== -1) state.list[index] = action.payload;
      })
      .addCase(deleteChannel.fulfilled, (state, action) => {
        state.list = state.list.filter(c => c.id !== action.payload);
        if (state.selectedChannel?.id === action.payload) state.selectedChannel = null;
      });
  },
});

export const { selectChannel, clearError } = channelSlice.actions;
export default channelSlice.reducer;