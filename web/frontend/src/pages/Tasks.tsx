import { useState } from 'react'
import { Target, Plus, Play, Pause, RotateCcw, BarChart3, CheckCircle, Clock, AlertCircle } from 'lucide-react'

interface Task {
  id: string
  name: string
  description: string
  type: 'xor' | 'sequence' | 'custom'
  status: 'active' | 'paused' | 'completed' | 'failed'
  difficulty: 'easy' | 'medium' | 'hard'
  bestScore: number
  avgScore: number
  attempts: number
  createdAt: string
  lastRun: string
}

const Tasks = () => {
  const [tasks, setTasks] = useState<Task[]>([
    {
      id: '1',
      name: 'XOR задача',
      description: 'Классическая задача исключающего ИЛИ',
      type: 'xor',
      status: 'active',
      difficulty: 'easy',
      bestScore: 0.98,
      avgScore: 0.76,
      attempts: 45,
      createdAt: '2024-12-17 18:00:00',
      lastRun: '2024-12-17 20:15:00'
    },
    {
      id: '2',
      name: 'Последовательности',
      description: 'Генерация и распознавание числовых последовательностей',
      type: 'sequence',
      status: 'active',
      difficulty: 'medium',
      bestScore: 0.87,
      avgScore: 0.62,
      attempts: 32,
      createdAt: '2024-12-17 18:30:00',
      lastRun: '2024-12-17 20:10:00'
    },
    {
      id: '3',
      name: 'Паттерны',
      description: 'Распознавание визуальных паттернов',
      type: 'custom',
      status: 'paused',
      difficulty: 'hard',
      bestScore: 0.45,
      avgScore: 0.28,
      attempts: 18,
      createdAt: '2024-12-17 19:00:00',
      lastRun: '2024-12-17 19:45:00'
    }
  ])

  const [showNewTaskForm, setShowNewTaskForm] = useState(false)
  const [newTask, setNewTask] = useState({
    name: '',
    description: '',
    type: 'xor' as const,
    difficulty: 'easy' as const,
    status: 'active' as const
  })

  const taskTypes = [
    { value: 'xor' as const, label: 'XOR', description: 'Логическая операция исключающего ИЛИ' },
    { value: 'sequence' as const, label: 'Последовательности', description: 'Запоминание и воспроизведение последовательностей' },
    { value: 'classification' as const, label: 'Классификация', description: 'Разделение данных на классы' },
    { value: 'regression' as const, label: 'Регрессия', description: 'Предсказание числовых значений' },
    { value: 'custom' as const, label: 'Пользовательская', description: 'Собственная задача с настраиваемыми параметрами' }
  ]

  const difficulties = [
    { value: 'easy' as const, label: 'Легкая', description: 'Базовые задачи для начинающих мозгов' },
    { value: 'medium' as const, label: 'Средняя', description: 'Задачи средней сложности' },
    { value: 'hard' as const, label: 'Сложная', description: 'Сложные задачи для продвинутых мозгов' }
  ]

  const getStatusIcon = (status: Task['status']) => {
    switch (status) {
      case 'active':
        return <Play className="h-4 w-4 text-green-600" />
      case 'paused':
        return <Pause className="h-4 w-4 text-yellow-600" />
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-blue-600" />
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-600" />
      default:
        return <Clock className="h-4 w-4 text-gray-600" />
    }
  }

  const getStatusColor = (status: Task['status']) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'paused':
        return 'bg-yellow-100 text-yellow-800'
      case 'completed':
        return 'bg-blue-100 text-blue-800'
      case 'failed':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getDifficultyColor = (difficulty: Task['difficulty']) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800'
      case 'medium':
        return 'bg-yellow-100 text-yellow-800'
      case 'hard':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const handleCreateTask = () => {
    if (newTask.name && newTask.description) {
      const task: Task = {
        id: Date.now().toString(),
        ...newTask,
        status: 'active',
        bestScore: 0,
        avgScore: 0,
        attempts: 0,
        createdAt: new Date().toLocaleString(),
        lastRun: '-'
      }
      setTasks([...tasks, task])
      setNewTask({ name: '', description: '', type: 'custom', difficulty: 'medium' })
      setShowNewTaskForm(false)
    }
  }

  const toggleTaskStatus = (taskId: string) => {
    setTasks(tasks.map(task => 
      task.id === taskId 
        ? { ...task, status: task.status === 'active' ? 'paused' : 'active' }
        : task
    ))
  }

  const deleteTask = (taskId: string) => {
    setTasks(tasks.filter(task => task.id !== taskId))
  }

  const resetTask = (taskId: string) => {
    setTasks(tasks.map(task => 
      task.id === taskId 
        ? { ...task, bestScore: 0, avgScore: 0, attempts: 0, lastRun: '-' }
        : task
    ))
  }

  return (
    <div className="px-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Задачи</h1>
        <p className="text-gray-600">Управление задачами для обучения мозгов</p>
      </div>

      {/* Статистика задач */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
              <Target className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Всего задач</p>
              <p className="text-2xl font-bold text-gray-900">{tasks.length}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
              <Play className="h-5 w-5 text-green-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Активные</p>
              <p className="text-2xl font-bold text-gray-900">
                {tasks.filter(t => t.status === 'active').length}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <BarChart3 className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Лучший результат</p>
              <p className="text-2xl font-bold text-gray-900">
                {Math.max(...tasks.map(t => t.bestScore), 0).toFixed(2)}
              </p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-lg bg-orange-100 flex items-center justify-center">
              <RotateCcw className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Всего попыток</p>
              <p className="text-2xl font-bold text-gray-900">
                {tasks.reduce((sum, t) => sum + t.attempts, 0)}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Кнопка создания новой задачи */}
      <div className="mb-6">
        <button
          onClick={() => setShowNewTaskForm(true)}
          className="btn-primary flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Создать новую задачу</span>
        </button>
      </div>

      {/* New Task Form */}
      {showNewTaskForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold mb-4">Создать новую задачу</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Название задачи *
                </label>
                <input
                  type="text"
                  value={newTask.name}
                  onChange={(e) => setNewTask({...newTask, name: e.target.value})}
                  className="input-field w-full"
                  placeholder="Например: XOR с 3 входами"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Описание
                </label>
                <textarea
                  value={newTask.description}
                  onChange={(e) => setNewTask({...newTask, description: e.target.value})}
                  className="input-field w-full h-20"
                  placeholder="Подробное описание задачи, входные данные, ожидаемый результат..."
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Тип задачи *
                </label>
                <select
                  value={newTask.type}
                  onChange={(e) => setNewTask({...newTask, type: e.target.value})}
                  className="input-field w-full"
                >
                  {taskTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.label} - {type.description}
                    </option>
                  ))}
                </select>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Сложность *
                </label>
                <select
                  value={newTask.difficulty}
                  onChange={(e) => setNewTask({...newTask, difficulty: e.target.value})}
                  className="input-field w-full"
                >
                  {difficulties.map(diff => (
                    <option key={diff.value} value={diff.value}>
                      {diff.label} - {diff.description}
                    </option>
                  ))}
                </select>
              </div>
              
              <div className="text-sm text-gray-600 bg-gray-50 p-3 rounded">
                <p><strong>Советы по созданию задач:</strong></p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li><strong>XOR:</strong> Логическая задача для проверки способности к нелинейному мышлению</li>
                  <li><strong>Последовательности:</strong> Проверяет память и способность к паттернам</li>
                  <li><strong>Пользовательская:</strong> Создайте собственную задачу с помощью Python кода</li>
                </ul>
              </div>
            </div>
            
            <div className="flex space-x-3 mt-6">
              <button
                onClick={() => setShowNewTaskForm(false)}
                className="btn-secondary flex-1"
              >
                Отмена
              </button>
              <button
                onClick={handleCreateTask}
                className="btn-primary flex-1"
                disabled={!newTask.name.trim()}
              >
                Создать
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Список задач */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Задача
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Статус
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Сложность
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Лучший результат
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Попытки
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Действия
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {tasks.map((task) => (
                <tr key={task.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <div className="text-sm font-medium text-gray-900">{task.name}</div>
                      <div className="text-sm text-gray-500">{task.description}</div>
                      <div className="text-xs text-gray-400 mt-1">
                        Создана: {task.createdAt}
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(task.status)}`}>
                      {getStatusIcon(task.status)}
                      <span className="ml-1 capitalize">{task.status}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getDifficultyColor(task.difficulty)}`}>
                      {task.difficulty}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center space-x-2">
                      <span>{task.bestScore.toFixed(2)}</span>
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full" 
                          style={{ width: `${task.bestScore * 100}%` }}
                        />
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {task.attempts}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex space-x-2">
                      <button
                        onClick={() => toggleTaskStatus(task.id)}
                        className="text-brain-600 hover:text-brain-900"
                        title={task.status === 'active' ? 'Приостановить' : 'Запустить'}
                      >
                        {task.status === 'active' ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                      </button>
                      <button
                        onClick={() => resetTask(task.id)}
                        className="text-yellow-600 hover:text-yellow-900"
                        title="Сбросить статистику"
                      >
                        <RotateCcw className="h-4 w-4" />
                      </button>
                      <button
                        onClick={() => deleteTask(task.id)}
                        className="text-red-600 hover:text-red-900"
                        title="Удалить задачу"
                      >
                        ×
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {tasks.length === 0 && (
        <div className="text-center py-12">
          <Target className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">Задачи не найдены</h3>
          <p className="mt-1 text-sm text-gray-500">
            Создайте первую задачу для начала обучения мозгов.
          </p>
        </div>
      )}
    </div>
  )
}

export default Tasks 