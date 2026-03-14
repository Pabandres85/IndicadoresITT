# Proyecto ITT - Pulmon de Oriente

Aplicacion web estatica para visualizacion territorial e indice ITT (Indice de Transformacion Territorial).
Sin framework ni build step: HTML, CSS y JavaScript vanilla.

---

## Stack tecnico

| Libreria | Version | Uso |
|---|---|---|
| Leaflet.js | 1.9.4 | Renderizado del mapa interactivo |
| Leaflet.MarkerCluster | 1.5.3 | Agrupacion de puntos en mapa |
| Leaflet.heat | 0.2.0 | Heatmap de hurtos |
| Chart.js | 4.4.0 | Graficos ITT, series, radar, gauge |
| Turf.js | 6 | Operaciones geoespaciales en cliente |
| proj4.js | 2.11.0 | Reproyeccion CRS en cliente (MAGNA-SIRGAS → WGS84) |
| Python 3.11+ | — | Calculo ITT (Opcion C: GeoJSON + manuales JSON) |
| openpyxl | — | Conversion Excel → JSON (`excel_to_json.py`) |

---

## Estructura del repositorio

```
PoryectoITT/
├── index.html
├── paginas/
│   ├── pulmon_oriente_impacto_v2.html       # Dashboard ITT
│   ├── pulmon_oriente_mapa_v2.html           # Mapa interactivo
│   ├── pulmon_oriente_informe-v2.html        # Informe de inversion
│   ├── pulmon_oriente_metodologia.html       # Metodologia ITT
│   └── pulmon_oriente_seguridad.html         # Panel seguridad
├── assets/
│   ├── css/
│   │   ├── informe.css                       # Variables :root y componentes base
│   │   ├── mapa.css                          # Estilos mapa, filtros, leyenda
│   │   └── itt.css                           # Estilos modulo ITT
│   └── js/
│       ├── mapa.js                           # Logica completa del mapa
│       └── services/
│           └── dataService.js                # Carga y cache de datos
├── data/
│   ├── indices/
│   │   └── itt_pulmon.json                   # Fuente de verdad ITT para frontend
│   ├── vivienda/                             # GeoJSON vivienda (EPSG:6249)
│   ├── territorio/                           # GeoJSON comunas (ESRI:103599)
│   ├── seguridad/                            # Puntos SIEDCO (WGS84)
│   ├── infraestructura/                      # Puntos obras (WGS84)
│   ├── equipamientos/                        # Puntos equipamientos (WGS84)
│   └── ambiente/                             # Puntos arboles/zonas verdes (WGS84)
├── scripts/
│   ├── calcular_itt.py                       # Motor de calculo ITT
│   └── excel_to_json.py                      # Conversion Excel → JSON
└── docs/
    └── CONTEXTO_TECNICO_ITT_PULMON.md        # Referencia tecnica completa
```

---

## Modulos frontend

### `pulmon_oriente_impacto_v2.html` — Dashboard ITT
Lee `data/indices/itt_pulmon.json` y renderiza todo dinamicamente:
- KPI strip animado (countUp) con metricas clave
- Alertas automaticas detectadas desde campo `nota_real` del JSON
- Gauge ITT global + radar de dimensiones (actual vs anterior)
- Grafico de contribucion ponderada por dimension (`score × peso`)
- Grafico de evolucion temporal con toggle por dimension
- Tabs de indicadores por dimension con serie trimestral de hurtos
- Ranking de barrios con sort dinamico (ITT / Poblacion / Proyectos)
- Seccion de calidad y madurez del dato

### `pulmon_oriente_mapa_v2.html` — Mapa interactivo
5 modos de vista activados desde la barra de filtros:
- **Infraestructura** — frentes de obra y contratos
- **Seguridad** — puntos SIEDCO + heatmap de hurtos
- **Equipamientos** — colegios, CAI, salud, estaciones MECAL
- **Ambiente** — arboles y zonas verdes
- **Vivienda** — poligonos AHDI (legalizacion) y sectores de mejoramiento

Filtros organizados en filas etiquetadas por modo; panel colapsable.

### `pulmon_oriente_informe-v2.html` — Informe de inversion
Analitica de proyectos e inversion por secretaria y periodo.

### `pulmon_oriente_metodologia.html` — Metodologia ITT
Formula de calculo, pesos por dimension, normalizacion y clasificacion de niveles.

### `pulmon_oriente_seguridad.html` — Panel seguridad
Series por tipo de delito, comparativo comunas, indicadores SIEDCO.

---

## Capa de datos

### `assets/js/services/dataService.js`
- Carga de fuentes base por modo del mapa
- Cache en memoria y `sessionStorage`
- Utilidades de filtrado espacial
- Normalizacion de categorias y colores

### Reproyeccion CRS en cliente (`mapa.js`)
Los GeoJSON de vivienda y comunas vienen en sistemas proyectados locales.
`mapa.js` los convierte a WGS84 en tiempo de carga usando `proj4.js`:

```
ESRI:103599  →  comunas (MAGNA-SIRGAS Origen Unico)
EPSG:6249    →  vivienda (MAGNA-SIRGAS Colombia West)
```

La funcion `reprojectGeoJSONToWGS84()` detecta el CRS del campo `geojson.crs.properties.name`
y convierte coordenadas antes de pasarlas a Leaflet.

### `data/indices/itt_pulmon.json`
Fuente unica de verdad para el frontend ITT. Estructura:
```
{
  meta: { territorio, version, periodo, cobertura_datos, fuentes_activas, fuentes_total, nota },
  itt_global: { score, score_anterior, variacion, clasificacion, rango, periodo_comparacion },
  dimensiones: [ { id, nombre, peso, score, score_anterior, variacion, cobertura,
                   calidad_dato, indicadores: [...], hurtos_series?: {...} } ],
  serie_temporal: [ { periodo, itt, seguridad, entorno_urbano, movilidad, ... } ],
  barrios: [ { nombre, itt, poblacion, proyectos } ]
}
```

---

## Scripts de mantenimiento

### Calculo ITT

```bash
# Generar plantilla manual (primera vez)
python scripts/calcular_itt.py --generar-manuales

# Calcular para un periodo
python scripts/calcular_itt.py --periodo 2025-T4 --version preliminar

# Salida custom opcional
python scripts/calcular_itt.py --periodo 2025-T4 --output data/indices/custom.json
```

Salida principal: `data/indices/itt_pulmon.json`  
Archivos auxiliares: `data/indices/itt_historico.json` y `data/indices/indicadores_manuales.json`

Pesos configurados (alineados al perfil Pulmon de Oriente):

| Dimension | Peso |
|---|---:|
| Entorno Urbano | 0.30 |
| Seguridad | 0.20 |
| Movilidad | 0.20 |
| Desarrollo Social | 0.15 |
| Actividad Economica | 0.15 |

### Conversion Excel → JSON

```bash
python scripts/excel_to_json.py
python scripts/excel_to_json.py data/excel/archivo.xlsx
```

Requiere: `pip install openpyxl`

---

## Ejecucion local

Levantar servidor estatico desde la raiz del proyecto:

```bash
python -m http.server 8000
```

Abrir: `http://localhost:8000/`

---

## Flujo de actualizacion

1. Actualizar fuentes en `data/` (GeoJSON, JSON, Excel).
2. Si hay indicadores nuevos, ejecutar `calcular_itt.py` para recalcular `itt_pulmon.json`.
3. Verificar vistas clave en el navegador: ITT, Mapa, Informe, Seguridad.
4. Confirmar consola sin errores JS (especialmente reproyeccion CRS y carga de datos).
5. Commit de cambios.

---

## Referencia tecnica completa

Ver `docs/CONTEXTO_TECNICO_ITT_PULMON.md` para:
- Matriz de pesos modelo vs implementacion
- Matriz de indicadores por dimension con fuentes y notas
- Documentacion de capas GIS y CRS
- Historial de cambios por sesion
- Brechas tecnicas pendientes

---

## Notas de repositorio

- `.gitignore` excluye documentos locales de contexto que no deben versionarse.
- Si un archivo ya estaba trackeado antes de ignorarlo, retirarlo con `git rm --cached`.
