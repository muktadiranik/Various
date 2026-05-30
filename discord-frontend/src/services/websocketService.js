// src/services/websocketService.js
import toast from 'react-hot-toast';

class WebSocketService {
  constructor() {
    this.ws = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000;
    this.listeners = new Map();
    this.heartbeatInterval = null;
  }

  connect(token) {
    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/v1/ws';
    this.ws = new WebSocket(`${wsUrl}?token=${token}`);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      this.emit('connected', {});
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handleMessage(data);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.emit('error', error);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.stopHeartbeat();
      this.emit('disconnected', {});
      this.reconnect(token);
    };
  }

  handleMessage(data) {
    switch (data.type) {
      case 'new_message':
        this.emit('new_message', data.data);
        break;
      case 'message_updated':
        this.emit('message_updated', data);
        break;
      case 'message_deleted':
        this.emit('message_deleted', data.message_id);
        break;
      case 'reaction_added':
        this.emit('reaction_added', data);
        break;
      case 'reaction_removed':
        this.emit('reaction_removed', data);
        break;
      case 'presence_update':
        this.emit('presence_update', data);
        break;
      case 'user_typing':
        this.emit('user_typing', data);
        break;
      case 'heartbeat_ack':
        this.emit('heartbeat_ack', data);
        break;
      case 'error':
        toast.error(data.message);
        this.emit('error', data);
        break;
      default:
        console.log('Unknown message type:', data.type);
    }
  }

  send(type, data = {}) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, ...data }));
    }
  }

  joinGuild(guildId) {
    this.send('join_guild', { guild_id: guildId });
  }

  leaveGuild(guildId) {
    this.send('leave_guild', { guild_id: guildId });
  }

  joinChannel(channelId) {
    this.send('join_channel', { channel_id: channelId });
  }

  leaveChannel(channelId) {
    this.send('leave_channel', { channel_id: channelId });
  }

  sendMessage(channelId, content, replyToId = null) {
    this.send('send_message', { channel_id: channelId, content, reply_to_id: replyToId });
  }

  startTyping(channelId, guildId) {
    this.send('typing_start', { channel_id: channelId, guild_id: guildId });
  }

  stopTyping(channelId) {
    this.send('typing_stop', { channel_id: channelId });
  }

  startHeartbeat() {
    this.heartbeatInterval = setInterval(() => {
      this.send('heartbeat');
    }, 30000);
  }

  stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  reconnect(token) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      setTimeout(() => {
        this.reconnectAttempts++;
        console.log(`Reconnecting attempt ${this.reconnectAttempts}...`);
        this.connect(token);
      }, this.reconnectDelay * Math.pow(2, this.reconnectAttempts));
    } else {
      toast.error('WebSocket connection lost. Please refresh the page.');
    }
  }

  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }

  off(event, callback) {
    if (this.listeners.has(event)) {
      const callbacks = this.listeners.get(event);
      const index = callbacks.indexOf(callback);
      if (index !== -1) callbacks.splice(index, 1);
    }
  }

  emit(event, data) {
    if (this.listeners.has(event)) {
      this.listeners.get(event).forEach(callback => callback(data));
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
    }
    this.stopHeartbeat();
  }
}

// eslint-disable-next-line import/no-anonymous-default-export
export default new WebSocketService();