import React, { useState, useEffect } from 'react'
import { useParams, Link, useSearchParams } from 'react-router-dom'
import { ArrowLeft, Brain, Activity, Zap, Eye, BarChart3, Network } from 'lucide-react'
import { useBrainStore } from '../stores/brainStore'
import BrainVisualizer from '../components/BrainVisualizer'

interface BrainDetail {
  id: number
  nodes: Array<{
    id: number
    type: 'input' | 'output' | 'hidden' | 'memory'
    activation: string
    bias: number
    threshold: number
  }>
  connections: Array<{
    id: number
    from: number
    to: number
    weight: number
    plasticity: number
    enabled: boolean
  }>
  gp: number
  fitness: number
  age: number
}

const BrainDetail = () => {
  const { id } = useParams<{ id: string }>()
  const [searchParams] = useSearchParams()
  const [brainDetail, setBrainDetail] = useState<BrainDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<number | null>(null)
  const [selectedConnection, setSelectedConnection] = useState<number | null>(null)
  const [showVisualizer, setShowVisualizer] = useState(false)

  useEffect(() => {
    const fetchBrainDetail = async () => {
      if (!id) return
      
      try {
        setLoading(true)
        const response = await fetch(`/api/population/${id}`)
        if (!response.ok) {
          throw new Error('Мозг не найден')
        }
        const data = await response.json()
        setBrainDetail(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Ошибка загрузки')
      } finally {
        setLoading(false)
      }
    }

    fetchBrainDetail()
  }, [id])

  // Автоматически показываем визуализатор при переходе с параметром view=visualizer
  useEffect(() => {
    const view = searchParams.get('view')
    if (view === 'visualizer' && brainDetail) {
      setShowVisualizer(true)
    }
  }, [searchParams, brainDetail])

  const getNodeTypeColor = (type: string) => {
    switch (type) {
      case 'input':
        return 'bg-blue-100 text-blue-800'
      case 'output':
        return 'bg-green-100 text-green-800'
      case 'memory':
        return 'bg-purple-100 text-purple-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getNodeTypeIcon = (type: string) => {
    switch (type) {
      case 'input':
        return '📥'
      case 'output':
        return '📤'
      case 'memory':
        return '💾'
      default:
        return '⚙️'
    }
  }

  const getWeightColor = (weight: number) => {
    if (weight > 0.5) return 'text-green-600'
    if (weight < -0.5) return 'text-red-600'
    return 'text-gray-600'
  }

  const getWeightStrength = (weight: number) => {
    return Math.abs(weight) > 0.7 ? 'font-bold' : 'font-normal'
  }

  if (loading) {
    return (
      <div className="px-8 flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brain-600"></div>
      </div>
    )
  }

  if (error || !brainDetail) {
    return (
      <div className="px-8">
        <div className="text-center py-12">
          <Brain className="mx-auto h-12 w-12 text-gray-400 mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Ошибка загрузки</h3>
          <p className="text-gray-500 mb-4">{error || 'Мозг не найден'}</p>
          <Link to="/population" className="btn-primary">
            Вернуться к популяции
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="px-8">
      {/* Заголовок и навигация */}
      <div className="mb-8">
        <div className="flex items-center space-x-4 mb-4">
          <Link
            to="/population"
            className="flex items-center space-x-2 text-brain-600 hover:text-brain-800"
          >
            <ArrowLeft className="h-5 w-5" />
            <span>К популяции</span>
          </Link>
        </div>
        
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Мозг #{brainDetail.id}
            </h1>
            <p className="text-gray-600">
              Детальная информация о структуре и параметрах
            </p>
          </div>
          
          <div className="flex items-center space-x-2">
            <span className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${
              brainDetail.fitness > 0.8 ? 'bg-green-100 text-green-800' :
              brainDetail.fitness > 0.5 ? 'bg-yellow-100 text-yellow-800' :
              'bg-red-100 text-red-800'
            }`}>
              Фитнес: {brainDetail.fitness.toFixed(3)}
            </span>
          </div>
        </div>
      </div>

      {/* Основная статистика */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                 <div className="card">
           <div className="flex items-center space-x-3">
             <div className="h-10 w-10 rounded-lg bg-blue-100 flex items-center justify-center">
               <Brain className="h-5 w-5 text-blue-600" />
             </div>
             <div>
               <p className="text-sm font-medium text-gray-600">Узлы</p>
               <p className="text-2xl font-bold text-gray-900">{brainDetail.nodes.length}</p>
             </div>
           </div>
         </div>

         <div className="card">
           <div className="flex items-center space-x-3">
             <div className="h-10 w-10 rounded-lg bg-green-100 flex items-center justify-center">
               <Network className="h-5 w-5 text-green-600" />
             </div>
             <div>
               <p className="text-sm font-medium text-gray-600">Связи</p>
               <p className="text-2xl font-bold text-gray-900">{brainDetail.connections.length}</p>
             </div>
           </div>
         </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-lg bg-purple-100 flex items-center justify-center">
              <Zap className="h-5 w-5 text-purple-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">GP</p>
              <p className="text-2xl font-bold text-gray-900">{brainDetail.gp.toFixed(1)}</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center space-x-3">
            <div className="h-10 w-10 rounded-lg bg-orange-100 flex items-center justify-center">
              <Activity className="h-5 w-5 text-orange-600" />
            </div>
            <div>
              <p className="text-sm font-medium text-gray-600">Возраст</p>
              <p className="text-2xl font-bold text-gray-900">{brainDetail.age}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Список узлов */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Brain className="h-5 w-5 text-brain-600" />
            <span>Узлы ({brainDetail.nodes.length})</span>
          </h3>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {brainDetail.nodes.map((node) => (
              <div
                key={node.id}
                className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                  selectedNode === node.id
                    ? 'border-brain-500 bg-brain-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedNode(selectedNode === node.id ? null : node.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <span className="text-lg">{getNodeTypeIcon(node.type)}</span>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-medium">#{node.id}</span>
                        <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getNodeTypeColor(node.type)}`}>
                          {node.type}
                        </span>
                      </div>
                      <div className="text-sm text-gray-600">
                        {node.activation} | bias: {node.bias.toFixed(2)} | threshold: {node.threshold.toFixed(2)}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Список связей */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <Network className="h-5 w-5 text-green-600" />
            <span>Связи ({brainDetail.connections.length})</span>
          </h3>
          
          <div className="space-y-3 max-h-96 overflow-y-auto">
            {brainDetail.connections.map((conn) => (
              <div
                key={conn.id}
                className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                  selectedConnection === conn.id
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => setSelectedConnection(selectedConnection === conn.id ? null : conn.id)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="text-sm text-gray-500">
                      #{conn.from} → #{conn.to}
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <span className={`text-sm ${getWeightColor(conn.weight)} ${getWeightStrength(conn.weight)}`}>
                      w: {conn.weight.toFixed(3)}
                    </span>
                    <span className="text-sm text-gray-500">
                      p: {conn.plasticity.toFixed(2)}
                    </span>
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                      conn.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {conn.enabled ? 'активна' : 'отключена'}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Визуализация графа */}
      <div className="card mt-8">
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center space-x-2">
          <BarChart3 className="h-5 w-5 text-purple-600" />
          <span>Визуализация структуры</span>
        </h3>
        
        <div className="h-96 bg-gray-50 rounded-lg flex items-center justify-center">
          <div className="text-center">
            <Network className="mx-auto h-16 w-16 text-gray-400 mb-4" />
            <p className="text-lg font-medium text-gray-900 mb-2">Граф структуры мозга</p>
            <p className="text-sm text-gray-500 mb-4">
              Здесь будет интерактивная визуализация через Cytoscape.js
            </p>
            <button 
              className="btn-primary flex items-center mx-auto space-x-2"
              onClick={() => setShowVisualizer(true)}
            >
              <Eye className="h-4 w-4" />
              <span>Открыть визуализатор</span>
            </button>
          </div>
        </div>
      </div>

      {/* Детальная информация о выбранном узле */}
      {selectedNode !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Узел #{selectedNode}</h3>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            
            {brainDetail.nodes[selectedNode] && (
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-gray-600">Тип:</span>
                  <span className={`ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getNodeTypeColor(brainDetail.nodes[selectedNode].type)}`}>
                    {getNodeTypeIcon(brainDetail.nodes[selectedNode].type)}
                    <span className="ml-1 capitalize">{brainDetail.nodes[selectedNode].type}</span>
                  </span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Активация:</span>
                  <span className="ml-2 text-sm">{brainDetail.nodes[selectedNode].activation}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Bias:</span>
                  <span className="ml-2 text-sm">{brainDetail.nodes[selectedNode].bias.toFixed(3)}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Threshold:</span>
                  <span className="ml-2 text-sm">{brainDetail.nodes[selectedNode].threshold.toFixed(3)}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Детальная информация о выбранной связи */}
      {selectedConnection !== null && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Связь #{selectedConnection}</h3>
              <button
                onClick={() => setSelectedConnection(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            
            {brainDetail.connections[selectedConnection] && (
              <div className="space-y-3">
                <div>
                  <span className="text-sm font-medium text-gray-600">От узла:</span>
                  <span className="ml-2 text-sm">#{brainDetail.connections[selectedConnection].from}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">К узлу:</span>
                  <span className="ml-2 text-sm">#{brainDetail.connections[selectedConnection].to}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Вес:</span>
                  <span className={`ml-2 text-sm ${getWeightColor(brainDetail.connections[selectedConnection].weight)}`}>
                    {brainDetail.connections[selectedConnection].weight.toFixed(3)}
                  </span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Пластичность:</span>
                  <span className="ml-2 text-sm">{brainDetail.connections[selectedConnection].plasticity.toFixed(2)}</span>
                </div>
                <div>
                  <span className="text-sm font-medium text-gray-600">Статус:</span>
                  <span className={`ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    brainDetail.connections[selectedConnection].enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                  }`}>
                    {brainDetail.connections[selectedConnection].enabled ? 'активна' : 'отключена'}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Brain Visualizer */}
      {showVisualizer && (
        <BrainVisualizer
          brainId={Number(id)}
          onClose={() => setShowVisualizer(false)}
        />
      )}
    </div>
  )
}

export default BrainDetail 