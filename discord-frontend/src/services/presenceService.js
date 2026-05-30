// src/services/presenceService.js
import api from './api';

class PresenceService {
  async setOnline(guildId) {
    await api.post(`/presence/guilds/${guildId}/online`);
  }

  async setOffline(guildId) {
    await api.post(`/presence/guilds/${guildId}/offline`);
  }

  async getOnlineUsers(guildId) {
    const response = await api.get(`/presence/guilds/${guildId}/online`);
    return response.data;
  }

  async startTyping(channelId, guildId) {
    await api.post(`/presence/channels/${channelId}/typing`, { guild_id: guildId });
  }

  async stopTyping(channelId) {
    await api.delete(`/presence/channels/${channelId}/typing`);
  }
}

// eslint-disable-next-line import/no-anonymous-default-export
export default new PresenceService();