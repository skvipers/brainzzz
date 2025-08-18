import React, { useEffect, useRef, useState } from 'react'
import cytoscape, { Core, NodeSingular, EdgeSingular } from 'cytoscape'
import { Brain, Eye, Settings, Download, RotateCcw, Info, BarChart3, Activity } from 'lucide-react'

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

interface SelectedElement {
  type: 'node' | 'edge'
  data: any
}

const BrainVisualizer = ({ brainId, onClose }: BrainVisualizerProps) => {
  const cyRef = useRef<HTMLDivElement>(null)
  const cyInstanceRef = useRef<cytoscape.Core | null>(null)
  const [brainData, setBrainData] = useState<{
    id: number
    nodes: BrainNode[]
    connections: BrainConnection[]
    gp: number
    fitness: number
    age: number
  } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [layout, setLayout] = useState<'grid' | 'circle' | 'random' | 'concentric'>('concentric')
  const [showWeights, setShowWeights] = useState(true)
  const [nodeSize, setNodeSize] = useState(30)
  const [selectedElement, setSelectedElement] = useState<SelectedElement | null>(null)
  const [showStats, setShowStats] = useState(true)
  const [showDisabledConnections, setShowDisabledConnections] = useState(false)
  const [showLegend, setShowLegend] = useState(true)

  // Функция валидации данных мозга
  const validateBrainData = (data: any): boolean => {
    if (!data || typeof data !== 'object') {
      console.error('❌ Данные мозга не являются объектом:', data)
      return false
    }

    if (!Array.isArray(data.nodes) || !Array.isArray(data.connections)) {
      console.error('❌ Отсутствуют nodes или connections:', data)
      return false
    }

    if (typeof data.gp !== 'number' || typeof data.fitness !== 'number' || typeof data.age !== 'number') {
      console.error('❌ Отсутствуют обязательные поля gp, fitness или age:', data)
      return false
    }

    // Проверяем структуру узлов
    for (const node of data.nodes) {
      if (!node.id || !node.type || !node.activation || typeof node.bias !== 'number' || typeof node.threshold !== 'number') {
        console.error('❌ Неверная структура узла:', node)
        return false
      }
    }

    // Проверяем структуру связей
    for (const conn of data.connections) {
      if (!conn.id || !conn.from || !conn.to || typeof conn.weight !== 'number' || typeof conn.plasticity !== 'number' || typeof conn.enabled !== 'boolean') {
        console.error('❌ Неверная структура связи:', conn)
        return false
      }
    }

    console.log('✅ Данные мозга прошли валидацию')
    return true
  }

  // Вычисляем статистику мозга
  const calculateBrainStats = () => {
    if (!brainData) return null

    const enabledConnections = brainData.connections.filter(c => c.enabled)
    const weights = enabledConnections.map(c => c.weight)
    const plasticities = enabledConnections.map(c => c.plasticity)

    const nodeTypes = brainData.nodes.reduce((acc, node) => {
      acc[node.type] = (acc[node.type] || 0) + 1
      return acc
    }, {} as Record<string, number>)

    return {
      totalNodes: brainData.nodes.length,
      totalConnections: enabledConnections.length,
      networkDensity: enabledConnections.length / (brainData.nodes.length * (brainData.nodes.length - 1)),
      avgWeight: weights.reduce((a, b) => a + b, 0) / weights.length,
      weightStd: Math.sqrt(weights.reduce((acc, w) => acc + Math.pow(w - weights.reduce((a, b) => a + b, 0) / weights.length, 2), 0) / weights.length),
      avgPlasticity: plasticities.reduce((a, b) => a + b, 0) / plasticities.length,
      nodeTypes,
      positiveConnections: weights.filter(w => w > 0).length,
      negativeConnections: weights.filter(w => w < 0).length,
      strongConnections: weights.filter(w => Math.abs(w) > 0.5).length
    }
  }

  // Загружаем данные о мозге
  useEffect(() => {
    // Предотвращаем дублирование вызовов
    let isMounted = true

    const fetchBrainData = async () => {
      try {
        if (!isMounted) return
        setLoading(true)
        console.log('🔄 Загружаю данные для мозга #', brainId)

        const response = await fetch(`/api/population/${brainId}`)
        console.log('📡 API Response status:', response.status)

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }

        const data = await response.json()
        console.log('📊 Полученные данные:', data)

        // Отладочная информация о весах связей
        if (data.connections) {
          console.log('🔍 Анализ весов связей:')
          data.connections.forEach((conn: any) => {
            const weight = conn.weight
            let category = ''
            if (weight > 0.7) category = 'Очень сильная положительная (>0.7)'
            else if (weight > 0.3) category = 'Сильная положительная (0.3-0.7)'
            else if (weight > 0) category = 'Слабая положительная (0-0.3)'
            else if (weight < -0.7) category = 'Очень сильная отрицательная (<-0.7)'
            else if (weight < -0.3) category = 'Сильная отрицательная (-0.7--0.3)'
            else if (weight < 0) category = 'Слабая отрицательная (-0.3-0)'
            else category = 'Нулевая (=0)'

            console.log(`  Связь ${conn.id}: вес=${weight}, категория=${category}, enabled=${conn.enabled}`)
          })
        }

        // Валидируем данные перед установкой
        if (validateBrainData(data) && isMounted) {
          setBrainData(data)

          // Автоматически включаем показ неактивных связей, если все связи неактивны
          if (data.connections && data.connections.length > 0 && data.connections.every(c => !c.enabled)) {
            console.log('⚠️ Все связи неактивны, автоматически включаю показ неактивных связей')
            setShowDisabledConnections(true)
          }
        } else if (isMounted) {
          throw new Error('Неверная структура данных мозга')
        }
      } catch (err) {
        if (isMounted) {
          console.error('❌ Ошибка загрузки данных:', err)
          setError(err instanceof Error ? err.message : 'Ошибка загрузки')
        }
      } finally {
        if (isMounted) {
          setLoading(false)
        }
      }
    }

    // Проверяем, что brainId изменился, чтобы избежать дублирования
    if (brainId && (!brainData || brainData.id !== brainId)) {
      fetchBrainData()
    }

    return () => {
      isMounted = false
    }
  }, [brainId]) // Убираем brainData из зависимостей

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
            threshold: node.threshold,
            // Дополнительные данные для подсказок
            fullLabel: `${node.type.toUpperCase()} ${node.id}\n${node.activation}\nbias: ${node.bias.toFixed(3)}\nthreshold: ${node.threshold.toFixed(3)}`
          }
        })),
        edges: brainData.connections
          .filter(conn => conn.enabled || showDisabledConnections)
          .map(conn => ({
            data: {
              id: `edge_${conn.id}_${conn.from}_${conn.to}`, // Уникальный ID для каждой связи
              source: conn.from.toString(),
              target: conn.to.toString(),
              weight: conn.weight,
              plasticity: conn.plasticity,
              enabled: conn.enabled,
              label: showWeights ? conn.weight.toFixed(2) : '',
              // Дополнительные данные для подсказок
              fullLabel: `Связь ${conn.id}\nВес: ${conn.weight.toFixed(3)}\nПластичность: ${conn.plasticity.toFixed(3)}\n${conn.weight > 0 ? 'Возбуждающая' : 'Тормозящая'}\n${conn.enabled ? 'Активна' : 'Неактивна'}`
            }
          }))
      }

      // Дополнительная диагностика формата элементов
      console.log('🔍 Диагностика формата элементов:')
      console.log('  - Формат узла:', JSON.stringify(elements.nodes[0], null, 2))
      console.log('  - Формат связи:', JSON.stringify(elements.edges[0], null, 2))
      console.log('  - Все узлы имеют data.id:', elements.nodes.every(n => n.data && n.data.id))
      console.log('  - Все связи имеют data.source и data.target:', elements.edges.every(e => e.data && e.data.source && e.data.target))

      // Проверяем, что все узлы существуют для связей
      const nodeIds = new Set(elements.nodes.map(n => n.data.id))
      const invalidEdges = elements.edges.filter(edge =>
        !nodeIds.has(edge.data.source) || !nodeIds.has(edge.data.target)
      )
      if (invalidEdges.length > 0) {
        console.warn('⚠️ Найдены связи с несуществующими узлами:', invalidEdges)
      }

      // Дополнительная проверка данных связей
      console.log('🔍 Детали связей:')
      elements.edges.forEach((edge, index) => {
        console.log(`  Связь ${index + 1}:`, {
          id: edge.data.id,
          source: edge.data.source,
          target: edge.data.target,
          weight: edge.data.weight,
          sourceExists: nodeIds.has(edge.data.source),
          targetExists: nodeIds.has(edge.data.target)
        })
      })

      // Создаем экземпляр Cytoscape
      const cy = cytoscape({
        container: cyRef.current,
        elements: elements, // Передаем все элементы (узлы и связи)
        style: [
          // Стили для узлов
          {
            selector: 'node',
            style: {
              'background-color': '#e5e7eb',
              'border-color': '#374151',
              'border-width': '3px',
              'width': function(ele: NodeSingular) {
                const nodeType = ele.data('type') as string
                if (nodeType === 'input' || nodeType === 'output') return (nodeSize * 1.2).toString()
                if (nodeType === 'memory') return (nodeSize * 1.1).toString()
                return nodeSize.toString()
              },
              'height': function(ele: NodeSingular) {
                const nodeType = ele.data('type') as string
                if (nodeType === 'input' || nodeType === 'output') return (nodeSize * 1.2).toString()
                if (nodeType === 'memory') return (nodeSize * 1.1).toString()
                return nodeSize.toString()
              },
              'label': 'data(label)',
              'font-size': 10,
              'font-weight': 'bold',
              'text-valign': 'center',
              'text-halign': 'center',
              'text-wrap': 'wrap',
              'text-max-width': (nodeSize * 0.8).toString(),
              'text-outline-color': 'white',
              'text-outline-width': '2px',
              'shape': 'ellipse'
            }
          },
          // Стили для входных узлов
          {
            selector: 'node[type = "input"]',
            style: {
              'background-color': '#3b82f6',
              'border-color': '#1e40af',
              'border-width': '4px',
              'color': 'white',
              'text-outline-color': '#1e40af',
              'text-outline-width': '2px'
            }
          },
          // Стили для выходных узлов
          {
            selector: 'node[type = "output"]',
            style: {
              'background-color': '#10b981',
              'border-color': '#047857',
              'border-width': '4px',
              'color': 'white',
              'text-outline-color': '#047857',
              'text-outline-width': '2px'
            }
          },
          // Стили для скрытых узлов
          {
            selector: 'node[type = "hidden"]',
            style: {
              'background-color': '#f59e0b',
              'border-color': '#d97706',
              'border-width': '3px',
              'color': 'white',
              'text-outline-color': '#d97706',
              'text-outline-width': '2px'
            }
          },
          // Стили для узлов памяти
          {
            selector: 'node[type = "memory"]',
            style: {
              'background-color': '#8b5cf6',
              'border-color': '#7c3aed',
              'border-width': '3px',
              'color': 'white',
              'text-outline-color': '#7c3aed',
              'text-outline-width': '2px'
            }
          },
          // Стили для связей
          {
            selector: 'edge',
            style: {
              'width': function(ele: EdgeSingular) {
                const weight = Math.abs(ele.data('weight') as number)
                const enabled = ele.data('enabled') as boolean
                if (!enabled) return 1
                return Math.max(1.5, weight * 4 + 1.5)
              },
              'line-color': '#6b7280', // Базовый цвет (будет переопределен)
              'target-arrow-color': '#6b7280', // Базовый цвет (будет переопределен)
              'target-arrow-shape': 'triangle',
              'arrow-scale': function(ele: EdgeSingular) {
                const enabled = ele.data('enabled') as boolean
                return enabled ? 0.8 : 0.4
              },
              'curve-style': 'bezier',
              'line-style': function(ele: EdgeSingular) {
                const enabled = ele.data('enabled') as boolean
                return enabled ? 'solid' : 'dashed'
              },
              'label': function(ele: EdgeSingular) {
                if (!showWeights) return ''
                const weight = ele.data('weight') as number
                const plasticity = ele.data('plasticity') as number
                const enabled = ele.data('enabled') as boolean
                if (!enabled) return 'DISABLED'
                return `${weight.toFixed(2)}\n${plasticity.toFixed(2)}`
              },
              'font-size': 8,
              'text-rotation': 'autorotate',
              'text-margin-y': -15,
              'text-outline-color': 'white',
              'text-outline-width': '2px',
              'text-background-color': 'rgba(255, 255, 255, 0.8)',
              'text-background-padding': '2px',
              'text-background-opacity': 0.8
            }
          }
        ],
        layout: {
          name: layout,
          ...(layout === 'concentric' && {
            concentric: function(node: any) {
              return node.degree()
            },
            levelWidth: function(nodes: any) {
              return 2
            },
            animate: true,
            animationDuration: 1000
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
        } as any
      })

      console.log('✅ Cytoscape инициализирован успешно')
      console.log('🔍 Проверка элементов после создания:')
      console.log('  Узлы:', cy.elements('node').length)
      console.log('  Связи:', cy.elements('edge').length)
      console.log('  Всего элементов:', cy.elements().length)

      // Дополнительная проверка через небольшую задержку
      setTimeout(() => {
        console.log('🔍 Проверка элементов через 50ms:')
        console.log('  Узлы:', cy.elements('node').length)
        console.log('  Связи:', cy.elements('edge').length)
        console.log('  Всего элементов:', cy.elements().length)
      }, 50)

      // Сохраняем экземпляр
      cyInstanceRef.current = cy

      // Добавляем обработчики событий
      cy.on('tap', 'node', function(evt) {
        const node = evt.target as NodeSingular
        const data = node.data()
        setSelectedElement({
          type: 'node',
          data: data
        })
        console.log('👆 Узел:', data)
      })

      cy.on('tap', 'edge', function(evt) {
        const edge = evt.target as EdgeSingular
        const data = edge.data()
        setSelectedElement({
          type: 'edge',
          data: data
        })
        console.log('👆 Связь:', data)
      })

      // Сброс выбора при клике на пустое место
      cy.on('tap', function(evt) {
        if (evt.target === cy) {
          setSelectedElement(null)
        }
      })

      // Автоматически подгоняем размер
      cy.fit()
      cy.center()

      // Проверяем, что все элементы добавлены корректно
      console.log('🔍 Проверка элементов после инициализации:')
      console.log('  Ожидалось узлов:', elements.nodes.length)
      console.log('  Фактически узлов:', cy.elements('node').length)
      console.log('  Ожидалось связей:', elements.edges.length)
      console.log('  Фактически связей:', cy.elements('edge').length)

      // Применяем стили к связям один раз после инициализации
      console.log('🎯 Вызываю applyEdgeStyles после инициализации...')
      setTimeout(() => {
        applyEdgeStyles(cy)
      }, 200) // Увеличиваем время на отрисовку

      // Дополнительная проверка размеров после инициализации
      setTimeout(() => {
        try {
          cy.resize()
          cy.fit()
          cy.center()

          // Дополнительная проверка элементов
          console.log('🔍 Проверка элементов после инициализации:')
          console.log('  Узлы:', cy.elements('node').length)
          console.log('  Связи:', cy.elements('edge').length)
        } catch (err) {
          console.error('Ошибка дополнительной проверки размеров:', err)
        }
      }, 200)

      return () => {
        console.log('🧹 Уничтожаю Cytoscape')
        cy.destroy()
      }
    } catch (err) {
      console.error('❌ Ошибка инициализации Cytoscape:', err)
      setError(`Ошибка инициализации: ${err instanceof Error ? err.message : 'Неизвестная ошибка'}`)
    }
  }, [brainData, layout, showWeights, nodeSize]) // Убираем showDisabledConnections из зависимостей

  // Ref для отслеживания первого рендера
  const isFirstRender = useRef(true)

  // Отдельный useEffect для обновления связей при изменении showDisabledConnections
  useEffect(() => {
    if (!cyInstanceRef.current || !brainData) return

    // Пропускаем первый рендер, чтобы не конфликтовать с основным useEffect
    if (isFirstRender.current) {
      isFirstRender.current = false
      return
    }

    const cy = cyInstanceRef.current
    console.log('🔄 Обновляю связи при изменении showDisabledConnections:', showDisabledConnections)
    console.log('🔍 Текущее количество связей до удаления:', cy.elements('edge').length)

    try {
      // Удаляем все существующие связи
      cy.elements('edge').remove()
      console.log('🗑️ Все связи удалены')

      // Создаем новые связи с учетом текущего состояния showDisabledConnections
      console.log('🔍 Всего связей в данных:', brainData.connections.length)
      console.log('🔍 Активных связей:', brainData.connections.filter(c => c.enabled).length)
      console.log('🔍 Неактивных связей:', brainData.connections.filter(c => !c.enabled).length)

      const filteredConnections = brainData.connections.filter(conn => conn.enabled || showDisabledConnections)
      console.log('🔍 Связей после фильтрации:', filteredConnections.length)

      const newEdges = filteredConnections.map(conn => ({
          data: {
            id: `edge_${conn.id}_${conn.from}_${conn.to}`, // Уникальный ID для каждой связи
            source: conn.from.toString(),
            target: conn.to.toString(),
            weight: conn.weight,
            plasticity: conn.plasticity,
            enabled: conn.enabled,
            label: showWeights ? conn.weight.toFixed(2) : '',
            fullLabel: `Связь ${conn.id}\nВес: ${conn.weight.toFixed(3)}\nПластичность: ${conn.plasticity.toFixed(3)}\n${conn.weight > 0 ? 'Возбуждающая' : 'Тормозящая'}\n${conn.enabled ? 'Активна' : 'Неактивна'}`
          }
        }))

      // Добавляем новые связи
      const addedEdges = cy.add(newEdges)
      console.log('🔍 Добавленные связи:', addedEdges.length)
      console.log('🔍 Всего связей в Cytoscape после добавления:', cy.elements('edge').length)

      // Применяем стили к новым связям
      setTimeout(() => {
        applyEdgeStyles(cy)
      }, 50)

      console.log('✅ Связи обновлены:', newEdges.length)
    } catch (err) {
      console.error('❌ Ошибка обновления связей:', err)
    }
  }, [showDisabledConnections, brainData, showWeights])

  // Применяем новый layout
  const applyLayout = () => {
    if (!cyInstanceRef.current) return

    const cy = cyInstanceRef.current
    const layoutOptions = {
      name: layout,
      ...(layout === 'concentric' && {
        concentric: function(node: any) {
          return node.degree()
        },
        levelWidth: function(nodes: any) {
          return 2
        },
        animate: true,
        animationDuration: 1000
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
    } as any

    cy.layout(layoutOptions).run()

    // Обновляем стили связей после изменения layout
    setTimeout(() => {
      applyEdgeStyles(cy)
    }, 1100) // После завершения анимации
  }

  // Обновляем размер Cytoscape при изменении статистики
  useEffect(() => {
    if (cyInstanceRef.current && brainData) {
      const cy = cyInstanceRef.current
      // Увеличиваем задержку для корректного обновления DOM
      setTimeout(() => {
        try {
          // Проверяем, что контейнер существует и имеет размеры
          const container = cy.container()
          if (container && container.offsetWidth > 0 && container.offsetHeight > 0) {
            // Принудительно обновляем размеры
            cy.resize()

            // Пересчитываем позиции элементов
            cy.elements().forEach(ele => {
              ele.position('x', ele.position('x'))
              ele.position('y', ele.position('y'))
            })

            // Подгоняем размер и центрируем
            cy.fit()
            cy.center()

            // Применяем текущий layout заново только если есть элементы
            if (cy.elements().length > 0) {
              const layoutOptions = {
                name: layout,
                ...(layout === 'concentric' && {
                  concentric: function(node: any) {
                    return node.degree()
                  },
                  levelWidth: function(nodes: any) {
                    return 2
                  },
                  animate: true,
                  animationDuration: 500
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
              } as any

              cy.layout(layoutOptions).run()
            }

            console.log('✅ Cytoscape успешно обновлен после изменения статистики')
          } else {
            console.warn('⚠️ Контейнер Cytoscape не готов для обновления')
          }
        } catch (err) {
          console.error('❌ Ошибка обновления размеров Cytoscape:', err)
          // Пытаемся восстановить состояние
          try {
            cy.fit()
            cy.center()
          } catch (recoveryErr) {
            console.error('❌ Не удалось восстановить состояние Cytoscape:', recoveryErr)
          }
        }
      }, 200) // Увеличиваем задержку до 200ms
    }
  }, [showStats, layout, brainData])

  // Обработчик изменения размеров окна
  useEffect(() => {
    const handleResize = () => {
      if (cyInstanceRef.current) {
        const cy = cyInstanceRef.current
        setTimeout(() => {
          try {
            cy.resize()
            cy.fit()
            cy.center()
          } catch (err) {
            console.error('Ошибка обработки изменения размера окна:', err)
          }
        }, 100)
      }
    }

    window.addEventListener('resize', handleResize)
    return () => window.removeEventListener('resize', handleResize)
  }, [])

  // Обновляем стили связей при изменении параметров
  useEffect(() => {
    if (cyInstanceRef.current) {
      const cy = cyInstanceRef.current
      setTimeout(() => {
        applyEdgeStyles(cy)
      }, 100)
    }
  }, [showWeights]) // showWeights обрабатывается отдельно для обновления только стилей

  // Экспорт графа
  const exportGraph = (format: 'png' | 'json' = 'png') => {
    if (!cyInstanceRef.current) return

    const cy = cyInstanceRef.current

    if (format === 'png') {
      const png = cy.png({
        full: true,
        output: 'blob'
      })

      const url = URL.createObjectURL(png)
      const a = document.createElement('a')
      a.href = url
      a.download = `brain-${brainId}-${layout}.png`
      a.click()
      URL.revokeObjectURL(url)
    } else if (format === 'json') {
      const json = cy.json()
      const dataStr = JSON.stringify(json, null, 2)
      const dataBlob = new Blob([dataStr], { type: 'application/json' })

      const url = URL.createObjectURL(dataBlob)
      const a = document.createElement('a')
      a.href = url
      a.download = `brain-${brainId}-${layout}.json`
      a.click()
      URL.revokeObjectURL(url)
    }
  }

  // Сброс к исходному виду
  const resetView = () => {
    if (!cyInstanceRef.current) return

    const cy = cyInstanceRef.current
    cy.fit()
    cy.center()
  }

  // Принудительное обновление размеров
  const forceResize = () => {
    if (!cyInstanceRef.current) return

    const cy = cyInstanceRef.current
    try {
      // Проверяем, что контейнер существует и имеет размеры
      const container = cy.container()
      if (container && container.offsetWidth > 0 && container.offsetHeight > 0) {
        // Принудительно обновляем размеры
        cy.resize()

        // Пересчитываем позиции элементов
        cy.elements().forEach(ele => {
          ele.position('x', ele.position('x'))
          ele.position('y', ele.position('y'))
        })

        // Подгоняем размер и центрируем
        cy.fit()
        cy.center()

        console.log('✅ Размеры Cytoscape принудительно обновлены')
      } else {
        console.warn('⚠️ Контейнер Cytoscape не готов для обновления')
        // Пытаемся восстановить состояние
        cy.fit()
        cy.center()
      }
    } catch (err) {
      console.error('❌ Ошибка принудительного обновления размеров:', err)
      // Пытаемся восстановить состояние
      try {
        cy.fit()
        cy.center()
      } catch (recoveryErr) {
        console.error('❌ Не удалось восстановить состояние Cytoscape:', recoveryErr)
      }
    }
  }

  // Принудительное обновление стилей
  const forceStyleUpdate = () => {
    if (!cyInstanceRef.current) {
      console.log('❌ cyInstanceRef.current не существует')
      return
    }

    const cy = cyInstanceRef.current
    try {
      // Принудительно обновляем стили всех элементов
      cy.elements('edge').forEach(ele => {
        // Обновляем стили связей
        const weight = ele.data('weight') as number
        const enabled = ele.data('enabled') as boolean

        let color: string
        if (!enabled) {
          color = '#d1d5db'
        } else if (weight > 0.7) {
          color = '#059669'
        } else if (weight > 0.3) {
          color = '#10b981'
        } else if (weight > 0) {
          color = '#34d399'
        } else if (weight < -0.7) {
          color = '#dc2626'
        } else if (weight < -0.3) {
          color = '#ef4444'
        } else if (weight < 0) {
          color = '#f87171'
        } else {
          color = '#6b7280'
        }

        ele.style('line-color', color)
        ele.style('target-arrow-color', color)
      })

      console.log('✅ Стили Cytoscape принудительно обновлены')
    } catch (err) {
      console.error('❌ Ошибка обновления стилей:', err)
    }
  }

    // Функция для применения стилей к связям
  const applyEdgeStyles = (cy: cytoscape.Core) => {
    const edgeCount = cy.elements('edge').length
    console.log('🎨 Применяю стили к связям. Всего связей:', edgeCount)

    // Дополнительная диагностика
    console.log('🔍 Все элементы в Cytoscape:', cy.elements().length)
    console.log('🔍 Узлы:', cy.elements('node').length)
    console.log('🔍 Связи:', cy.elements('edge').length)
    console.log('🔍 Типы элементов:', cy.elements().map(ele => ele.isNode() ? 'node' : 'edge'))

    if (edgeCount === 0) {
      console.warn('⚠️ Связи не найдены для применения стилей')

      // Попробуем принудительно обновить DOM
      cy.elements().forEach(ele => {
        ele.position('x', ele.position('x'))
        ele.position('y', ele.position('y'))
      })

      const retryEdgeCount = cy.elements('edge').length
      console.log('🔍 Связи после принудительного обновления DOM:', retryEdgeCount)

      if (retryEdgeCount === 0) {
        // Попробуем принудительно обновить все элементы
        cy.elements().forEach(ele => {
          if (ele.isEdge()) {
            ele.style('line-color', ele.style('line-color'))
            ele.style('target-arrow-color', ele.style('target-arrow-color'))
          }
        })

        const finalRetryCount = cy.elements('edge').length
        console.log('🔍 Связи после принудительного обновления стилей:', finalRetryCount)

        if (finalRetryCount === 0) {
          return
        }
      }
    }

    // Применяем стили к каждой связи
    cy.elements('edge').forEach((edge) => {
      applyEdgeStyle(edge)
    })
  }

  // Вспомогательная функция для применения стиля к одной связи
  const applyEdgeStyle = (edge: cytoscape.EdgeSingular) => {
    const weight = edge.data('weight') as number
    const enabled = edge.data('enabled') as boolean

    let color: string
    if (!enabled) {
      color = '#d1d5db' // Светло-серый для неактивных
    } else if (weight > 0.7) {
      color = '#059669' // Темно-зеленый для очень сильных положительных
    } else if (weight > 0.3) {
      color = '#10b981' // Зеленый для сильных положительных
    } else if (weight > 0) {
      color = '#34d399' // Светло-зеленый для слабых положительных
    } else if (weight < -0.7) {
      color = '#dc2626' // Темно-красный для очень сильных отрицательных
    } else if (weight < -0.3) {
      color = '#ef4444' // Красный для сильных отрицательных
    } else if (weight < 0) {
      color = '#f87171' // Светло-красный для слабых отрицательных
    } else {
      color = '#6b7280' // Серый для нулевых
    }

    // Применяем стили напрямую
    try {
      edge.style('line-color', color)
      edge.style('target-arrow-color', color)

      // Стиль применен успешно (Cytoscape возвращает RGB, а мы передаем HEX - это нормально)
    } catch (err) {
      console.error(`❌ Ошибка применения стиля к связи ${edge.data('id')}:`, err)
    }
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

  const brainStats = calculateBrainStats()

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-[95vw] h-[95vh] flex flex-col">
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
            {/* Предупреждение о неактивных связях */}
            {brainData && brainData.connections.length > 0 && brainData.connections.every(c => !c.enabled) && (
              <div className="text-xs text-orange-600 bg-orange-100 px-2 py-1 rounded border border-orange-300">
                ⚠️ Все связи неактивны
              </div>
            )}

            {/* Управление layout */}
            <select
              value={layout}
              onChange={(e) => setLayout(e.target.value as any)}
              className="input-field text-sm"
            >
              <option value="concentric">Концентрический</option>
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

            {/* Показать/скрыть неактивные связи */}
            <button
              onClick={() => setShowDisabledConnections(!showDisabledConnections)}
              className={`btn-secondary p-2 ${showDisabledConnections ? 'bg-brain-100 text-brain-800' : ''}`}
              title="Показать неактивные связи"
            >
              <Activity className="h-4 w-4" />
            </button>

            {/* Индикатор состояния связей */}
            {brainData && (
              <div className="text-xs text-gray-600 bg-gray-100 px-2 py-1 rounded">
                Связи: {brainData.connections.filter(c => c.enabled).length}/{brainData.connections.length}
              </div>
            )}

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

            {/* Статистика */}
            <button
              onClick={() => setShowStats(!showStats)}
              className={`btn-secondary p-2 ${showStats ? 'bg-brain-100 text-brain-800' : ''}`}
              title="Показать статистику"
            >
              <BarChart3 className="h-4 w-4" />
            </button>

            {/* Легенда */}
            <button
              onClick={() => setShowLegend(!showLegend)}
              className={`btn-secondary p-2 ${showLegend ? 'bg-brain-100 text-brain-800' : ''}`}
              title="Показать легенду"
            >
              <Info className="h-4 w-4" />
            </button>

            {/* Экспорт */}
            <button
              onClick={() => exportGraph()}
              className="btn-secondary p-2"
              title="Экспортировать граф (PNG)"
            >
              <Download className="h-4 w-4" />
            </button>

            {/* Экспорт JSON */}
            <button
              onClick={() => exportGraph('json')}
              className="btn-secondary p-2"
              title="Экспортировать граф (JSON)"
            >
              <Settings className="h-4 w-4" />
            </button>

            {/* Сброс к исходному виду */}
            <button
              onClick={resetView}
              className="btn-secondary p-2"
              title="Сбросить вид"
            >
              <RotateCcw className="h-4 w-4" />
            </button>

            {/* Принудительное обновление размеров */}
            <button
              onClick={forceResize}
              className="btn-secondary p-2"
              title="Обновить размеры"
            >
              <Activity className="h-4 w-4" />
            </button>

            {/* Принудительное обновление стилей */}
            <button
              onClick={forceStyleUpdate}
              className="btn-secondary p-2"
              title="Обновить стили"
            >
              <RotateCcw className="h-4 w-4" />
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
        {showLegend && (
          <div className="px-4 py-2 bg-gray-50 border-b">
            <div className="grid grid-cols-3 gap-4 text-xs">
              {/* Типы узлов */}
              <div>
                <h4 className="font-medium text-gray-800 mb-2 text-sm">Узлы:</h4>
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-blue-500 rounded-full border border-blue-700"></div>
                    <span>Входные</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-orange-500 rounded-full border border-orange-700"></div>
                    <span>Скрытые</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-green-500 rounded-full border border-green-700"></div>
                    <span>Выходные</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-3 h-3 bg-purple-500 rounded-full border border-purple-700"></div>
                    <span>Память</span>
                  </div>
                </div>
              </div>

              {/* Типы связей - левый столбец */}
              <div>
                <h4 className="font-medium text-gray-800 mb-2 text-sm">Связи (положительные):</h4>
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-1.5 bg-green-800 rounded"></div>
                    <span>&gt;0.7 (темно-зеленый)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-1.5 bg-green-500 rounded"></div>
                    <span>0.3-0.7 (зеленый)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-1.5 bg-green-300 rounded"></div>
                    <span>0-0.3 (светло-зеленый)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-1.5 bg-gray-300 border border-dashed border-gray-500 rounded"></div>
                    <span>Неактивные (серый)</span>
                  </div>
                </div>
              </div>

              {/* Типы связей - правый столбец */}
              <div>
                <h4 className="font-medium text-gray-800 mb-2 text-sm">Связи (отрицательные):</h4>
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-1.5 bg-red-800 rounded"></div>
                    <span>&lt;-0.7 (темно-красный)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-1.5 bg-red-500 rounded"></div>
                    <span>-0.7--0.3 (красный)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-1.5 bg-red-300 rounded"></div>
                    <span>-0.3-0 (светло-красный)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-1.5 bg-gray-400 rounded"></div>
                    <span>Нулевые (=0)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Основной контент */}
        <div className="flex-1 flex">
          {/* Граф */}
          <div className={`p-4 ${showStats ? 'flex-1' : 'w-full'}`}>
            <div
              ref={cyRef}
              className="w-full h-full border border-gray-200 rounded-lg bg-gray-50"
              style={{ minHeight: '500px' }}
            />
          </div>

          {/* Панель справа */}
          {showStats && (
            <div className="w-80 border-l bg-gray-50 p-4 overflow-y-auto">
              {/* Статистика мозга */}
              {brainStats && (
                <div className="mb-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <BarChart3 className="h-5 w-5 mr-2" />
                    Статистика мозга
                  </h3>

                  {/* Основные характеристики */}
                  <div className="bg-white p-3 rounded border mb-4">
                    <h4 className="font-medium text-gray-800 mb-2">Основные характеристики:</h4>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">ID мозга:</span>
                        <span className="font-medium">#{brainId}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">GP:</span>
                        <span className="font-medium text-blue-600">{brainData?.gp.toFixed(3)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Fitness:</span>
                        <span className="font-medium text-green-600">{brainData?.fitness.toFixed(3)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Возраст:</span>
                        <span className="font-medium text-orange-600">{brainData?.age}</span>
                      </div>
                    </div>
                  </div>

                  {/* Сетевая статистика */}
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Всего узлов:</span>
                      <span className="font-medium">{brainStats.totalNodes}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Активных связей:</span>
                      <span className="font-medium">{brainStats.totalConnections}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Плотность сети:</span>
                      <span className="font-medium">{(brainStats.networkDensity * 100).toFixed(1)}%</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Средний вес:</span>
                      <span className="font-medium">{brainStats.avgWeight.toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Стд. вес:</span>
                      <span className="font-medium">{brainStats.weightStd.toFixed(3)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Средняя пластичность:</span>
                      <span className="font-medium">{brainStats.avgPlasticity.toFixed(3)}</span>
                    </div>
                  </div>

                  {/* Распределение узлов по типам */}
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-800 mb-2">Распределение узлов:</h4>
                    <div className="space-y-1">
                      {Object.entries(brainStats.nodeTypes).map(([type, count]) => (
                        <div key={type} className="flex justify-between text-sm">
                          <span className="text-gray-600 capitalize">{type}:</span>
                          <span className="font-medium">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Функции активации */}
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-800 mb-2">Функции активации:</h4>
                    <div className="space-y-1">
                      {brainData && Object.entries(
                        brainData.nodes.reduce((acc, node) => {
                          acc[node.activation] = (acc[node.activation] || 0) + 1
                          return acc
                        }, {} as Record<string, number>)
                      ).map(([activation, count]) => (
                        <div key={activation} className="flex justify-between text-sm">
                          <span className="text-gray-600">{activation}:</span>
                          <span className="font-medium">{count}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Распределение связей */}
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-800 mb-2">Распределение связей:</h4>
                    <div className="space-y-1 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Возбуждающие:</span>
                        <span className="font-medium text-green-600">{brainStats.positiveConnections}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Тормозящие:</span>
                        <span className="font-medium text-red-600">{brainStats.negativeConnections}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Сильные (|w|&gt;0.5):</span>
                        <span className="font-medium">{brainStats.strongConnections}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Неактивные:</span>
                        <span className="font-medium text-gray-500">{brainData?.connections.filter(c => !c.enabled).length || 0}</span>
                      </div>
                    </div>
                  </div>

                  {/* Диапазоны параметров */}
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-800 mb-2">Диапазоны параметров:</h4>
                    <div className="space-y-1 text-sm">
                      {brainData && (() => {
                        const biases = brainData.nodes.map(n => n.bias)
                        const thresholds = brainData.nodes.map(n => n.threshold)
                        const minBias = Math.min(...biases)
                        const maxBias = Math.max(...biases)
                        const minThreshold = Math.min(...thresholds)
                        const maxThreshold = Math.max(...thresholds)

                        return (
                          <>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Bias:</span>
                              <span className="font-medium">[{minBias.toFixed(2)}, {maxBias.toFixed(2)}]</span>
                            </div>
                            <div className="flex justify-between">
                              <span className="text-gray-600">Threshold:</span>
                              <span className="font-medium">[{minThreshold.toFixed(2)}, {maxThreshold.toFixed(2)}]</span>
                            </div>
                          </>
                        )
                      })()}
                    </div>
                  </div>
                </div>
              )}

              {/* Детальная информация о выбранном элементе */}
              {selectedElement && (
                <div className="border-t pt-4">
                  <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                    <Info className="h-5 w-5 mr-2" />
                    {selectedElement.type === 'node' ? 'Детали узла' : 'Детали связи'}
                  </h3>
                  <div className="bg-white p-3 rounded border">
                    {selectedElement.type === 'node' ? (
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">ID:</span>
                          <span className="font-medium">{selectedElement.data.id}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Тип:</span>
                          <span className="font-medium capitalize">{selectedElement.data.type}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Активация:</span>
                          <span className="font-medium">{selectedElement.data.activation}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Bias:</span>
                          <span className="font-medium">{selectedElement.data.bias.toFixed(3)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Threshold:</span>
                          <span className="font-medium">{selectedElement.data.threshold.toFixed(3)}</span>
                        </div>
                      </div>
                    ) : (
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-gray-600">ID:</span>
                          <span className="font-medium">{selectedElement.data.id}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">От:</span>
                          <span className="font-medium">{selectedElement.data.source}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">К:</span>
                          <span className="font-medium">{selectedElement.data.target}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Вес:</span>
                          <span className={`font-medium ${selectedElement.data.weight > 0 ? 'text-green-600' : 'text-red-600'}`}>
                            {selectedElement.data.weight.toFixed(3)}
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Пластичность:</span>
                          <span className="font-medium">{selectedElement.data.plasticity.toFixed(3)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-gray-600">Статус:</span>
                          <span className={`font-medium ${selectedElement.data.enabled ? 'text-green-600' : 'text-gray-500'}`}>
                            {selectedElement.data.enabled ? 'Активна' : 'Неактивна'}
                          </span>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Инструкции */}
              <div className="border-t pt-4 mt-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
                  <Activity className="h-5 w-5 mr-2" />
                  Инструкции
                </h3>
                <div className="text-sm text-gray-600 space-y-2">
                  <p>• Кликните на узел или связь для детальной информации</p>
                  <p>• Используйте мышь для масштабирования и перемещения</p>
                  <p>• Измените layout для лучшего обзора</p>
                  <p>• Включите/выключите отображение весов</p>
                  <p>• Покажите/скройте неактивные связи</p>
                  <p>• Покажите/скройте панель статистики</p>
                  <p>• Покажите/скройте легенду для экономии места</p>
                  <p>• Экспортируйте граф в PNG или JSON</p>
                  <p>• Настройте размер узлов для лучшей видимости</p>
                  <p>• Используйте кнопку "Обновить стили" для принудительного обновления цветов</p>
                  <p>• Цвета связей зависят от веса: зеленые (положительные), красные (отрицательные)</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Статистика внизу */}
        <div className="px-4 py-2 bg-gray-50 border-t">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>
              Узлов: {brainData?.nodes.length} |
              Связей: {brainData?.connections.filter(c => c.enabled).length} |
              {showDisabledConnections && `Неактивных: ${brainData?.connections.filter(c => !c.enabled).length || 0} | `}
              Layout: {layout} |
              {brainStats && `Плотность: ${(brainStats.networkDensity * 100).toFixed(1)}%`}
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
