// src/utils/constants.js
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';
export const WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/v1/ws';

export const PERMISSIONS = {
  VIEW_CHANNEL: 1 << 0,
  SEND_MESSAGES: 1 << 1,
  READ_MESSAGE_HISTORY: 1 << 2,
  CREATE_INVITE: 1 << 3,
  MANAGE_MESSAGES: 1 << 4,
  ADD_REACTIONS: 1 << 5,
  ATTACH_FILES: 1 << 6,
  EMBED_LINKS: 1 << 7,
  MENTION_EVERYONE: 1 << 8,
  USE_EXTERNAL_EMOJIS: 1 << 9,
  CONNECT: 1 << 10,
  SPEAK: 1 << 11,
  MUTE_MEMBERS: 1 << 12,
  DEAFEN_MEMBERS: 1 << 13,
  MOVE_MEMBERS: 1 << 14,
  USE_VAD: 1 << 15,
  MANAGE_CHANNELS: 1 << 16,
  MANAGE_GUILD: 1 << 17,
  ADMINISTRATOR: 1 << 18,
  MANAGE_ROLES: 1 << 19,
  MANAGE_NICKNAMES: 1 << 20,
  CHANGE_NICKNAME: 1 << 21,
  KICK_MEMBERS: 1 << 22,
  BAN_MEMBERS: 1 << 23,
  VIEW_AUDIT_LOG: 1 << 24,
  MANAGE_WEBHOOKS: 1 << 25,
  MANAGE_EMOJIS: 1 << 26,
};

export const MESSAGE_TYPES = {
  TEXT: 'text',
  IMAGE: 'image',
  VIDEO: 'video',
  FILE: 'file',
};

export const CHANNEL_TYPES = {
  TEXT: 'text',
  VOICE: 'voice',
};