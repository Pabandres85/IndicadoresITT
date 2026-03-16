# Contexto Tecnico ITT - Pulmon de Oriente

Documento interno para alinear metodologia, codigo y tablero del ITT en Pulmon de Oriente.

---

## VERSION OFICIAL VIGENTE — v7 calibrada (2026-03-15)

> **METODOLOGIA CONGELADA. Esta es la version oficial de referencia para presentaciones, comites tecnicos y rendicion de cuentas.**
>
> - ITT de referencia: **46.9/100** · Nivel 2 · Consolidacion · 2025-T4
> - Los valores anteriores 72.5/71.7/72.1/66.4 corresponden a versiones pre-calibracion con rangos de diseno no anclados a datos historicos reales. **No deben usarse en presentaciones publicas.**
> - Cambios de `ref_min`/`ref_max` solo por ventana anual o decision de comite tecnico — no en caliente.

### Tabla comparativa antes vs despues de calibracion (2025-T4)

| Dimension | ITT pre-calibracion | ITT v7 calibrado | Diferencia | Principal causa |
|---|---:|---:|---:|---|
| Seguridad | 72.8 | 53.6 | -19.2 | ref_max homicidios 130→50; hurtos 500→450 |
| Movilidad | 81.2 | 35.0 | -46.2 | ref_max siniestralidad 260→80; lesionados 180→65; muertes 30→10; velocidad retirada del modelo |
| Entorno Urbano | 70.0 | 52.7 | -17.3 | ref_max area verde 300k→3M m² (correccion critica) |
| Educacion y Desarrollo | 61.0 | 61.0 | 0.0 | Sin cambio (refs normativos validos) |
| Cohesion Social | 70.0 | 57.6 | -12.4 | ref_max rinas 220→160; VIF ajuste leve |
| **ITT Global** | **72.5** | **46.9** | **-25.6** | Recalibracion con 12 trimestres de data real + retiro de velocidad corredor |

> El cambio de -19.8 pts NO representa deterioro real del territorio. Representa la correccion de rangos de normalizacion que estaban inflados respecto a la realidad historica del poligono. El territorio sigue igual; la escala de medicion ahora es correcta.

### Rangos operacionales provisionales (sin serie historica)

Los siguientes indicadores usan rangos de diseno mientras se acumula serie historica propia. Deben citarse como **"rango operativo provisional"** en contextos tecnicos:

| Indicador | Rango provisional | Pendiente para anclaje real |
|---|---|---|
| Velocidad corredor | [12, 32] km/h | Acumular Excel Waze por año |
| Area verde neta | [500k, 3M] m² | Procesar TIF de años anteriores |
| Deficit AHDI | [0, 100] % | Definir si mide cobertura o resolucion real |
| Matricula escolar | [5k, 60k] est. | Excel 2023-2025 ya disponibles para recalibrar |
| Vulnerabilidad activa | [30, 160] p/1000 | Solicitar cortes anteriores a Sec. Bienestar |
| Aforo Villa del Lago | [1k, 7k] pers/mes | Pendiente dato oficial Sec. Deportes |

---

## 1) Alcance

Este documento resume:
- Que define el modelo metodologico (`Modelo_Medicion_Apuestas_Cali_v4.docx`)
- Que calcula hoy el motor (`scripts/calcular_itt.py`)
- Que publica hoy el tablero (`data/indices/itt_pulmon.json`)
- Que visualiza el frontend (mapa + pagina ITT + informe)

Objetivo: tener una referencia tecnica unica para decisiones de implementacion.

---

## 2) Referencias revisadas

- `Modelo_Medicion_Apuestas_Cali_v4.docx` (secciones 7.3, 7.4, 8, 14.2)
- `scripts/calcular_itt.py`
- `data/indices/itt_pulmon.json`
- `data/vivienda/INTERV_AHDI_LEG_URBA_PULMON.geojson` (nuevo)
- `data/vivienda/INTERV_MEJOR_VIV_25_26_PULMON.geojson` (nuevo)
- `assets/js/mapa.js`
- `paginas/pulmon_oriente_impacto_v2.html`
- `docs/SUSTENTO_EMPIRICO_PARAMETROS_ITT.md` — Consolidado técnico con evidencia de soporte para ref_min/ref_max por indicador

---

## 3) Estado actual de arquitectura ITT

- Motor de calculo: Python (`scripts/calcular_itt.py`)
- Normalizacion: Min-Max por indicador, con soporte `inverso=True` para indicadores donde menor es mejor
- Agregacion por dimension: promedio simple de indicadores disponibles
- Agregacion global: suma ponderada por dimension
- Publicacion: JSON estatico (`data/indices/itt_pulmon.json`) consumido por frontend
- Cobertura datos (estado actual Opcion C): 100% (17/17 indicadores) — 16 reales + 1 manual (aforo)

---

## 4) Matriz de pesos (modelo vs implementacion)

**Estado al 2026-03-14 v4: PERFIL OPERATIVO PULMON DE ORIENTE**

| Dimension               | Perfil Pulmon (doc 7.4) | Script actual | JSON actual | Estado   |
|---|---:|---:|---:|---|
| Seguridad               | 0.30                    | **0.30**      | **0.30**    | Alineado |
| Movilidad               | 0.25                    | **0.25**      | **0.25**    | Alineado |
| Entorno Urbano          | 0.20                    | **0.20**      | **0.20**    | Alineado |
| Educacion y Desarrollo  | 0.13                    | **0.13**      | **0.13**    | Alineado |
| Cohesion Social         | 0.12                    | **0.12**      | **0.12**    | Alineado |
| **TOTAL**               | **1.00**                | **1.00**      | **1.00**    | OK       |

Formula operativa: `ITT = 0.30*I_Seg + 0.25*I_Mov + 0.20*I_Ent + 0.13*I_EyD + 0.12*I_Coh`

---

## 5) Matriz de indicadores por dimension

**Corte 2025-T4 · ITT Global: 46.9 · Nivel 2 · Consolidacion**
*(refs recalibrados con serie historica real 12 trimestres — ver seccion 15.6)*

### Seguridad (peso 0.30 | score 53.6 | cobertura 100%)

| Indicador | Valor | ref_min | ref_max | Score | Fuente efectiva | Oficial |
|---|---|---:|---:|---:|---|---|
| Homicidios (trimestral) | 36 casos | 5 | 50 | 31.1 | GeoJSON SIEDCO | Si |
| Hurtos (trimestral) | 260 casos | 200 | 450 | 76.0 | GeoJSON SIEDCO | Si |

Serie temporal hurtos: 12 trimestres 2023-T1 a 2025-T4 (campo `hurtos_series` en JSON).

### Movilidad (peso 0.25 | score 35.0 | cobertura 100%)

| Indicador | Valor | ref_min | ref_max | Score | Fuente efectiva | Oficial |
|---|---|---:|---:|---:|---|---|
| Siniestralidad vial | 63 eventos | 30 | 80 | 34.0 | GeoJSON BD_SINIESTROS | Si |
| Accidentes con lesionados | 53 eventos | 20 | 65 | 26.7 | GeoJSON BD_SINIESTROS (Lesiones) | Si |
| Muertes en via | 6 casos | 1 | 10 | 44.4 | GeoJSON BD_SINIESTROS (Mortal) | Si |

> **Velocidad promedio del corredor (26.8 km/h)** retirada del modelo v7. Razón: dato único 2025 sin serie histórica — generaba score 74/100 que inflaba la dimensión sin respaldo empírico. Queda como dato de contexto. Se reintegrará cuando se acumulen cortes trimestrales Waze for Cities.

### Entorno Urbano (peso 0.20 | score 39.2 | cobertura 100%)

| Indicador | Valor | ref_min | ref_max | Score | Fuente efectiva | Oficial |
|---|---|---:|---:|---:|---|---|
| NDVI / cobertura vegetal | 0.20 (indice) | 0.15 | 0.65 | 10.0 | TIF ndvi_resultado.tif (media pixels validos) | Si |
| Area verde neta | 1.699.769 m² | 500.000 | 3.000.000 | 48.0 | TIF ndvi_resultado.tif (pixels NDVI >= 0.20) | Si |
| Deficit habitacional cualitativo | 46.4% pendiente | 0 | 100 | 53.6 | Excel AHDI / avance ponderado por etapa · corte 2025-T4 | Si |

Nota v7: NDVI y Area verde calculados sobre poligono completo del Pulmon. En v8 se recalcularan sobre sub-poligono ambiental (Charco Azul + El Pondaje). Ver seccion 16.

### Educacion y Desarrollo (peso 0.13 | score 56.0 | cobertura 100%)

| Indicador | Valor | ref_min | ref_max | Score | Fuente efectiva | Oficial |
|---|---|---:|---:|---:|---|---|
| Matricula escolar · Territorio Pulmon | 50.336 est. | 5.000 | 60.000 | 82.4 | Excel Indicadores_Sectoriales_2025.xlsx | Si |
| Desercion escolar · Territorio Pulmon | 4.3% | 1.0 | 10.0 | 63.3 | Excel Indicadores_Sectoriales_2025.xlsx | Si |
| Repitencia escolar · Territorio Pulmon | 8.4% | 1.0 | 15.0 | 47.1 | Excel Indicadores_Sectoriales_2025.xlsx | Si |
| Estudiantes por docente · Territorio Pulmon | 27.1 ratio | 18 | 40 | 58.6 | Excel Indicadores_Sectoriales_2025.xlsx | Si |
| Cobertura deportiva activa · Territorio Pulmon | 3.877 pers. registradas | 1.000 | 7.000 | ~48 | Secretaria de Deportes · Caracterizacion de Escenarios 2024 (proxy oficial) | Si |

Nota indicador deportivo: dato proxy — aforo directo de Villa del Lago no disponible. 3.877 = suma de deportistas en clubes (1.292) + estudiantes usando escenarios (2.585) en 25 escenarios de la Comuna 14, segun formulario oficial Sec. Deportes marzo 2024. No es conteo directo de asistencia.

### Cohesion Social (peso 0.12 | score 57.6 | cobertura 100%)

| Indicador | Valor | ref_min | ref_max | Score | Fuente efectiva | Oficial |
|---|---|---:|---:|---:|---|---|
| VIF trimestral | 105 casos | 60 | 200 | 67.9 | GeoJSON SIEDCO (patron VIF) | Si |
| Rinas / conflictividad | 127 casos | 20 | 160 | 23.6 | GeoJSON COMPARENDOS (agrupado=RIÑAS) | Si |
| Concentracion de vulnerabilidad activa | 54.1 p/1000 | 30 | 160 | 81.5 | Excel Bienestar / Caracterizacion Sub PyE 2025 (C13+C14) | Si |

**Resumen oficial/manual:** 17 indicadores con fuente verificable. 0 manuales sin respaldo. Cobertura 100%.

---

## 6) Que ya esta calculado y visualizado hoy

### Motor de calculo (`calcular_itt.py`)
- ITT global por formula ponderada (verificado, pesos alineados al perfil Pulmon 7.4)
- Subindice por dimension con cobertura
- Clasificacion por nivel (4 niveles: Emergencia, Consolidacion, Avance, Transformacion)

### Datos publicados (`data/indices/`)

Tres archivos JSON separados por lapso:
- `itt_pulmon_trimestral.json` — ultimo: 2025-T4 | ITT **46.9** · Nivel 2 · Consolidacion (-8.1 vs T3)
- `itt_pulmon_semestral.json` — ultimo: 2025-S2 | ITT **56.2** · Nivel 2 · Consolidacion
- `itt_pulmon_anual.json` — ultimo: 2025 | ITT **57.2** · Nivel 2 · Consolidacion
- `itt_pulmon.json` — copia del ultimo trimestral (compatibilidad hacia atras)

> Los tres lapsos dan valores distintos porque miden periodos de tiempo diferentes. El trimestral T4 refleja el peor trimestre del año (pico de homicidios y rinas). El semestral y anual promedian ese pico con trimestres mas estables. Ver seccion 15.7 para explicacion metodologica.

Cada JSON contiene:
- 5 dimensiones con score, score_anterior, variacion, peso, cobertura
- 17 indicadores con fuente, tendencia, oficial (bool) y nota_real donde aplica
- `serie_temporal` filtrada por lapso (solo T, solo S, o solo anuales)
- Serie hurtos: 12 trimestres 2023-2025 (campo `hurtos_series` en dimension Seguridad)
- Ranking de 8 barrios con ITT estimado, poblacion y proyectos

### Tablero de visualizacion

#### Pagina ITT (`paginas/pulmon_oriente_impacto_v2.html`)
- **KPI strip animado**: 6 metricas clave (ITT, hurtos, VIF, NDVI, desercion) con countUp animation
- **Alertas automaticas**: escanea `nota_real` con "ALERTA" + tendencia alza en Seguridad oficial
- **Gauge ITT Global**: semicirculo animado con insight de clasificacion y trazabilidad
- **Radar de dimensiones**: toggle propio Trimestral / Semestral / Anual (2 o 3 periodos superpuestos)
- **`calidad_dato` auto-derivado**: en frontend, segun `oficial` de cada indicador — no depende del JSON
- **Grafico de contribucion ponderada**: barras horizontales apiladas; insight con mayor contribucion y mayor potencial real
- **Grafico de evolucion temporal**: lineas con toggle individual; Entorno Urbano y Educacion con linea escalonada (dato anual)
- **Tabs de indicadores**: por dimension, con badges oficial/estimado/real
- **Hurtos agrupados por trimestre**: T1-T4 x 2023/2024/2025 — dentro de tab Seguridad
- **VIF anual**: 3 barras 2023/2024/2025 con alerta de tendencia — dentro de tab Cohesion Social
- **Score Movilidad comparativo**: barras agrupadas T1-T4 por año con insight ejecutivo — dentro de tab Movilidad
- **Seccion 04 — Seguridad vs Movilidad**: barras agrupadas por periodo, reemplaza ranking de barrios
- Todos los valores leidos de JSON — sin valores hardcodeados en HTML

#### Mapa interactivo (`paginas/pulmon_oriente_mapa_v2.html`)
- 6 modos de vista: Infraestructura · Seguridad · Equipamientos · Ambiente · Vivienda · **Movilidad** (nuevo)
- Panel de filtros con filas etiquetadas (filter-row) por modo
- Heatmap de hurtos (3.990 puntos SIEDCO 2023-2025)
- Capas base: calles / satelite / hibrido
- **NDVI overlay**: boton "Ver NDVI" en modo Ambiente — carga TIF con `georaster-layer-for-leaflet`, recortado al poligono del area con opcion `mask`
- **Modo Movilidad**: sub-modos Siniestros (693 eventos 2023-2025) y Comparendos (4.808 registros 2025)
- **Modo Seguridad**: 5 sub-modos — Hurtos · Homicidios · VIF · VBG · **Comparendos** (nuevo: 24.134 eventos 2023-2025, 4 tipos: Riñas/Armas/Sustancias/Desacato)

---

## 7) Capas de datos geoespaciales

| Archivo | CRS fuente | CRS final | Tipo | Descripcion |
|---------|-----------|-----------|------|-------------|
| `data/territorio/COMUNAS_PULMON.geojson` | ESRI:103599 | WGS84 | Poligono | Limites comunas en area Pulmon |
| `data/vivienda/INTERV_AHDI_LEG_URBA_PULMON.geojson` | EPSG:6249 | WGS84 | MultiPoligono | 6 poligonos legalizacion urbanistica AHDI |
| `data/vivienda/INTERV_MEJOR_VIV_25_26_PULMON.geojson` | EPSG:6249 | WGS84 | MultiPoligono | 8 sectores mejoramiento de vivienda |
| `data/seguridad/*.geojson` | WGS84 | WGS84 | Puntos | Hurtos, homicidios, VIF, VBG (SIEDCO) |
| `data/infraestructura/*.geojson` | WGS84 | WGS84 | Puntos | Frentes de obra, contratos |
| `data/equipamientos/*.geojson` | WGS84 | WGS84 | Puntos | Colegios, CAI, salud, MECAL |
| `data/ambiente/*.geojson` | WGS84 | WGS84 | Puntos | Arboles, zonas verdes |

### Reproyeccion en cliente (mapa.js)

Todos los GeoJSON con CRS proyectado se convierten a WGS84 en el cliente usando `proj4.js`:

```javascript
const PROJ_DEFS = {
  'ESRI:103599': '+proj=tmerc +lat_0=4 +lon_0=-73 +k=0.9992 +x_0=5000000 +y_0=2000000 +ellps=GRS80 +units=m +no_defs',
  'EPSG:3116':   '+proj=tmerc +lat_0=4.596200416667 +lon_0=-77.07750796388889 +k=1 +x_0=1000000 +y_0=1000000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs',
};
PROJ_DEFS['EPSG:6249'] = PROJ_DEFS['EPSG:3116']; // mismo perfil Colombia West, datum shift < 3m
```

La funcion `reprojectGeoJSONToWGS84(geojson)` detecta el CRS del campo `geojson.crs.properties.name` y reproyecta todas las coordenadas antes de pasarlas a Leaflet. Se aplica al cargar los datos (no al renderizar), almacenando el resultado ya en WGS84 en memoria.

---

## 8) Modo Vivienda en el mapa

### Sub-modo: Legalizacion Urbanistica (AHDI)

- Fuente: `INTERV_AHDI_LEG_URBA_PULMON.geojson`
- 6 MultiPoligonos, 11.71 ha totales
- Campos clave: `NOMBRE`, `BARRIOS_SE`, `AREA_HA`, `PORC_URBAN`, `ESTADO_LU`, `Ano_interv`, `PROCESO`
- Valores PROCESO: `"Con Radicacion"` (3), `"Proceso de Legalizacion"` (3)
- Filtros: Año (2024/2025) y Proceso
- Colores: `#FFC300` (Con Radicacion), `#6A1B9A` (Proceso de Legalizacion)

### Sub-modo: Mejoramiento de Vivienda (2025-2026)

- Fuente: `INTERV_MEJOR_VIV_25_26_PULMON.geojson`
- 8 MultiPoligonos, 157 viviendas totales
- Campos clave: `NOMBRE_LOC`, `CANT_MEJOR` (string), `CONVOCATOR`, `ESTADO`
- Valores ESTADO reales: `"ASIGNADO"` (5 sectores), `"EN EJECUCION / ASIGNADO"` (2), `"EN EJECUCION / EJECUTADO"` (1)
- Labels mostrados al usuario: `"Asignado"`, `"En Ejecucion"`, `"Ejecutado"` (funcion `getEstadoLabel()`)
- Valores CONVOCATOR: `"EMPRESTITO"`, `"CONVENIO MINISTERIO - EMPRESTITO"`
- Labels mostrados: `"Emprestito"`, `"Conv. Ministerio"` (funcion `getConvocLabel()`)
- Filtros: Estado (por label agrupado) y Fuente
- Colores: Asignado `#1565C0` · En Ejecucion `#E65100` · Ejecutado `#2E7D32`
- CANT_MEJOR almacenado como string — se convierte con `parseInt()` al acumular totales

### Logica de renderizado

```
renderVivienda()
  → renderVivSubMode(shouldFit=true)
    → renderVivLegalizacion(shouldFit) | renderVivMejoramiento(shouldFit)
```

- Al cambiar filtros se llama a la funcion de render directamente con `shouldFit=false` (no re-hace zoom)
- Al entrar al modo o cambiar sub-modo, `shouldFit=true` → `map.fitBounds()`
- Cada llamada elimina `vivLayer` anterior antes de crear uno nuevo (evita apilamiento)

---

## 9) Arquitectura del frontend

```
PoryectoITT/
├── index.html                              # Pagina de inicio
├── paginas/
│   ├── pulmon_oriente_impacto_v2.html      # Pagina ITT (KPIs, charts, indicadores)
│   ├── pulmon_oriente_mapa_v2.html         # Mapa interactivo
│   ├── pulmon_oriente_informe-v2.html      # Informe de inversion
│   ├── pulmon_oriente_metodologia.html     # Metodologia ITT
│   └── pulmon_oriente_seguridad.html       # Dashboard seguridad
├── assets/
│   ├── css/
│   │   ├── informe.css                     # Variables :root, layout base, componentes comunes
│   │   ├── mapa.css                        # Estilos mapa Leaflet, filtros, leyenda
│   │   └── itt.css                         # Estilos modulo ITT (gauge, dim-cards, contrib, alertas, kpi-strip)
│   └── js/
│       ├── mapa.js                         # Logica completa del mapa interactivo
│       └── services/
│           └── dataService.js              # Carga de datos para el mapa
├── data/
│   ├── indices/
│   │   └── itt_pulmon.json                 # Fuente de verdad del ITT para el frontend
│   ├── territorio/
│   │   └── COMUNAS_PULMON.geojson          # CRS: ESRI:103599 → reproyectado a WGS84
│   ├── vivienda/
│   │   ├── INTERV_AHDI_LEG_URBA_PULMON.geojson    # CRS: EPSG:6249 → reproyectado a WGS84
│   │   └── INTERV_MEJOR_VIV_25_26_PULMON.geojson  # CRS: EPSG:6249 → reproyectado a WGS84
│   ├── seguridad/                          # Puntos SIEDCO (WGS84)
│   ├── infraestructura/                    # Puntos obras (WGS84)
│   ├── equipamientos/                      # Puntos equipamientos (WGS84)
│   └── ambiente/                           # Puntos arboles/zonas (WGS84)
└── scripts/
    └── calcular_itt.py                     # Motor de calculo Python
```

### Stack tecnico

- Vanilla JS (ES2020+) — sin frameworks ni bundler
- Leaflet.js 1.9.4 — renderizado mapa
- Leaflet.MarkerCluster 1.5.3 — agrupacion puntos
- Leaflet.heat 0.2.0 — heatmap hurtos
- Chart.js 4.4.0 — graficos ITT y estadisticas
- Turf.js 6 — operaciones geoespaciales
- proj4.js 2.11.0 — reproyeccion CRS cliente
- Google Fonts: Inter, Montserrat, JetBrains Mono

---

## 10) Brechas tecnicas pendientes

| # | Brecha | Prioridad | Estado |
|---|--------|-----------|--------|
| 1 | ~~Alinear pesos Movilidad y Desarrollo Social~~ | Alta | **RESUELTO 2026-03-13** |
| 2 | ~~Unificar contrato de indicadores entre `calcular_itt.py` y `itt_pulmon.json`~~ | Media | **RESUELTO 2026-03-14** |
| 3 | ~~Incorporar siniestralidad vial como nucleo de Movilidad~~ | Media | **RESUELTO 2026-03-14** (GeoJSON BD_SINIESTROS) |
| 4 | Agregar verificacion automatica de consistencia (pesos, cobertura, estructura) | Baja | Pendiente |
| 5 | ~~Recalcular `itt_pulmon.json` desde script para eliminar ajustes manuales~~ | Media | **RESUELTO 2026-03-13** |
| 6 | ~~Cobertura vegetal explicita en Entorno Urbano (NDVI)~~ | Baja | **RESUELTO 2026-03-14** (TIF + georaster overlay) |
| 7 | ~~Indicadores de Educacion y Desarrollo basados en datos reales~~ | Alta | **RESUELTO 2026-03-14** |
| 8 | Aforo Villa del Lago — reemplazado por proxy oficial (3.877 personas · Sec. Deportes 2024). Dato directo aun pendiente. | Media | Parcial v7 |
| 13 | NDVI medido sobre poligono completo — recalibrar sobre sub-poligono ambiental (Charco Azul + El Pondaje) | Media | Pendiente v8 |
| 9 | ~~Datos de Movilidad (siniestralidad, lesionados, muertes)~~ | Alta | **RESUELTO 2026-03-14** (BD_SINIESTROS_2023_2025) |
| 10 | ~~Datos de Cohesion Social (concentracion vulnerabilidad, rinas)~~ | Media | **RESUELTO 2026-03-14** (riñas: GeoJSON comparendos · vulnerabilidad: Excel Bienestar C13+C14) |
| 11 | Serie temporal mezclaba lapsos (T/S/A juntos) | Alta | **RESUELTO 2026-03-14** (filtro por lapso en leer_historico) |
| 12 | Orden historico lexicografico en vez de cronologico real | Media | **RESUELTO 2026-03-14** (_periodo_sort_key) |

---

## 11) Motor de calculo v2 — `scripts/calcular_itt.py`

### Flujo general

```
calcular_itt.py --periodo 2025-T4
  1. parsear_periodo('2025-T4') → year=2025, mes_inicio=10, mes_fin=12, lapso='trimestral'
  2. leer_historico(lapso='trimestral') → score_anterior / variacion (solo mismo lapso)
  3. leer_manuales('2025-T4') → valores manuales (default + override especifico)
  4. Fuentes automaticas extras (inyectadas en manuales antes del loop):
       a. leer_ndvi_tif() → ndvi_medio, area_verde_m2  [Entorno Urbano]
       b. leer_deficit_ahdi_excel(year) → deficit_restante (100 - avance)  [Entorno Urbano]
       c. leer_velocidad_excel() → km/h fila General  [Movilidad]
       d. leer_vulnerabilidad_excel(comunas={'C13','C14'}) → p/1000 hab  [Cohesion Social]
  5. Para cada dimension → para cada indicador:
       a. extraer_gis(ind, year, mes_inicio, mes_fin) → valor desde GeoJSON
       b. Si None → man_dim.get(ind_id)  → valor manual
       c. ref_factor = n_trim si gis_tipo=='conteo_periodo' else 1 (escala refs por lapso)
       d. normalizar(valor, ref_min * ref_factor, ref_max * ref_factor, inverso) → [0,100]
  6. Generar notas_extra desde GIS (nota_hurtos, nota_homicidios, nota_vif, nota_deficit)
  7. Calcular score dimension (promedio simple indicadores con valor), score global (suma ponderada)
  8. Construir serie_temporal filtrada por lapso desde itt_historico.json
  9. Guardar data/indices/itt_pulmon_{lapso}.json + itt_pulmon.json (si trimestral)
  10. Actualizar data/indices/itt_historico.json
```

### Tipos de extraccion GIS (`extraer_gis`)

| gis_tipo | Descripcion |
|---|---|
| `conteo_periodo` | Cuenta features con `FECHA_HECH` en el trimestre/año |
| `conteo_total` | Cuenta todos los features en el directorio (opcional: `gis_patron` filtra por nombre de archivo) |
| `conteo_archivo` | Cuenta features en un archivo especifico (opcional: `gis_filtro` dict para filtrar por campo) |
| `suma_campo` | Suma valores de un campo numerico (usado para `CANT_MEJOR` en mejoramiento vivienda) |
| `longitud_lineas` | Suma longitudes de LineStrings con Haversine (en km) |

### Archivos generados

| Archivo | Descripcion |
|---|---|
| `data/indices/itt_pulmon.json` | Fuente de verdad del frontend; sobreescrita en cada ejecucion |
| `data/indices/itt_historico.json` | Acumula periodos para proveer `score_anterior` y `serie_temporal` |
| `data/indices/indicadores_manuales.json` | Valores para indicadores sin fuente GIS; editar manualmente |

### Indicadores manuales

Creados con `--generar-manuales` (solo si el archivo no existe).
Estructura de `indicadores_manuales.json`:

```json
{
  "default": {
    "seguridad":           { "percepcion_seguridad": 38 },
    "entorno_urbano":      { "espacio_publico": 4.2, "luminarias": 210, "parques": 6 },
    "movilidad":           { "accesibilidad_mio": 72, "tiempo_desplazamiento": 38, "ciclorutas": 1.2 },
    "desarrollo_social":   { "ninos_programas": 1840, "acceso_salud": 76, "familias_subsidio": 520 },
    "actividad_economica": { "negocios_formalizados": 87, "empleos_obra": 340, ... },
    "_barrios": [ {"nombre": "...", "itt": 65.2, "poblacion": 18400, "proyectos": 12} ]
  },
  "2025-T4": { /* overrides especificos por periodo */ }
}
```

El bloque `"2025-T4"` (u otro periodo) sobreescribe `"default"` indicador a indicador.
`_barrios` siempre se reemplaza completo si el periodo especifico lo trae.

### Comandos

```bash
# Primera vez: generar indicadores_manuales.json con valores por defecto
python scripts/calcular_itt.py --generar-manuales

# Calcular para un periodo (usa periodo actual si se omite --periodo)
python scripts/calcular_itt.py --periodo 2025-T4

# Opciones adicionales
python scripts/calcular_itt.py --periodo 2025-T4 --version oficial --output data/indices/custom.json
```

---

## 12) Historial de cambios

### 2026-03-14 — Ajuste de ponderacion por prioridad operativa

- Se ajusta perfil ITT para priorizar Seguridad y Movilidad:
  - Seguridad: 0.20 -> 0.25
  - Movilidad: 0.20 -> 0.25
  - Entorno Urbano: 0.30 -> 0.20
  - Desarrollo Social: 0.15 (sin cambio)
  - Actividad Economica: 0.15 (sin cambio)
- Archivos actualizados: `scripts/calcular_itt.py`, `data/indices/itt_pulmon.json`
- Recalculo ejecutado para `2025-T4`:
  - ITT Global: **44.0/100**
  - Variacion: **+2.9 pts** vs `2025-T3`

### 2026-03-14 — Vulnerabilidad activa desde Excel Bienestar + Comparendos en mapa Seguridad (v6)

**Nuevas fuentes integradas:**
- `data/excel/bienestar/Caracterizaci*.xlsx` — 24.087 personas caracterizadas en programas Sub PyE (ciudad completa). Filtro: Comunas 13 y 14 (nucleo Pulmon). 4.781 personas → 54.1 p/1.000 hab.
- Modo Seguridad en el mapa: nuevo sub-modo **Comparendos** (24.134 eventos 2023-2025, 4 tipos: Riñas/Armas/Sustancias/Desacato) desde `data/seguridad/comparendos/COMPARENDOS_2023_2025_PULMON.geojson`.

**Cambios en `scripts/calcular_itt.py`:**
- Nueva funcion `leer_vulnerabilidad_excel(comunas, poblacion)` — lee Excel por zipfile/XML, filtra por columna `nom_comuna` (indice 10), calcula rate p/1000 hab.
- `concentracion_vulnerabilidad_activa`: `oficial=False` / manual 78.0 → `oficial=True` / Excel auto 54.1 p/1000 hab.
- Comunas configurables via parametro: por defecto `{'Comuna 13', 'Comuna 14'}` — cambiar set para incluir C15/C21 si se requiere comparacion.
- Inyeccion en `manuales["cohesion_social"]` antes del loop (mismo patron que NDVI/AHDI/velocidad).

**Cambios en `assets/js/mapa.js`:**
- `comparendosData` (nueva variable, diferente de `comparendosMovData` de movilidad).
- Sub-modo `comparendos` agregado a `renderSeguridad()`: config completa con colorFn por tipo, leyenda 4 colores, popup (barrio, sitio, direccion, fecha, hora, estrato).
- Fetch al iniciar: `data/seguridad/comparendos/COMPARENDOS_2023_2025_PULMON.geojson`.

**JSON regenerados (2025-T4):**
- Cohesion Social: 63.9 → 70.0 (vulnerabilidad real 54.1 vs manual 78.0)
- ITT Global: 71.7 → **72.5/100** · Nivel 3 · Avance (+6.4 vs 2025-T3)

**Estado trazabilidad post-integracion:**
- Indicadores reales: **16/17** — cobertura 100% con valor para todos los indicadores. **1 manual pendiente de dato externo.**
- Unico manual restante: aforo Villa del Lago (valor fijo 4.200; pendiente Sec. Deportes)

---

### 2026-03-14 — Rinas + velocidad corredor desde datos reales (v5)

**Nuevas fuentes integradas:**
- `data/seguridad/comparendos/COMPARENDOS_2023_2025_PULMON.geojson` — 24.134 eventos (2023-2025), filtro `agrupado=RIÑAS` extrae 1.002 registros de riñas/conflictividad
- `data/excel/movilidad/Velocidades Ciudad de Cali_Pulmon Oriente -2025-YTD2026.xlsx` — hoja "Velocidades Jornadas", fila General = 26.8 km/h (promedio acumulado 2025-YTD2026)

**Cambios en `scripts/calcular_itt.py`:**
- `rinas_conflictividad`: `oficial=False` / manual → `oficial=True` / GeoJSON `conteo_periodo`, `gis_campo_fecha: fecha_hech`, `gis_filtro: {agrupado: RIÑAS}`
- `velocidad_corredor`: `oficial=False` / manual 18.5 km/h → `oficial=True` / Excel via nueva funcion `leer_velocidad_excel()` → 26.8 km/h
- Nueva funcion `leer_velocidad_excel()` usa `_leer_xlsx_sheet()` ya existente con hoja "Velocidades Jornadas"
- Velocidad inyectada en `manuales["movilidad"]` antes del loop de indicadores (mismo patron que NDVI/AHDI)

**Cambios en `data/indices/indicadores_manuales.json`:**
- Retirado `rinas_conflictividad: 74` del bloque `cohesion_social` (ahora viene del GeoJSON)

**JSON regenerados (2025-T4):**
- Cohesion Social: 72.7 → 63.9 (rinas reales: dato mayor que estimado manual)
- Movilidad: 70.8 → 81.2 (velocidad real 26.8 km/h vs 18.5 estimado)
- ITT Global: 70.2 → **71.7/100** · Nivel 3 · Avance

**Estado trazabilidad post-integracion:**
- Indicadores reales: **15/17** (GeoJSON + TIF + Excel)
- Manuales restantes: aforo Villa del Lago (Sec. Deportes) + concentracion vulnerabilidad activa (Sec. Bienestar)

### 2026-03-14 — Integracion movilidad + NDVI mapa + estabilizacion lapso + entorno urbano real

**Nuevas fuentes de datos integradas al motor ITT:**
- `data/movilidad/BD_SINIESTROS_2023_2025_COMUNA_BARRIO_PULMON.geojson` (693 eventos): siniestralidad_vial, accidentes_lesionados, muertes_via → indicadores oficiales
- `data/movilidad/BD_COMPARENDOS_2025_COMUNA_BARRIO_PULMON.geojson` (4.808 registros): capa analitica en mapa (no KPI ITT — datos 2025-T1 a T3)
- `data/NVDI/ndvi_resultado.tif`: NDVI medio (0.20) y area verde neta (1.699.769 m²) — extraccion automatica via `leer_ndvi_tif()` con tifffile + numpy
- `data/excel/vivienda/INTERVENCION_AHDI_AÑOS_24_25_26.xlsx`: deficit habitacional cualitativo como % pendiente de legalizacion — extraccion via `leer_deficit_ahdi_excel(year)`

**Indicadores pasados de manual/estimado a oficial/real:**
- siniestralidad_vial, accidentes_lesionados, muertes_via: Estimado → Oficial (GeoJSON)
- ndvi_cobertura_vegetal: Estimado → Oficial (TIF)
- area_verde_neta: Estimado → Oficial (TIF derivado)
- deficit_habitacional_cualitativo: Estimado → Oficial (Excel AHDI)
- Total oficial: 9/17 GeoJSON/TIF/derivado + 4/17 Excel = 13/17 reales

**Mapa interactivo — nuevos modulos:**
- Modo Movilidad (nuevo): sub-modos Siniestros + Comparendos con filtros dinamicos por tipo/año/comuna
- NDVI overlay (modo Ambiente): boton "Ver NDVI" carga TIF con georaster-layer-for-leaflet, recortado al poligono del area (opcion `mask: globalPerimetro`)
- CDN agregados: georaster@1.6.0 + georaster-layer-for-leaflet@3.10.0

**Estabilizacion metodologica del motor:**
- `leer_historico(lapso=...)` filtra comparaciones por mismo lapso (T, S, anual) — evita "vs periodo de otro lapso"
- `_periodo_sort_key()`: orden cronologico real (year, mes_inicio, mes_fin, duracion) — reemplaza orden lexicografico
- `serie_temporal` en cada JSON filtrada por lapso propio
- Comportamiento neutral cuando no hay periodo previo del mismo lapso (sin variacion artificial)

**Archivos JSON regenerados:**
- `itt_pulmon_trimestral.json`: serie ['2025-T3', '2025-T4'] | ITT 70.2
- `itt_pulmon_semestral.json`: serie ['2025-S1', '2025-S2'] | ITT 58.6
- `itt_pulmon_anual.json`: serie ['2023', '2024', '2025'] | ITT 58.5
- `itt_pulmon.json`: copia de trimestral (retrocompatibilidad)

**Documentacion:**
- `CONTEXTO_TECNICO_ITT_PULMON.md` actualizado: pesos, indicadores, brechas, arquitectura mapa, historial

### 2026-03-13 — Sesion de integracion datos vivienda + mejoras ITT

**Datos integrados:**
- Integrados 2 nuevos datasets GIS reales de Secretaria de Vivienda:
  - `INTERV_AHDI_LEG_URBA_PULMON.geojson` — 6 poligonos legalizacion urbanistica (11.71 ha)
  - `INTERV_MEJOR_VIV_25_26_PULMON.geojson` — 8 sectores mejoramiento vivienda (157 unidades)

**Correcciones tecnicas:**
- Corregidos pesos en `calcular_itt.py` y `itt_pulmon.json`: Movilidad 0.15→0.20, Desarrollo Social 0.20→0.15
- Corregida reproyeccion EPSG:6249 en `mapa.js`: datos vivienda de MAGNA-SIRGAS Colombia West (coordenadas ~1M m) convertidos correctamente a WGS84 con proj4.js
- Corregido apilamiento de capas en modo Vivienda: vivLayer ahora se elimina siempre antes de re-renderizar
- Corregidos labels duplicados en filtro Estado de Mejoramiento: `getEstadoLabel()` agrupa "EN EJECUCION / ASIGNADO" → "En Ejecucion" sin colision con "ASIGNADO"

**Nuevas funcionalidades en mapa:**
- Modo Vivienda completo con 2 sub-modos (Legalizacion Urbanistica / Mejoramiento Vivienda)
- Filtros dinamicos por Año/Proceso (legalizacion) y Estado/Fuente (mejoramiento)
- Popups con datos reales por poligono (area, % urbanizado, cantidad viviendas, estado)
- KPIs de cabecera actualizados por filtro (poligonos + ha / sectores + viviendas)
- Leyenda dinamica por sub-modo con colores reales
- `fitBounds` solo al entrar al modo o cambiar sub-modo, no al cambiar filtros
- UI de filtros reorganizada en filas etiquetadas (.filter-row) para todos los modos

**Actualizaciones en `itt_pulmon.json`:**
- Cobertura datos: 72% → 78% (12/14 fuentes activas)
- 2 nuevos indicadores oficiales en Entorno Urbano con `nota_real` trazable
- Score Entorno Urbano: 59.4 → 71.8 (+12.4 pts)
- ITT Global: 51.6 → 58.3 (+6.7 pts)

**Mejoras pagina ITT (`pulmon_oriente_impacto_v2.html`):**
- KPI strip con 6 metricas animadas (countUp) leidas del JSON
- Alertas automaticas para indicadores con nota_real "ALERTA"
- Grafico de contribucion ponderada (score x peso por dimension)
- Toggle de lineas individuales en grafico de evolucion
- Serie trimestral de hurtos 2023-2025 en tab Seguridad
- Sort dinamico del ranking de barrios (ITT / Poblacion / Proyectos)
- Nota metodologica desde campo `meta.nota` del JSON
- Todas las referencias de periodo/texto leidas del JSON (sin hardcodeo en HTML)

---

## 13) Alineacion con `Modelo_Medicion_Apuestas_Cali_v4.docx` (enfoque Pulmon)

Revision tecnica realizada sobre las secciones del modelo:
- Cadena causal: `Output -> Outcome inmediato -> Outcome intermedio -> Impact` (sec. 5.1)
- Formula ITT y perfiles diferenciados por apuesta (sec. 7.3 y 7.4)
- Algoritmo de calculo y normalizacion (sec. 8)
- Escala de madurez (sec. 18)

### 13.1 Estado de acople (resumen ejecutivo)

| Componente del modelo | Estado en la solucion actual | Observacion |
|---|---|---|
| Perfil de pesos Pulmon (0.25, 0.20, 0.25, 0.15, 0.15) | **Configurado** | Implementado en `scripts/calcular_itt.py` y `itt_pulmon.json` (ajuste operativo; difiere del perfil 7.4 del documento) |
| Normalizacion Min-Max + escala 0-100 | **Alineado** | Implementado en motor Python |
| Integracion multifuente (GIS + manuales) | **Alineado** | Opcion C operativa, generacion automatica del JSON |
| Escala de madurez 1-4 | **Parcial** | Se usa clasificacion de niveles, falta incorporar criterios cualitativos completos del modelo |
| Cadena causal 4 niveles (Output/Outcome/Impact) | **Parcial** | Hoy el tablero esta organizado por dimensiones, no por nivel causal |
| Atribuibilidad con territorio espejo (DiD) | **No implementado** | El pipeline actual no calcula `Impacto = (Post_T - Pre_T) - (Post_C - Pre_C)` |

### 13.2 Cobertura de indicadores frente a Pulmon (sec. 5.1)

El sistema actual ya cubre parte importante del nucleo operativo del modelo (homicidios, hurtos, VIF, movilidad basica, vivienda, equipamientos), pero todavia faltan varios indicadores estructurales y de outcome intermedio mencionados en el documento.

**Cubiertos hoy (ejemplos):**
- Homicidios, hurtos, violencia intrafamiliar, VBG
- Tramos viales, accesibilidad MIO, ciclorutas
- Luminarias, parques, espacio publico
- Viviendas en mejoramiento y poligonos AHDI
- Sedes educativas, acceso salud, empleo de obra

**Ya integrados (antes pendientes, ahora operativos):**
- Siniestralidad vial, lesionados, muertes en via — **REAL (auto)** desde GeoJSON BD_SINIESTROS (integrado 2026-03-14)
- Rinas / conflictividad — **REAL (auto)** desde GeoJSON Comparendos filtro RIÑAS (integrado 2026-03-14)
- NDVI / cobertura vegetal y area verde — **REAL (auto)** desde TIF Sentinel-2 (integrado 2026-03-14)

**Pendientes para alineacion completa con 5.1:**
- Temperatura superficial (LST) — sin fuente disponible
- Valor catastral promedio y dinamica predial — sin fuente disponible
- Indicadores estructurales de impacto (IPM, permanencia escolar, permanencia residencial, confianza institucional)

### 13.3 Brecha metodologica principal

La brecha mas relevante no es visual sino analitica:
- El modelo define atribuibilidad con territorio control (DiD) y tabla de territorios espejo.
- La implementacion actual mide evolucion interna del territorio tratado (Pulmon), pero **sin contrafactual formal**.
- Por tanto, hoy el ITT es util para seguimiento y gestion operativa, pero aun no soporta plenamente inferencia causal tipo DiD exigida por el modelo.

### 13.4 Conclusión tecnica

La solucion actual esta bien acoplada para una fase operativa de monitoreo territorial de Pulmon de Oriente (pesos, formula, normalizacion, integracion GIS, tablero dinamico), y queda preparada para escalar a la fase metodologica completa del documento una vez se integren:
1. Los indicadores estructurales faltantes.
2. El esquema de territorio espejo y calculo DiD.
3. La trazabilidad institucional de validacion por fuente para declaratoria de ITT oficial.

---

## 14) Nuevo contexto base (2026-03-14) — `Extracto_Resultados_Pulmon.docx` + `Indicadores_Pulmon_Oriente.xlsx`

### 14.1 Linea metodologica a usar desde ahora

Se define como referencia operativa para Pulmon de Oriente:
- Dimensiones: **Seguridad, Movilidad, Entorno Urbano, Educacion y Desarrollo, Cohesion Social**
- Formula objetivo:
  `ITT = 0.30 * I_Seg + 0.25 * I_Mov + 0.20 * I_Ent + 0.13 * I_EyD + 0.12 * I_Coh`
- Prioridad explicita: Seguridad y Movilidad (por encuesta ciudadana)

> Esta formula proviene del extracto y del archivo de indicadores entregados el 2026-03-14.

### 14.2 Inventario de indicadores (xlsx) y estado de disponibilidad

**Seguridad**
- Homicidios en poligono — Disponible
- Hurtos en poligono — Disponible
- Rinas / conflictividad — Disponible

**Movilidad**
- Siniestralidad vial — Disponible
- Accidentes con lesionados — Disponible
- Muertes en via — Disponible
- Velocidad promedio del corredor — **Integrado (Excel auto - Waze for Cities 2025)**

**Entorno Urbano**
- NDVI / cobertura vegetal — **Integrado (TIF local Sentinel/Copernicus)**
- Area verde neta — **Integrado (derivado desde NDVI > 0.20)**
- Deficit habitacional cualitativo — **Integrado (AHDI Excel, avance invertido)**

**Educacion y Desarrollo**
- Aforo polideportivo Villa del Lago — Disponible (manual). Pendiente fuente oficial Sec. Deportes.
- Matricula escolar (por sede) — Disponible
- Desercion escolar (por sede) — Disponible
- Repitencia escolar (por sede) — Disponible
- Estudiantes por docente (por sede) — Disponible

**Cohesion Social**
- Violencia intrafamiliar (VIF) — Disponible
- Concentracion de vulnerabilidad activa — Disponible

### 14.3 Implicacion para el roadmap ITT

Hasta recibir la capa/dataset de Movilidad que falta (segun coordinacion actual):
1. Mantener el ITT actual operativo para seguimiento.
2. Preparar migracion de modelo a las 5 dimensiones nuevas (incluyendo Educacion y Desarrollo + Cohesion Social).
3. Priorizar integracion de indicadores marcados como "Gestionar" para evitar que el nuevo ITT nazca con cobertura incompleta.

---

## 15) Control operativo vigente - Real vs Manual/Hardcodeado (corte 2026-03-14 v3)

Esta seccion es la referencia de control para no perder trazabilidad en la implementacion actual.

### 15.1 Estado por indicador en el motor (`scripts/calcular_itt.py`)

| Dimension | Indicador | Estado actual | Fuente efectiva |
|---|---|---|---|
| Seguridad | Homicidios en poligono (trimestral) | **REAL (auto)** | GeoJSON `data/seguridad/homicidios/*` |
| Seguridad | Hurtos en poligono (trimestral) | **REAL (auto)** | GeoJSON `data/seguridad/hurtos/*` |
| Cohesion Social | Rinas / conflictividad (trimestral) | **REAL (auto)** | GeoJSON `data/seguridad/comparendos/COMPARENDOS*.geojson` (filtro `agrupado=RIÑAS`) |
| Movilidad | Siniestralidad vial | **REAL (auto)** | GeoJSON `data/movilidad/BD_SINIESTROS_2023_2025_COMUNA_BARRIO_PULMON.geojson` |
| Movilidad | Accidentes con lesionados | **REAL (auto)** | GeoJSON `data/movilidad/BD_SINIESTROS_2023_2025_COMUNA_BARRIO_PULMON.geojson` (`Tipo_Confi=Lesiones`) |
| Movilidad | Muertes en via | **REAL (auto)** | GeoJSON `data/movilidad/BD_SINIESTROS_2023_2025_COMUNA_BARRIO_PULMON.geojson` (`Tipo_Confi=Mortal`) |
| Movilidad | Velocidad promedio corredor | **REAL (Excel auto)** | `data/excel/movilidad/Velocidades*.xlsx` — hoja Velocidades Jornadas, fila General |
| Entorno Urbano | NDVI / cobertura vegetal | **REAL (auto)** | TIF `data/NVDI/ndvi_resultado.tif` (media NDVI válida) |
| Entorno Urbano | Area verde neta | **REAL (auto)** | TIF `data/NVDI/ndvi_resultado.tif` (pixeles NDVI >= 0.20) |
| Entorno Urbano | Deficit habitacional cualitativo | **REAL (Excel auto)** | `data/excel/vivienda/INTERVENCION_AHDI_AÑOS_24_25_26.xlsx` |
| Educacion y Desarrollo | Matricula escolar | **REAL (Excel)** | `data/excel/educacion/Indicadores_Sectoriales_{year}.xlsx` |
| Educacion y Desarrollo | Desercion escolar | **REAL (Excel)** | `data/excel/educacion/Indicadores_Sectoriales_{year}.xlsx` |
| Educacion y Desarrollo | Repitencia escolar | **REAL (Excel)** | `data/excel/educacion/Indicadores_Sectoriales_{year}.xlsx` |
| Educacion y Desarrollo | Estudiantes por docente (RAD) | **REAL (Excel)** | `data/excel/educacion/Indicadores_Sectoriales_{year}.xlsx` |
| Educacion y Desarrollo | Aforo Villa del Lago | **MANUAL** | `data/indices/indicadores_manuales.json` — pendiente Sec. Deportes |
| Cohesion Social | VIF trimestral | **REAL (auto)** | GeoJSON `data/seguridad/violencia/*` (patron VIF) |
| Cohesion Social | Concentracion de vulnerabilidad activa | **REAL (Excel auto)** | `data/excel/bienestar/Caracterizaci*.xlsx` — filtra Comunas 13+14, calcula p/1000 hab |

Resumen operativo del motor (corte 2026-03-14 v6):
- Indicadores totales: 17
- Reales autoextraidos (GeoJSON/TIF/derivado): 10 (homicidios, hurtos, VIF, rinas, siniestralidad, lesionados, muertes via, NDVI, area verde neta, deficit habitacional)
- Reales desde Excel oficial: 6 (matricula, desercion, repitencia, RAD, velocidad corredor, concentracion vulnerabilidad)
- Manuales/estimados: 1 (aforo Villa del Lago — pendiente Sec. Deportes)

### 15.2 Extraccion de indicadores educativos (Excel)

Funcion: `leer_indicadores_educacion(year, sector)` en `scripts/calcular_itt.py`

Los archivos Excel provienen de la Secretaria de Educacion de Cali (Indicadores Sectoriales anuales).
Ubicacion: `data/excel/educacion/Indicadores_Sectoriales_{YYYY}.xlsx`
Disponibles: 2023, 2024, 2025.
Territorio: Comunas 13 y 14 (nucleo del Poligono Pulmon de Oriente).

**Sector configurable** — variable global `EDU_SECTOR` en el script:

```python
EDU_SECTOR = "total"     # todos los sectores (oficial + no oficial + contratada)  ← default
EDU_SECTOR = "oficial"   # solo sector oficial
EDU_SECTOR = "no_oficial" # solo sector no oficial
```

**Valores 2025 por sector (Comunas 13+14):**

| Indicador | Total | Oficial | No oficial |
|---|---:|---:|---:|
| Matricula | 50.336 | 18.716 | 12.635 |
| Repitencia | 8.4% | 8.4% | 8.4% |
| Desercion | 4.3% | 4.7% | 4.1% |
| RAD (est/docente) | 27.1 | 27.1 | 27.1 |

> RAD siempre usa el sector oficial (sheet20) porque es el unico con docentes contabilizados con rigor metodologico. Matricula y desercion si varian por sector.

**Serie historica real:**

| Año | Matricula total | Repitencia | Desercion | RAD oficial |
|---|---:|---:|---:|---:|
| 2023 | 53.746 | 9.4% | 4.7% | 28.3 |
| 2024 | 53.138 | 9.2% | 5.3% | 26.7 |
| 2025 | 50.336 | 8.4% | 4.3% | 27.1 |

Tendencia: matricula en descenso leve (-6.3% en 3 años), repitencia y desercion mejoran sostenidamente.

**Mapa de hojas Excel (por contenido real, no por nombre en workbook):**

| Archivo sheet | Contenido | Uso en script |
|---|---|---|
| `sheet7.xml` | Matricula por sector (Contratada/No Oficial/Oficial) y comuna | Extrae `matricula` por sector |
| `sheet14.xml` | Matricula + Repitentes totales por comuna | Extrae `tasa_repitencia` |
| `sheet16.xml` | Desercion sector oficial por comuna | Extrae `tasa_desercion` (sector=oficial) |
| `sheet18.xml` | Desercion sector no oficial por comuna | Extrae `tasa_desercion` (sector=no_oficial) |
| `sheet20.xml` | RAD oficial por comuna (MATRICULA, DOCENTES, RAD) | Extrae `rad` (siempre oficial) |

> Los nombres de hojas en `workbook.xml` no coinciden linealmente con los archivos XML internos del xlsx. El script usa rutas de archivo directas para evitar errores de mapeo.

### 15.3 Consistencia de historico y lapsos (estabilizacion v3)

Correcciones aplicadas en `scripts/calcular_itt.py`:

1. `leer_historico(periodo_actual, lapso)` ahora filtra por lapso y luego ordena cronologicamente con clave temporal (`_periodo_sort_key`), evitando mezclar comparaciones entre anual/semestral/trimestral.
2. `guardar_historico()` ya no ordena lexicograficamente el string del periodo; usa orden temporal real.
3. `serie_temporal` en cada JSON de salida se construye solo con periodos del mismo lapso activo.
4. Si no existe periodo previo del mismo lapso, la comparacion queda en `N/A` y la variacion se mantiene neutra (0.0), evitando "saltos" artificiales por base inexistente.

Estado esperado de `serie_temporal` por archivo:
- `itt_pulmon_trimestral.json`: solo `YYYY-Tn`
- `itt_pulmon_semestral.json`: solo `YYYY-Sn`
- `itt_pulmon_anual.json`: solo `YYYY`
### 15.4 Que esta hardcodeado en frontend hoy

1. **Pagina de seguridad** (`paginas/pulmon_oriente_seguridad.html`)
   - Objeto `MODULES` con KPIs, textos, series y rankings hardcodeados para narrativa ejecutiva.
   - Vista por dimension SI toma datos del ITT JSON.

2. **Pagina ITT** (`paginas/pulmon_oriente_impacto_v2.html`)
   - Todos los valores numericos vienen del JSON.
   - Copy/subtitulos editoriales fijos (no alteran calculo).

3. **Pagina metodologia** (`paginas/pulmon_oriente_metodologia.html`)
   - Tabla y tarjetas dinamicas desde `itt_pulmon.json`.
   - Texto explicativo editorial hardcodeado.

### 15.6 Auditoria y calibracion de ref_min / ref_max (2026-03-15)

Se realizo auditoria completa de los rangos de normalizacion frente a dos criterios:

**(b) Ancla historica real:** Los `ref_min` y `ref_max` deben provenir de datos reales del territorio, no de estimados de diseño. Rangos teoricos producen scores artificialmente altos o bajos al posicionar cualquier valor intermedio en la mitad de una escala que no refleja la distribucion real.

**(c) Inversion de indicadores negativos:** Para indicadores donde mas es peor (homicidios, hurtos, siniestralidad, VIF, etc.), la formula correcta es `score = 1 - (valor - ref_min) / (ref_max - ref_min)`. Auditoria confirmo que todos los indicadores negativos tienen `inverso=True` en el script — **no hay error de inversion**.

**Resultado de la auditoria por indicador:**

| Tipo de ancla | Indicadores | Base |
|---|---|---|
| **GeoJSON real (12 trimestres)** | Homicidios, Hurtos, Siniestralidad, Lesionados, Muertes en via, VIF, Rinas | Serie 2023-T1 a 2025-T4 del propio territorio |
| **Referencia normativa/tecnica** | NDVI, Desercion, Repitencia, RAD | Escala Sentinel-2 estandar / MEN / ODS |
| **Estimado operativo sin historico** | Velocidad, Area verde, Deficit AHDI, Matricula, Vulnerabilidad, Aforo | Un solo corte disponible; sin serie temporal propia |

**Correcciones aplicadas (refs anteriores → nuevos):**

| Indicador | ref_max anterior | ref_max nuevo | Motivo |
|---|---:|---:|---|
| Homicidios | 130 | 50 | Max historico real = 38; anterior era irreal para este territorio |
| Hurtos | 500 | 450 | Max historico real = 434; ref_min ajustado 150→200 |
| Siniestralidad | 260 | 80 | Max historico real = 68; ref_max 260 era 3.8x el maximo observado |
| Lesionados | 180 | 65 | Max historico real = 56; ref_max 180 era 3.2x el maximo observado |
| Muertes en via | 30 | 10 | Max historico real = 6; ref_max 30 era 5x el maximo observado |
| VIF | 220 | 200 | Max historico real = 189; leve ajuste; ref_min 80→60 |
| Rinas | 220 | 160 | Max historico real = 144; ajuste con margen 10% |
| Area verde neta | 300.000 m² | 3.000.000 m² | Anterior era irreal para un poligono de 12 km²; nuevo = 25% del area total |

**Impacto en ITT 2025-T4:**

| Dimension | Score anterior | Score nuevo |
|---|---:|---:|
| Seguridad | 72.8 | 53.6 |
| Movilidad | 81.2 | 44.8 |
| Entorno Urbano | 70.0 | 52.7 |
| Educacion y Desarrollo | 61.0 | 61.0 |
| Cohesion Social | 70.0 | 57.6 |
| **ITT Global** | **72.5** | **52.7** |

El ITT 72.5 anterior era artificialmente alto por tres causas: (1) ref_max de siniestralidad/lesionados/muertes muy por encima del maximo real del territorio, haciendo que valores tipicos parecieran excelentes; (2) area_verde siempre capada al 100 por ref_max incorrecto; (3) refs de homicidios y rinas subestimaban la gravedad real.

El 52.7 (Nivel 2 - Consolidacion) es metodologicamente defendible: el territorio tiene brechas reales en seguridad (score 53.6) y movilidad (score 44.8) que justifican la intervencion, sin estar en nivel critico de emergencia.

**Correcciones tecnicas adicionales:**
- Bug en `serie_temporal`: si el periodo actual ya existia en el historico (de una corrida anterior), se usaba el valor viejo en vez del recalculado. Corregido: el periodo actual siempre reemplaza cualquier entrada previa antes de escribir el JSON.
- Todos los periodos existentes (T3, T4, S1, S2, 2025) fueron recalculados con los nuevos refs para mantener consistencia historica.

### 15.7 Por que trimestral, semestral y anual dan valores distintos

Esta es la diferencia esperada por diseno del modelo, no un error.

**Cada lapso mide un periodo de tiempo distinto:**

| Lapso | Periodo medido | Eventos contados |
|---|---|---|
| Trimestral T4 | Oct–Dic 2025 | Solo Q4 |
| Semestral S2 | Jul–Dic 2025 | Q3 + Q4 |
| Anual 2025 | Ene–Dic 2025 | Q1 + Q2 + Q3 + Q4 |

**Mecanismo de escala (`ref_factor`):**

Para indicadores de conteo (`gis_tipo=conteo_periodo`), el motor escala `ref_min` y `ref_max` proporcionalmente al numero de trimestres del lapso:

```
n_trim = (mes_fin - mes_inicio + 1) / 3
ref_min_efectivo = ref_min * n_trim
ref_max_efectivo = ref_max * n_trim
```

Ejemplo para homicidios:
```
Trimestral (n=1): ref=[5, 50]   · T4=36      → score 31.1
Semestral  (n=2): ref=[10, 100] · T3+T4=45   → score 61.1  (T3 fue bajo: 9 casos)
Anual      (n=4): ref=[20, 200] · T1..T4=85  → score 63.9  (T1-T3 suavizaron el pico)
```

**Por que T4 trimestral da el score mas bajo:**
El Q4-2025 fue el peor trimestre del año en seguridad (36 homicidios vs promedio 24 del año). El trimestral es el indicador mas sensible a cambios recientes. El semestral y anual promedian ese pico con trimestres mejores.

**Lectura correcta para el usuario:**
- **Trimestral**: mas sensible a la situacion reciente; util para alertas y seguimiento operativo.
- **Semestral**: equilibra picos y valles; util para tendencias de mediano plazo.
- **Anual**: vision de conjunto del año; util para comparacion interanual y rendicion de cuentas.

Los tres son validos y complementarios. El valor mas bajo del trimestral no significa que el modelo falla — significa que el ultimo trimestre fue particularmente adverso.

### 15.8 Indicadores sin serie historica — plan de mejora

Los siguientes indicadores usan refs de diseno por no tener serie historica propia. Para anclarlos a datos reales se requiere:

| Indicador | Accion necesaria |
|---|---|
| Velocidad corredor | Conservar Excel Waze de cada año en `data/excel/movilidad/` para construir serie |
| Area verde neta | Procesar TIF de otros años o trimestres para ver variacion estacional |
| Deficit AHDI | Definir si el indicador debe medir cobertura del programa (actual) o resolucion real (escrituras entregadas) |
| Matricula | Conservar Excel de cada año — ya disponibles 2023/2024/2025; usar historico para calibrar ref_max |
| Vulnerabilidad | Solicitar a Sec. Bienestar cortes anteriores (2022, 2023, 2024) del mismo Excel de caracterizacion |
| Aforo Villa del Lago | Pendiente dato oficial de Sec. Deportes |

### 15.9 Regla de gobernanza para siguientes cambios

Para evitar confusion en futuras sesiones:
1. Si un indicador pasa de manual a real, actualizar en el mismo commit:
   - `scripts/calcular_itt.py` (bloque `DIMENSIONES` + logica de extraccion)
   - `data/indices/indicadores_manuales.json` (retirar o dejar como respaldo)
   - Seccion 15.1 de este documento
2. Mantener la etiqueta explicita: `REAL (auto)`, `REAL (Excel)` o `MANUAL`.
3. Tratar `data/indices/itt_pulmon.json` como salida del script, nunca editar manualmente.
4. Al agregar un nuevo Excel de educacion (ej. 2026), depositarlo en `data/excel/educacion/` con el patron `Indicadores_Sectoriales_{YYYY}.xlsx` — el script lo detecta automaticamente.

---

## 16) Historial de cambios

### 2026-03-15 — Calibracion de ref_min/ref_max con serie historica real (v7)

**Problema identificado:**
Auditoria metodologica detecto que los rangos de normalizacion de 8 indicadores no estaban anclados a la serie historica real del territorio. Los ref_max de siniestralidad (260), lesionados (180) y muertes en via (30) eran entre 3x y 5x el valor maximo observado en 12 trimestres reales, haciendo que valores tipicos del territorio aparecieran como excelentes. El area verde neta tenia ref_max=300k m² cuando el territorio mide 1.7M m², capando siempre en 100. Resultado: ITT artificialmente alto de 72.5.

**Correcciones en `scripts/calcular_itt.py` — bloque `DIMENSIONES`:**

| Indicador | ref anterior | ref nuevo | Fuente del nuevo rango |
|---|---|---|---|
| Homicidios | [8, 130] | [5, 50] | Serie real C13-C14: min=9 max=38 (2023-2025) |
| Hurtos | [150, 500] | [200, 450] | Serie real C13-C14: min=259 max=434 (2023-2025) |
| Siniestralidad | [30, 260] | [30, 80] | Serie real C13-C14: min=47 max=68 (2023-2025) |
| Lesionados | [20, 180] | [20, 65] | Serie real C13-C14: min=42 max=56 (2023-2025) |
| Muertes en via | [2, 30] | [1, 10] | Serie real C13-C14: min=2 max=6 (2023-2025) |
| VIF | [80, 220] | [60, 200] | Serie real C13-C14: min=88 max=189 (2023-2025) |
| Rinas | [20, 220] | [20, 160] | Serie real C13-C14: min=38 max=144 (2023-2025) |
| Area verde neta | [50k, 300k] | [500k, 3M] | ref_max = 25% del poligono (12 km²) |

**Bug corregido — `serie_temporal`:**
Si el periodo actual ya existia en `itt_historico.json` (de una corrida anterior con refs diferentes), la serie exportada al JSON usaba el valor viejo en vez del recien calculado. Corregido: el periodo actual siempre reemplaza cualquier entrada previa en la serie antes de escribir el JSON de salida.

**Todos los periodos recalculados con nuevos refs:**

| Periodo | Lapso | ITT anterior | ITT nuevo |
|---|---|---:|---:|
| 2025-T3 | Trimestral | 66.1 | 59.8 |
| 2025-T4 | Trimestral | 72.5 | **52.7** |
| 2025-S1 | Semestral | 71.8 | 58.2 |
| 2025-S2 | Semestral | 71.8 | 56.2 |
| 2025 | Anual | 72.1 | 57.2 |

**Auditoria de inversion (punto c):**
Confirmado: todos los indicadores negativos (donde mas es peor) tienen `inverso=True` en el script. La formula `score = 1 - (valor - ref_min)/(ref_max - ref_min)` se aplica correctamente en todos los casos. No habia error de inversion.

**Estado post-calibracion 2025-T4:**
- ITT Global: **52.7/100** · Nivel 2 · Consolidacion
- Seguridad: 53.6 · Movilidad: 44.8 · Entorno: 52.7 · EyD: 61.0 · CohSoc: 57.6
- 16/17 indicadores reales; 1 manual (aforo)



### 2026-03-14 — Integracion Movilidad real (GeoJSON) en ITT + mapa

**Nuevos datasets operativos:**
- `data/movilidad/BD_SINIESTROS_2023_2025_COMUNA_BARRIO_PULMON.geojson`
- `data/movilidad/BD_COMPARENDOS_2025_COMUNA_BARRIO_PULMON.geojson`

**Cambios en `scripts/calcular_itt.py`:**
- `siniestralidad_vial`, `accidentes_lesionados` y `muertes_via` pasan de manual a **REAL (auto)**.
- Extraccion por `gis_tipo=conteo_periodo` sobre fuente de siniestros:
  - Total siniestros (sin filtro de tipo)
  - Lesionados (`Tipo_Confi=Lesiones`)
  - Muertes (`Tipo_Confi=Mortal`)
- `velocidad_corredor` se mantiene manual (pendiente sensores/corredor).

**Cambios en mapa (`pulmon_oriente_mapa_v2.html` + `assets/js/mapa.js`):**
- Nuevo modo principal: `🚦 Movilidad`.
- Sub-modos dinamicos:
  - `Siniestros`: filtros por año, tipo y comuna.
  - `Comparendos`: filtros por mes, clase, inmovilizacion y comuna.
- Popups tematicos y KPIs dinamicos por sub-modo.

### 2026-03-14 — Estabilizacion lapso/historico + Entorno Urbano automatico (v3)

**Cambios en motor (`scripts/calcular_itt.py`):**
- Nuevo orden temporal robusto con `_periodo_sort_key()` para periodos `YYYY`, `YYYY-Sn`, `YYYY-Tn`.
- `leer_historico()` ahora compara solo contra periodos del mismo lapso.
- `guardar_historico()` ordena por clave temporal (no por string lexicografico).
- `serie_temporal` se exporta filtrada por lapso activo:
  - trimestral -> solo `YYYY-Tn`
  - semestral -> solo `YYYY-Sn`
  - anual -> solo `YYYY`
- Si no hay periodo previo del mismo lapso, la comparacion queda en `N/A` y no se fuerza una variacion artificial.

**Entorno Urbano (datos reales integrados):**
- `ndvi_cobertura_vegetal`: lectura automatica desde `data/NVDI/ndvi_resultado.tif`.
- `area_verde_neta`: derivada automatica de pixeles con `NDVI >= 0.20`.
- `deficit_habitacional_cualitativo`: calculado automaticamente desde avance AHDI en `data/excel/vivienda/INTERVENCION_AHDI_AÑOS_24_25_26.xlsx`.

**Estado operativo posterior al ajuste (2025-T4):**
- ITT Global: **66.4/100** (Nivel 3 · Avance)
- Distribucion de trazabilidad: 10 indicadores reales / 7 manuales.

### 2026-03-14 — Integracion datos reales de Educacion

**Nuevo dataset:**
- `data/excel/educacion/Indicadores_Sectoriales_2023.xlsx`
- `data/excel/educacion/Indicadores_Sectoriales_2024.xlsx`
- `data/excel/educacion/Indicadores_Sectoriales_2025.xlsx`
- Fuente: Secretaria de Educacion de Cali / Indicadores Sectoriales
- Comunas relevantes: 13 y 14 (68 sedes en el poligono Pulmon, identificadas con campo `CodDane`)

**Cambios en `scripts/calcular_itt.py`:**
- Nueva funcion `leer_indicadores_educacion(year, sector)` que lee directamente los Excel
- Nueva funcion auxiliar `_leer_xlsx_sheet` con mapeo correcto por relaciones del workbook (rId)
- Nueva funcion `_edu_excel_path(year)` para resolver ruta por año
- Constante `EDU_SECTOR = "total"` configurable para alternar sector de calculo
- Constante `COMUNAS_PULMON_EDU = {13, 14}` como territorio base
- Nuevo tipo de extraccion `"gis_tipo": "excel_edu"` en `extraer_gis()`
- Indicadores de Educacion y Desarrollo actualizados: matricula, desercion, repitencia, RAD usan Excel real
- Aforo Villa del Lago sigue en `manuales.json` (pendiente Sec. Deportes)

**Resultado del recalculo 2025-T4 con datos reales de educacion (corte de esa fecha):**
- Educacion y Desarrollo: score 55.8 → **61.0** (con datos reales vs estimados)
- ITT Global: 60.5 → **61.2** (+0.7 pts por correccion de calidad de dato)
- Cobertura real: 7/17 indicadores con datos verificados (antes 3/17)

**Analisis de disponibilidad de datos (vs `Extracto_Resultados_Pulmon.docx` y `Indicadores_Pulmon_Oriente.xlsx`):**

| Indicador | Disponibilidad segun xlsx | Estado en script |
|---|---|---|
| Homicidios | Disponible (GeoJSON) | REAL |
| Hurtos | Disponible (GeoJSON) | REAL |
| Rinas | Disponible (Observatorio) | **REAL (auto)** — GeoJSON comparendos filtro `agrupado=RIÑAS` |
| Siniestralidad vial | Disponible (GeoJSON Movilidad) | **REAL (auto)** |
| Lesionados en via | Disponible (GeoJSON Movilidad) | **REAL (auto)** |
| Muertes en via | Disponible (GeoJSON Movilidad) | **REAL (auto)** |
| Velocidad corredor | Disponible (Excel Waze for Cities) | **REAL (Excel auto)** — hoja Velocidades Jornadas, fila General |
| NDVI / area verde | Disponible (TIF local) | **REAL (auto)** |
| Deficit habitacional | Disponible (AHDI Excel) | **REAL (Excel auto)** |
| Matricula / Desercion / Repitencia / RAD | Disponible (Sec. Educacion) | **REAL (Excel)** |
| Aforo Villa del Lago | Disponible (Sec. Deportes) | MANUAL — pendiente dato oficial |
| VIF | Disponible (GeoJSON) | **REAL (auto)** |
| Concentracion vulnerabilidad | Disponible (Sec. Bienestar) | **REAL (Excel auto)** — `Caracterizaci*.xlsx` C13+C14 |

---

---

## 16) Notas metodologicas formales

### 16.1 NDVI — Alcance del poligono de medicion (v7)

**Indicador afectado:** NDVI / cobertura vegetal · Dimension Entorno Urbano
**Registrada:** 2026-03-15 · Origen: revision metodologica Prof. Fernando Barraza (Maestria UAO)

**Nota oficial:**

> En esta version del indice el NDVI se calcula sobre el poligono completo del Pulmon de Oriente.
> Se reconoce que el poligono incluye areas de alta densidad constructiva donde la cobertura vegetal
> es estructuralmente baja e independiente de la intervencion. En versiones posteriores del indice,
> el NDVI se calculara sobre el subpoligono ambiental de las lagunas de Charco Azul y El Pondaje,
> que es la zona donde la intervencion tiene impacto ambiental directo y donde los valores de
> referencia son metodologicamente mas apropiados.

**Implicaciones tecnicas:**

- Score actual (10/100) refleja el piso estructural del area urbana densa, no la calidad ambiental de las lagunas.
- El `ref_max = 0.65` es aspiracional para el poligono completo pero apropiado para vegetacion de humedal — la recalibracion de refs ocurre automaticamente al cambiar el area de medicion.
- El sub-poligono (Charco Azul + El Pondaje) es la zona de intervencion directa del proyecto; medir ahi hace el indicador sensible a los cambios reales producidos por la inversion publica.

**Precedente metodologico:**
El _Index of Multiple Deprivation_ (IMD, Reino Unido) utiliza unidades de analisis diferenciadas segun el fenomeno que mide. No todos los indicadores de un indice compuesto tienen que medirse sobre exactamente el mismo poligono.

**Ruta de implementacion (v8):**
1. Obtener o delimitar el GeoJSON del sub-poligono ambiental (Charco Azul + El Pondaje).
2. En `leer_ndvi_tif()`: recortar el raster al sub-poligono en vez del perimetro completo.
3. Recalibrar `ref_min` y `ref_max` con serie historica de NDVI sobre ese sub-poligono.
4. Actualizar nota metodologica a "resuelto".

---

Ultima actualizacion: 2026-03-15 v7.

**Estado operativo final 2025-T4:**
- ITT Global: **52.7/100** · Nivel 2 · Consolidacion (-7.1 vs 2025-T3)
- Indicadores reales: **16/17** (GeoJSON + TIF + Excel) — cobertura 100% con valor para todos los indicadores
- Indicadores manuales/estimados: 1 (aforo Villa del Lago — valor fijo 4.200; pendiente Sec. Deportes)
- Cobertura: 100% (todos con valor)
- Refs anclados a serie historica real: 7/17 (GeoJSON 12 trimestres) · Refs normativa/tecnica: 4/17 · Estimado operativo: 6/17
