<template>
  <div class="project-manager glass-panel">
    <div class="manager-header">
      <Icon name="folder" :size="20" />
      <h3 class="manager-title">Gestor de Proyectos y Persistencia JSON Estándar</h3>
      <span class="manager-subtitle font-mono">Formato ABIERTO JSON (.bioiga.json / .json)</span>
    </div>

    <div class="manager-grid">
      <!-- Save & Export Form -->
      <div class="manager-card">
        <h4 class="card-title">1. Guardar y Exportar Proyecto</h4>
        <p class="card-desc">Guarde en el servidor local o descargue el archivo JSON abierto para usar en Python, MATLAB o Julia.</p>

        <div class="form-group">
          <label class="form-label">Nombre del Proyecto</label>
          <input type="text" v-model="projectName" placeholder="ej. Placa_Cantilever_Perforada" class="form-input" />
        </div>

        <div class="btn-group">
          <button @click="onSave" :disabled="!projectName" class="btn btn-primary">
            <Icon name="save" :size="16" />
            <span>Guardar en Servidor Local</span>
          </button>
          <button @click="exportJsonFile" :disabled="!projectName" class="btn btn-secondary">
            <Icon name="download" :size="16" />
            <span>Exportar Archivo JSON</span>
          </button>
        </div>
        <span v-if="saveMessage" class="status-msg success">{{ saveMessage }}</span>

        <h4 class="card-title section-title">2. Importar Proyecto desde Archivo JSON</h4>
        <div class="import-box">
          <input type="file" ref="fileInput" accept=".json,.bioiga.json" @change="importJsonFile" class="file-input" />
          <button @click="triggerFileInput" class="btn btn-secondary btn-block">
            <Icon name="upload" :size="16" />
            <span>Subir e Importar Archivo JSON</span>
          </button>
        </div>
      </div>

      <!-- Projects List -->
      <div class="manager-card">
        <h4 class="card-title">Proyectos Guardados en Servidor Local (.bioiga_projects/)</h4>
        <div class="projects-list">
          <div v-for="pName in projectsList" :key="pName" class="project-item font-mono">
            <span class="project-name">{{ pName }}.json</span>
            <div class="item-actions">
              <button @click="onLoad(pName)" class="btn btn-secondary btn-sm">
                <Icon name="download" :size="14" />
                <span>Cargar</span>
              </button>
              <button @click="onDelete(pName)" class="btn btn-danger btn-sm">
                <Icon name="trash" :size="14" />
                <span>Eliminar</span>
              </button>
            </div>
          </div>
          <div v-if="projectsList.length === 0" class="empty-msg">
            No hay proyectos guardados en la carpeta local aún.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import Icon from './Icon.vue'

const projectName = ref<string>('')
const projectsList = ref<string[]>([])
const saveMessage = ref<string>('')
const fileInput = ref<HTMLInputElement | null>(null)

const emit = defineEmits<{
  (e: 'load-project', projectData: any): void
}>()

async function fetchProjects() {
  try {
    const res = await fetch('/api/projects')
    if (res.ok) {
      const data = await res.json()
      projectsList.value = data.projects || []
    }
  } catch (err) {
    console.error('Error fetching projects:', err)
  }
}

async function onSave() {
  if (!projectName.value) return
  try {
    const payload = {
      name: projectName.value,
      description: 'Proyecto creado desde BioIGA UI',
    }
    const res = await fetch('/api/projects', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    })
    if (res.ok) {
      saveMessage.value = `Proyecto '${projectName.value}' guardado correctamente.`
      projectName.value = ''
      await fetchProjects()
      setTimeout(() => { saveMessage.value = '' }, 3000)
    }
  } catch (err) {
    console.error('Error saving project:', err)
  }
}

function exportJsonFile() {
  if (!projectName.value) return
  const projectData = {
    version: '0.3.0',
    project_name: projectName.value,
    timestamp: new Date().toISOString(),
    geometry: { shape_type: 'rectangle', dim_a: 2.0, dim_b: 1.0, degree_p: 2, degree_q: 2 },
    material: { name: 'Steel A36', young_modulus: 200e9, poisson_ratio: 0.29, density: 7850 },
    boundary_conditions: { bc_type: 'cantilever', pbc_x: false, pbc_y: false },
    optimization_config: { algorithm: 'MPMBPSO', generations: 50, pop_size: 20, num_variables: 100 }
  }

  const jsonStr = JSON.stringify(projectData, null, 2)
  const blob = new Blob([jsonStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `${projectName.value}.bioiga.json`
  a.click()
  URL.revokeObjectURL(url)
}

function triggerFileInput() {
  if (fileInput.value) {
    fileInput.value.click()
  }
}

function importJsonFile(e: Event) {
  const target = e.target as HTMLInputElement
  if (!target.files || target.files.length === 0) return
  const file = target.files[0]
  const reader = new FileReader()
  reader.onload = (evt) => {
    try {
      const data = JSON.parse(evt.target?.result as string)
      emit('load-project', data)
      saveMessage.value = `Proyecto '${file.name}' importado con éxito.`
      setTimeout(() => { saveMessage.value = '' }, 3000)
    } catch (err) {
      alert('Error al leer el archivo JSON: formato no válido.')
    }
  }
  reader.readAsText(file)
}

async function onLoad(name: string) {
  try {
    const res = await fetch(`/api/projects/${name}`)
    if (res.ok) {
      const data = await res.json()
      emit('load-project', data)
      saveMessage.value = `Proyecto '${name}' cargado.`
      setTimeout(() => { saveMessage.value = '' }, 3000)
    }
  } catch (err) {
    console.error('Error loading project:', err)
  }
}

async function onDelete(name: string) {
  if (!confirm(`¿Eliminar proyecto '${name}'?`)) return
  try {
    const res = await fetch(`/api/projects/${name}`, { method: 'DELETE' })
    if (res.ok) {
      await fetchProjects()
    }
  } catch (err) {
    console.error('Error deleting project:', err)
  }
}

onMounted(() => {
  fetchProjects()
})
</script>

<style scoped>
.project-manager {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.manager-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #38bdf8;
  border-bottom: 1px solid #334155;
  padding-bottom: 0.5rem;
}

.manager-title {
  font-size: 1rem;
  font-weight: 700;
  color: #f8fafc;
}

.manager-subtitle {
  font-size: 0.8rem;
  color: #34d399;
  margin-left: auto;
}

.manager-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.manager-card {
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

.card-desc {
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.3;
}

.section-title {
  border-top: 1px solid #1e293b;
  padding-top: 0.5rem;
  margin-top: 0.25rem;
}

.btn-group {
  display: flex;
  gap: 0.5rem;
}

.file-input {
  display: none;
}

.status-msg {
  font-size: 0.8rem;
  padding: 0.4rem;
  border-radius: 4px;
}

.status-msg.success {
  color: #34d399;
  background: rgba(52, 211, 153, 0.1);
}

.projects-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 250px;
  overflow-y: auto;
}

.project-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #1e293b;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.82rem;
}

.project-name {
  color: #f8fafc;
}

.item-actions {
  display: flex;
  gap: 0.4rem;
}

.btn-block {
  width: 100%;
  justify-content: center;
}

.btn-sm {
  padding: 0.3rem 0.6rem !important;
  font-size: 0.75rem !important;
}

.empty-msg {
  font-size: 0.8rem;
  color: #64748b;
  font-style: italic;
  text-align: center;
  padding: 1rem 0;
}
</style>
