// src/store/slices/guildSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import guildService from '../../services/guildService';

export const fetchGuilds = createAsyncThunk('guilds/fetch', async (_, { rejectWithValue }) => {
  try {
    return await guildService.getUserGuilds();
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch guilds');
  }
});

export const createGuild = createAsyncThunk('guilds/create', async (guildData, { rejectWithValue }) => {
  try {
    return await guildService.createGuild(guildData);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to create guild');
  }
});

export const updateGuild = createAsyncThunk('guilds/update', async ({ guildId, data }, { rejectWithValue }) => {
  try {
    return await guildService.updateGuild(guildId, data);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to update guild');
  }
});

export const deleteGuild = createAsyncThunk('guilds/delete', async (guildId, { rejectWithValue }) => {
  try {
    await guildService.deleteGuild(guildId);
    return guildId;
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to delete guild');
  }
});

export const joinGuild = createAsyncThunk('guilds/join', async (guildId, { rejectWithValue }) => {
  try {
    return await guildService.joinGuild(guildId);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to join guild');
  }
});

export const leaveGuild = createAsyncThunk('guilds/leave', async (guildId, { rejectWithValue }) => {
  try {
    await guildService.leaveGuild(guildId);
    return guildId;
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to leave guild');
  }
});

export const fetchGuildMembers = createAsyncThunk('guilds/fetchMembers', async (guildId, { rejectWithValue }) => {
  try {
    return await guildService.getGuildMembers(guildId);
  } catch (error) {
    return rejectWithValue(error.response?.data?.detail || 'Failed to fetch members');
  }
});

const guildSlice = createSlice({
  name: 'guilds',
  initialState: {
    list: [],
    selectedGuild: null,
    members: [],
    loading: false,
    error: null,
  },
  reducers: {
    selectGuild: (state, action) => {
      state.selectedGuild = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchGuilds.pending, (state) => {
        state.loading = true;
      })
      .addCase(fetchGuilds.fulfilled, (state, action) => {
        state.list = action.payload;
        state.loading = false;
      })
      .addCase(fetchGuilds.rejected, (state, action) => {
        state.error = action.payload;
        state.loading = false;
      })
      .addCase(createGuild.fulfilled, (state, action) => {
        state.list.push(action.payload);
      })
      .addCase(updateGuild.fulfilled, (state, action) => {
        const index = state.list.findIndex(g => g.id === action.payload.id);
        if (index !== -1) state.list[index] = action.payload;
        if (state.selectedGuild?.id === action.payload.id) state.selectedGuild = action.payload;
      })
      .addCase(deleteGuild.fulfilled, (state, action) => {
        state.list = state.list.filter(g => g.id !== action.payload);
        if (state.selectedGuild?.id === action.payload) state.selectedGuild = null;
      })
      .addCase(joinGuild.fulfilled, (state, action) => {
        state.list.push(action.payload);
      })
      .addCase(leaveGuild.fulfilled, (state, action) => {
        state.list = state.list.filter(g => g.id !== action.payload);
        if (state.selectedGuild?.id === action.payload) state.selectedGuild = null;
      })
      .addCase(fetchGuildMembers.fulfilled, (state, action) => {
        state.members = action.payload;
      });
  },
});

export const { selectGuild, clearError } = guildSlice.actions;
export default guildSlice.reducer;