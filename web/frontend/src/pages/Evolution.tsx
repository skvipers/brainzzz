import React, { useState, useEffect } from 'react'
import { TrendingUp, Play, BarChart3, Zap } from 'lucide-react'
import { useBrainStore } from '../stores/brainStore'

interface EvolutionHistoryEntry {
  id: number
  timestamp: string
  action: string
  populationSize: number
  mutationRate: number
  message: string
  status: 'success' | 'error'
  generation?: number
  bestFitness?: number
  avgFitness?: number
}

const Evolution = () => {
  const { stats, evaluatePopulation, fetchStats, loading, startEvolution, fetchPopulation } = useBrainStore()
  const [mutationRate, setMutationRate] = useState(0.3)
  const [populationSize, setPopulationSize] = useState(20)
  const [isEvolving, setIsEvolving] = useState(false)
  const [isRefreshing, setIsRefreshing] = useState(false)
  const [evolutionHistory, setEvolutionHistory] = useState<EvolutionHistoryEntry[]>([
    {
      id: 1,
      timestamp: '2024-12-17 20:30:00',
      action: 'Инициализация',
      populationSize: 20,
      mutationRate: 0.3,
      message: 'Начальная популяция создана',
      status: 'success',
      generation: 0,
      bestFitness: 0.0,
      avgFitness: 0.0
    }
  ])

  // Загружаем статистику при загрузке компонента и обновляем периодически
  useEffect(() => {
    fetchStats()

    // Обновляем данные каждые 3 секунды для отображения актуальной информации
    const interval = setInterval(() => {
      fetchStats()
    }, 3000)

    return () => clearInterval(interval)
  }, [fetchStats])

  const handleStartEvolution = async () => {
    try {
      setIsEvolving(true)

      // Запускаем эволюцию через store
      await startEvolution(mutationRate, populationSize)

      // Добавляем в историю
      const newEntry: EvolutionHistoryEntry = {
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        action: 'Эволюция',
        populationSize: populationSize,
        mutationRate: mutationRate,
        message: 'Эволюция запущена успешно',
        status: 'success',
        generation: (stats.generation || 0) + 1,
        bestFitness: stats.max_fitness || 0,
        avgFitness: stats.avg_fitness || 0
      }

      setEvolutionHistory(prev => [newEntry, ...prev.slice(0, 9)]) // Оставляем последние 10 записей

      // Обновляем данные популяции и статистику
      await fetchPopulation()
      await evaluatePopulation()
      await fetchStats()

      // Добавляем небольшую задержку и повторно обновляем для гарантии
      setTimeout(async () => {
        await fetchPopulation()
        await fetchStats()
      }, 1000)

    } catch (error) {
      console.error('Ошибка:', error)

      // Добавляем ошибку в историю
      const errorEntry: EvolutionHistoryEntry = {
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        action: 'Эволюция',
        populationSize: populationSize,
        mutationRate: mutationRate,
        message: error instanceof Error ? error.message : 'Неизвестная ошибка',
        status: 'error',
        generation: stats.generation || 0,
        bestFitness: stats.max_fitness || 0,
        avgFitness: stats.avg_fitness || 0
      }

      setEvolutionHistory(prev => [errorEntry, ...prev.slice(0, 9)])
    } finally {
      setIsEvolving(false)
    }
  }

  const handleResizePopulation = async () => {
    try {
      // Изменяем размер популяции через store
      await startEvolution(mutationRate, populationSize)

      // Добавляем в историю
      const newEntry: EvolutionHistoryEntry = {
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        action: 'Изменение размера',
        populationSize: populationSize,
        mutationRate: mutationRate,
        message: 'Размер популяции изменен успешно',
        status: 'success',
        generation: stats.generation || 0,
        bestFitness: stats.max_fitness || 0,
        avgFitness: stats.avg_fitness || 0
      }

      setEvolutionHistory(prev => [newEntry, ...prev.slice(0, 9)])

      // Обновляем данные популяции и статистику
      await fetchPopulation()
      await fetchStats()

      // Добавляем небольшую задержку и повторно обновляем для гарантии
      setTimeout(async () => {
        await fetchPopulation()
        await fetchStats()
      }, 1000)

    } catch (error) {
      console.error('Ошибка изменения размера популяции:', error)

      const errorEntry: EvolutionHistoryEntry = {
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        action: 'Изменение размера',
        populationSize: populationSize,
        mutationRate: mutationRate,
        message: error instanceof Error ? error.message : 'Неизвестная ошибка',
        status: 'error',
        generation: stats.generation || 0,
        bestFitness: stats.max_fitness || 0,
        avgFitness: stats.avg_fitness || 0
      }

      setEvolutionHistory(prev => [errorEntry, ...prev.slice(0, 9)])
    }
  }

  return (
    <div className="px-8">
                <div className="mb-8 flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Эволюция</h1>
              <p className="text-gray-600">Управление эволюционным процессом популяции</p>
            </div>
            <button
              onClick={async () => {
                setIsRefreshing(true)
                await fetchPopulation()
                await fetchStats()
                setIsRefreshing(false)
              }}
              className="btn-secondary flex items-center space-x-2 px-4 py-2"
              title="Обновить данные"
              disabled={isRefreshing}
            >
              {isRefreshing ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <TrendingUp className="h-4 w-4" />
              )}
              <span>{isRefreshing ? 'Обновление...' : 'Обновить'}</span>
            </button>
          </div>

      {/* Параметры эволюции - исправленная вёрстка */}
      <div className="card mb-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-6">Параметры эволюции</h3>

        <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6 mb-6">
          {/* Скорость мутации */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">
              Скорость мутации
            </label>
            <input
              type="range"
              min="0.1"
              max="1.0"
              step="0.1"
              value={mutationRate}
              onChange={(e) => setMutationRate(Number(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0.1</span>
              <span className="font-medium text-brain-600">{mutationRate}</span>
              <span>1.0</span>
            </div>
          </div>

          {/* Размер популяции */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">
              Размер популяции
            </label>
            <input
              type="number"
              min="5"
              max="100"
              value={populationSize}
              onChange={(e) => setPopulationSize(Number(e.target.value))}
              className="input-field w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brain-500 focus:border-transparent"
            />
          </div>

          {/* Кнопки управления */}
          <div className="space-y-3">
            <label className="block text-sm font-medium text-gray-700">
              Действия
            </label>
            <div className="flex space-x-3">
              <button
                onClick={handleResizePopulation}
                className="btn-secondary flex-1 py-2"
                disabled={isEvolving}
              >
                Изменить размер
              </button>
              <button
                onClick={handleStartEvolution}
                className="btn-primary flex-1 py-2"
                disabled={isEvolving}
              >
                {isEvolving ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mx-auto"></div>
                ) : (
                  <div className="flex items-center justify-center space-x-2">
                    <Play className="h-4 w-4" />
                    <span>Запустить</span>
                  </div>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Основная сетка с исправленной структурой */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
        {/* Текущая статистика */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Zap className="h-5 w-5 text-yellow-600" />
            <span>Текущее состояние</span>
            {loading && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-brain-600 ml-2"></div>
            )}
          </h3>

          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Поколение:</span>
              <span className="font-medium">{stats.generation || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Лучший фитнес:</span>
              <span className="font-medium">{(stats.max_fitness || 0).toFixed(3)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Средний фитнес:</span>
              <span className="font-medium">{(stats.avg_fitness || 0).toFixed(3)}</span>
            </div>

            <div className="flex justify-between">
              <span className="text-sm text-gray-600">Размер популяции:</span>
              <span className="font-medium">{stats.size || 0}</span>
            </div>
          </div>
        </div>

        {/* История эволюции и график - занимают оставшиеся 2 колонки */}
        <div className="xl:col-span-2 space-y-6">
          {/* История эволюции */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-green-600" />
              <span>История эволюции</span>
            </h3>

            <div className="overflow-x-auto">
              <table className="w-full">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Поколение
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Лучший фитнес
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Средний фитнес
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Размер популяции
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Время
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {evolutionHistory.map((gen) => (
                    <tr key={gen.id} className="hover:bg-gray-50">
                      <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        #{gen.generation || 0}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        <div className="flex items-center space-x-2">
                          <div className={`w-3 h-3 rounded-full ${
                            (gen.bestFitness || 0) > 0.8 ? 'bg-green-500' :
                            (gen.bestFitness || 0) > 0.5 ? 'bg-yellow-500' :
                            'bg-red-500'
                          }`} />
                          <span>{(gen.bestFitness || 0).toFixed(3)}</span>
                        </div>
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {(gen.avgFitness || 0).toFixed(3)}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                        {gen.populationSize}
                      </td>
                      <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-500">
                        {gen.timestamp}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {evolutionHistory.length === 0 && (
              <div className="text-center py-12">
                <TrendingUp className="mx-auto h-12 w-12 text-gray-400" />
                <h3 className="mt-2 text-sm font-medium text-gray-900">История пуста</h3>
                <p className="mt-1 text-sm text-gray-500">
                  Запустите эволюцию, чтобы увидеть прогресс.
                </p>
              </div>
            )}
          </div>

          {/* График прогресса */}
          <div className="card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Прогресс эволюции</h3>
            <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
              <div className="text-center">
                <BarChart3 className="mx-auto h-12 w-12 text-gray-400 mb-2" />
                <p className="text-sm text-gray-500">График прогресса</p>
                <p className="text-xs text-gray-400">Здесь будет ECharts график</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Evolution
