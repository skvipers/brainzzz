import React, { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Users, Brain, TrendingUp, Eye, Search, Network } from 'lucide-react'
import { useBrainStore } from '../stores/brainStore'

const Population = () => {
  const { population, stats, loading, fetchPopulation, fetchStats } = useBrainStore()
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState('fitness')
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc')

  useEffect(() => {
    fetchPopulation()
    fetchStats() // Добавляем загрузку статистики
    
    // Обновляем данные каждые 5 секунд для отображения актуальной информации
    const interval = setInterval(() => {
      fetchPopulation()
      fetchStats()
    }, 5000)
    
    return () => clearInterval(interval)
  }, [fetchPopulation, fetchStats])

  // Фильтрация и сортировка
  const filteredPopulation = population
    .filter(brain => 
      brain.id.toString().includes(searchTerm) ||
      brain.fitness.toString().includes(searchTerm)
    )
    .sort((a, b) => {
      let aValue: number
      let bValue: number
      
      switch (sortBy) {
        case 'fitness':
          aValue = a.fitness
          bValue = b.fitness
          break
        case 'nodes':
          aValue = a.nodes
          bValue = b.nodes
          break
        case 'connections':
          aValue = a.connections
          bValue = b.connections
          break
        case 'gp':
          aValue = a.gp
          bValue = b.gp
          break
        case 'age':
          aValue = a.age
          bValue = b.age
          break
        default:
          aValue = a.fitness
          bValue = b.fitness
      }
      
      return sortOrder === 'asc' ? aValue - bValue : bValue - aValue
    })

  const toggleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('desc')
    }
  }

  const getSortIcon = (field: string) => {
    if (sortBy !== field) return null
    return sortOrder === 'asc' ? '↑' : '↓'
  }

  if (loading) {
    return (
      <div className="px-8 flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brain-600"></div>
      </div>
    )
  }

  return (
    <div className="px-8">
      <div className="mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Популяция мозгов</h1>
          <p className="text-gray-600">Управление и мониторинг когнитивных структур</p>
        </div>
        <button
          onClick={async () => {
            await fetchPopulation()
            await fetchStats()
          }}
          className="btn-secondary flex items-center space-x-2 px-4 py-2"
          title="Обновить данные"
          disabled={loading}
        >
          {loading ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
          ) : (
            <Users className="h-4 w-4" />
          )}
          <span>{loading ? 'Обновление...' : 'Обновить'}</span>
        </button>
      </div>

      {/* Статистика */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <Users className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Всего мозгов</p>
              <p className="text-2xl font-bold text-gray-900">{stats.size || 0}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
              <Brain className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Средние узлы</p>
              <p className="text-2xl font-bold text-gray-900">{(stats.avg_nodes || 0).toFixed(1)}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <TrendingUp className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Лучший фитнес</p>
              <p className="text-2xl font-bold text-gray-900">{(stats.max_fitness || 0).toFixed(3)}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-lg bg-orange-100 flex items-center justify-center">
              <Brain className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Средние связи</p>
              <p className="text-2xl font-bold text-gray-900">{(stats.avg_connections || 0).toFixed(1)}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Контролы */}
      <div className="card mb-6">
        <div className="flex flex-col sm:flex-row gap-4 items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <input
                type="text"
                placeholder="Поиск по ID или фитнесу..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brain-500 focus:border-transparent"
              />
            </div>
            
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brain-500 focus:border-transparent"
            >
              <option value="fitness">По фитнесу</option>
              <option value="nodes">По узлам</option>
              <option value="connections">По связям</option>
              <option value="gp">По GP</option>
              <option value="age">По возрасту</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Показано:</span>
            <span className="font-medium">{filteredPopulation.length}</span>
            <span className="text-sm text-gray-600">из {population.length}</span>
          </div>
        </div>
      </div>

      {/* Таблица популяции */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => toggleSort('id')}>
                  ID {getSortIcon('id')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => toggleSort('fitness')}>
                  Фитнес {getSortIcon('fitness')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => toggleSort('nodes')}>
                  Узлы {getSortIcon('nodes')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => toggleSort('connections')}>
                  Связи {getSortIcon('connections')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => toggleSort('gp')}>
                  GP {getSortIcon('gp')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100" onClick={() => toggleSort('age')}>
                  Возраст {getSortIcon('age')}
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredPopulation.map((brain) => (
                <tr key={brain.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    #{brain.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center space-x-2">
                      <div className={`w-3 h-3 rounded-full ${
                        brain.fitness > 0.8 ? 'bg-green-500' :
                        brain.fitness > 0.5 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`} />
                      <span>{brain.fitness.toFixed(3)}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {brain.nodes}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {brain.connections}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center space-x-2">
                      <span>{brain.gp.toFixed(1)}</span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-brain-500 h-2 rounded-full" 
                          style={{ width: `${Math.min(brain.gp / 20 * 100, 100)}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {brain.age}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <Link
                        to={`/brain/${brain.id}`}
                        className="text-brain-600 hover:text-brain-900"
                        title="Просмотр деталей"
                      >
                        <Eye className="h-4 w-4" />
                      </Link>
                      <Link
                        to={`/brain/${brain.id}?view=visualizer`}
                        className="text-purple-600 hover:text-purple-900"
                        title="Визуализация"
                      >
                        <Network className="h-4 w-4" />
                      </Link>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {filteredPopulation.length === 0 && (
        <div className="text-center py-12">
          <Brain className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Мозги не найдены</h3>
          <p className="mt-1 text-sm text-gray-500">
            Попробуйте изменить параметры поиска или фильтрации.
          </p>
        </div>
      )}
    </div>
  )
}

export default Population 