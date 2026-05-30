// src/services/roleService.js
import api from './api';

class RoleService {
  async getGuildRoles(guildId) {
    const response = await api.get('/roles/', { params: { guild_id: guildId } });
    return response.data;
  }

  async createRole(guildId, roleData) {
    const response = await api.post('/roles/', roleData, { params: { guild_id: guildId } });
    return response.data;
  }

  async getRole(roleId) {
    const response = await api.get(`/roles/${roleId}`);
    return response.data;
  }

  async updateRole(roleId, roleData) {
    const response = await api.put(`/roles/${roleId}`, roleData);
    return response.data;
  }

  async deleteRole(roleId) {
    await api.delete(`/roles/${roleId}`);
  }

  async assignRole(guildId, userId, roleId) {
    await api.post('/roles/assign', { guild_id: guildId, user_id: userId, role_id: roleId });
  }

  async removeRole(guildId, userId, roleId) {
    await api.post('/roles/remove', { guild_id: guildId, user_id: userId, role_id: roleId });
  }

  async getUserRoles(guildId, userId) {
    const response = await api.get(`/roles/user/${userId}`, { params: { guild_id: guildId } });
    return response.data;
  }
}

// eslint-disable-next-line import/no-anonymous-default-export
export default new RoleService();