import React, { useEffect } from 'react'
import { Brain, Users, TrendingUp, Target, Activity, Zap, Wifi, WifiOff } from 'lucide-react'
import { useBrainStore } from '../stores/brainStore'
import { useWebSocketContext } from '../components/WebSocketProvider'

const Dashboard = () => {
  const { population, stats, loading, fetchPopulation, fetchStats, startEvolution, evaluatePopulation, wsConnected } = useBrainStore()
  const { isConnected } = useWebSocketContext()

  useEffect(() => {
    // Загружаем начальные данные
    fetchPopulation()
    fetchStats()

    // Убираем автоматическое обновление - теперь данные обновляются через WebSocket
  }, [fetchPopulation, fetchStats])

  const handleStartEvolution = async () => {
    try {
      await startEvolution(0.3) // стандартная скорость мутации
      // Обновляем данные после запуска эволюции
      setTimeout(() => {
        fetchPopulation()
        fetchStats()
      }, 1000)
    } catch (error) {
      console.error('Ошибка запуска эволюции:', error)
    }
  }

  const handleEvaluatePopulation = async () => {
    try {
      await evaluatePopulation()
      // Обновляем данные после оценки
      setTimeout(() => {
        fetchPopulation()
        fetchStats()
      }, 1000)
    } catch (error) {
      console.error('Ошибка оценки популяции:', error)
    }
  }

  const handleAddTask = () => {
    // Переходим на страницу задач
    window.location.href = '/tasks'
  }

  const metrics = [
    {
      name: 'Размер популяции',
      value: stats.size || 0,
      icon: Users,
      change: '+12%',
      changeType: 'positive' as const,
    },
    {
      name: 'Средняя приспособленность',
      value: (stats.avg_fitness || 0).toFixed(3),
      icon: TrendingUp,
      change: '+5.2%',
      changeType: 'positive' as const,
    },
    {
      name: 'Лучший мозг',
      value: (stats.max_fitness || 0).toFixed(3),
      icon: Brain,
      change: '+8.1%',
      changeType: 'positive' as const,
    },
    {
      name: 'Поколение',
      value: stats.generation || 0,
      icon: Target,
      change: '+1',
      changeType: 'neutral' as const,
    },
    {
      name: 'Средние узлы',
      value: (stats.avg_nodes || 0).toFixed(1),
      icon: Brain,
      change: '-2%',
      changeType: 'negative' as const,
    },
  ]

  const recentActivity = [
    { id: 1, type: 'evolution' as const, message: 'Завершена эволюция поколения 15', time: '2 мин назад' },
    { id: 2, type: 'growth' as const, message: 'Мозг #7 вырос на 3 узла', time: '5 мин назад' },
    { id: 3, type: 'task' as const, message: 'Задача XOR решена с точностью 98%', time: '12 мин назад' },
    { id: 4, type: 'mutation' as const, message: 'Применены мутации к 12 мозгам', time: '18 мин назад' },
  ]

  return (
    <div className="px-8">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Дашборд</h1>
          <p className="text-gray-600">Обзор состояния популяции и эволюции</p>
        </div>

        {/* WebSocket статус */}
        <div className="flex items-center space-x-2">
          <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${
            isConnected ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {isConnected ? (
              <>
                <Wifi className="w-4 h-4" />
                <span className="text-sm font-medium">WebSocket подключен</span>
              </>
            ) : (
              <>
                <WifiOff className="w-4 h-4" />
                <span className="text-sm font-medium">WebSocket отключен</span>
              </>
            )}
          </div>

          {/* Убрали блок "Последнее событие" для чистоты интерфейса */}
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {metrics.map((metric) => (
          <div key={metric.name} className="card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{metric.name}</p>
                <p className="text-2xl font-bold text-gray-900">{metric.value}</p>
              </div>
              <div className="h-12 w-12 rounded-lg bg-brain-100 flex items-center justify-center">
                <metric.icon className="h-6 w-6 text-brain-600" />
              </div>
            </div>
            <div className="mt-4 flex items-center">
              <span className={`text-sm font-medium ${
                metric.changeType === 'positive' ? 'text-green-600' :
                metric.changeType === 'negative' ? 'text-red-600' : 'text-gray-600'
              }`}>
                {metric.change}
              </span>
              <span className="text-sm text-gray-500 ml-2">с прошлого обновления</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Population Overview */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Обзор популяции</h3>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-brain-600"></div>
            </div>
          ) : (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Средние узлы</span>
                <span className="font-medium">{(stats.avg_nodes || 0).toFixed(1)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Средние связи</span>
                <span className="font-medium">{(stats.avg_connections || 0).toFixed(1)}</span>
              </div>

              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Активные задачи</span>
                <span className="font-medium">2</span>
              </div>
            </div>
          )}
        </div>

        {/* Recent Activity */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Последняя активность</h3>
          <div className="space-y-3">
            {recentActivity.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3">
                <div className={`h-2 w-2 rounded-full mt-2 ${
                  activity.type === 'evolution' ? 'bg-blue-500' :
                  activity.type === 'growth' ? 'bg-green-500' :
                  activity.type === 'task' ? 'bg-purple-500' :
                  'bg-gray-500'
                }`} />
                <div className="flex-1">
                  <p className="text-sm text-gray-900">{activity.message}</p>
                  <p className="text-xs text-gray-500">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Быстрые действия</h3>
        <div className="flex space-x-4">
          <button
            onClick={handleStartEvolution}
            className="btn-primary flex items-center space-x-2"
          >
            <Zap className="h-4 w-4" />
            <span>Запустить эволюцию</span>
          </button>
          <button
            onClick={handleEvaluatePopulation}
            className="btn-secondary flex items-center space-x-2"
          >
            <Activity className="h-4 w-4" />
            <span>Оценить популяцию</span>
          </button>
          <button
            onClick={handleAddTask}
            className="btn-secondary flex items-center space-x-2"
          >
            <Target className="h-4 w-4" />
            <span>Добавить задачу</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default Dashboard
