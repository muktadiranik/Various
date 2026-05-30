// src/store/slices/uiSlice.js
import { createSlice } from '@reduxjs/toolkit';

const uiSlice = createSlice({
  name: 'ui',
  initialState: {
    sidebarOpen: true,
    modalOpen: false,
    modalContent: null,
    modalProps: {},
    notifications: [],
    theme: 'dark',
    activeTab: 'channels',
    searchOpen: false,
    searchQuery: '',
    settingsOpen: false,
    settingsTab: 'profile',
    loadingOverlay: false,
    loadingMessage: '',
  },
  reducers: {
    toggleSidebar: (state) => {
      state.sidebarOpen = !state.sidebarOpen;
    },
    setSidebarOpen: (state, action) => {
      state.sidebarOpen = action.payload;
    },
    openModal: (state, action) => {
      state.modalOpen = true;
      state.modalContent = action.payload.content;
      state.modalProps = action.payload.props || {};
    },
    closeModal: (state) => {
      state.modalOpen = false;
      state.modalContent = null;
      state.modalProps = {};
    },
    addNotification: (state, action) => {
      state.notifications.push({
        id: Date.now(),
        timestamp: new Date().toISOString(),
        read: false,
        ...action.payload,
      });
    },
    removeNotification: (state, action) => {
      state.notifications = state.notifications.filter(n => n.id !== action.payload);
    },
    markNotificationRead: (state, action) => {
      const notification = state.notifications.find(n => n.id === action.payload);
      if (notification) {
        notification.read = true;
      }
    },
    markAllNotificationsRead: (state) => {
      state.notifications.forEach(n => { n.read = true; });
    },
    clearAllNotifications: (state) => {
      state.notifications = [];
    },
    setTheme: (state, action) => {
      state.theme = action.payload;
      // Save to localStorage
      localStorage.setItem('theme', action.payload);
    },
    setActiveTab: (state, action) => {
      state.activeTab = action.payload;
    },
    openSearch: (state) => {
      state.searchOpen = true;
    },
    closeSearch: (state) => {
      state.searchOpen = false;
      state.searchQuery = '';
    },
    setSearchQuery: (state, action) => {
      state.searchQuery = action.payload;
    },
    openSettings: (state, action) => {
      state.settingsOpen = true;
      if (action.payload) {
        state.settingsTab = action.payload;
      }
    },
    closeSettings: (state) => {
      state.settingsOpen = false;
      state.settingsTab = 'profile';
    },
    setSettingsTab: (state, action) => {
      state.settingsTab = action.payload;
    },
    showLoadingOverlay: (state, action) => {
      state.loadingOverlay = true;
      state.loadingMessage = action.payload || 'Loading...';
    },
    hideLoadingOverlay: (state) => {
      state.loadingOverlay = false;
      state.loadingMessage = '';
    },
  },
});

// Load theme from localStorage on app initialization
export const initializeTheme = () => (dispatch) => {
  const savedTheme = localStorage.getItem('theme');
  if (savedTheme && (savedTheme === 'dark' || savedTheme === 'light')) {
    dispatch(setTheme(savedTheme));
  }
};

export const {
  toggleSidebar,
  setSidebarOpen,
  openModal,
  closeModal,
  addNotification,
  removeNotification,
  markNotificationRead,
  markAllNotificationsRead,
  clearAllNotifications,
  setTheme,
  setActiveTab,
  openSearch,
  closeSearch,
  setSearchQuery,
  openSettings,
  closeSettings,
  setSettingsTab,
  showLoadingOverlay,
  hideLoadingOverlay,
} = uiSlice.actions;

export default uiSlice.reducer;