<template>
  <div class="chart-container glass-panel">
    <div class="chart-header">
      <span class="chart-title">Curva de Convergencia en Tiempo Real</span>
      <span class="chart-subtitle" v-if="history.length > 0">
        Último Fitness: {{ history[history.length - 1].toFixed(4) }}
      </span>
    </div>
    <div class="chart-wrapper">
      <Line :data="chartData" :options="chartOptions" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Line } from 'vue-chartjs'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
)

const props = defineProps<{
  history: number[]
}>()

const chartData = computed(() => {
  return {
    labels: props.history.map((_, i) => `G${i + 1}`),
    datasets: [
      {
        label: 'Mejor Fitness (Global Best)',
        borderColor: '#38bdf8',
        backgroundColor: 'rgba(56, 189, 248, 0.1)',
        data: props.history,
        tension: 0.3,
        borderWidth: 2,
        pointRadius: 2,
      },
    ],
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      labels: {
        color: '#94a3b8',
        font: { family: 'Inter', size: 12 },
      },
    },
  },
  scales: {
    x: {
      grid: { color: '#1e293b' },
      ticks: { color: '#64748b', font: { family: 'JetBrains Mono' } },
    },
    y: {
      grid: { color: '#1e293b' },
      ticks: { color: '#64748b', font: { family: 'JetBrains Mono' } },
    },
  },
}
</script>

<style scoped>
.chart-container {
  display: flex;
  flex-direction: column;
  padding: 1.25rem;
  height: 260px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.chart-title {
  font-weight: 700;
  font-size: 0.9rem;
  color: #f8fafc;
}

.chart-subtitle {
  font-family: 'JetBrains Mono', monospace;
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
