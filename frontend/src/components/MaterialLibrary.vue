<template>
  <div class="material-library glass-panel">
    <div class="library-header">
      <Icon name="settings" :size="20" />
      <h3 class="library-title">Biblioteca de Materiales Estructurales</h3>
      <span class="library-subtitle">Propiedades mecánicas, elásticas y de fluencia</span>
    </div>

    <div class="library-grid">
      <!-- Selector & Presets -->
      <div class="library-card">
        <h4 class="card-title">Seleccionar Material o Preset</h4>
        <div class="form-group">
          <label class="form-label">Materiales Disponibles</label>
          <select v-model="selectedMaterialName" @change="onSelectMaterial" class="form-select">
            <option v-for="mat in materialsList" :key="mat.name" :value="mat.name">
              {{ mat.name }} {{ mat.category === 'default' ? '(Estándar)' : '(Personalizado)' }}
            </option>
          </select>
        </div>

        <div class="material-preview font-mono">
          <div class="prop-row"><span>E (Módulo de Young):</span> <span class="val">{{ (activeMat.E / 1e9).toFixed(1) }} GPa</span></div>
          <div class="prop-row"><span>ν (Coeficiente de Poisson):</span> <span class="val">{{ activeMat.nu.toFixed(2) }}</span></div>
          <div class="prop-row"><span>ρ (Densidad):</span> <span class="val">{{ activeMat.rho.toFixed(0) }} kg/m³</span></div>
          <div class="prop-row"><span>σ_Y (Límite de Fluencia):</span> <span class="val">{{ (activeMat.yield_strength / 1e6).toFixed(0) }} MPa</span></div>
        </div>

        <button v-if="activeMat.category === 'custom'" @click="onDelete(activeMat.name)" class="btn btn-danger btn-block">
          <Icon name="trash" :size="16" />
          <span>Eliminar Material Personalizado</span>
        </button>
      </div>

      <!-- Custom Material Editor Form -->
      <div class="library-card">
        <h4 class="card-title">Definir y Guardar Nuevo Material</h4>
        <div class="form-group">
          <label class="form-label">Nombre del Material</label>
          <input type="text" v-model="form.name" placeholder="ej. Aleación de Magnesio WE43" class="form-input" />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Módulo Young E (GPa)</label>
            <input type="number" v-model.number="formE_GPa" step="0.1" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">Poisson ν</label>
            <input type="number" v-model.number="form.nu" min="0.0" max="0.49" step="0.01" class="form-input" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Densidad ρ (kg/m³)</label>
            <input type="number" v-model.number="form.rho" step="10" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">Fluencia σ_Y (MPa)</label>
            <input type="number" v-model.number="formYield_MPa" step="5" class="form-input" />
          </div>
        </div>

        <button @click="onSave" :disabled="!form.name" class="btn btn-primary btn-block">
          <Icon name="save" :size="16" />
          <span>Guardar Material en Biblioteca</span>
        </button>
        <span v-if="saveMessage" class="status-msg success">{{ saveMessage }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import Icon from './Icon.vue'

interface Material {
  name: string
  E: number
  nu: number
  rho: number
  yield_strength: number
  safety_factor: number
  category: string
}

const materialsList = ref<Material[]>([])
const selectedMaterialName = ref<string>('Acero Estructural A36')
const saveMessage = ref<string>('')

const activeMat = computed(() => {
  return materialsList.value.find(m => m.name === selectedMaterialName.value) || {
    name: 'Acero Estructural A36',
    E: 200e9,
    nu: 0.26,
    rho: 7850.0,
    yield_strength: 250e6,
    safety_factor: 1.67,
    category: 'default',
  }
})

const form = reactive({
  name: '',
  nu: 0.30,
  rho: 2700.0,
  safety_factor: 1.5,
})

const formE_GPa = ref<number>(70.0)
const formYield_MPa = ref<number>(250.0)

async function fetchMaterials() {
  try {
    const res = await fetch('/api/materials')
    if (res.ok) {
      const data = await res.json()
      materialsList.value = data.materials || []
    }
  } catch (err) {
    console.error('Error fetching materials:', err)
  }
}

function onSelectMaterial() {
  const mat = activeMat.value
  form.name = mat.name + ' (Copia)'
  form.nu = mat.nu
  form.rho = mat.rho
  formE_GPa.value = mat.E / 1e9
  formYield_MPa.value = mat.yield_strength / 1e6
}

async function onSave() {
  if (!form.name) return
  try {
    const payload = {
      name: form.name,
      E: formE_GPa.value * 1e9,
      nu: form.nu,
      rho: form.rho,
      yield_strength: formYield_MPa.value * 1e6,
      safety_factor: form.safety_factor,
    }
    const res = await fetch('/api/materials', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (res.ok) {
      saveMessage.value = `Material '${form.name}' guardado correctamente.`
      await fetchMaterials()
      selectedMaterialName.value = form.name
      setTimeout(() => { saveMessage.value = '' }, 3000)
    }
  } catch (err) {
    console.error('Error saving material:', err)
  }
}

async function onDelete(name: string) {
  try {
    const res = await fetch(`/api/materials/${name}`, { method: 'DELETE' })
    if (res.ok) {
      selectedMaterialName.value = 'Acero Estructural A36'
      await fetchMaterials()
    }
  } catch (err) {
    console.error('Error deleting material:', err)
  }
}

onMounted(() => {
  fetchMaterials()
})
</script>

<style scoped>
.material-library {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.library-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #38bdf8;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.5rem;
}

.library-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f8fafc;
}

.library-subtitle {
  font-size: 0.8rem;
  color: #94a3b8;
  margin-left: auto;
}

.library-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.library-card {
  background: #0f172a;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #1e293b;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.card-title {
  font-size: 0.85rem;
  font-weight: 700;
  color: #38bdf8;
}

.material-preview {
  background: #1e293b;
  padding: 0.75rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.8rem;
}

.prop-row {
  display: flex;
  justify-content: space-between;
  color: #94a3b8;
}

.val {
  color: #38bdf8;
  font-weight: 700;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.btn-block {
  width: 100%;
  justify-content: center;
}

.status-msg.success {
  font-size: 0.8rem;
  color: #34d399;
}
</style>
