// src/services/channelService.js
import api from './api';

class ChannelService {
  async getGuildChannels(guildId) {
    const response = await api.get('/channels/', { params: { guild_id: guildId } });
    return response.data;
  }

  async createChannel(guildId, channelData) {
    const response = await api.post('/channels/', channelData, {
      params: { guild_id: guildId },
    });
    return response.data;
  }

  async getChannel(channelId) {
    const response = await api.get(`/channels/${channelId}`);
    return response.data;
  }

  async updateChannel(channelId, channelData) {
    const response = await api.put(`/channels/${channelId}`, channelData);
    return response.data;
  }

  async deleteChannel(channelId) {
    await api.delete(`/channels/${channelId}`);
  }

  async reorderChannels(guildId, channelIds) {
    const response = await api.post('/channels/reorder', channelIds, {
      params: { guild_id: guildId },
    });
    return response.data;
  }
}

// eslint-disable-next-line import/no-anonymous-default-export
export default new ChannelService();