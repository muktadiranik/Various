// src/utils/formatters.js
import { formatDistanceToNow, format } from 'date-fns';

export const formatMessageDate = (date) => {
  const now = new Date();
  const messageDate = new Date(date);
  
  if (format(now, 'yyyy-MM-dd') === format(messageDate, 'yyyy-MM-dd')) {
    return format(messageDate, 'h:mm a');
  }
  
  if (now - messageDate < 7 * 24 * 60 * 60 * 1000) {
    return format(messageDate, 'EEEE');
  }
  
  return format(messageDate, 'MMM d, yyyy');
};

export const formatRelativeTime = (date) => {
  return formatDistanceToNow(new Date(date), { addSuffix: true });
};

export const truncateText = (text, maxLength = 100) => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
};

export const getInitials = (name) => {
  if (!name) return '?';
  return name.charAt(0).toUpperCase();
};

export const generateColorFromString = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    hash = str.charCodeAt(i) + ((hash << 5) - hash);
  }
  const hue = hash % 360;
  return `hsl(${hue}, 70%, 50%)`;
};