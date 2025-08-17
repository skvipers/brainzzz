import React, { useEffect, useRef, useState } from 'react'
import cytoscape from 'cytoscape'
import { Brain, Eye, Settings, Download, RotateCcw } from 'lucide-react'

interface BrainNode {
  id: number
  type: 'input' | 'output' | 'hidden' | 'memory'
  activation: string
  bias: number
  threshold: number
}

interface BrainConnection {
  id: number
  from: number
  to: number
  weight: number
  plasticity: number
  enabled: boolean
}

interface BrainVisualizerProps {
  brainId: number
  onClose?: () => void
}

const BrainVisualizer = ({ brainId, onClose }: BrainVisualizerProps) => {
  const cyRef = useRef<HTMLDivElement>(null)
  const cyInstanceRef = useRef<cytoscape.Core | null>(null)
  const [brainData, setBrainData] = useState<{
    nodes: BrainNode[]
    connections: BrainConnection[]
    gp: number
    fitness: number
    age: number
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [layout, setLayout] = useState<'grid' | 'circle' | 'random' | 'cola'>('cola')
  const [showWeights, setShowWeights] = useState(true)
  const [nodeSize, setNodeSize] = useState(30)

  // Загружаем данные о мозге
  useEffect(() => {
    const fetchBrainData = async () => {
      try {
        setLoading(true)
        console.log('🔄 Загружаю данные для мозга #', brainId)
        
        const response = await fetch(`/api/population/${brainId}`)
        console.log('📡 API Response status:', response.status)
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        console.log('📊 Полученные данные:', data)
        
        setBrainData(data)
      } catch (err) {
        console.error('❌ Ошибка загрузки данных:', err)
        setError(err instanceof Error ? err.message : 'Ошибка загрузки')
      } finally {
        setLoading(false)
      }
    }

    fetchBrainData()
  }, [brainId])

  // Инициализация Cytoscape
  useEffect(() => {
    if (!cyRef.current || !brainData) {
      console.log('⚠️ Не могу инициализировать Cytoscape:', { 
        hasRef: !!cyRef.current, 
        hasData: !!brainData 
      })
      return
    }

    console.log('🎯 Инициализирую Cytoscape с данными:', brainData)

    try {
      // Создаем элементы для Cytoscape
      const elements = {
        nodes: brainData.nodes.map(node => ({
          data: {
            id: node.id.toString(),
            label: `${node.type.charAt(0).toUpperCase()}${node.id}`,
            type: node.type,
            activation: node.activation,
            bias: node.bias,
            threshold: node.threshold
          }
        })),
        edges: brainData.connections
          .filter(conn => conn.enabled)
          .map(conn => ({
            data: {
              id: conn.id.toString(),
              source: conn.from.toString(),
              target: conn.to.toString(),
              weight: conn.weight,
              plasticity: conn.plasticity,
              label: showWeights ? conn.weight.toFixed(2) : ''
            }
          }))
      }

      console.log('🔗 Созданные элементы:', elements)

      // Создаем экземпляр Cytoscape
      const cy = cytoscape({
        container: cyRef.current,
        elements: elements,
        style: [
          // Стили для узлов
          {
            selector: 'node',
            style: {
              'background-color': '#e5e7eb',
              'border-color': '#374151',
              'border-width': 2,
              'width': nodeSize,
              'height': nodeSize,
              'label': 'data(label)',
              'font-size': '10px',
              'font-weight': 'bold',
              'text-valign': 'center',
              'text-halign': 'center',
              'text-wrap': 'wrap',
              'text-max-width': nodeSize * 0.8
            }
          },
          // Стили для входных узлов
          {
            selector: 'node[type = "input"]',
            style: {
              'background-color': '#3b82f6',
              'border-color': '#1e40af',
              'color': 'white'
            }
          },
          // Стили для выходных узлов
          {
            selector: 'node[type = "output"]',
            style: {
              'background-color': '#10b981',
              'border-color': '#047857',
              'color': 'white'
            }
          },
          // Стили для скрытых узлов
          {
            selector: 'node[type = "hidden"]',
            style: {
              'background-color': '#f59e0b',
              'border-color': '#d97706',
              'color': 'white'
            }
          },
          // Стили для узлов памяти
          {
            selector: 'node[type = "memory"]',
            style: {
              'background-color': '#8b5cf6',
              'border-color': '#7c3aed',
              'color': 'white'
            }
          },
          // Стили для связей
          {
            selector: 'edge',
            style: {
              'width': 'data(weight)',
              'line-color': function(ele: any) {
                const weight = ele.data('weight')
                if (weight > 0.5) return '#10b981' // Зеленый для сильных положительных
                if (weight < -0.5) return '#ef4444' // Красный для сильных отрицательных
                return '#6b7280' // Серый для слабых
              },
              'target-arrow-color': function(ele: any) {
                const weight = ele.data('weight')
                if (weight > 0.5) return '#10b981'
                if (weight < -0.5) return '#ef4444'
                return '#6b7280'
              },
              'target-arrow-shape': 'triangle',
              'arrow-scale': 0.5,
              'curve-style': 'bezier',
              'label': 'data(label)',
              'font-size': '8px',
              'text-rotation': 'autorotate',
              'text-margin-y': '-10px'
            }
          }
        ],
        layout: {
          name: layout,
          ...(layout === 'cola' && {
            nodeSpacing: 50,
            edgeLength: 100,
            animate: true,
            randomize: false,
            maxSimulationTime: 1500
          }),
          ...(layout === 'circle' && {
            radius: 200,
            startAngle: 0,
            sweep: 360
          }),
          ...(layout === 'grid' && {
            rows: Math.ceil(Math.sqrt(brainData.nodes.length)),
            cols: Math.ceil(Math.sqrt(brainData.nodes.length))
          })
        }
      })

      console.log('✅ Cytoscape инициализирован успешно')

      // Сохраняем экземпляр
      cyInstanceRef.current = cy

      // Добавляем обработчики событий
      cy.on('tap', 'node', function(evt) {
        const node = evt.target
        const data = node.data()
        console.log('👆 Узел:', data)
      })

      cy.on('tap', 'edge', function(evt) {
        const edge = evt.target
        const data = edge.data()
        console.log('👆 Связь:', data)
      })

      // Автоматически подгоняем размер
      cy.fit()
      cy.center()

      return () => {
        console.log('🧹 Уничтожаю Cytoscape')
        cy.destroy()
      }
    } catch (err) {
      console.error('❌ Ошибка инициализации Cytoscape:', err)
      setError(`Ошибка инициализации: ${err instanceof Error ? err.message : 'Неизвестная ошибка'}`)
    }
  }, [brainData, layout, showWeights, nodeSize])

  // Применяем новый layout
  const applyLayout = () => {
    if (!cyInstanceRef.current) return

    const cy = cyInstanceRef.current
    const layoutOptions = {
      name: layout,
      ...(layout === 'cola' && {
        nodeSpacing: 50,
        edgeLength: 100,
        animate: true,
        randomize: false,
        maxSimulationTime: 1500
      }),
      ...(layout === 'circle' && {
        radius: 200,
        startAngle: 0,
        sweep: 360
      }),
      ...(layout === 'grid' && {
        rows: Math.ceil(Math.sqrt(brainData?.nodes.length || 1)),
        cols: Math.ceil(Math.sqrt(brainData?.nodes.length || 1))
      })
    }

    cy.layout(layoutOptions).run()
  }

  // Экспорт графа
  const exportGraph = () => {
    if (!cyInstanceRef.current) return

    const cy = cyInstanceRef.current
    const png = cy.png({
      full: true,
      quality: 1,
      output: 'blob'
    })

    const url = URL.createObjectURL(png)
    const a = document.createElement('a')
    a.href = url
    a.download = `brain-${brainId}-${layout}.png`
    a.click()
    URL.revokeObjectURL(url)
  }

  // Сброс к исходному виду
  const resetView = () => {
    if (!cyInstanceRef.current) return

    const cy = cyInstanceRef.current
    cy.fit()
    cy.center()
  }

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brain-600 mx-auto"></div>
          <p className="mt-4 text-center text-gray-600">Загрузка структуры мозга...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 max-w-md">
          <div className="text-red-600 text-center mb-4">
            <Brain className="h-12 w-12 mx-auto" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Ошибка загрузки</h3>
          <p className="text-gray-600 mb-4">{error}</p>
          <div className="flex space-x-3">
            <button
              onClick={() => window.location.reload()}
              className="btn-primary flex-1"
            >
              Попробовать снова
            </button>
            {onClose && (
              <button
                onClick={onClose}
                className="btn-secondary flex-1"
              >
                Закрыть
              </button>
            )}
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-[90vw] h-[90vh] flex flex-col">
        {/* Заголовок */}
        <div className="flex items-center justify-between p-4 border-b">
          <div className="flex items-center space-x-3">
            <Brain className="h-6 w-6 text-brain-600" />
            <div>
              <h2 className="text-lg font-semibold text-gray-900">
                Визуализация мозга #{brainId}
              </h2>
              <p className="text-sm text-gray-600">
                GP: {brainData?.gp.toFixed(3)} | Fitness: {brainData?.fitness.toFixed(3)} | Age: {brainData?.age}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2">
            {/* Управление layout */}
            <select
              value={layout}
              onChange={(e) => setLayout(e.target.value as any)}
              className="input-field text-sm"
            >
              <option value="cola">Cola (автоматический)</option>
              <option value="circle">Круг</option>
              <option value="grid">Сетка</option>
              <option value="random">Случайный</option>
            </select>
            
            <button
              onClick={applyLayout}
              className="btn-secondary p-2"
              title="Применить layout"
            >
              <RotateCcw className="h-4 w-4" />
            </button>
            
            {/* Показать/скрыть веса */}
            <button
              onClick={() => setShowWeights(!showWeights)}
              className={`btn-secondary p-2 ${showWeights ? 'bg-brain-100 text-brain-800' : ''}`}
              title="Показать веса связей"
            >
              <Eye className="h-4 w-4" />
            </button>
            
            {/* Размер узлов */}
            <select
              value={nodeSize}
              onChange={(e) => setNodeSize(Number(e.target.value))}
              className="input-field text-sm w-20"
            >
              <option value={20}>20</option>
              <option value={30}>30</option>
              <option value={40}>40</option>
              <option value={50}>50</option>
            </select>
            
            {/* Экспорт */}
            <button
              onClick={exportGraph}
              className="btn-secondary p-2"
              title="Экспортировать граф"
            >
              <Download className="h-4 w-4" />
            </button>
            
            {/* Настройки */}
            <button className="btn-secondary p-2" title="Настройки">
              <Settings className="h-4 w-4" />
            </button>
            
            {/* Закрыть */}
            {onClose && (
              <button
                onClick={onClose}
                className="btn-secondary p-2"
                title="Закрыть"
              >
                ×
              </button>
            )}
          </div>
        </div>
        
        {/* Легенда */}
        <div className="px-4 py-2 bg-gray-50 border-b">
          <div className="flex items-center space-x-6 text-sm">
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-blue-500 rounded-full"></div>
              <span>Входные узлы</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-orange-500 rounded-full"></div>
              <span>Скрытые узлы</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-500 rounded-full"></div>
              <span>Выходные узлы</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-purple-500 rounded-full"></div>
              <span>Узлы памяти</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-green-500 rounded-full"></div>
              <span>Положительные связи</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-4 h-4 bg-red-500 rounded-full"></div>
              <span>Отрицательные связи</span>
            </div>
          </div>
        </div>
        
        {/* Граф */}
        <div className="flex-1 p-4">
          <div
            ref={cyRef}
            className="w-full h-full border border-gray-200 rounded-lg bg-gray-50"
            style={{ minHeight: '500px' }}
          />
          {/* Отладочная информация */}
          <div className="mt-2 text-xs text-gray-500">
            Debug: brainData={brainData ? 'loaded' : 'null'}, 
            nodes={brainData?.nodes.length || 0}, 
            connections={brainData?.connections.length || 0}
          </div>
        </div>
        
        {/* Статистика */}
        <div className="px-4 py-2 bg-gray-50 border-t">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>
              Узлов: {brainData?.nodes.length} | 
              Связей: {brainData?.connections.filter(c => c.enabled).length} | 
              Layout: {layout}
            </span>
            <button
              onClick={resetView}
              className="text-brain-600 hover:text-brain-800"
            >
              Сбросить вид
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default BrainVisualizer 