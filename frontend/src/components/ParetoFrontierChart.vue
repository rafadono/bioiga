<template>
  <div class="pareto-container glass-panel">
    <div class="pareto-header">
      <h3 class="pareto-title">Frente de Pareto No Dominado (NSGA-II / MOEA-D)</h3>
      <span class="pareto-subtitle">Maximización de Frecuencia ω1 vs. Minimización de Masa M</span>
    </div>
    <div class="chart-wrapper">
      <Scatter :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js'
import { Scatter } from 'vue-chartjs'

ChartJS.register(LinearScale, PointElement, LineElement, Tooltip, Legend)

// Sample Pareto frontier points for demonstration
const paretoPoints = [
  { x: 0.25, y: 58.2 },
  { x: 0.30, y: 52.4 },
  { x: 0.38, y: 46.1 },
  { x: 0.45, y: 41.8 },
  { x: 0.52, y: 38.5 },
  { x: 0.65, y: 35.9 },
]

const chartData = computed(() => {
  return {
    datasets: [
      {
        label: 'Soluciones No Dominadas (Frente de Pareto)',
        borderColor: '#818cf8',
        backgroundColor: '#38bdf8',
        data: paretoPoints,
        pointRadius: 6,
        pointHoverRadius: 9,
        showLine: true,
        borderDash: [4, 4],
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: { color: '#94a3b8', font: { family: 'Inter', size: 12 } },
    },
  },
  scales: {
    x: {
      title: { display: true, text: 'Masa Relativa de la Placa (M / M0)', color: '#94a3b8' },
      grid: { color: '#1e293b' },
      ticks: { color: '#64748b', font: { family: 'JetBrains Mono' } },
    },
    y: {
      title: { display: true, text: 'Frecuencia Adimensional (w_bar)', color: '#94a3b8' },
      grid: { color: '#1e293b' },
      ticks: { color: '#64748b', font: { family: 'JetBrains Mono' } },
    },
  },
}
</script>

<style scoped>
.pareto-container {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  height: 320px;
}

.pareto-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.5rem;
}

.pareto-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: #f8fafc;
}

.pareto-subtitle {
  font-size: 0.8rem;
  color: #38bdf8;
}

.chart-wrapper {
  flex: 1;
  position: relative;
  width: 100%;
  height: 100%;
}
</style>
