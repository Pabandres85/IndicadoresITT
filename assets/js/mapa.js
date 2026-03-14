// ── CONFIGURACIÓN DEL MAPA ──────────────────────────────────────────────────
const map = L.map('map', { zoomControl: true, attributionControl: false }).setView([3.430, -76.488], 14);

const baseLayers = {
  streets:   L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', { maxZoom: 19, subdomains: 'abc' }),
  satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 }),
  hybrid:    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', { maxZoom: 19 })
};
const labelsLayer = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_only_labels/{z}/{x}/{y}{r}.png',
  { maxZoom: 19, subdomains: 'abcd', pane: 'shadowPane' });
baseLayers.streets.addTo(map);

window.setLayer = function(type) {
  const keep = new Set([clusters, heatLayer, comunasLayer, vivLayer].filter(Boolean));
  map.eachLayer(l => { if (!keep.has(l) && !l.feature) map.removeLayer(l); });
  if (type === 'streets')   baseLayers.streets.addTo(map);
  if (type === 'satellite') baseLayers.satellite.addTo(map);
  if (type === 'hybrid')    { baseLayers.hybrid.addTo(map); labelsLayer.addTo(map); }
  document.querySelectorAll('.layer-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('btn-' + type).classList.add('active');
};

// ── CLUSTER (color dinámico por modo) ────────────────────────────────────────
function clusterStyle() {
  const styles = {
    infraestructura: ['rgba(27,77,46,0.95)',    '#4CAF77'],
    seguridad:       ['rgba(193,39,45,0.92)',   '#E57373'],
    equipamientos:   ['rgba(21,101,192,0.92)',  '#64B5F6'],
    ambiente:        ['rgba(46,125,50,0.92)',   '#81C784'],
    vivienda:        ['rgba(106,27,154,0.92)',  '#CE93D8'],
  };
  return styles[currentDataMode] || styles.infraestructura;
}

const clusters = L.markerClusterGroup({
  maxClusterRadius: 45, showCoverageOnHover: false,
  iconCreateFunction: c => {
    const n = c.getChildCount();
    const sz = n < 10 ? 36 : n < 50 ? 44 : 52;
    const [bg, bdr] = clusterStyle();
    return L.divIcon({
      html: `<div style="width:${sz}px;height:${sz}px;border-radius:50%;background:${bg};border:3px solid ${bdr};display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;color:white;box-shadow:0 3px 10px rgba(0,0,0,0.4);">${n}</div>`,
      className: '', iconSize: [sz, sz]
    });
  }
});

// ── ESTADO GLOBAL ────────────────────────────────────────────────────────────
let globalPerimetro  = null;
let allMarkers       = [];
let currentDataMode  = 'infraestructura';
let _data            = null;
let heatLayer        = null;
let heatVisible      = false;
let comunasLayer     = null;
let mecalLayer       = null;   // polígonos MECAL (equipamientos)
let filtersPanelOpen = false;

// Datasets cacheados
let hurtosData      = null;
let homicidiosData  = null;
let vifData         = null;
let vbgData         = null;
let sedesData       = null;
let caiData         = null;
let arbolesData     = null;
let arbolesLoading  = false;

// Datasets: Vivienda
let vivLegalizacionData = null;
let vivMejoramientoData = null;
let vivLayer            = null;

// Filtros: Vivienda
let vivSubMode = 'legalizacion';
let vivAño     = 'all';
let vivProceso = 'all';
let vivEstado  = 'all';

// Filtros: Infraestructura
let activeFilter = 'all';
let activeEstado = 'all';
let currentMode  = 'ups';

// Filtros: Seguridad
let secSubMode = 'hurtos';
let secAño     = 'all';
let secTipo    = 'all';
let secComuna  = 'all';

// Filtros: Equipamientos
let eqTipo = 'all';   // 'sedes' | 'cai' | 'all'

// Filtros: Ambiente
let ambEstado = 'all';
let ambComuna = 'all';

// ── REPROYECCIÓN GeoJSON → WGS84 ────────────────────────────────────────────
// Soporta las dos proyecciones que usan los shapefiles locales:
//   ESRI:103599  (Origen Único MAGNA-SIRGAS, usado por comunas)
//   EPSG:6249 / EPSG:3116  (MAGNA-SIRGAS / Colombia West zone, usado por vivienda)
const PROJ_DEFS = {
  'ESRI:103599': '+proj=tmerc +lat_0=4 +lon_0=-73 +k=0.9992 +x_0=5000000 +y_0=2000000 +ellps=GRS80 +units=m +no_defs',
  'EPSG:3116':   '+proj=tmerc +lat_0=4.596200416667 +lon_0=-77.07750796388889 +k=1 +x_0=1000000 +y_0=1000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
};
// Alias: EPSG:6249 usa la misma zona que 3116 (Colombia West, datum shift < 3 m)
PROJ_DEFS['EPSG:6249'] = PROJ_DEFS['EPSG:3116'];

function detectSrcCrs(crsName) {
  if (/103599/.test(crsName))   return 'ESRI:103599';
  if (/6249/.test(crsName))     return 'EPSG:6249';
  if (/3116/.test(crsName))     return 'EPSG:3116';
  return null;
}

function reprojectGeoJSONToWGS84(geojson) {
  const crsName = geojson?.crs?.properties?.name || '';
  const srcCrs  = detectSrcCrs(crsName);
  if (!srcCrs) return geojson;                       // ya es WGS84 u otro CRS desconocido
  if (typeof proj4 !== 'function') {
    console.warn('proj4 no disponible; GeoJSON no reproyectado:', crsName);
    return geojson;
  }

  proj4.defs(srcCrs, PROJ_DEFS[srcCrs]);
  const cloned = JSON.parse(JSON.stringify(geojson));

  function mapCoords(coords) {
    if (!Array.isArray(coords)) return coords;
    if (coords.length >= 2 && typeof coords[0] === 'number' && typeof coords[1] === 'number') {
      const [lon, lat] = proj4(srcCrs, 'EPSG:4326', [coords[0], coords[1]]);
      return [lon, lat];
    }
    return coords.map(mapCoords);
  }

  cloned.features = (cloned.features || []).map(f => ({
    ...f,
    geometry: f.geometry ? { ...f.geometry, coordinates: mapCoords(f.geometry.coordinates) } : f.geometry,
  }));
  delete cloned.crs;
  return cloned;
}

// ── PALETAS DE COLORES ───────────────────────────────────────────────────────
const VIV_LEG_COLORS = {
  'Con Radicación':       '#FFC300',
  'Proceso de Legalización': '#6A1B9A',
};
const VIV_MEJ_COLORS = {
  ASIGNADO:   '#1565C0',
  EJECUCION:  '#E65100',
  EJECUTADO:  '#2E7D32',
};

function getVivLegColor(proceso) {
  return VIV_LEG_COLORS[proceso] || '#607D8B';
}
function getVivMejColor(estado) {
  if (!estado) return '#607D8B';
  if (estado.includes('EJECUTADO') && !estado.includes('EJECUCI')) return VIV_MEJ_COLORS.EJECUTADO;
  if (estado.includes('EJECUCI')) return VIV_MEJ_COLORS.EJECUCION;
  return VIV_MEJ_COLORS.ASIGNADO;
}
function getEstadoLabel(estado) {
  if (!estado) return '—';
  if (estado.includes('EJECUCI') && estado.includes('EJECUTADO')) return 'Ejecutado';
  if (estado.includes('EJECUCI')) return 'En Ejecución';
  if (estado === 'ASIGNADO') return 'Asignado';
  return estado;
}
function getConvocLabel(conv) {
  if (!conv) return '—';
  if (conv.includes('MINISTERIO')) return 'Conv. Ministerio';
  if (conv === 'EMPRESTITO') return 'Empréstito';
  return conv;
}

const HURTO_COLORS = {
  'ATRACO': '#C1272D', 'RAPONAZO': '#E65100', 'COSQUILLEO': '#F57F17',
  'DESCUIDO': '#1565C0', 'FLETEO': '#6A1B9A', 'OTRAS': '#607D8B'
};
const HOM_COLORS = {
  'DELINCUENCIA': '#C1272D', 'CONVIVENCIA': '#E67E22', 'OTRO': '#607D8B'
};
const AMB_COLORS = {
  'Nuevo': '#4CAF77', 'Vivo': '#2196F3', 'Muerto': '#9E9E9E', 'Eliminado': '#E74C3C'
};

function getHurtoColor(tipo) {
  return HURTO_COLORS[(tipo || '').toUpperCase()] || HURTO_COLORS['OTRAS'];
}
function getHomColor(tipo) {
  return HOM_COLORS[(tipo || '').toUpperCase()] || HOM_COLORS['OTRO'];
}
function getAmbColor(estado) {
  return AMB_COLORS[estado] || '#607D8B';
}
function capitalize(s) {
  return s ? s.charAt(0).toUpperCase() + s.slice(1).toLowerCase() : '';
}

function shouldShowHeatmapControls() {
  return currentDataMode === 'seguridad' && secSubMode === 'hurtos';
}

function syncFiltersPanelUI() {
  const panel = document.getElementById('filters-panel');
  const btn = document.getElementById('btn-filters-toggle');
  if (!panel || !btn) return;
  panel.classList.toggle('show', filtersPanelOpen);
  panel.setAttribute('aria-hidden', filtersPanelOpen ? 'false' : 'true');
  btn.classList.toggle('active', filtersPanelOpen);
  btn.setAttribute('aria-expanded', filtersPanelOpen ? 'true' : 'false');
}

function setFiltersPanelOpen(open) {
  filtersPanelOpen = !!open;
  syncFiltersPanelUI();
}

function syncHeatmapUI() {
  const controls = document.getElementById('heatmap-controls');
  const btn = document.getElementById('btn-heatmap');
  const scale = document.getElementById('heat-scale');
  const allowHeat = shouldShowHeatmapControls();

  if (controls) controls.classList.toggle('show', allowHeat);

  if (!allowHeat && heatLayer && map.hasLayer(heatLayer)) {
    map.removeLayer(heatLayer);
    heatVisible = false;
  }

  if (btn) {
    btn.classList.toggle('active', allowHeat && heatVisible);
    btn.disabled = allowHeat && !heatLayer;
    btn.title = allowHeat ? '3.990 hurtos 2023-2025' : 'Disponible en Seguridad > Hurtos';
  }

  if (scale) {
    const showScale = allowHeat && heatVisible;
    scale.classList.toggle('show', showScale);
    scale.setAttribute('aria-hidden', showScale ? 'false' : 'true');
  }
}

// ── HELPERS UI ───────────────────────────────────────────────────────────────
function setKPI(frentes, frentesLbl, inversion, invLbl) {
  document.getElementById('kpi-frentes').innerText     = frentes;
  document.getElementById('kpi-frentes-lbl').innerText = frentesLbl;
  document.getElementById('kpi-inversion').innerText   = inversion;
  const el = document.getElementById('kpi-inv-lbl');
  if (el) el.innerText = invLbl;
}

function dotIcon(color, size = 14) {
  return L.divIcon({
    html: `<div style="width:${size}px;height:${size}px;border-radius:50%;background:${color};border:2.5px solid rgba(255,255,255,0.9);box-shadow:0 2px 6px rgba(0,0,0,0.5);"></div>`,
    className: '', iconSize: [size, size], iconAnchor: [size/2, size/2]
  });
}

function legendItems(entries) {
  return entries.map(([label, color]) =>
    `<div class="legend-item"><div class="legend-dot" style="background:${color};"></div> ${label}</div>`
  ).join('');
}

// ── FILTROS ──────────────────────────────────────────────────────────────────
function applyFilters() {
  clusters.clearLayers();
  let visible = 0;

  allMarkers.forEach(m => {
    let ok = false;
    switch (currentDataMode) {
      case 'infraestructura':
        ok = (activeFilter === 'all' || m._secGroup === activeFilter) &&
             (activeEstado === 'all' || m._estado   === activeEstado);
        break;
      case 'seguridad':
        ok = (secAño    === 'all' || m._año    === secAño) &&
             (secTipo   === 'all' || m._tipo   === secTipo) &&
             (secComuna === 'all' || m._comuna === secComuna);
        break;
      case 'equipamientos':
        ok = (eqTipo === 'all' || m._eqTipo === eqTipo);
        break;
      case 'ambiente':
        ok = (ambEstado === 'all' || m._estado === ambEstado) &&
             (ambComuna === 'all' || m._comuna === ambComuna);
        break;
    }
    if (ok) { clusters.addLayer(m); visible++; }
  });

  // KPIs dinámicos en modos no-infraestructura
  if (currentDataMode === 'seguridad') {
    const total = allMarkers.length || 1;
    const pct = Math.round(visible / total * 100);
    setKPI(visible.toLocaleString('es-CO'), 'Registros Filtrados',
           pct + '%', 'Del total (' + total.toLocaleString('es-CO') + ')');
  }
  if (currentDataMode === 'equipamientos') {
    setKPI(visible, 'Equipamientos', '—', 'Filtrados');
  }
  if (currentDataMode === 'ambiente') {
    setKPI(visible.toLocaleString('es-CO'), 'Árboles Filtrados',
           Math.round(visible / (allMarkers.length || 1) * 100) + '%',
           'Del total (' + (allMarkers.length).toLocaleString('es-CO') + ')');
  }
}

// ── RENDER: INFRAESTRUCTURA ──────────────────────────────────────────────────
function renderInfraestructura() {
  clusters.clearLayers();
  allMarkers = [];

  const proyectos          = DataService.getProyectos({ pts: _data.pts, perimetro: globalPerimetro, mode: currentMode });
  const kpis               = DataService.getKPIs(proyectos);
  const secretariasActivas = [...new Set(proyectos.map(p => p.secretaria))].sort();
  if (activeFilter !== 'all' && !secretariasActivas.includes(activeFilter)) activeFilter = 'all';

  const dyn = document.getElementById('filter-dynamic');
  dyn.innerHTML =
    `<div class="filter-row filter-row-primary">
      <span class="filter-row-label">Sub-modo</span>
      <button class="filter-btn ${currentMode === 'ups' ? 'active' : ''}" data-modo="ups">Frentes UPS</button>
      <button class="filter-btn ${currentMode === 'contratos' ? 'active' : ''}" data-modo="contratos">Contratos</button>
    </div>` +
    `<div class="filter-row-divider"></div>` +
    `<div class="filter-row">
      <span class="filter-row-label">Secretaría</span>
      <button class="filter-btn ${activeFilter === 'all' ? 'active' : ''}" data-filter="all">Todas</button>` +
    secretariasActivas.map(sec => {
      const c = DataService.SEC_COLORS[sec] || DataService.SEC_COLORS['Otras'];
      return `<button class="filter-btn ${activeFilter === sec ? 'active' : ''}" data-filter="${sec}" style="border-color:${c};">${sec}</button>`;
    }).join('') +
    `</div>` +
    `<div class="filter-row">
      <span class="filter-row-label">Estado</span>` +
    [['all','Todos'],['En ejecución','En ejecución'],['En alistamiento','Alistamiento'],['Terminado','Terminado']].map(([val,lbl]) =>
      `<button class="filter-btn ${activeEstado === val ? 'active' : ''}" data-estado="${val}">${lbl}</button>`
    ).join('') +
    `</div>`;

  dyn.querySelectorAll('[data-filter]').forEach(b => b.addEventListener('click', e => {
    dyn.querySelectorAll('[data-filter]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); activeFilter = e.target.dataset.filter; applyFilters();
  }));
  dyn.querySelectorAll('[data-estado]').forEach(b => b.addEventListener('click', e => {
    dyn.querySelectorAll('[data-estado]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); activeEstado = e.target.dataset.estado; applyFilters();
  }));
  dyn.querySelectorAll('[data-modo]').forEach(b => b.addEventListener('click', e => {
    dyn.querySelectorAll('[data-modo]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); currentMode = e.target.dataset.modo; renderInfraestructura();
  }));

  setKPI(kpis.total, currentMode === 'ups' ? 'Frentes de Obra' : 'Contratos Totales',
         '$' + (kpis.inversion / 1e6).toLocaleString('es-CO', { maximumFractionDigits: 0 }) + 'M', 'Inversión COP');

  document.getElementById('legend-dynamic').innerHTML =
    legendItems(secretariasActivas.map(sec => [sec, DataService.SEC_COLORS[sec] || DataService.SEC_COLORS['Otras']]));

  proyectos.forEach(p => {
    const color    = DataService.getColor(p.secretaria);
    const estLower = p.estado.toLowerCase();
    const badge    = estLower.includes('ejecuc') ? 'badge-ejecucion' : estLower.includes('terminad') ? 'badge-terminado' : 'badge-alistamiento';
    const presStr  = p.presupuesto > 0 ? `$${Math.round(p.presupuesto/1e6).toLocaleString('es-CO')}M` : '<span style="color:#E74C3C;">No reportado</span>';
    const mk = L.marker([p.lat, p.lon], { icon: dotIcon(color) }).bindPopup(`
      <div style="min-width:240px;">
        <div class="popup-title">${p.nombre}</div>
        <div class="popup-row"><span class="popup-label">Secretaría</span><span class="popup-val" style="color:${color};">${p.secretaria}</span></div>
        <div class="popup-row"><span class="popup-label">Tipo</span><span class="popup-val">${p.tipo}</span></div>
        <div class="popup-row"><span class="popup-label">Dirección</span><span class="popup-val" style="white-space:normal;max-width:140px;">${p.direccion}</span></div>
        <div class="popup-row"><span class="popup-label">Presupuesto</span><span class="popup-val">${presStr}</span></div>
        <span class="popup-badge ${badge}">${p.estado}</span>
      </div>`, { maxWidth: 320 });
    mk._secGroup = p.secretaria;
    mk._estado   = estLower.includes('ejecuc') ? 'En ejecución' : estLower.includes('terminad') ? 'Terminado' : 'En alistamiento';
    allMarkers.push(mk);
  });
  applyFilters();
}

// ── RENDER: SEGURIDAD (con sub-modos) ────────────────────────────────────────
function renderSeguridad() {
  clusters.clearLayers();
  allMarkers = [];

  // Sub-selector común
  const subBtns = ['hurtos','homicidios','vif','vbg'].map(m => {
    const labels = { hurtos:'Hurtos', homicidios:'Homicidios', vif:'Viol. Intrafamiliar', vbg:'VBG' };
    return `<button class="filter-btn${secSubMode === m ? ' active' : ''}" data-subsec="${m}">${labels[m]}</button>`;
  }).join('');

  const dyn = document.getElementById('filter-dynamic');
  dyn.innerHTML =
    `<div class="filter-row filter-row-primary">
      <span class="filter-row-label">Delito</span>
      ${subBtns}
    </div>
    <div class="filter-row-divider"></div>
    <div id="sec-sub-filters"></div>`;

  dyn.querySelectorAll('[data-subsec]').forEach(b => b.addEventListener('click', e => {
    dyn.querySelectorAll('[data-subsec]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active');
    secSubMode = e.target.dataset.subsec;
    secAño = 'all'; secTipo = 'all'; secComuna = 'all';
    syncHeatmapUI();
    renderSecSubMode();
  }));

  syncHeatmapUI();
  renderSecSubMode();
}

function buildSecFilters(features, getAño, getTipo, getComuna, colorFn) {
  const años    = [...new Set(features.map(getAño).filter(Boolean))].sort();
  const tipos   = [...new Set(features.map(getTipo).filter(Boolean))].sort();
  const comunas = [...new Set(features.map(getComuna).filter(Boolean))].sort();

  if (secAño    !== 'all' && !años.includes(secAño))       secAño    = 'all';
  if (secTipo   !== 'all' && !tipos.includes(secTipo))     secTipo   = 'all';
  if (secComuna !== 'all' && !comunas.includes(secComuna)) secComuna = 'all';

  const sf = document.getElementById('sec-sub-filters');
  if (!sf) return;

  sf.innerHTML =
    (años.length > 1 ?
      `<div class="filter-row">
        <span class="filter-row-label">Período</span>
        <button class="filter-btn ${secAño==='all'?'active':''}" data-sec-año="all">Todos</button>` +
        años.map(a => `<button class="filter-btn ${secAño===a?'active':''}" data-sec-año="${a}">${a}</button>`).join('') +
      `</div>` : '') +
    (tipos.length > 1 ?
      `<div class="filter-row">
        <span class="filter-row-label">Tipo</span>
        <button class="filter-btn ${secTipo==='all'?'active':''}" data-sec-tipo="all">Todos</button>` +
        tipos.map(t => {
          const c = colorFn(t);
          return `<button class="filter-btn ${secTipo===t?'active':''}" data-sec-tipo="${t}" style="border-color:${c};">${capitalize(t)}</button>`;
        }).join('') +
      `</div>` : '') +
    `<div class="filter-row">
      <span class="filter-row-label">Comuna</span>
      <button class="filter-btn ${secComuna==='all'?'active':''}" data-sec-comuna="all">Todas</button>` +
      comunas.map(c => `<button class="filter-btn ${secComuna===c?'active':''}" data-sec-comuna="${c}">${c.replace(/COMUNA /i,'C')}</button>`).join('') +
    `</div>`;

  sf.querySelectorAll('[data-sec-año]').forEach(b => b.addEventListener('click', e => {
    sf.querySelectorAll('[data-sec-año]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); secAño = e.target.dataset.secAño; applyFilters();
  }));
  sf.querySelectorAll('[data-sec-tipo]').forEach(b => b.addEventListener('click', e => {
    sf.querySelectorAll('[data-sec-tipo]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); secTipo = e.target.dataset.secTipo; applyFilters();
  }));
  sf.querySelectorAll('[data-sec-comuna]').forEach(b => b.addEventListener('click', e => {
    sf.querySelectorAll('[data-sec-comuna]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); secComuna = e.target.dataset.secComuna; applyFilters();
  }));
}

function renderSecSubMode() {
  clusters.clearLayers();
  allMarkers = [];
  syncHeatmapUI();

  const subConfigs = {
    hurtos: {
      data: hurtosData,
      getAño:    f => f.properties.FECHA_HECH?.substring(0,4) || '',
      getTipo:   f => (f.properties.TIPO_HURTO || 'OTRAS').toUpperCase(),
      getComuna: f => f.properties.NOM_COMUNA || '',
      colorFn:   getHurtoColor,
      legend: Object.entries(HURTO_COLORS).map(([t,c]) => [capitalize(t), c]),
      total: hurtosData?.length || 0,
      kpiLbl: 'Hurtos',
    },
    homicidios: {
      data: homicidiosData,
      getAño:    f => f.properties.FECHA_HECH?.substring(0,4) || '',
      getTipo:   f => (f.properties.TIPO_VIOLE || 'OTRO').toUpperCase(),
      getComuna: f => f.properties.NOM_COMUNA || '',
      colorFn:   getHomColor,
      legend: Object.entries(HOM_COLORS).map(([t,c]) => [capitalize(t), c]),
      total: homicidiosData?.length || 0,
      kpiLbl: 'Homicidios',
    },
    vif: {
      data: vifData,
      getAño:    f => f.properties.FECHA_HECH?.substring(0,4) || '',
      getTipo:   f => f.properties.FECHA_HECH?.substring(0,4) || '',   // año como tipo para mostrar tendencia por color
      getComuna: f => f.properties.NOM_COMUNA || '',
      colorFn:   y => y === '2023' ? '#1565C0' : y === '2024' ? '#E65100' : '#C1272D',
      legend: [['2023 (457 casos)', '#1565C0'], ['2024 (483 casos)', '#E65100'], ['2025 (562 casos)', '#C1272D']],
      total: vifData?.length || 0,
      kpiLbl: 'Casos VIF',
    },
    vbg: {
      data: vbgData,
      getAño:    _f => '2025',
      getTipo:   f => f.properties.DELITO || 'VBG',
      getComuna: f => f.properties.COMUNA || '',
      colorFn:   () => '#E91E63',
      legend: [['VBG 2025', '#E91E63']],
      total: vbgData?.length || 0,
      kpiLbl: 'Casos VBG',
    },
  };

  const cfg = subConfigs[secSubMode];
  if (!cfg.data) {
    const sf = document.getElementById('sec-sub-filters');
    if (sf) sf.innerHTML = '<span class="filter-label" style="color:#E74C3C;">⚠ Datos no disponibles</span>';
    return;
  }

  buildSecFilters(cfg.data, cfg.getAño, cfg.getTipo, cfg.getComuna, cfg.colorFn);

  setKPI(cfg.total.toLocaleString('es-CO'), cfg.kpiLbl, '—', '—');
  document.getElementById('legend-dynamic').innerHTML = legendItems(cfg.legend);

  // Popup builder por sub-modo
  const popupBuilders = {
    hurtos: (props, color) => {
      const tipo = (props.TIPO_HURTO || 'OTRAS').toUpperCase();
      return `<div style="min-width:220px;">
        <div class="popup-title" style="color:${color};">${capitalize(tipo)}</div>
        <div class="popup-row"><span class="popup-label">Modalidad</span><span class="popup-val">${capitalize(props.MODALIDAD)||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Barrio</span><span class="popup-val">${props.NOM_BARRIO||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Sitio</span><span class="popup-val">${capitalize(props.SITIO)||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Fecha</span><span class="popup-val">${props.FECHA_HECH||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Hora</span><span class="popup-val">${props.HORA_HECHO||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Estrato</span><span class="popup-val">${props.ESTRATO||'—'}</span></div>
      </div>`;
    },
    homicidios: (props, color) => `<div style="min-width:220px;">
        <div class="popup-title" style="color:${color};">Homicidio</div>
        <div class="popup-row"><span class="popup-label">Tipo Violencia</span><span class="popup-val">${capitalize(props.TIPO_VIOLE)||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Barrio</span><span class="popup-val">${props.NOM_BARRIO||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Fecha</span><span class="popup-val">${props.FECHA_HECH||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Hora</span><span class="popup-val">${props.HORA_HECHO||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Estrato</span><span class="popup-val">${props.ESTRATO||'—'}</span></div>
      </div>`,
    vif: (props, color) => `<div style="min-width:220px;">
        <div class="popup-title" style="color:${color};">Violencia Intrafamiliar</div>
        <div class="popup-row"><span class="popup-label">Barrio</span><span class="popup-val">${props.NOM_BARRIO||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Sitio</span><span class="popup-val">${capitalize(props.SITIO)||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Fecha</span><span class="popup-val">${props.FECHA_HECH||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Hora</span><span class="popup-val">${props.HORA_HECHO||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Estrato</span><span class="popup-val">${props.ESTRATO||'—'}</span></div>
      </div>`,
    vbg: (props, color) => `<div style="min-width:220px;">
        <div class="popup-title" style="color:${color};">Violencia Basada en Género</div>
        <div class="popup-row"><span class="popup-label">Barrio</span><span class="popup-val">${props.BARRIO||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Comuna</span><span class="popup-val">${props.COMUNA||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Dirección</span><span class="popup-val" style="white-space:normal;max-width:140px;">${props.DIRECCION||'—'}</span></div>
      </div>`,
  };

  cfg.data.forEach(f => {
    if (!f.geometry?.coordinates) return;
    const props = f.properties;
    const [lon, lat] = f.geometry.coordinates;
    const año    = cfg.getAño(f);
    const tipo   = cfg.getTipo(f);
    const comuna = cfg.getComuna(f);
    const color  = cfg.colorFn(tipo);
    const sz     = secSubMode === 'homicidios' ? 12 : 10;

    const mk = L.marker([lat, lon], { icon: dotIcon(color, sz) })
      .bindPopup(popupBuilders[secSubMode](props, color), { maxWidth: 300 });
    mk._año    = año;
    mk._tipo   = tipo;
    mk._comuna = comuna;
    allMarkers.push(mk);
  });

  applyFilters();
}

// ── RENDER: EQUIPAMIENTOS ────────────────────────────────────────────────────
function renderEquipamientos() {
  clusters.clearLayers();
  allMarkers = [];

  // Toggle MECAL polygons visibility
  if (mecalLayer) {
    eqTipo === 'sedes' ? map.removeLayer(mecalLayer) : mecalLayer.addTo(map);
  }

  const dyn = document.getElementById('filter-dynamic');
  dyn.innerHTML =
    `<div class="filter-row filter-row-primary">
      <span class="filter-row-label">Tipo</span>` +
    [['all','Todos'],['sedes','Sedes Educativas'],['cai','CAI / Policía']].map(([v,l]) =>
      `<button class="filter-btn ${eqTipo===v?'active':''}" data-eq="${v}">${l}</button>`
    ).join('') +
    `</div>`;

  dyn.querySelectorAll('[data-eq]').forEach(b => b.addEventListener('click', e => {
    dyn.querySelectorAll('[data-eq]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); eqTipo = e.target.dataset.eq; renderEquipamientos();
  }));

  const totalSedes = sedesData?.length || 0;
  const totalCAI   = caiData?.length || 0;
  setKPI(totalSedes + totalCAI, 'Equipamientos', totalSedes + ' sedes · ' + totalCAI + ' CAI', 'Disponibles');

  document.getElementById('legend-dynamic').innerHTML = legendItems([
    ['Sede Educativa', '#1565C0'],
    ['CAI / Policía', '#C1272D'],
    ['Jurisdicción MECAL', '#E67E22'],
  ]);

  // Sedes educativas
  if (sedesData && eqTipo !== 'cai') {
    sedesData.forEach(f => {
      if (!f.geometry?.coordinates) return;
      const props = f.properties;
      const [lon, lat] = f.geometry.coordinates;
      const nombre = props.NombreSede || props.NombreInst || 'Sede';
      const estado = props.Estado_DUE || '—';
      const sector = props.Sector || '—';

      const mk = L.marker([lat, lon], { icon: dotIcon('#1565C0', 14) }).bindPopup(`
        <div style="min-width:240px;">
          <div class="popup-title" style="color:#1565C0;">🏫 ${nombre}</div>
          <div class="popup-row"><span class="popup-label">Institución</span><span class="popup-val" style="white-space:normal;max-width:150px;">${props.NombreInst||'—'}</span></div>
          <div class="popup-row"><span class="popup-label">Barrio</span><span class="popup-val">${props.BarrioVere||'—'}</span></div>
          <div class="popup-row"><span class="popup-label">Comuna</span><span class="popup-val">${props.ComunaCorr||'—'}</span></div>
          <div class="popup-row"><span class="popup-label">Sector</span><span class="popup-val">${sector}</span></div>
          <div class="popup-row"><span class="popup-label">Estado</span><span class="popup-val">${estado}</span></div>
        </div>`, { maxWidth: 320 });
      mk._eqTipo = 'sedes';
      allMarkers.push(mk);
    });
  }

  // CAI / MECAL puntos
  if (caiData && eqTipo !== 'sedes') {
    caiData.forEach(f => {
      if (!f.geometry?.coordinates) return;
      const props = f.properties;
      const [lon, lat] = f.geometry.coordinates;

      const mk = L.marker([lat, lon], { icon: dotIcon('#C1272D', 16) }).bindPopup(`
        <div style="min-width:220px;">
          <div class="popup-title" style="color:#C1272D;">🚔 ${props.UNIDAD||'CAI'}</div>
          <div class="popup-row"><span class="popup-label">Tipo</span><span class="popup-val">${props.TIPO||'—'}</span></div>
          <div class="popup-row"><span class="popup-label">Distrito</span><span class="popup-val">${props.DISTRITO||'—'}</span></div>
          <div class="popup-row"><span class="popup-label">Sigla</span><span class="popup-val">${props.SIGLA||'—'}</span></div>
        </div>`, { maxWidth: 280 });
      mk._eqTipo = 'cai';
      allMarkers.push(mk);
    });
  }

  applyFilters();
}

// ── RENDER: AMBIENTE ─────────────────────────────────────────────────────────
function renderAmbiente() {
  clusters.clearLayers();
  allMarkers = [];

  const dyn = document.getElementById('filter-dynamic');

  if (!arbolesData) {
    if (arbolesLoading) {
      dyn.innerHTML = '<span class="filter-label">⏳ Cargando árboles (10 MB)...</span>';
      return;
    }
    arbolesLoading = true;
    dyn.innerHTML = '<span class="filter-label">⏳ Cargando árboles (10 MB)...</span>';
    fetch('../data/ambiente/ARBOLES_PULMON.geojson')
      .then(r => r.json())
      .then(geo => { arbolesData = geo.features; arbolesLoading = false; renderAmbiente(); })
      .catch(() => {
        arbolesLoading = false;
        dyn.innerHTML = '<span class="filter-label" style="color:#E74C3C;">⚠ Error cargando árboles</span>';
      });
    return;
  }

  const comunas = [...new Set(arbolesData.map(f => f.properties.comuna).filter(Boolean))].sort((a,b)=>+a-+b);
  if (ambComuna !== 'all' && !comunas.includes(ambComuna)) ambComuna = 'all';

  dyn.innerHTML =
    `<div class="filter-row filter-row-primary">
      <span class="filter-row-label">Estado</span>` +
    [['all','Todos'],['Nuevo','Nuevo'],['Vivo','Vivo'],['Muerto','Muerto'],['Eliminado','Eliminado']].map(([v,l]) => {
      const c = v === 'all' ? null : AMB_COLORS[v];
      return `<button class="filter-btn ${ambEstado===v?'active':''}" data-amb="${v}"${c?` style="border-color:${c};"`:''}">${l}</button>`;
    }).join('') +
    `</div>` +
    `<div class="filter-row">
      <span class="filter-row-label">Comuna</span>
      <button class="filter-btn ${ambComuna==='all'?'active':''}" data-amb-com="all">Todas</button>` +
    comunas.map(c => `<button class="filter-btn ${ambComuna===c?'active':''}" data-amb-com="${c}">C${c}</button>`).join('') +
    `</div>`;

  dyn.querySelectorAll('[data-amb]').forEach(b => b.addEventListener('click', e => {
    dyn.querySelectorAll('[data-amb]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); ambEstado = e.target.dataset.amb; applyFilters();
  }));
  dyn.querySelectorAll('[data-amb-com]').forEach(b => b.addEventListener('click', e => {
    dyn.querySelectorAll('[data-amb-com]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); ambComuna = e.target.dataset.ambCom; applyFilters();
  }));

  setKPI(arbolesData.length.toLocaleString('es-CO'), 'Árboles Totales', '—', 'Filtrados');
  document.getElementById('legend-dynamic').innerHTML =
    legendItems(Object.entries(AMB_COLORS).map(([e,c]) => [e, c]));

  arbolesData.forEach(f => {
    if (!f.geometry?.coordinates) return;
    const props = f.properties;
    const [lon, lat] = f.geometry.coordinates;
    const estado = props.estado_arb || '—';
    const color  = getAmbColor(estado);

    const mk = L.marker([lat, lon], { icon: dotIcon(color, 8) }).bindPopup(`
      <div style="min-width:200px;">
        <div class="popup-title" style="color:${color};">🌳 Árbol #${props.id_arbol||'—'}</div>
        <div class="popup-row"><span class="popup-label">Estado</span><span class="popup-val" style="color:${color};font-weight:600;">${estado}</span></div>
        <div class="popup-row"><span class="popup-label">Comuna</span><span class="popup-val">${props.comuna||'—'}</span></div>
        <div class="popup-row"><span class="popup-label">Especie ID</span><span class="popup-val">${props.id_especie||'—'}</span></div>
      </div>`, { maxWidth: 260 });
    mk._estado = estado;
    mk._comuna = props.comuna || '';
    allMarkers.push(mk);
  });

  applyFilters();
}

// ── RENDER: VIVIENDA ─────────────────────────────────────────────────────────
function renderVivienda() {
  clusters.clearLayers();
  allMarkers = [];

  const subBtns = ['legalizacion','mejoramiento'].map(m => {
    const labels = { legalizacion: 'Legalización Urbanística', mejoramiento: 'Mejoramiento Vivienda' };
    return `<button class="filter-btn${vivSubMode === m ? ' active' : ''}" data-vivsub="${m}">${labels[m]}</button>`;
  }).join('');

  const dyn = document.getElementById('filter-dynamic');
  dyn.innerHTML =
    `<div class="filter-row filter-row-primary">
      <span class="filter-row-label">Programa</span>
      ${subBtns}
    </div>
    <div class="filter-row-divider"></div>
    <div id="viv-sub-filters"></div>`;

  dyn.querySelectorAll('[data-vivsub]').forEach(b => b.addEventListener('click', e => {
    dyn.querySelectorAll('[data-vivsub]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active');
    vivSubMode = e.target.dataset.vivsub;
    vivAño = 'all'; vivProceso = 'all'; vivEstado = 'all';
    renderVivSubMode();
  }));

  renderVivSubMode();
}

function renderVivSubMode() {
  vivSubMode === 'legalizacion' ? renderVivLegalizacion(true) : renderVivMejoramiento(true);
}

function renderVivLegalizacion(shouldFit = false) {
  if (vivLayer) { map.removeLayer(vivLayer); vivLayer = null; }

  const sf = document.getElementById('viv-sub-filters');
  if (!vivLegalizacionData) {
    if (sf) sf.innerHTML = '<div class="filter-row"><span class="filter-row-label" style="color:#E74C3C;">⚠ Datos no disponibles</span></div>';
    return;
  }

  const feats    = vivLegalizacionData.features;
  const años     = [...new Set(feats.map(f => String(f.properties.Ano_interv)).filter(Boolean))].sort();
  const procesos = [...new Set(feats.map(f => f.properties.PROCESO).filter(Boolean))].sort();

  if (sf) sf.innerHTML =
    `<div class="filter-row">
      <span class="filter-row-label">Año</span>
      <button class="filter-btn ${vivAño==='all'?'active':''}" data-viv-anio="all">Todos</button>` +
      años.map(a => `<button class="filter-btn ${vivAño===a?'active':''}" data-viv-anio="${a}">${a}</button>`).join('') +
    `</div>
    <div class="filter-row">
      <span class="filter-row-label">Proceso</span>
      <button class="filter-btn ${vivProceso==='all'?'active':''}" data-viv-proc="all">Todos</button>` +
      procesos.map(p => {
        const c = getVivLegColor(p);
        return `<button class="filter-btn ${vivProceso===p?'active':''}" data-viv-proc="${p}" style="border-color:${c};">${p}</button>`;
      }).join('') +
    `</div>`;

  sf.querySelectorAll('[data-viv-anio]').forEach(b => b.addEventListener('click', e => {
    sf.querySelectorAll('[data-viv-anio]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); vivAño = e.target.dataset.vivAnio; renderVivLegalizacion();
  }));
  sf.querySelectorAll('[data-viv-proc]').forEach(b => b.addEventListener('click', e => {
    sf.querySelectorAll('[data-viv-proc]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); vivProceso = e.target.dataset.vivProc; renderVivLegalizacion();
  }));

  const filtered = feats.filter(f => {
    const p = f.properties;
    return (vivAño === 'all' || String(p.Ano_interv) === vivAño) &&
           (vivProceso === 'all' || p.PROCESO === vivProceso);
  });

  const totalHa = filtered.reduce((s, f) => s + (f.properties.AREA_HA || 0), 0);
  const avgUrb  = filtered.length ? filtered.reduce((s, f) => s + (f.properties.PORC_URBAN || 0), 0) / filtered.length : 0;
  setKPI(filtered.length, 'Polígonos AHDI', totalHa.toFixed(1) + ' ha', `Promedio ${avgUrb.toFixed(0)}% urbanizado`);

  document.getElementById('legend-dynamic').innerHTML = legendItems(
    Object.entries(VIV_LEG_COLORS).map(([t,c]) => [t, c]).concat([['Sin clasificar','#607D8B']])
  );

  vivLayer = L.geoJSON({ type:'FeatureCollection', features: filtered }, {
    style: f => {
      const c = getVivLegColor(f.properties.PROCESO);
      return { color: c, weight: 2.5, fillColor: c, fillOpacity: 0.28, opacity: 0.9 };
    },
    onEachFeature: (f, layer) => {
      const p = f.properties;
      const c = getVivLegColor(p.PROCESO);
      layer.bindPopup(`
        <div style="min-width:240px;">
          <div class="popup-title" style="color:${c};">🏘 ${p.NOMBRE||'—'}</div>
          <div class="popup-row"><span class="popup-label">Barrio</span><span class="popup-val">${p.BARRIOS_SE||'—'}</span></div>
          <div class="popup-row"><span class="popup-label">Área total</span><span class="popup-val">${p.AREA_HA} ha</span></div>
          <div class="popup-row"><span class="popup-label">% Urbanizado</span><span class="popup-val" style="color:${c};font-weight:700;">${p.PORC_URBAN}%</span></div>
          <div class="popup-row"><span class="popup-label">Año</span><span class="popup-val">${p.Ano_interv||'—'}</span></div>
          <div class="popup-row"><span class="popup-label">Proceso</span><span class="popup-val">${p.PROCESO||'—'}</span></div>
          <div class="popup-row"><span class="popup-label">Estado</span><span class="popup-val">${p.ESTADO_LU||'—'}</span></div>
        </div>`, { maxWidth: 320 });
      layer.on('mouseover', () => layer.setStyle({ fillOpacity: 0.55, weight: 3.5 }));
      layer.on('mouseout',  () => vivLayer?.resetStyle(layer));
    }
  }).addTo(map);

  if (shouldFit && filtered.length) map.fitBounds(vivLayer.getBounds(), { padding: [50, 50] });
}

function renderVivMejoramiento(shouldFit = false) {
  if (vivLayer) { map.removeLayer(vivLayer); vivLayer = null; }

  const sf = document.getElementById('viv-sub-filters');
  if (!vivMejoramientoData) {
    if (sf) sf.innerHTML = '<div class="filter-row"><span class="filter-row-label" style="color:#E74C3C;">⚠ Datos no disponibles</span></div>';
    return;
  }

  const feats   = vivMejoramientoData.features;
  // Deduplicate estados por color-category para evitar labels duplicadas
  const estadosSeen = new Map(); // label → original value
  feats.forEach(f => {
    const est = f.properties.ESTADO;
    if (!est) return;
    const lbl = getEstadoLabel(est);
    if (!estadosSeen.has(lbl)) estadosSeen.set(lbl, est);
  });
  const convocs = [...new Set(feats.map(f => f.properties.CONVOCATOR).filter(Boolean))].sort();

  if (sf) sf.innerHTML =
    `<div class="filter-row">
      <span class="filter-row-label">Estado</span>
      <button class="filter-btn ${vivEstado==='all'?'active':''}" data-viv-est="all">Todos</button>` +
      [...estadosSeen.entries()].map(([lbl, val]) => {
        const c = getVivMejColor(val);
        // active if vivEstado matches any feature with this label
        const isActive = vivEstado !== 'all' && getEstadoLabel(vivEstado) === lbl;
        return `<button class="filter-btn ${isActive?'active':''}" data-viv-est-lbl="${lbl}" style="border-color:${c};">${lbl}</button>`;
      }).join('') +
    `</div>
    <div class="filter-row">
      <span class="filter-row-label">Fuente</span>
      <button class="filter-btn ${vivProceso==='all'?'active':''}" data-viv-conv="all">Todas</button>` +
      convocs.map(c => {
        return `<button class="filter-btn ${vivProceso===c?'active':''}" data-viv-conv="${c}">${getConvocLabel(c)}</button>`;
      }).join('') +
    `</div>`;

  sf.querySelectorAll('[data-viv-est-lbl]').forEach(b => b.addEventListener('click', e => {
    sf.querySelectorAll('[data-viv-est-lbl]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active');
    // map label back to a filter: store the label, match at filter time
    vivEstado = e.target.dataset.vivEstLbl;
    renderVivMejoramiento();
  }));
  sf.querySelectorAll('[data-viv-est="all"]').forEach(b => b.addEventListener('click', e => {
    sf.querySelectorAll('[data-viv-est]').forEach(x => x.classList.remove('active'));
    sf.querySelectorAll('[data-viv-est-lbl]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); vivEstado = 'all'; renderVivMejoramiento();
  }));
  sf.querySelectorAll('[data-viv-conv]').forEach(b => b.addEventListener('click', e => {
    sf.querySelectorAll('[data-viv-conv]').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active'); vivProceso = e.target.dataset.vivConv; renderVivMejoramiento();
  }));

  const filtered = feats.filter(f => {
    const p = f.properties;
    const estadoMatch = vivEstado === 'all' || getEstadoLabel(p.ESTADO) === vivEstado;
    const convMatch   = vivProceso === 'all' || p.CONVOCATOR === vivProceso;
    return estadoMatch && convMatch;
  });

  const totalViv = filtered.reduce((s, f) => s + (parseInt(f.properties.CANT_MEJOR) || 0), 0);
  setKPI(filtered.length, 'Sectores activos', totalViv, 'Viviendas beneficiadas');

  document.getElementById('legend-dynamic').innerHTML = legendItems([
    ['Asignado',     VIV_MEJ_COLORS.ASIGNADO],
    ['En Ejecución', VIV_MEJ_COLORS.EJECUCION],
    ['Ejecutado',    VIV_MEJ_COLORS.EJECUTADO],
  ]);

  vivLayer = L.geoJSON({ type:'FeatureCollection', features: filtered }, {
    style: f => {
      const c = getVivMejColor(f.properties.ESTADO);
      return { color: c, weight: 2.5, fillColor: c, fillOpacity: 0.30, opacity: 0.9 };
    },
    onEachFeature: (f, layer) => {
      const p = f.properties;
      const c = getVivMejColor(p.ESTADO);
      const cant = parseInt(p.CANT_MEJOR) || 0;
      const pct  = totalViv ? Math.round(cant / totalViv * 100) : 0;
      layer.bindPopup(`
        <div style="min-width:240px;">
          <div class="popup-title" style="color:${c};">🏠 ${p.NOMBRE_LOC||'—'}</div>
          <div class="popup-row"><span class="popup-label">Mejoramientos</span><span class="popup-val" style="color:${c};font-size:18px;font-weight:800;">${cant}</span></div>
          <div class="popup-row"><span class="popup-label">% del total</span><span class="popup-val">${pct}%</span></div>
          <div class="popup-row"><span class="popup-label">Estado</span><span class="popup-val">${getEstadoLabel(p.ESTADO)}</span></div>
          <div class="popup-row"><span class="popup-label">Fuente</span><span class="popup-val" style="white-space:normal;max-width:140px;">${getConvocLabel(p.CONVOCATOR)||'—'}</span></div>
        </div>`, { maxWidth: 300 });
      layer.on('mouseover', () => layer.setStyle({ fillOpacity: 0.58, weight: 3.5 }));
      layer.on('mouseout',  () => vivLayer?.resetStyle(layer));
    }
  }).addTo(map);

  if (shouldFit && filtered.length) map.fitBounds(vivLayer.getBounds(), { padding: [50, 50] });
}

// ── RENDER PRINCIPAL ─────────────────────────────────────────────────────────
function renderMapData() {
  // Limpiar vivLayer al salir del modo vivienda
  if (vivLayer && currentDataMode !== 'vivienda') {
    map.removeLayer(vivLayer);
    vivLayer = null;
  }
  // MECAL solo en equipamientos
  if (mecalLayer) {
    currentDataMode === 'equipamientos' ? mecalLayer.addTo(map) : map.removeLayer(mecalLayer);
  }

  switch (currentDataMode) {
    case 'infraestructura': renderInfraestructura(); break;
    case 'seguridad':       renderSeguridad();       break;
    case 'equipamientos':   renderEquipamientos();   break;
    case 'ambiente':        renderAmbiente();         break;
    case 'vivienda':        renderVivienda();         break;
  }
  syncHeatmapUI();
}

// ── CARGA INICIAL ────────────────────────────────────────────────────────────
async function initDynamicMap() {
  _data = await DataService.load('../data/');

  // Perímetro
  globalPerimetro = DataService.getPerimetro(_data.poly);
  const perimeterLayer = L.geoJSON(globalPerimetro, { style: { color: '#E91E8C', weight: 4, fill: false } }).addTo(map);
  map.fitBounds(perimeterLayer.getBounds(), { padding: [20, 20] });

  // Polígonos de obra
  const areasLayer = L.layerGroup().addTo(map);
  const polyColors = ['#F1C40F', '#E67E22', '#4CAF77', '#9B59B6'];
  let ci = 0;
  _data.poly.features.forEach(f => {
    if (f.properties.Name !== 'Perimetro Proyecto') {
      L.geoJSON(f, { style: { color: polyColors[ci++ % polyColors.length], weight: 2, fillOpacity: 0.3 } })
        .bindTooltip(`<b>Polígono de Obra:</b><br>${f.properties.Name}`).addTo(areasLayer);
    }
  });

  // Corredor hídrico
  const tramosLayer = L.geoJSON(_data.tramos, { style: { color: '#00BCD4', weight: 4, opacity: 0.9 } })
    .bindTooltip('<b>Corredor Hídrico</b>').addTo(map);

  // ── Comunas (capa base permanente) ──────────────────────────────────────
  try {
    const comRes  = await fetch('../data/territorio/COMUNAS_PULMON.geojson');
    const comRaw  = await comRes.json();
    const comData = reprojectGeoJSONToWGS84(comRaw);
    comunasLayer  = L.geoJSON(comData, {
      style: { color: '#003087', weight: 2.2, fillColor: '#64B5F6', fillOpacity: 0.12, opacity: 0.95 },
      onEachFeature: (f, layer) => {
        const name = f.properties.nombre || `Comuna ${f.properties.comuna}`;
        layer.bindTooltip(name, { permanent: false, className: 'comuna-tooltip', direction: 'center' });
      }
    }).addTo(map);
  } catch(e) { console.warn('Comunas no disponibles:', e); }

  map.addLayer(clusters);

  // ── Cargar datasets en paralelo (excepto árboles - lazy) ──────────────
  const loads = [
    fetch('../data/seguridad/hurtos/IND_HURTOS_2023_2025_PULMON_GeoJson.geojson').then(r=>r.json())
      .then(g => { hurtosData = g.features;
        const pts = hurtosData.map(f => [f.geometry.coordinates[1], f.geometry.coordinates[0], 0.6]);
        heatLayer = L.heatLayer(pts, { radius:20, blur:18, maxZoom:17, gradient:{0.2:'#1565C0',0.5:'#FFC300',1.0:'#C1272D'} });
      }).catch(e => console.warn('Hurtos:', e)),

    fetch('../data/seguridad/homicidios/HOMICIDIOS_2023_2025_PULMON.geojson').then(r=>r.json())
      .then(g => { homicidiosData = g.features; }).catch(e => console.warn('Homicidios:', e)),

    fetch('../data/seguridad/violencia/VIOLENCIA_INTRAFAMILIAR_2023_2025_PULMON.geojson').then(r=>r.json())
      .then(g => { vifData = g.features; }).catch(e => console.warn('VIF:', e)),

    fetch('../data/seguridad/violencia/VBG_2025_PULMON.geojson').then(r=>r.json())
      .then(g => { vbgData = g.features; }).catch(e => console.warn('VBG:', e)),

    fetch('../data/equipamientos/Sedes_educativas_oficiales_PULMON_1K.geojson').then(r=>r.json())
      .then(g => { sedesData = g.features; }).catch(e => console.warn('Sedes:', e)),

    fetch('../data/seguridad/institucional/CAI_MECAL_CALI_PULMON.geojson').then(r=>r.json())
      .then(g => { caiData = g.features; }).catch(e => console.warn('CAI:', e)),

    fetch('../data/seguridad/institucional/Estaciones_MECAL_PULMON.geojson').then(r=>r.json())
      .then(g => {
        mecalLayer = L.geoJSON(g, {
          style: { color: '#E67E22', weight: 2, fillColor: '#E67E22', fillOpacity: 0.08, dashArray: '5,5' },
          onEachFeature: (f, layer) => layer.bindTooltip(`<b>${f.properties.ESTACION||'Estación MECAL'}</b>`)
        });
      }).catch(e => console.warn('MECAL:', e)),

    fetch('../data/vivienda/INTERV_AHDI_LEG_URBA_PULMON.geojson').then(r=>r.json())
      .then(g => { vivLegalizacionData = reprojectGeoJSONToWGS84(g); }).catch(e => console.warn('Vivienda AHDI:', e)),

    fetch('../data/vivienda/INTERV_MEJOR_VIV_25_26_PULMON.geojson').then(r=>r.json())
      .then(g => { vivMejoramientoData = reprojectGeoJSONToWGS84(g); }).catch(e => console.warn('Vivienda Mejoramiento:', e)),
  ];
  await Promise.allSettled(loads);

  // ── Control de capas ─────────────────────────────────────────────────────
  L.control.layers(null, {
    '📍 Puntos':            clusters,
    '🟣 Límite del Pulmón': perimeterLayer,
    '💧 Corredor Hídrico':  tramosLayer,
    '🏘 Comunas':           comunasLayer,
    '🟩 Áreas de Proyecto': areasLayer,
  }, { position: 'topright' }).addTo(map);

  renderMapData();
}

// ── HEATMAP TOGGLE ───────────────────────────────────────────────────────────
window.toggleHeatmap = function() {
  if (!heatLayer || !shouldShowHeatmapControls()) return;
  heatVisible = !heatVisible;
  heatVisible ? heatLayer.addTo(map) : map.removeLayer(heatLayer);
  syncHeatmapUI();
};

// ── LISTENERS: MODO PRINCIPAL ────────────────────────────────────────────────
document.querySelectorAll('#filter-data-mode .filter-btn').forEach(btn => {
  btn.addEventListener('click', e => {
    document.querySelectorAll('#filter-data-mode .filter-btn').forEach(x => x.classList.remove('active'));
    e.target.classList.add('active');
    currentDataMode = e.target.dataset.datamode;
    activeFilter = 'all'; activeEstado = 'all'; currentMode = 'ups';
    secSubMode = 'hurtos'; secAño = 'all'; secTipo = 'all'; secComuna = 'all';
    eqTipo = 'all'; ambEstado = 'all'; ambComuna = 'all';
    vivSubMode = 'legalizacion'; vivAño = 'all'; vivProceso = 'all'; vivEstado = 'all';
    renderMapData();
  });
});

document.getElementById('btn-reset').addEventListener('click', () => {
  activeFilter = 'all'; activeEstado = 'all'; currentMode = 'ups';
  secAño = 'all'; secTipo = 'all'; secComuna = 'all';
  eqTipo = 'all'; ambEstado = 'all'; ambComuna = 'all';
  vivAño = 'all'; vivProceso = 'all'; vivEstado = 'all';
  renderMapData();
});

const btnFiltersToggle = document.getElementById('btn-filters-toggle');
if (btnFiltersToggle) {
  btnFiltersToggle.addEventListener('click', () => setFiltersPanelOpen(!filtersPanelOpen));
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && filtersPanelOpen) setFiltersPanelOpen(false);
});

document.addEventListener('click', e => {
  if (!filtersPanelOpen) return;
  const panel = document.getElementById('filters-panel');
  const bar = document.getElementById('filter-bar');
  if (panel?.contains(e.target) || bar?.contains(e.target)) return;
  setFiltersPanelOpen(false);
});

setFiltersPanelOpen(false);
initDynamicMap();
