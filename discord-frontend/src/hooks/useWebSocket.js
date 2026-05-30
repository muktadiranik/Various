// src/hooks/useWebSocket.js
import { useEffect } from 'react';
import websocketService from '../services/websocketService';

function useWebSocket(event, callback) {
  useEffect(() => {
    websocketService.on(event, callback);
    
    return () => {
      websocketService.off(event, callback);
    };
  }, [event, callback]);
}

export default useWebSocket;