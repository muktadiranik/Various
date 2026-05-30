// src/services/authService.js
import api from './api';

class AuthService {
  async register(userData) {
    const response = await api.post('/auth/register', userData);
    return response.data;
  }

  async login(credentials) {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  }

  async logout() {
    await api.post('/auth/logout');
  }

  async refreshToken(refreshToken) {
    const response = await api.post('/auth/refresh', { refresh_token: refreshToken });
    return response.data;
  }

  async getCurrentUser() {
    const response = await api.get('/users/me');
    return response.data;
  }

  async updateUser(userData) {
    const response = await api.put('/users/me', userData);
    return response.data;
  }

  async getUser(userId) {
    const response = await api.get(`/users/${userId}`);
    return response.data;
  }

  async searchUsers(query, limit = 20) {
    const response = await api.get(`/users/`, { params: { q: query, limit } });
    return response.data;
  }
}

// eslint-disable-next-line import/no-anonymous-default-export
export default new AuthService();