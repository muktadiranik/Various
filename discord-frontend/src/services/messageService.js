// src/services/messageService.js
import api from './api';

class MessageService {
  async getChannelMessages(channelId, limit = 50, offset = 0, before = null, after = null) {
    const params = { limit, offset };
    if (before) params.before = before;
    if (after) params.after = after;
    const response = await api.get(`/messages/${channelId}`, { params });
    return response.data;
  }

  async createMessage(channelId, messageData) {
    const response = await api.post(`/messages/${channelId}`, messageData);
    return response.data;
  }

  async getMessage(messageId) {
    const response = await api.get(`/messages/single/${messageId}`);
    return response.data;
  }

  async updateMessage(messageId, messageData) {
    const response = await api.put(`/messages/${messageId}`, messageData);
    return response.data;
  }

  async deleteMessage(messageId) {
    await api.delete(`/messages/${messageId}`);
  }

  async addReaction(messageId, reactionData) {
    await api.post(`/messages/${messageId}/reactions`, reactionData);
  }

  async removeReaction(messageId, emoji) {
    await api.delete(`/messages/${messageId}/reactions`, { params: { emoji } });
  }

  async pinMessage(messageId) {
    const response = await api.post(`/messages/${messageId}/pin`);
    return response.data;
  }

  async unpinMessage(messageId) {
    const response = await api.delete(`/messages/${messageId}/pin`);
    return response.data;
  }

  async getPinnedMessages(channelId) {
    const response = await api.get(`/channels/${channelId}/pinned`);
    return response.data;
  }

  async searchMessages(channelId, query, limit = 50) {
    const response = await api.get(`/channels/${channelId}/search`, {
      params: { q: query, limit },
    });
    return response.data;
  }

  async getThreadMessages(parentMessageId, limit = 50, offset = 0) {
    const response = await api.get(`/messages/thread/${parentMessageId}`, {
      params: { limit, offset },
    });
    return response.data;
  }
}

// eslint-disable-next-line import/no-anonymous-default-export
export default new MessageService();