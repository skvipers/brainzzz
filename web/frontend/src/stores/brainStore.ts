import { create } from 'zustand'
import axios from 'axios'

interface Brain {
  id: number
  nodes: number
  connections: number
  gp: number
  fitness: number
  age: number
}

interface PopulationStats {
  size: number
  avg_fitness: number
  max_fitness: number
  avg_nodes: number
  avg_connections: number
  generation: number
}

interface BrainStore {
  population: Brain[]
  stats: PopulationStats
  loading: boolean
  error: string | null
  
  // Actions
  fetchPopulation: () => Promise<void>
  fetchStats: () => Promise<void>
  startEvolution: (mutationRate: number) => Promise<void>
  evaluatePopulation: () => Promise<void>
  resetError: () => void
}

const API_BASE = '/api'

export const useBrainStore = create<BrainStore>((set, get) => ({
  population: [],
  stats: {
    size: 0,
    avg_fitness: 0,
    max_fitness: 0,
    avg_nodes: 0,
    avg_connections: 0,
    generation: 0,
  },
  loading: false,
  error: null,
  
  fetchPopulation: async () => {
    try {
      set({ loading: true, error: null })
      const response = await axios.get(`${API_BASE}/population`)
      set({ population: response.data, loading: false })
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Ошибка загрузки популяции',
        loading: false 
      })
    }
  },
  
  fetchStats: async () => {
    try {
      set({ loading: true, error: null })
      const response = await axios.get(`${API_BASE}/stats`)
      set({ stats: response.data, loading: false })
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Ошибка загрузки статистики',
        loading: false 
      })
    }
  },
  
  startEvolution: async (mutationRate: number) => {
    try {
      set({ loading: true, error: null })
      await axios.post(`${API_BASE}/evolve`, {
        mutation_rate: mutationRate,
        population_size: get().population.length
      })
      
      // Обновляем данные после эволюции
      await get().fetchPopulation()
      await get().fetchStats()
      set({ loading: false })
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Ошибка запуска эволюции',
        loading: false 
      })
    }
  },
  
  evaluatePopulation: async () => {
    try {
      set({ loading: true, error: null })
      await axios.post(`${API_BASE}/evaluate`)
      
      // Обновляем статистику после оценки
      await get().fetchStats()
      set({ loading: false })
    } catch (error) {
      set({ 
        error: error instanceof Error ? error.message : 'Ошибка оценки популяции',
        loading: false 
      })
    }
  },
  
  resetError: () => set({ error: null }),
})) 