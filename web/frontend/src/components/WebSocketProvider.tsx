import React, { createContext, useContext, ReactNode, useCallback } from 'react'
import { useWebSocket } from '../hooks/useWebSocket'
import { useBrainStore } from '../stores/brainStore'

interface WebSocketContextType {
  isConnected: boolean
  sendMessage: (message: any) => void
}

const WebSocketContext = createContext<WebSocketContextType | null>(null)

interface WebSocketProviderProps {
  children: ReactNode
}

export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ children }) => {
  const { setWebSocketConnected, handleWebSocketMessage } = useBrainStore()
  
  // Стабилизируем колбэки с useCallback
  const handleOpen = useCallback(() => {
    setWebSocketConnected(true)
    console.log('🎉 WebSocket подключен к Brainzzz API')
  }, [setWebSocketConnected])
  
  const handleClose = useCallback(() => {
    setWebSocketConnected(false)
    console.log('🔌 WebSocket отключен от Brainzzz API')
  }, [setWebSocketConnected])
  
  const handleError = useCallback((error: Event) => {
    console.error('❌ WebSocket ошибка:', error)
    setWebSocketConnected(false)
  }, [setWebSocketConnected])
  
  const handleMessage = useCallback((message: any) => {
    handleWebSocketMessage(message)
  }, [handleWebSocketMessage])
  
  const { isConnected, sendMessage } = useWebSocket({
    url: 'ws://localhost:8000/ws',
    onOpen: handleOpen,
    onClose: handleClose,
    onError: handleError,
    onMessage: handleMessage,
    reconnectInterval: 5000,
    maxReconnectAttempts: 3
  })

  const contextValue: WebSocketContextType = {
    isConnected,
    sendMessage
  }

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  )
}

export const useWebSocketContext = () => {
  const context = useContext(WebSocketContext)
  if (!context) {
    throw new Error('useWebSocketContext должен использоваться внутри WebSocketProvider')
  }
  return context
}
