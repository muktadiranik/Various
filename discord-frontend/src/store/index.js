// src/store/index.js
import { configureStore } from '@reduxjs/toolkit';
import authReducer from './slices/authSlice';
import guildReducer from './slices/guildSlice';
import channelReducer from './slices/channelSlice';
import messageReducer from './slices/messageSlice';
import presenceReducer from './slices/presenceSlice';
import uiReducer from './slices/uiSlice';
import roleReducer from './slices/roleSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    guilds: guildReducer,
    channels: channelReducer,
    messages: messageReducer,
    presence: presenceReducer,
    ui: uiReducer,
    roles: roleReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: false,
      immutableCheck: false,
    }),
  devTools: process.env.NODE_ENV !== 'production',
});

// Infer the `RootState` and `AppDispatch` types from the store itself
export const getRootState = store.getState;
export const getAppDispatch = store.dispatch;

// Helper to get store state
export const getStore = () => store;

export default store;