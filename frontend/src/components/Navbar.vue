<template>
  <header class="navbar glass-panel">
    <div class="brand">
      <div class="logo-badge">
        <Icon name="cpu" :size="20" />
        <span>BioIGA</span>
      </div>
      <div class="brand-text">
        <span class="title">BioIGA-2D Suite</span>
        <span class="subtitle">Isogeometric & Evolutionary Structural Optimization</span>
      </div>
    </div>

    <div class="status-indicators">
      <div class="indicator">
        <span class="indicator-dot" :class="statusClass"></span>
        <span class="status-text">{{ statusText }}</span>
      </div>
    </div>
  </header>

</template>

<script setup lang="ts">
import { computed } from 'vue'
import Icon from './Icon.vue'

const props = defineProps<{
  status: string
}>()

const statusClass = computed(() => {
  switch (props.status) {
    case 'running': return 'dot-running'
    case 'paused': return 'dot-paused'
    case 'completed': return 'dot-completed'
    case 'error': return 'dot-error'
    default: return 'dot-idle'
  }
})

const statusText = computed(() => {
  return props.status.toUpperCase()
})
</script>

<style scoped>
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 1.5rem;
  margin: 1rem 1rem 0 1rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-badge {
  background: linear-gradient(135deg, #38bdf8, #818cf8);
  color: #0f172a;
  font-weight: 800;
  padding: 0.45rem 0.85rem;
  border-radius: 8px;
  font-size: 1.1rem;
  display: flex;
  align-items: center;
  gap: 0.4rem;
  letter-spacing: -0.02em;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.title {
  font-weight: 700;
  font-size: 1.05rem;
  color: #f8fafc;
}

.subtitle {
  font-size: 0.75rem;
  color: #94a3b8;
}

.status-indicators {
  display: flex;
  align-items: center;
  gap: 1.25rem;
}

.indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #0f172a;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  border: 1px solid #334155;
}

.indicator-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.dot-idle { background: #64748b; }
.dot-running { background: #38bdf8; box-shadow: 0 0 10px #38bdf8; }
.dot-paused { background: #fbbf24; }
.dot-completed { background: #34d399; box-shadow: 0 0 10px #34d399; }
.dot-error { background: #f87171; }

.status-text {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.75rem;
  font-weight: 600;
  color: #e2e8f0;
}

.backend-tag {
  font-size: 0.75rem;
  color: #94a3b8;
  background: rgba(15, 23, 42, 0.6);
  padding: 0.35rem 0.75rem;
  border-radius: 6px;
  border: 1px solid #1e293b;
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
</style>
