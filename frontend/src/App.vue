<template>
  <div id="app">
    <Navbar :status="status" />

    <!-- Visual Engineering Workflow Navigator Header -->
    <div class="workflow-header-nav">
      <!-- Block 1: Structural Definition -->
      <div class="nav-block block-def">
        <span class="block-label">DEFINICIÓN ESTRUCTURAL</span>
        <div class="block-btns">
          <button
            @click="activeTab = 'knots'"
            class="tab-btn"
            :class="{ active: activeTab === 'knots' }"
          >
            <Icon name="layers" :size="15" />
            <span>1. Geometría & Nudos</span>
          </button>
          <button
            @click="activeTab = 'materials'"
            class="tab-btn"
            :class="{ active: activeTab === 'materials' }"
          >
            <Icon name="settings" :size="15" />
            <span>2. Materiales</span>
          </button>
          <button
            @click="activeTab = 'loads'"
            class="tab-btn"
            :class="{ active: activeTab === 'loads' }"
          >
            <Icon name="shield" :size="15" />
            <span>3. Cargas y Apoyos</span>
          </button>
        </div>
      </div>

      <div class="block-divider font-mono">➔</div>

      <!-- Block 2: Simulation Modes (Direct IGA vs. Evolutionary Optimizer) -->
      <div class="nav-block block-sim">
        <span class="block-label">MODOS DE SIMULACIÓN Y CÁLCULO</span>
        <div class="block-btns">
          <button
            @click="activeTab = 'vibrations'"
            class="tab-btn tab-direct"
            :class="{ active: activeTab === 'vibrations' }"
          >
            <Icon name="activity" :size="15" />
            <span>Modo A: Directo Standalone</span>
          </button>

          <button
            @click="activeTab = 'optimizer'"
            class="tab-btn tab-optimizer"
            :class="{ active: activeTab === 'optimizer' }"
          >
            <Icon name="sliders" :size="15" />
            <span>Modo B: Optimizador SIMP</span>
          </button>
        </div>
      </div>

      <div class="block-divider font-mono">➔</div>

      <!-- Block 3: Advanced Research & Management -->
      <div class="nav-block block-research">
        <span class="block-label">INVESTIGACIÓN Y PROYECTOS</span>
        <div class="block-btns">
          <button
            @click="activeTab = 'advanced'"
            class="tab-btn"
            :class="{ active: activeTab === 'advanced' }"
          >
            <Icon name="layers" :size="15" />
            <span>6. Ciencia & Pareto</span>
          </button>
          <button
            @click="activeTab = 'frontier'"
            class="tab-btn"
            :class="{ active: activeTab === 'frontier' }"
          >
            <Icon name="cpu" :size="15" />
            <span>7. Frontera (2024–2026)</span>
          </button>
          <button
            @click="activeTab = 'projects'"
            class="tab-btn"
            :class="{ active: activeTab === 'projects' }"
          >
            <Icon name="folder" :size="15" />
            <span>8. Proyectos</span>
          </button>
        </div>
      </div>
    </div>

    <main class="main-layout">
      <!-- Tab 1: Predefined Geometry & Reactive Knot Inspector -->
      <template v-if="activeTab === 'knots'">
        <div class="tab-container">
          <GeometryBuilder />
        </div>
      </template>

      <!-- Tab 2: Material Library -->
      <template v-else-if="activeTab === 'materials'">
        <div class="tab-container">
          <MaterialLibrary />
        </div>
      </template>

      <!-- Tab 3: Loads & BCs Editor -->
      <template v-else-if="activeTab === 'loads'">
        <div class="tab-container">
          <LoadsEditor />
        </div>
      </template>

      <!-- Mode B: Evolutionary Optimizer -->
      <template v-else-if="activeTab === 'optimizer'">
        <ControlPanel
          :status="status"
          @start="handleStart"
          @pause="handlePause"
          @resume="handleResume"
          @stop="handleStop"
        />

        <div class="content-area">
          <MetricsCards
            :currentGen="currentGen"
            :maxGen="maxGen"
            :bestFitness="bestFitness"
            :algorithm="currentAlgorithm"
          />

          <div class="workspace-grid">
            <NurbsViewport
              :solution="currentSolution"
              :numVariables="numVariables"
            />

            <ConvergenceChart
              :history="fitnessHistory"
            />
          </div>
        </div>
      </template>

      <!-- Mode A: Standalone Direct Mechanical Analysis -->
      <template v-else-if="activeTab === 'vibrations'">
        <div class="tab-container">
          <VibrationsPanel />
        </div>
      </template>

      <!-- Tab 6: Advanced Science, Sensitivity & Pareto -->
      <template v-else-if="activeTab === 'advanced'">
        <div class="tab-container flex-col">
          <BenchmarkSuiteSelector @load-benchmark="onLoadBenchmark" />
          <SensitivityAnalysisPanel />
          <AdvancedSciencePanel />
          <ParetoFrontierChart />
        </div>
      </template>

      <!-- Tab 7: Frontier Roadmap Modules -->
      <template v-else-if="activeTab === 'frontier'">
        <div class="tab-container">
          <RoadmapFrontierPanel />
        </div>
      </template>

      <!-- Tab 8: Project Manager & Multi-Project Comparator -->
      <template v-else-if="activeTab === 'projects'">
        <div class="tab-container flex-col">
          <ProjectManager @load-project="onProjectLoaded" />
          <ProjectComparator />
        </div>
      </template>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import Navbar from './components/Navbar.vue'
import ControlPanel from './components/ControlPanel.vue'
import NurbsViewport from './components/NurbsViewport.vue'
import ConvergenceChart from './components/ConvergenceChart.vue'
import MetricsCards from './components/MetricsCards.vue'
import KnotInspector from './components/KnotInspector.vue'
import LoadsEditor from './components/LoadsEditor.vue'
import ProjectManager from './components/ProjectManager.vue'
import AdvancedSciencePanel from './components/AdvancedSciencePanel.vue'
import ParetoFrontierChart from './components/ParetoFrontierChart.vue'
import MaterialLibrary from './components/MaterialLibrary.vue'
import VibrationsPanel from './components/VibrationsPanel.vue'
import RoadmapFrontierPanel from './components/RoadmapFrontierPanel.vue'
import GeometryBuilder from './components/GeometryBuilder.vue'
import BenchmarkSuiteSelector from './components/BenchmarkSuiteSelector.vue'
import SensitivityAnalysisPanel from './components/SensitivityAnalysisPanel.vue'
import ProjectComparator from './components/ProjectComparator.vue'
import Icon from './components/Icon.vue'

import type { OptimizationConfig } from './types'

const activeTab = ref<'knots' | 'materials' | 'loads' | 'optimizer' | 'vibrations' | 'advanced' | 'frontier' | 'projects'>('knots')
const status = ref<string>('idle')
const currentGen = ref<number>(0)
const maxGen = ref<number>(50)
const bestFitness = ref<number | null>(null)
const currentSolution = ref<number[] | null>(null)
const numVariables = ref<number>(100)
const currentAlgorithm = ref<string>('MPMBPSO')
const fitnessHistory = ref<number[]>([])

let socket: WebSocket | null = null

function connectWebSocket() {
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const wsUrl = `${protocol}//${window.location.host}/ws/optimization`

  socket = new WebSocket(wsUrl)

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      if (data.type === 'progress') {
        currentGen.value = data.generation + 1
        maxGen.value = data.max_generations
        bestFitness.value = data.best_fitness
        currentSolution.value = data.best_solution
        fitnessHistory.value.push(data.best_fitness)
        status.value = 'running'
      } else if (data.type === 'status') {
        status.value = data.status
      } else if (data.type === 'completed') {
        status.value = 'completed'
      } else if (data.type === 'error') {
        status.value = 'error'
      }
    } catch (e) {
      console.error('Error parsing WebSocket message:', e)
    }
  }

  socket.onclose = () => {
    setTimeout(connectWebSocket, 3000)
  }
}

async function handleStart(config: OptimizationConfig) {
  currentAlgorithm.value = config.algorithm
  numVariables.value = config.num_variables
  maxGen.value = config.generations
  currentGen.value = 0
  bestFitness.value = null
  currentSolution.value = null
  fitnessHistory.value = []

  try {
    const res = await fetch('/api/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config),
    })
    if (res.ok) {
      status.value = 'running'
    }
  } catch (err) {
    console.error('Error starting simulation:', err)
  }
}

async function handlePause() {
  await fetch('/api/pause', { method: 'POST' })
}

async function handleResume() {
  await fetch('/api/resume', { method: 'POST' })
}

async function handleStop() {
  await fetch('/api/stop', { method: 'POST' })
  status.value = 'stopped'
}

function onLoadBenchmark(benchmarkId: string) {
  activeTab.value = 'optimizer'
}

function onProjectLoaded(projectData: any) {
  if (projectData.optimization_config) {
    currentAlgorithm.value = projectData.optimization_config.algorithm
    numVariables.value = projectData.optimization_config.num_variables
    maxGen.value = projectData.optimization_config.generations
  }
  activeTab.value = 'optimizer'
}

onMounted(() => {
  connectWebSocket()
})

onUnmounted(() => {
  if (socket) {
    socket.close()
  }
})
</script>

<style scoped>
.workflow-header-nav {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 1rem;
  background: #0f172a;
  border-bottom: 1px solid #1e293b;
  overflow-x: auto;
}

.nav-block {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  background: #1e293b;
  padding: 0.4rem 0.6rem;
  border-radius: 8px;
  border: 1px solid #334155;
}

.block-def {
  border-color: rgba(56, 189, 248, 0.4);
}

.block-sim {
  border-color: rgba(52, 211, 153, 0.4);
}

.block-research {
  border-color: rgba(192, 132, 252, 0.4);
}

.block-label {
  font-size: 0.68rem;
  font-weight: 800;
  letter-spacing: 0.05em;
  color: #94a3b8;
}

.block-def .block-label { color: #38bdf8; }
.block-sim .block-label { color: #34d399; }
.block-research .block-label { color: #c084fc; }

.block-btns {
  display: flex;
  gap: 0.35rem;
}

.block-divider {
  color: #64748b;
  font-size: 1.1rem;
  font-weight: 700;
}

.tab-btn {
  background: #0f172a;
  color: #94a3b8;
  border: 1px solid #334155;
  padding: 0.4rem 0.7rem;
  border-radius: 6px;
  font-family: var(--font-sans);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.tab-btn:hover {
  color: #f8fafc;
  background: #334155;
}

.tab-btn.active {
  color: #38bdf8;
  background: #334155;
  border-color: #38bdf8;
}

.tab-direct.active {
  color: #0f172a;
  background: #38bdf8;
  border-color: #38bdf8;
}

.tab-optimizer.active {
  color: #0f172a;
  background: #34d399;
  border-color: #34d399;
}

.main-layout {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  flex: 1;
}

.content-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tab-container {
  flex: 1;
  width: 100%;
}

.flex-col {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.workspace-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  flex: 1;
}

@media (max-width: 1024px) {
  .workflow-header-nav {
    flex-wrap: wrap;
    gap: 0.5rem;
    padding: 0.5rem;
  }

  .block-divider {
    display: none;
  }
}

@media (max-width: 860px) {
  .main-layout {
    flex-direction: column;
    padding: 0.5rem;
  }

  .workspace-grid {
    grid-template-columns: 1fr;
  }
}
</style>
