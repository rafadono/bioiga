<template>
  <div class="geometry-builder glass-panel">
    <div class="builder-header">
      <div class="header-left">
        <Icon name="layers" :size="22" />
        <div>
          <h3 class="builder-title">Suite CAD e IGA Avanzada: Malla de Nudos, Coordenadas y Trimmed NURBS</h3>
          <span class="builder-subtitle font-mono">
            p = {{ degreeP }}, q = {{ degreeQ }} | {{ totalControlPoints }} Puntos de Control | Grid Snap: {{ snapGridEnabled ? `${gridStep}m` : 'Off' }}
          </span>
        </div>
      </div>

      <!-- Import/Export Quick Action Bar -->
      <div class="action-bar">
        <label class="btn btn-secondary btn-sm file-input-label">
          <Icon name="upload" :size="14" />
          <span>Importar DXF 2D</span>
          <input type="file" accept=".dxf" @change="handleDxfImport" class="hidden-input" />
        </label>
        <button @click="handleDxfExport" class="btn btn-secondary btn-sm">
          <Icon name="download" :size="14" />
          <span>Exportar DXF</span>
        </button>
        <button @click="handleSvgExport" class="btn btn-secondary btn-sm">
          <Icon name="image" :size="14" />
          <span>Exportar SVG</span>
        </button>
      </div>
    </div>

    <!-- Navigation Tabs (Consolidated 2 Clean CAD Tabs) -->
    <div class="tab-nav">
      <button :class="['tab-btn', { active: activeTab === 'cad' }]" @click="activeTab = 'cad'">
        1. Modelado CAD & Recortes
      </button>

      <button :class="['tab-btn', { active: activeTab === 'nurbs' }]" @click="activeTab = 'nurbs'">
        2. Refinamiento NURBS & Coordenadas (X, Y, W)
      </button>
    </div>

    <!-- Feedback Message Banner -->
    <div v-if="alertMessage" :class="['alert-banner', alertType]">
      <span>{{ alertMessage }}</span>
      <button @click="alertMessage = null" class="close-btn">&times;</button>
    </div>

    <div :class="['builder-grid', { 'grid-collapsed': isControlsCollapsed }]">
      <!-- Unified CAD Modeling & Cutouts Panel (Tab 1) -->
      <div v-if="activeTab === 'cad'" :class="['controls-card', { 'card-collapsed': isControlsCollapsed }]">
        <div class="card-header-row mb-1">
          <h4 class="card-title" v-if="!isControlsCollapsed">1. Formas de Dominio y Trazado CAD</h4>
          <button
            @click="isControlsCollapsed = !isControlsCollapsed"
            class="btn-icon-collapse"
            :title="isControlsCollapsed ? 'Expandir Panel de Herramientas CAD' : 'Colapsar Panel (Ampliar Lienzo CAD)'"
          >
            <Icon :name="isControlsCollapsed ? 'chevron-right' : 'chevron-left'" :size="16" />
          </button>
        </div>

        <template v-if="!isControlsCollapsed">
          <div class="form-group">
            <label class="form-label">Geometría Base del Dominio</label>
            <select v-model="shapeType" class="form-select">
              <option value="rectangle">Placa Rectangular / Cuadrada</option>
              <option value="circle">Disco Circular</option>
              <option value="l_shape">Placa en Forma de L</option>
            </select>
          </div>


        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Ancho a (m)</label>
            <input type="number" v-model.number="dimA" min="0.1" max="10.0" step="0.1" class="form-input" />
          </div>
          <div class="form-group" v-if="shapeType === 'rectangle'">
            <label class="form-label">Alto b (m)</label>
            <input type="number" v-model.number="dimB" min="0.1" max="10.0" step="0.1" class="form-input" />
          </div>
        </div>

        <!-- Mode Selector Toolbar -->
        <h4 class="card-title section-title">Herramientas de Trazado Directo</h4>

        <div class="cad-mode-selector">
          <button
            :class="['mode-btn', { active: cadDrawMode === 'draw_polygon' }]"
            @click="setDrawMode('draw_polygon')"
            title="Trazar Forma / Polígono Físico haciendo clic en los vértices del contorno"
          >
            <Icon name="edit-3" :size="14" />
            <span>Trazar Polígono / Libres</span>
          </button>
          <button
            :class="['mode-btn', { active: cadDrawMode === 'draw_rectangle' }]"
            @click="setDrawMode('draw_rectangle')"
            title="Trazar Rectángulo / Caja Rápida"
          >
            <Icon name="square" :size="14" />
            <span>Trazar Caja</span>
          </button>
          <button
            :class="['mode-btn', { active: cadDrawMode === 'edit_vertices' }]"
            @click="setDrawMode('edit_vertices')"
            title="Mover Vértices Geométricos del Contorno"
          >
            <Icon name="move" :size="14" />
            <span>Mover Vértices</span>
          </button>
          <button
            :class="['mode-btn', { active: cadDrawMode === 'edit_nurbs' }]"
            @click="setDrawMode('edit_nurbs')"
            title="Ajustar Nudos NURBS Manualmente"
          >
            <Icon name="grid" :size="14" />
            <span>Ajustar Nudos NURBS</span>
          </button>
        </div>

        <div class="cad-quick-actions">
          <button @click="clearDrawnShape" class="btn btn-secondary btn-sm btn-clear">
            <Icon name="trash-2" :size="12" />
            <span>Borrar Forma</span>
          </button>
          <button @click="autoFitNurbsToShape" class="btn btn-primary btn-sm">
            <Icon name="zap" :size="12" />
            <span>Auto-Adaptar Nudos</span>
          </button>
        </div>

        <!-- Section 2: Multi-Cutout Manager -->
        <h4 class="card-title section-title">2. Recortes Multi-Orificios (Trimmed NURBS / LSM)</h4>

        <div class="cutout-add-actions">
          <button @click="addCutout('circle')" class="btn btn-secondary btn-sm cutout-add-btn">
            <span>+ Círculo</span>
          </button>
          <button @click="addCutout('ellipse')" class="btn btn-secondary btn-sm cutout-add-btn">
            <span>+ Elipse</span>
          </button>
          <button @click="addCutout('square')" class="btn btn-secondary btn-sm cutout-add-btn">
            <span>+ Rectángulo</span>
          </button>
        </div>

        <div class="toggle-group">
          <label class="toggle-label">
            <input type="checkbox" v-model="trimmedNurbsEnabled" />
            <span>Integración Immersed Boundary (Cut-FEM)</span>
          </label>
        </div>

        <template v-if="trimmedNurbsEnabled">
          <div class="form-group">
            <label class="form-label">Sub-división Quadtree: <strong>Nivel {{ quadtreeLevel }}</strong></label>
            <input type="range" v-model.number="quadtreeLevel" min="2" max="6" step="1" class="range-input" />
          </div>

          <div class="cutouts-list">
            <div
              v-for="(hole, hIdx) in trimmedCutouts"
              :key="hole.id"
              :class="['cutout-card', { active: activeCutoutIdx === hIdx }]"
              @click="activeCutoutIdx = hIdx"
            >
              <div class="cutout-card-header">
                <span class="cutout-title">
                  <Icon name="circle" :size="14" class="text-rose" />
                  Orificio #{{ hIdx + 1 }} ({{ hole.shape.toUpperCase() }})
                </span>
                <button @click.stop="removeCutout(hIdx)" class="btn-icon-danger" title="Eliminar este Orificio">
                  &times;
                </button>
              </div>

              <div class="form-row">
                <div class="form-group">
                  <label class="form-label">Forma</label>
                  <select v-model="hole.shape" class="form-select sm-select">
                    <option value="circle">Circular</option>
                    <option value="ellipse">Elíptico</option>
                    <option value="square">Rectangular</option>
                  </select>
                </div>
                <div class="form-group">
                  <label class="form-label">Radio/Ancho</label>
                  <input type="number" v-model.number="hole.radius" min="0.02" step="0.05" class="form-input num-box" />
                </div>
                <div class="form-group" v-if="hole.shape !== 'circle'">
                  <label class="form-label">Alto (m)</label>
                  <input type="number" v-model.number="hole.radiusY" min="0.02" step="0.05" class="form-input num-box" />
                </div>
              </div>
            </div>
          </div>
        </template>
        </template>
      </div>


      <!-- Refinement & Coordinates Panel (Tab 2) -->
      <div v-else-if="activeTab === 'nurbs'" class="controls-card">
        <h4 class="card-title">1. Grados e Inserción de Nudos</h4>
        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Grado p (U)</label>
            <input type="number" v-model.number="degreeP" min="1" max="5" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">Grado q (V)</label>
            <input type="number" v-model.number="degreeQ" min="1" max="5" class="form-input" />
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label class="form-label">Nudos N_u</label>
            <input type="number" v-model.number="knotsInsertU" min="0" max="20" step="1" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">Nudos N_v</label>
            <input type="number" v-model.number="knotsInsertV" min="0" max="20" step="1" class="form-input" />
          </div>
        </div>

        <h4 class="card-title section-title">2. Tabla de Coordenadas (X, Y, W)</h4>
        <div class="card-header-row">
          <button @click="downloadCsv" class="btn btn-secondary btn-sm">
            <Icon name="download" :size="12" />
            <span>Descargar CSV</span>
          </button>
        </div>
        <div class="table-wrapper">
          <table class="coord-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>u_idx</th>
                <th>v_idx</th>
                <th>X (m)</th>
                <th>Y (m)</th>
                <th>W</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(pt, idx) in customControlPoints" :key="pt.id">
                <td>{{ pt.id }}</td>
                <td>{{ pt.u_idx }}</td>
                <td>{{ pt.v_idx }}</td>
                <td><input type="number" step="0.01" v-model.number="pt.x" class="table-input" /></td>
                <td><input type="number" step="0.01" v-model.number="pt.y" class="table-input" /></td>
                <td><input type="number" step="0.05" v-model.number="pt.w" class="table-input" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Interactive SVG Canvas Viewport -->
      <div class="preview-card">
        <div class="card-header-row">
          <h4 class="card-title">Viewport CAD 2D — Malla de Nudos y Red de Control</h4>

          <!-- CAD Viewport Navigation Controls Toolbar -->
          <div class="viewport-toolbar">
            <button @click="zoomIn" class="tool-btn" title="Acercar (Zoom In)">
              <span>+</span>
            </button>
            <button @click="zoomOut" class="tool-btn" title="Alejar (Zoom Out)">
              <span>-</span>
            </button>
            <button @click="resetView" class="tool-btn" title="Centrar Vista / Fit">
              <span>Fit / Centrar</span>
            </button>
            <button :class="['tool-btn', { active: isPanToolActive }]" @click="isPanToolActive = !isPanToolActive" title="Herramienta Pan / Desplazar">
              <span>Pan</span>
            </button>
            <span class="zoom-badge font-mono">{{ Math.round(zoomLevel * 100) }}%</span>
          </div>

          <span class="cursor-coords font-mono" v-if="mouseCoords">
            X: {{ mouseCoords.x.toFixed(2) }} m | Y: {{ mouseCoords.y.toFixed(2) }} m
          </span>
        </div>

        <div class="svg-wrapper" @mousemove="handleMouseMove" @mouseup="handleMouseUp" @mouseleave="handleMouseUp">
          <svg
            :viewBox="svgViewBox"
            class="preview-svg interactive-canvas"
            :style="{ cursor: getCanvasCursor() }"
            ref="svgRef"
            @wheel.prevent="handleWheelZoom"
            @mousedown="handleCanvasMouseDown"
            @click="handleCanvasClick"
          >
            <defs>
              <pattern id="gridPattern" width="20" height="20" patternUnits="userSpaceOnUse">
                <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="1" />
              </pattern>
            </defs>

            <!-- Background Grid -->
            <rect x="-1000" y="-1000" width="3000" height="3000" fill="url(#gridPattern)" />

            <!-- Drawn Geometric Polygon Boundary (Physical Part Contour) -->
            <polygon
              v-if="polygonVertices.length >= 3"
              :points="drawnPolygonPointsSvg"
              fill="rgba(244, 114, 182, 0.15)"
              stroke="#f472b6"
              stroke-width="3"
            />
            <path
              v-else-if="polygonVertices.length >= 2"
              :d="drawnPolylinePathSvg"
              fill="none"
              stroke="#f472b6"
              stroke-width="3"
            />

            <!-- Drawn Physical Geometry Vertices (Gold Handles) -->
            <g v-for="(v, vIdx) in polygonVertices" :key="'vert-' + vIdx">
              <circle
                :cx="transformRealToSvgX(v.x)"
                :cy="transformRealToSvgY(v.y)"
                r="7"
                fill="#fbbf24"
                stroke="#ffffff"
                stroke-width="2"
                class="vertex-handle"
                @mousedown.stop.prevent="handleVertexMouseDown(vIdx, $event)"
              />
              <text
                :x="transformRealToSvgX(v.x) + 9"
                :y="transformRealToSvgY(v.y) - 6"
                fill="#fbbf24"
                font-size="10"
                font-weight="bold"
                font-family="monospace"
              >
                V{{ vIdx + 1 }}
              </text>
            </g>

            <!-- Auto-Fitted NURBS Mesh Display (If enabled) -->
            <template v-if="showNurbsNet">
              <!-- Polygon Net connecting Control Points -->
              <path
                v-for="(row, rIdx) in controlGridRows"
                :key="'row-' + rIdx"
                :d="rowPath(row)"
                fill="none"
                stroke="#334155"
                stroke-width="1"
                stroke-dasharray="3,3"
              />
              <path
                v-for="(col, cIdx) in controlGridCols"
                :key="'col-' + cIdx"
                :d="rowPath(col)"
                fill="none"
                stroke="#334155"
                stroke-width="1"
                stroke-dasharray="3,3"
              />

              <!-- Outer Domain Surface Fill (NURBS Domain) -->
              <polygon
                v-if="!polygonVertices.length"
                :points="domainPolygonPoints"
                fill="rgba(56, 189, 248, 0.12)"
                stroke="#38bdf8"
                stroke-width="2.5"
              />

              <!-- Draggable & Clickable Control Points (Canvas CAD) -->
              <g v-for="(pt, idx) in customControlPoints" :key="'node-' + idx">
                <circle
                  :cx="transformRealToSvgX(pt.x)"
                  :cy="transformRealToSvgY(pt.y)"
                  :r="activePointIdx === idx ? 8 : 5"
                  :fill="activePointIdx === idx ? '#fbbf24' : '#38bdf8'"
                  stroke="#ffffff"
                  stroke-width="1.5"
                  class="draggable-point"
                  @mousedown.stop.prevent="handlePointMouseDown(idx, $event)"
                />
              </g>
            </template>

            <!-- Multi-Cutout Trimmed NURBS Display & Draggable Cutout Centers -->
            <template v-if="trimmedNurbsEnabled">
              <g v-for="(hole, hIdx) in trimmedCutouts" :key="'cutout-' + hole.id">
                <circle
                  v-if="hole.shape === 'circle'"
                  :cx="transformRealToSvgX(hole.cx)"
                  :cy="transformRealToSvgY(hole.cy)"
                  :r="hole.radius * 50"
                  fill="#0f172a"
                  :stroke="activeCutoutIdx === hIdx ? '#fbbf24' : '#f43f5e'"
                  stroke-width="2.5"
                  stroke-dasharray="5,5"
                />
                <ellipse
                  v-else-if="hole.shape === 'ellipse'"
                  :cx="transformRealToSvgX(hole.cx)"
                  :cy="transformRealToSvgY(hole.cy)"
                  :rx="hole.radius * 50"
                  :ry="(hole.radiusY || hole.radius) * 50"
                  fill="#0f172a"
                  :stroke="activeCutoutIdx === hIdx ? '#fbbf24' : '#f43f5e'"
                  stroke-width="2.5"
                  stroke-dasharray="5,5"
                />
                <rect
                  v-else-if="hole.shape === 'square'"
                  :x="transformRealToSvgX(hole.cx) - hole.radius * 50"
                  :y="transformRealToSvgY(hole.cy) - (hole.radiusY || hole.radius) * 50"
                  :width="hole.radius * 100"
                  :height="(hole.radiusY || hole.radius) * 100"
                  fill="#0f172a"
                  :stroke="activeCutoutIdx === hIdx ? '#fbbf24' : '#f43f5e'"
                  stroke-width="2.5"
                  stroke-dasharray="5,5"
                />

                <!-- Draggable Center Handle for Cutout -->
                <circle
                  :cx="transformRealToSvgX(hole.cx)"
                  :cy="transformRealToSvgY(hole.cy)"
                  r="6"
                  :fill="activeCutoutIdx === hIdx ? '#fbbf24' : '#f43f5e'"
                  stroke="#ffffff"
                  stroke-width="2"
                  class="cutout-handle"
                  @mousedown.stop.prevent="handleCutoutMouseDown(hIdx, $event)"
                />
                <text
                  :x="transformRealToSvgX(hole.cx) + 8"
                  :y="transformRealToSvgY(hole.cy) - 6"
                  fill="#f43f5e"
                  font-size="10"
                  font-family="monospace"
                  font-weight="bold"
                >
                  H{{ hIdx + 1 }}
                </text>
              </g>
            </template>
          </svg>
        </div>

        <div class="geom-summary font-mono">
          <div class="prop-row"><span>Forma Creada:</span> <span class="val text-pink">{{ polygonVertices.length }} Vértices Físicos</span></div>
          <div class="prop-row"><span>Orificios de Recorte:</span> <span class="val text-rose">{{ trimmedCutouts.length }} Orificios (Quadtree L{{ quadtreeLevel }})</span></div>
          <div class="prop-row"><span>Malla NURBS Adaptada:</span> <span class="val">{{ numCtrlU }} x {{ numCtrlV }} ({{ customControlPoints.length }} Nudos)</span></div>
          <div class="prop-row"><span>Elementos IGA:</span> <span class="val text-emerald">{{ totalIgaElements }} Elementos Spans</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Icon from './Icon.vue'
import type { ControlPoint } from '../types'

interface TrimmedCutout {
  id: string
  shape: 'circle' | 'ellipse' | 'square'
  cx: number
  cy: number
  radius: number
  radiusY: number
}

const isControlsCollapsed = ref<boolean>(false)
const activeTab = ref<'cad' | 'nurbs'>('cad')
const alertMessage = ref<string | null>(null)

const alertType = ref<'success' | 'warning' | 'error'>('success')

const shapeType = ref<'rectangle' | 'circle' | 'l_shape'>('rectangle')
const dimA = ref<number>(2.0)
const dimB = ref<number>(2.0)

const degreeP = ref<number>(2)
const degreeQ = ref<number>(2)
const knotsInsertU = ref<number>(2)
const knotsInsertV = ref<number>(2)

// Multi-Cutout Trimmed NURBS State
const trimmedNurbsEnabled = ref<boolean>(true)
const quadtreeLevel = ref<number>(4)
const activeCutoutIdx = ref<number | null>(null)
const trimmedCutouts = ref<TrimmedCutout[]>([
  { id: 'hole-1', shape: 'circle', cx: 0.0, cy: 0.0, radius: 0.35, radiusY: 0.35 },
])

function addCutout(shape: 'circle' | 'ellipse' | 'square') {
  const count = trimmedCutouts.value.length + 1
  trimmedCutouts.value.push({
    id: `hole-${count}`,
    shape,
    cx: (count - 1) * 0.2,
    cy: 0.0,
    radius: 0.3,
    radiusY: 0.3,
  })
  activeCutoutIdx.value = trimmedCutouts.value.length - 1
  alertType.value = 'success'
  alertMessage.value = `Nuevo Orificio #${count} (${shape.toUpperCase()}) agregado. Puedes arrastrarlo directamente en el canvas.`
}

function removeCutout(idx: number) {
  trimmedCutouts.value.splice(idx, 1)
  activeCutoutIdx.value = null
}

function handleCutoutMouseDown(idx: number, event: MouseEvent) {
  activeCutoutIdx.value = idx
}

// Zero-Friction Geometric Drawing State
const cadDrawMode = ref<'draw_polygon' | 'draw_rectangle' | 'edit_vertices' | 'edit_nurbs'>('draw_polygon')
const polygonVertices = ref<{ x: number; y: number }[]>([
  { x: -1.0, y: -1.0 },
  { x: 1.0, y: -1.0 },
  { x: 1.0, y: 1.0 },
  { x: -1.0, y: 1.0 },
])
const activeVertexIdx = ref<number | null>(null)
const showNurbsNet = ref<boolean>(true)

const snapGridEnabled = ref<boolean>(true)
const gridStep = ref<number>(0.05)
const activePointIdx = ref<number | null>(null)
const mouseCoords = ref<{ x: number; y: number } | null>(null)

// Zoom & Pan Navigation State
const zoomLevel = ref<number>(1.0)
const panX = ref<number>(0.0)
const panY = ref<number>(0.0)
const isPanning = ref<boolean>(false)
const isPanToolActive = ref<boolean>(false)
const panStart = ref<{ x: number; y: number }>({ x: 0, y: 0 })

const cadDrawModeTitle = computed(() => {
  if (cadDrawMode.value === 'draw_polygon') return 'Trazar Polígono (Haz clic para colocar vértices)'
  if (cadDrawMode.value === 'draw_rectangle') return 'Trazar Rectángulo (Haz clic en 2 esquinas)'
  if (cadDrawMode.value === 'edit_vertices') return 'Mover Vértices (Arrastra esquinas doradas)'
  return 'Ajuste Manual Red NURBS'
})

function setDrawMode(mode: 'draw_polygon' | 'draw_rectangle' | 'edit_vertices' | 'edit_nurbs') {
  cadDrawMode.value = mode
}

function getCanvasCursor(): string {
  if (isPanning.value || isPanToolActive.value) return 'grab'
  if (cadDrawMode.value === 'draw_polygon' || cadDrawMode.value === 'draw_rectangle') return 'crosshair'
  if (cadDrawMode.value === 'edit_vertices') return 'pointer'
  return 'default'
}

const svgViewBox = computed(() => {
  const w = 400 / zoomLevel.value
  const h = 300 / zoomLevel.value
  const x = panX.value + (400 - w) / 2
  const y = panY.value + (300 - h) / 2
  return `${x} ${y} ${w} ${h}`
})

function zoomIn() {
  zoomLevel.value = Math.min(5.0, parseFloat((zoomLevel.value + 0.25).toFixed(2)))
}

function zoomOut() {
  zoomLevel.value = Math.max(0.3, parseFloat((zoomLevel.value - 0.25).toFixed(2)))
}

function resetView() {
  zoomLevel.value = 1.0
  panX.value = 0.0
  panY.value = 0.0
  isPanToolActive.value = false
}

function handleWheelZoom(event: WheelEvent) {
  const delta = event.deltaY < 0 ? 0.15 : -0.15
  const newZoom = Math.min(5.0, Math.max(0.3, zoomLevel.value + delta))
  zoomLevel.value = parseFloat(newZoom.toFixed(2))
}

function handleCanvasMouseDown(event: MouseEvent) {
  if (event.button === 1 || event.button === 2 || event.shiftKey || isPanToolActive.value) {
    isPanning.value = true
    panStart.value = { x: event.clientX, y: event.clientY }
  }
}

// Zero-Friction Drawing Handler
function handleCanvasClick() {
  if (isPanning.value || !mouseCoords.value) return

  if (cadDrawMode.value === 'draw_polygon') {
    polygonVertices.value.push({ x: mouseCoords.value.x, y: mouseCoords.value.y })
    autoFitNurbsToShape()
  } else if (cadDrawMode.value === 'draw_rectangle') {
    if (polygonVertices.value.length >= 4) {
      polygonVertices.value = []
    }
    polygonVertices.value.push({ x: mouseCoords.value.x, y: mouseCoords.value.y })
    if (polygonVertices.value.length === 2) {
      const p1 = polygonVertices.value[0]
      const p2 = polygonVertices.value[1]
      polygonVertices.value = [
        { x: Math.min(p1.x, p2.x), y: Math.min(p1.y, p2.y) },
        { x: Math.max(p1.x, p2.x), y: Math.min(p1.y, p2.y) },
        { x: Math.max(p1.x, p2.x), y: Math.max(p1.y, p2.y) },
        { x: Math.min(p1.x, p2.x), y: Math.max(p1.y, p2.y) },
      ]
      autoFitNurbsToShape()
    }
  }
}

function handleVertexMouseDown(idx: number, event: MouseEvent) {
  if (cadDrawMode.value === 'edit_vertices' || cadDrawMode.value === 'draw_polygon') {
    activeVertexIdx.value = idx
  }
}

function handlePointMouseDown(idx: number, event: MouseEvent) {
  if (cadDrawMode.value === 'edit_nurbs') {
    activePointIdx.value = idx
  }
}

function clearDrawnShape() {
  polygonVertices.value = []
  recomputeGridPoints()
  alertType.value = 'warning'
  alertMessage.value = 'Geometría borrada. Haz clic en el lienzo para trazar la forma física de tu pieza.'
}

// Automatic NURBS Fitting Engine
function autoFitNurbsToShape() {
  if (polygonVertices.value.length < 2) return

  let minX = Infinity, maxX = -Infinity
  let minY = Infinity, maxY = -Infinity
  for (const v of polygonVertices.value) {
    if (v.x < minX) minX = v.x
    if (v.x > maxX) maxX = v.x
    if (v.y < minY) minY = v.y
    if (v.y > maxY) maxY = v.y
  }

  const width = Math.max(0.1, maxX - minX)
  const height = Math.max(0.1, maxY - minY)
  dimA.value = parseFloat(width.toFixed(2))
  dimB.value = parseFloat(height.toFixed(2))

  const nu = numCtrlU.value
  const nv = numCtrlV.value
  const pts: ControlPoint[] = []

  let idCount = 0
  for (let r = 0; r < nv; r++) {
    const y = minY + (r / (nv - 1)) * height
    for (let c = 0; c < nu; c++) {
      const x = minX + (c / (nu - 1)) * width
      idCount++
      pts.push({
        id: `cp-${idCount}`,
        u_idx: c,
        v_idx: r,
        x: parseFloat(x.toFixed(3)),
        y: parseFloat(y.toFixed(3)),
        w: 1.0,
      })
    }
  }
  customControlPoints.value = pts
}

const numCtrlU = computed(() => degreeP.value + 1 + knotsInsertU.value)
const numCtrlV = computed(() => degreeQ.value + 1 + knotsInsertV.value)
const totalControlPoints = computed(() => customControlPoints.value.length)
const totalIgaElements = computed(() => (knotsInsertU.value + 1) * (knotsInsertV.value + 1))

// Reactive Control Points list
const customControlPoints = ref<ControlPoint[]>([])

// Initialize grid control points based on dimensions
function recomputeGridPoints() {
  const pts: ControlPoint[] = []
  const nu = numCtrlU.value
  const nv = numCtrlV.value
  const width = dimA.value
  const height = shapeType.value === 'rectangle' ? dimB.value : dimA.value

  let idCount = 0
  for (let r = 0; r < nv; r++) {
    const y = (r / (nv - 1)) * height - height / 2
    for (let c = 0; c < nu; c++) {
      const x = (c / (nu - 1)) * width - width / 2
      idCount++
      pts.push({
        id: `cp-${idCount}`,
        u_idx: c,
        v_idx: r,
        x: parseFloat(x.toFixed(3)),
        y: parseFloat(y.toFixed(3)),
        w: 1.0,
      })
    }
  }
  customControlPoints.value = pts

  polygonVertices.value = [
    { x: -width / 2, y: -height / 2 },
    { x: width / 2, y: -height / 2 },
    { x: width / 2, y: height / 2 },
    { x: -width / 2, y: height / 2 },
  ]
}

// Watch dimension / refinement changes to recompute
watch([dimA, dimB, shapeType, degreeP, degreeQ, knotsInsertU, knotsInsertV], () => {
  recomputeGridPoints()
}, { immediate: true })

// SVG Transformations: Real Coords (m) <-> SVG Viewport (400x300 px)
function transformRealToSvgX(x: number): number {
  return 200 + x * 50
}
function transformRealToSvgY(y: number): number {
  return 150 - y * 50
}
function transformSvgToRealX(svgX: number): number {
  return (svgX - 200) / 50
}
function transformSvgToRealY(svgY: number): number {
  return (150 - svgY) / 50
}

const drawnPolygonPointsSvg = computed(() => {
  return polygonVertices.value
    .map((v) => `${transformRealToSvgX(v.x)},${transformRealToSvgY(v.y)}`)
    .join(' ')
})

const drawnPolylinePathSvg = computed(() => {
  if (!polygonVertices.value.length) return ''
  let d = `M ${transformRealToSvgX(polygonVertices.value[0].x)} ${transformRealToSvgY(polygonVertices.value[0].y)}`
  for (let i = 1; i < polygonVertices.value.length; i++) {
    d += ` L ${transformRealToSvgX(polygonVertices.value[i].x)} ${transformRealToSvgY(polygonVertices.value[i].y)}`
  }
  return d
})

// Control Grid Rows and Cols for dashed line display
const controlGridRows = computed(() => {
  const rows: { x: number; y: number }[][] = []
  const nu = numCtrlU.value
  const nv = numCtrlV.value
  const pts = customControlPoints.value

  for (let r = 0; r < nv; r++) {
    const row: { x: number; y: number }[] = []
    for (let c = 0; c < nu; c++) {
      const idx = r * nu + c
      if (pts[idx]) {
        row.push({
          x: transformRealToSvgX(pts[idx].x),
          y: transformRealToSvgY(pts[idx].y),
        })
      }
    }
    if (row.length) rows.push(row)
  }
  return rows
})

const controlGridCols = computed(() => {
  const cols: { x: number; y: number }[][] = []
  const nu = numCtrlU.value
  const nv = numCtrlV.value
  const pts = customControlPoints.value

  for (let c = 0; c < nu; c++) {
    const col: { x: number; y: number }[] = []
    for (let r = 0; r < nv; r++) {
      const idx = r * nu + c
      if (pts[idx]) {
        col.push({
          x: transformRealToSvgX(pts[idx].x),
          y: transformRealToSvgY(pts[idx].y),
        })
      }
    }
    if (col.length) cols.push(col)
  }
  return cols
})

const domainPolygonPoints = computed(() => {
  const pts = customControlPoints.value
  if (!pts.length) return ''

  return pts
    .map((pt) => `${transformRealToSvgX(pt.x)},${transformRealToSvgY(pt.y)}`)
    .join(' ')
})

function rowPath(row: { x: number; y: number }[]): string {
  if (!row.length) return ''
  let d = `M ${row[0].x} ${row[0].y}`
  for (let i = 1; i < row.length; i++) {
    d += ` L ${row[i].x} ${row[i].y}`
  }
  return d
}

// Mouse Event Handlers for Drag & Drop CAD Canvas
function handleMouseMove(event: MouseEvent) {
  if (isPanning.value) {
    const dx = (event.clientX - panStart.value.x) / (zoomLevel.value * 1.2)
    const dy = (event.clientY - panStart.value.y) / (zoomLevel.value * 1.2)
    panX.value -= dx
    panY.value -= dy
    panStart.value = { x: event.clientX, y: event.clientY }
    return
  }

  const svg = event.currentTarget as SVGSVGElement
  const rect = svg.getBoundingClientRect()
  const mouseSvgX = (event.clientX - rect.left) * (400 / rect.width)
  const mouseSvgY = (event.clientY - rect.top) * (300 / rect.height)

  let realX = transformSvgToRealX(mouseSvgX)
  let realY = transformSvgToRealY(mouseSvgY)

  if (snapGridEnabled.value) {
    const step = gridStep.value
    realX = Math.round(realX / step) * step
    realY = Math.round(realY / step) * step
  }

  mouseCoords.value = { x: realX, y: realY }

  // Dragging Physical Geometry Vertices
  if (activeVertexIdx.value !== null && polygonVertices.value[activeVertexIdx.value]) {
    polygonVertices.value[activeVertexIdx.value].x = parseFloat(realX.toFixed(3))
    polygonVertices.value[activeVertexIdx.value].y = parseFloat(realY.toFixed(3))
    autoFitNurbsToShape()
  }

  // Dragging Cutout Hole Center Handle
  if (activeCutoutIdx.value !== null && trimmedCutouts.value[activeCutoutIdx.value]) {
    trimmedCutouts.value[activeCutoutIdx.value].cx = parseFloat(realX.toFixed(3))
    trimmedCutouts.value[activeCutoutIdx.value].cy = parseFloat(realY.toFixed(3))
  }

  // Dragging Individual NURBS Control Points
  if (activePointIdx.value !== null && customControlPoints.value[activePointIdx.value]) {
    customControlPoints.value[activePointIdx.value].x = parseFloat(realX.toFixed(3))
    customControlPoints.value[activePointIdx.value].y = parseFloat(realY.toFixed(3))
  }
}

function handleMouseUp() {
  activePointIdx.value = null
  activeVertexIdx.value = null
  isPanning.value = false
}

// DXF Import / Export Functions
async function handleDxfImport(event: Event) {
  const target = event.target as HTMLInputElement
  if (!target.files || !target.files[0]) return

  const file = target.files[0]
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await fetch('/api/geometry/import-dxf', {
      method: 'POST',
      body: formData,
    })
    if (!response.ok) {
      const err = await response.json()
      throw new Error(err.detail || 'Error al importar DXF')
    }
    const resData = await response.json()
    if (resData.geometry && resData.geometry.ctrl_pts) {
      const flatPts: ControlPoint[] = []
      let idc = 0
      resData.geometry.ctrl_pts.forEach((row: number[][], r: number) => {
        row.forEach((pt: number[], c: number) => {
          idc++
          flatPts.push({
            id: `cp-${idc}`,
            u_idx: c,
            v_idx: r,
            x: pt[0],
            y: pt[1],
            w: 1.0,
          })
        })
      })
      customControlPoints.value = flatPts
      alertType.value = 'success'
      alertMessage.value = `Importación DXF 2D Exitosa: ${flatPts.length} puntos cargados correctamente.`
    }
  } catch (err: any) {
    alertType.value = 'error'
    alertMessage.value = `Error DXF 2D: ${err.message}`
  }
}

async function handleDxfExport() {
  try {
    const ctrlPts2D = customControlPoints.value.map((p) => [p.x, p.y])
    const response = await fetch('/api/geometry/export-dxf', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ control_points: ctrlPts2D }),
    })
    const text = await response.text()
    const blob = new Blob([text], { type: 'application/dxf' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'nurbs_geometry_2d.dxf'
    a.click()
    URL.revokeObjectURL(url)
  } catch (err: any) {
    alertType.value = 'error'
    alertMessage.value = 'Error al exportar DXF 2D'
  }
}

async function handleSvgExport() {
  try {
    const ctrlPts2D = customControlPoints.value.map((p) => [p.x, p.y])
    const response = await fetch('/api/geometry/export-svg', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ control_points: ctrlPts2D }),
    })
    const text = await response.text()
    const blob = new Blob([text], { type: 'image/svg+xml' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'nurbs_vector_geometry.svg'
    a.click()
    URL.revokeObjectURL(url)
  } catch (err: any) {
    alertType.value = 'error'
    alertMessage.value = 'Error al exportar SVG'
  }
}

function downloadCsv() {
  const header = 'id,u_idx,v_idx,x,y,w\n'
  const rows = customControlPoints.value
    .map((p) => `${p.id},${p.u_idx},${p.v_idx},${p.x},${p.y},${p.w}`)
    .join('\n')
  const blob = new Blob([header + rows], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'control_points.csv'
  a.click()
  URL.revokeObjectURL(url)
}
</script>

<style scoped>
.geometry-builder {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  width: 100%;
  box-sizing: border-box;
}

.builder-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #1e293b;
  padding-bottom: 0.75rem;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.action-bar {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tab-nav {
  display: flex;
  gap: 0.5rem;
  border-bottom: 2px solid #1e293b;
  flex-wrap: wrap;
}

.tab-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  padding: 0.5rem 1rem;
  font-weight: 600;
  font-size: 0.85rem;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  transition: all 0.2s;
}

.tab-btn.active {
  color: #38bdf8;
  border-bottom-color: #38bdf8;
}

.alert-banner {
  padding: 0.6rem 1rem;
  border-radius: 6px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.alert-banner.success {
  background: rgba(52, 211, 153, 0.15);
  border: 1px solid #34d399;
  color: #34d399;
}

.alert-banner.error {
  background: rgba(244, 63, 94, 0.15);
  border: 1px solid #f43f5e;
  color: #f43f5e;
}

.alert-banner.warning {
  background: rgba(251, 191, 36, 0.15);
  border: 1px solid #fbbf24;
  color: #fbbf24;
}

.close-btn {
  background: none;
  border: none;
  color: inherit;
  font-size: 1.2rem;
  cursor: pointer;
}

.builder-grid {
  display: grid;
  grid-template-columns: minmax(280px, 340px) 1fr;
  gap: 1.25rem;
  width: 100%;
  box-sizing: border-box;
  transition: all 0.25s ease-in-out;
}

.builder-grid.grid-collapsed {
  grid-template-columns: 48px 1fr;
}

.controls-card,
.preview-card {
  background: #0f172a;
  padding: 1rem;
  border-radius: 8px;
  border: 1px solid #1e293b;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  width: 100%;
  box-sizing: border-box;
  overflow: hidden;
  transition: all 0.25s ease-in-out;
}

.controls-card.card-collapsed {
  padding: 0.6rem 0.4rem;
  align-items: center;
}

.btn-icon-collapse {
  background: #1e293b;
  border: 1px solid #334155;
  color: #38bdf8;
  border-radius: 6px;
  padding: 0.35rem 0.45rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: auto;
  transition: all 0.15s ease;
}

.btn-icon-collapse:hover {
  background: #38bdf8;
  color: #0f172a;
}

.card-collapsed .btn-icon-collapse {
  margin-left: 0;
  width: 100%;
}

.card-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
  width: 100%;
}


.cutout-add-actions {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.35rem;
  width: 100%;
  box-sizing: border-box;
}

.cutout-add-btn {
  width: 100%;
  padding: 0.35rem 0.2rem;
  font-size: 0.72rem;
  justify-content: center;
  text-align: center;
  box-sizing: border-box;
  overflow: hidden;
  white-space: nowrap;
}

.cutouts-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  max-height: 220px;
  overflow-y: auto;
  width: 100%;
  box-sizing: border-box;
}

.cutout-card {
  background: #1e293b;
  border: 1px solid #334155;
  padding: 0.6rem 0.75rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  cursor: pointer;
  transition: border-color 0.15s;
  width: 100%;
  box-sizing: border-box;
}

.cutout-card:hover,
.cutout-card.active {
  border-color: #f43f5e;
}

.cutout-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 700;
  font-size: 0.78rem;
}

.cutout-title {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  color: #f1f5f9;
}

.btn-icon-danger {
  background: none;
  border: none;
  color: #f43f5e;
  font-size: 1.1rem;
  cursor: pointer;
  padding: 0 0.2rem;
}

.sm-select {
  font-size: 0.78rem;
  padding: 0.25rem 0.4rem;
}

.cad-mode-selector {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  width: 100%;
  box-sizing: border-box;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #1e293b;
  border: 1px solid #334155;
  color: #cbd5e1;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.82rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
  width: 100%;
  box-sizing: border-box;
}

.mode-btn:hover {
  background: #334155;
  border-color: #38bdf8;
}

.mode-btn.active {
  background: #38bdf8;
  color: #0f172a;
  border-color: #38bdf8;
}

.cad-quick-actions {
  display: flex;
  gap: 0.5rem;
  width: 100%;
  box-sizing: border-box;
}

.btn-clear {
  color: #f43f5e;
  border-color: rgba(244, 63, 94, 0.4);
}

.btn-clear:hover {
  background: rgba(244, 63, 94, 0.15);
}

.viewport-toolbar {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  background: #1e293b;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  border: 1px solid #334155;
}

.tool-btn {
  background: #0f172a;
  border: 1px solid #334155;
  color: #cbd5e1;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.15s;
}

.tool-btn:hover,
.tool-btn.active {
  background: #38bdf8;
  color: #0f172a;
  border-color: #38bdf8;
}

.zoom-badge {
  color: #fbbf24;
  font-size: 0.75rem;
  margin-left: 0.25rem;
}

.table-wrapper {
  max-height: 280px;
  overflow-y: auto;
  border: 1px solid #1e293b;
  border-radius: 4px;
  width: 100%;
  box-sizing: border-box;
}

.coord-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
}

.coord-table th,
.coord-table td {
  padding: 0.35rem 0.5rem;
  border: 1px solid #1e293b;
  text-align: center;
}

.coord-table th {
  background: #1e293b;
  color: #38bdf8;
}

.table-input {
  width: 100%;
  background: transparent;
  border: none;
  color: #cbd5e1;
  text-align: center;
  font-family: inherit;
}

.svg-wrapper {
  background: #020617;
  border-radius: 6px;
  border: 1px solid #1e293b;
  padding: 0.5rem;
  position: relative;
  overflow: hidden;
  width: 100%;
  box-sizing: border-box;
}

.interactive-canvas {
  width: 100%;
  height: 280px;
  user-select: none;
}

.draggable-point {
  cursor: pointer;
  transition: r 0.15s ease;
}

.draggable-point:hover {
  r: 8;
}

.vertex-handle {
  cursor: move;
  transition: r 0.15s ease;
}

.vertex-handle:hover {
  r: 9;
}

.cutout-handle {
  cursor: move;
  transition: r 0.15s ease;
}

.cutout-handle:hover {
  r: 8;
}

.cad-instructions {
  background: #1e293b;
  padding: 0.6rem 0.8rem;
  border-radius: 6px;
  font-size: 0.78rem;
  color: #94a3b8;
  width: 100%;
  box-sizing: border-box;
}

.cad-instructions ul {
  padding-left: 1.2rem;
  margin-top: 0.3rem;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

.text-amber {
  color: #fbbf24;
}

.text-pink {
  color: #f472b6;
}

.text-rose {
  color: #f43f5e;
}

.hidden-input {
  display: none;
}

.file-input-label {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.cursor-coords {
  color: #fbbf24;
  font-size: 0.78rem;
}

.geom-summary {
  background: #1e293b;
  padding: 0.75rem;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.78rem;
  width: 100%;
  box-sizing: border-box;
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

.text-emerald {
  color: #34d399;
}
</style>
