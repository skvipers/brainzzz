import { useEffect, useRef, useCallback, useState } from 'react';

interface WebSocketMessage {
  type: string;
  schema_version: string;
  ts: string;
  data: any;
}

interface UseWebSocketOptions {
  url: string;
  onMessage?: (message: WebSocketMessage) => void;
  onOpen?: () => void;
  onClose?: () => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
}

export const useWebSocket = ({
  url,
  onMessage,
  onOpen,
  onClose,
  onError,
  reconnectInterval = 3000,
  maxReconnectAttempts = 5,
}: UseWebSocketOptions) => {
  const [isConnected, setIsConnected] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<number | null>(null);
  const isConnectingRef = useRef(false);

  const connect = useCallback(() => {
    if (isConnectingRef.current) return;

    // Проверяем, не подключены ли уже
    if (wsRef.current && isConnected) {
      console.log('🔌 WebSocket уже подключен, пропускаю');
      return;
    }

    try {
      isConnectingRef.current = true;
      console.log('🔌 Подключаюсь к WebSocket:', url);

      const ws = new WebSocket(url);

      ws.onopen = () => {
        console.log('✅ WebSocket соединение установлено');
        setIsConnected(true);
        setReconnectAttempts(0);
        isConnectingRef.current = false;
        onOpen?.();
      };

      ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          console.log('📨 WebSocket сообщение получено:', message);
          onMessage?.(message);
        } catch (error) {
          console.error('❌ Ошибка парсинга WebSocket сообщения:', error);
        }
      };

      ws.onclose = (event) => {
        console.log('🔌 WebSocket соединение закрыто:', event.code, event.reason);
        setIsConnected(false);
        isConnectingRef.current = false;
        onClose?.();

        // Попытка переподключения только если это не было намеренное закрытие
        if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
          console.log(
            `🔄 Попытка переподключения ${reconnectAttempts + 1}/${maxReconnectAttempts}`,
          );

          reconnectTimeoutRef.current = setTimeout(() => {
            setReconnectAttempts((prev) => prev + 1);
            connect();
          }, reconnectInterval) as unknown as number;
        } else if (reconnectAttempts >= maxReconnectAttempts) {
          console.error('❌ Превышено максимальное количество попыток переподключения');
        }
      };

      ws.onerror = (error) => {
        console.error('❌ WebSocket ошибка:', error);
        isConnectingRef.current = false;
        onError?.(error);
      };

      wsRef.current = ws;
      console.log('🔌 WebSocket объект создан и сохранен в ref');
    } catch (error) {
      console.error('❌ Ошибка создания WebSocket:', error);
      isConnectingRef.current = false;
    }
  }, [
    url,
    onMessage,
    onOpen,
    onClose,
    onError,
    reconnectInterval,
    maxReconnectAttempts,
    reconnectAttempts,
    isConnected,
  ]);

  const disconnect = useCallback(() => {
    console.log('🔌 Вызываю disconnect');

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
      console.log('🔌 Таймер переподключения очищен');
    }

    if (wsRef.current) {
      console.log('🔌 Закрываю WebSocket соединение');
      wsRef.current.close(1000); // Нормальное закрытие
      wsRef.current = null;
      console.log('🔌 WebSocket объект очищен');
    }

    setIsConnected(false);
    setReconnectAttempts(0);
    isConnectingRef.current = false;
    console.log('🔌 Состояние WebSocket сброшено');
  }, []);

  const sendMessage = useCallback(
    (message: any) => {
      if (wsRef.current && isConnected) {
        try {
          const messageStr = typeof message === 'string' ? message : JSON.stringify(message);
          wsRef.current.send(messageStr);
          console.log('📤 WebSocket сообщение отправлено:', message);
        } catch (error) {
          console.error('❌ Ошибка отправки WebSocket сообщения:', error);
        }
      } else {
        console.warn('⚠️ WebSocket не подключен, сообщение не отправлено');
      }
    },
    [isConnected],
  );

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
        reconnectTimeoutRef.current = null;
      }
      disconnect();
    };
  }, []); // Убираем зависимости - connect и disconnect стабильны

  return {
    isConnected,
    sendMessage,
    disconnect,
    connect,
  };
};
