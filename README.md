# Proyecto ITT — Pulmón de Oriente

Aplicación web estática para visualización territorial e índice ITT (Índice de Transformación Territorial).
Sin framework ni build step: HTML, CSS y JavaScript vanilla. Motor de cálculo en Python puro con extracción automática desde fuentes GIS, Excel y GeoTIFF.

---

## Stack técnico

| Librería | Versión | Uso |
|---|---|---|
| Leaflet.js | 1.9.4 | Renderizado del mapa interactivo |
| Leaflet.MarkerCluster | 1.5.3 | Agrupación de puntos en mapa |
| Leaflet.heat | 0.2.0 | Heatmap de incidentes |
| Chart.js | 4.4.0 | Gráficos ITT, series, radar, gauge |
| Turf.js | 6 | Operaciones geoespaciales en cliente |
| proj4.js | 2.11.0 | Reproyección CRS en cliente (MAGNA-SIRGAS → WGS84) |
| georaster | 1.6.0 | Parseo de GeoTIFF en navegador |
| georaster-layer-for-leaflet | 3.10.0 | Renderizado de raster sobre Leaflet con máscara de polígono |
| Python 3.11+ | — | Motor de cálculo ITT |
| tifffile + numpy | — | Lectura y procesamiento de GeoTIFF (NDVI) |
| zipfile + xml | stdlib | Lectura directa de `.xlsx` sin dependencias pesadas |

---

## Estructura del repositorio

```
PoryectoITT/
├── index.html
├── paginas/
│   ├── pulmon_oriente_impacto_v2.html       # Dashboard ITT principal
│   ├── pulmon_oriente_mapa_v2.html           # Mapa interactivo multimodo
│   ├── pulmon_oriente_seguridad.html         # Panel de seguridad y cohesión social
│   └── pulmon_oriente_metodologia.html       # Metodología y fórmula ITT
├── assets/
│   ├── css/
│   │   ├── informe.css                       # Variables :root y componentes base
│   │   ├── mapa.css                          # Estilos mapa, filtros, leyenda
│   │   └── itt.css                           # Estilos módulo ITT
│   └── js/
│       ├── mapa.js                           # Lógica completa del mapa interactivo
│       └── services/
│           └── dataService.js                # Carga y caché de datos GeoJSON
├── data/
│   ├── indices/
│   │   ├── itt_pulmon.json                   # Fuente de verdad ITT (último período)
│   │   ├── itt_pulmon_trimestral.json         # Serie trimestral completa
│   │   ├── itt_pulmon_semestral.json          # Serie semestral agregada
│   │   └── indicadores_manuales.json          # Valores manuales (fallback)
│   ├── NVDI/                                 # GeoTIFF NDVI (Sentinel-2 / Copernicus)
│   ├── territorio/                           # GeoJSON perímetro y comunas (reproyectados)
│   ├── seguridad/
│   │   ├── comparendos/                      # GeoJSON comparendos (SIEDCO)
│   │   └── siniestros/                       # GeoJSON accidentalidad vial
│   ├── movilidad/                            # GeoJSON siniestros movilidad
│   ├── vivienda/                             # GeoJSON AHDI (EPSG:6249)
│   ├── infraestructura/                      # GeoJSON obras y contratos
│   ├── equipamientos/                        # GeoJSON equipamientos urbanos
│   ├── ambiente/                             # GeoJSON árboles y zonas verdes
│   └── excel/
│       ├── educacion/                        # Matrícula, deserción, repitencia
│       ├── movilidad/                        # Velocidades Waze for Cities + UsosEstacionesComuna14.xlsx (MIO)
│       ├── vivienda/                         # AHDI intervención por año
│       ├── bienestar/                        # Vulnerabilidad activa por comuna
│       └── deporte/                          # escenarios-deportivos.csv + secretaria_deporte_v2.xlsx
├── scripts/
│   ├── calcular_itt.py                       # Motor de cálculo ITT
│   └── excel_to_json.py                      # Conversión Excel → JSON (util)
└── docs/
    └── CONTEXTO_TECNICO_ITT_PULMON.md        # Referencia técnica completa
```

---

## Modelo ITT

### Fórmula y pesos

```
ITT = 0.30 × I_Seg  +  0.25 × I_Mov  +  0.20 × I_Ent  +  0.13 × I_EyD  +  0.12 × I_Coh
```

| Dimensión | Peso | Indicadores |
|---|---:|---:|
| Seguridad | 30% | 2 |
| Movilidad | 25% | 4 |
| Entorno Urbano | 20% | 3 |
| Educación y Desarrollo | 13% | 5 |
| Cohesión Social | 12% | 3 |
| **Total** | **100%** | **17** |

### Normalización de indicadores

Cada indicador se normaliza a escala 0–100:

```
score = clamp((valor - ref_min) / (ref_max - ref_min) × 100, 0, 100)
```

Para indicadores inversos (más es peor), la escala se invierte antes de aplicar la fórmula.
Los indicadores de conteo por período escalan `ref_min` y `ref_max` proporcionalmente al número de trimestres del lapso (`ref_factor`).

### Clasificación de niveles

| Rango | Nivel |
|---|---|
| 0 – 40 | Nivel 1 · Emergencia |
| 40 – 60 | Nivel 2 · Consolidación |
| 60 – 80 | Nivel 3 · Avance |
| 80 – 100 | Nivel 4 · Transformación |

---

## Motor de cálculo (`calcular_itt.py`)

### Fuentes de datos soportadas

El motor combina tres tipos de extracción automática:

**GeoJSON / GIS (`gis_tipo: conteo_periodo`)**
- Lee archivos `.geojson` o directorios de features desde `data/`
- Filtra por campo de fecha dentro del período activo
- Aplica filtros adicionales por campo (`gis_filtro`) para subcategorías específicas
- Soporta lapsos trimestral, semestral y anual con escala proporcional de referencias

**Excel nativo (zipfile + xml)**
- Lectura directa del formato `.xlsx` sin librerías de terceros pesadas
- `_leer_xlsx_sheet(path, nombre_hoja)`: extrae una hoja por nombre usando el mapeo `workbook.xml → rId → xl/worksheets/sheetN.xml`
- Shared strings resueltos desde `xl/sharedStrings.xml`
- Funciones específicas por fuente: velocidad de corredor, matrícula escolar, AHDI vivienda, vulnerabilidad por comuna

**GeoTIFF (`leer_ndvi_tif`)**
- Lee raster float32 comprimido LZW con `tifffile`
- Calcula NDVI medio sobre píxeles válidos (filtro `[-1.0, 1.0]`)
- Calcula área verde en m² contando píxeles con NDVI ≥ 0.20, ajustando área de píxel por latitud (proyección cónica)

### Sistema de lapsos

El script genera tres archivos JSON independientes por lapso:

| Lapso | Archivo | Agrupación |
|---|---|---|
| trimestral | `itt_pulmon_trimestral.json` | Por trimestre (T1–T4) |
| semestral | `itt_pulmon_semestral.json` | Por semestre (S1–S2) |
| anual | `itt_pulmon_anual.json` (si aplica) | Por año |

La función `_lapso_de_periodo()` determina el lapso desde el string de período y `_periodo_sort_key()` garantiza orden cronológico correcto en la serie temporal.

### Jerarquía de valores

Para cada indicador el motor busca en este orden:
1. Fuente GIS automática (si `gis_dir` está configurado)
2. Función de extracción Excel específica
3. Valor manual desde `data/indices/indicadores_manuales.json`
4. Valor por defecto del indicador

---

## Módulos frontend

### `pulmon_oriente_impacto_v2.html` — Dashboard ITT

Lee `data/indices/itt_pulmon_trimestral.json` y renderiza todo dinámicamente:
- KPI strip animado con métricas clave del período
- Alertas automáticas detectadas desde campo `nota_real` del JSON
- Gauge ITT global + radar de dimensiones con toggle Trimestral / Semestral / Anual
- Gráfico de contribución ponderada por dimensión (`score × peso`) con insight corregido (mayor potencial real)
- Gráfico de evolución temporal con toggle individual por dimensión; Entorno Urbano y Educación con línea escalonada (dato anual)
- Tabs de indicadores por dimensión con estado oficial/estimado
- `calidad_dato` derivado automáticamente en el frontend según `oficial` de cada indicador
- Gráfica de hurtos agrupada por trimestre (T1–T4 × 2023/2024/2025) — sólo Seguridad
- Gráfica VIF anual (2023/2024/2025) con alerta visual — sólo Cohesión Social
- Gráfica de score de Movilidad comparativo por trimestre con insight ejecutivo
- Sección 04: Seguridad vs Movilidad · Comparativo por Período (barras agrupadas, reemplaza ranking de barrios)

### `pulmon_oriente_mapa_v2.html` — Mapa interactivo

6 modos de vista activados desde la barra de filtros:
- **Infraestructura** — frentes de obra y contratos
- **Seguridad** — comparendos SIEDCO con filtros por categoría (sin filtro de comuna)
- **Movilidad** — siniestros viales con capas de lesionados y muertes
- **Equipamientos** — colegios, CAI, salud, estaciones MECAL
- **Ambiente** — árboles, zonas verdes y capa NDVI Sentinel-2 (recortada al polígono Pulmón)
- **Vivienda** — polígonos AHDI (legalización) y sectores de mejoramiento

La capa NDVI se activa bajo demanda en modo Ambiente: carga el GeoTIFF vía `fetch()`, lo parsea con `parseGeoraster()` y lo renderiza con `GeoRasterLayer` usando el perímetro del Pulmón como máscara.

### `pulmon_oriente_seguridad.html` — Panel seguridad y cohesión social

Series por tipo de evento, comparativo por dimensión ITT, narrativa dinámica por período.
Todas las dimensiones con fuentes operativas reales: GeoJSON + Excel oficial.

### `pulmon_oriente_metodologia.html` — Metodología ITT

Fórmula de cálculo, pesos por dimensión, normalización y clasificación de niveles.

---

## Capa de datos

### Reproyección CRS en cliente (`mapa.js`)

Los GeoJSON de vivienda y comunas vienen en sistemas proyectados locales.
`mapa.js` los convierte a WGS84 en tiempo de carga usando `proj4.js`:

```
ESRI:103599  →  comunas (MAGNA-SIRGAS Origen Único)
EPSG:6249    →  vivienda (MAGNA-SIRGAS Colombia West)
```

La función `reprojectGeoJSONToWGS84()` detecta el CRS desde `geojson.crs.properties.name`.

### `data/indices/itt_pulmon.json` — Estructura del JSON

```json
{
  "meta": {
    "territorio", "version", "periodo", "lapso",
    "cobertura_datos", "fuentes_activas", "fuentes_total", "nota"
  },
  "itt_global": {
    "score", "score_anterior", "variacion",
    "clasificacion", "rango", "periodo_comparacion"
  },
  "dimensiones": [{
    "id", "nombre", "peso", "score", "score_anterior",
    "variacion", "cobertura", "calidad_dato", "color", "icono",
    "indicadores": [{
      "nombre", "valor", "unidad", "tendencia",
      "fuente", "oficial", "nota_real"
    }]
  }],
  "serie_temporal": [{ "periodo", "itt", "seguridad", "movilidad", ... }],
  "barrios": [{ "nombre", "itt", "poblacion", "proyectos" }]
}
```

---

## Scripts de mantenimiento

### Cálculo ITT

```bash
# Calcular para un período trimestral
python scripts/calcular_itt.py --periodo 2025-T4

# Calcular con versión específica
python scripts/calcular_itt.py --periodo 2025-T4 --version preliminar

# Generar plantilla de manuales (primera vez)
python scripts/calcular_itt.py --generar-manuales

# Salida custom opcional
python scripts/calcular_itt.py --periodo 2025-T4 --output data/indices/custom.json
```

Salidas: `data/indices/itt_pulmon.json` (último período) + `itt_pulmon_trimestral.json` / `itt_pulmon_semestral.json`

### Conversión Excel → JSON (util)

```bash
python scripts/excel_to_json.py
python scripts/excel_to_json.py data/excel/archivo.xlsx
```

---

## Ejecución local

```bash
python -m http.server 8000
```

Abrir: `http://localhost:8000/`

---

## Flujo de actualización periódica

1. Depositar nuevas fuentes en `data/` (GeoJSON, Excel, TIF según corresponda).
2. Si hay indicadores manuales a actualizar, editar `data/indices/indicadores_manuales.json`.
3. Ejecutar `python scripts/calcular_itt.py --periodo YYYY-TX` para recalcular los JSON.
4. Verificar en navegador: Dashboard ITT, Mapa, Panel Seguridad.
5. Confirmar consola sin errores JS (carga GeoJSON, reproyección CRS, fetch NDVI).
6. Commit.

---

## Referencia técnica completa

Ver `docs/CONTEXTO_TECNICO_ITT_PULMON.md` para:
- Matriz de indicadores por dimensión con fuentes y metodología
- Documentación de capas GIS y sistemas de coordenadas
- Decisiones de diseño del motor de cálculo
- Historial de cambios por versión
- Brechas técnicas pendientes

Ver `docs/SUSTENTO_EMPIRICO_PARAMETROS_ITT.md` para:
- Evidencia empírica de soporte para cada ref_min / ref_max
- Clasificación por calidad de serie: serie real (12 trim) · serie anual por diseño · dato débil
- Peso metodológico de cada grupo dentro del ITT (~35% / ~11% / ~54%)
- Hoja de ruta de fortalecimiento empírico

---

## Notas de repositorio

- `.gitignore` excluye documentos locales de contexto que no deben versionarse.
- Si un archivo ya estaba trackeado antes de ignorarlo, retirarlo con `git rm --cached`.
