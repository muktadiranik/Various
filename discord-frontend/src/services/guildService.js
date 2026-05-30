// src/services/guildService.js
import api from './api';

class GuildService {
  async getUserGuilds() {
    const response = await api.get('/guilds/');
    return response.data;
  }

  async createGuild(guildData) {
    const response = await api.post('/guilds/', guildData);
    return response.data;
  }

  async getGuild(guildId) {
    const response = await api.get(`/guilds/${guildId}`);
    return response.data;
  }

  async updateGuild(guildId, guildData) {
    const response = await api.put(`/guilds/${guildId}`, guildData);
    return response.data;
  }

  async deleteGuild(guildId) {
    await api.delete(`/guilds/${guildId}`);
  }

  async joinGuild(guildId) {
    const response = await api.post(`/guilds/${guildId}/join`);
    return response.data;
  }

  async leaveGuild(guildId) {
    await api.post(`/guilds/${guildId}/leave`);
  }

  async getGuildMembers(guildId, skip = 0, limit = 100) {
    const response = await api.get(`/guilds/${guildId}/members`, {
      params: { skip, limit },
    });
    return response.data;
  }

  async kickMember(guildId, userId) {
    await api.delete(`/guilds/${guildId}/members/${userId}`);
  }

  async transferOwnership(guildId, newOwnerId) {
    await api.post(`/guilds/${guildId}/transfer/${newOwnerId}`);
  }
}

// eslint-disable-next-line import/no-anonymous-default-export
export default new GuildService();