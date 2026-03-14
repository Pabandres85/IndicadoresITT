# Proyecto ITT - Pulmon de Oriente

Aplicacion web estatica para visualizacion territorial e indice ITT.
No usa framework ni build step: HTML, CSS y JavaScript vanilla.

## Stack tecnico

- `HTML/CSS/JS` (frontend estatico)
- `Chart.js` para visualizaciones
- `Leaflet` + `Leaflet.markercluster` + `leaflet.heat` para mapa
- `Turf.js` para operaciones geoespaciales en cliente
- `Python` + `openpyxl` para preparacion de datos

## Estructura del repositorio

```text
.
|-- index.html
|-- paginas/
|   |-- pulmon_oriente_impacto_v2.html
|   |-- pulmon_oriente_metodologia.html
|   |-- pulmon_oriente_seguridad.html
|   |-- pulmon_oriente_mapa_v2.html
|   |-- pulmon_oriente_informe-v2.html
|   `-- intervenciones_v1.html
|-- assets/
|   |-- css/
|   `-- js/
|       |-- services/dataService.js
|       |-- index.js
|       |-- informe.js
|       |-- mapa.js
|       `-- intervenciones.js
|-- data/
|   |-- indices/
|   |-- infraestructura/
|   |-- intervenciones/
|   |-- seguridad/
|   |-- equipamientos/
|   |-- ambiente/
|   |-- territorio/
|   `-- excel/
|-- scripts/
|   |-- calcular_itt.py
|   `-- excel_to_json.py
`-- .github/workflows/
```

## Modulos frontend

- `index.html`: landing y navegacion principal.
- `pulmon_oriente_impacto_v2.html`: dashboard ITT (lectura de `data/indices/itt_pulmon.json`).
- `pulmon_oriente_metodologia.html`: metodologia y reglas de calculo ITT.
- `pulmon_oriente_seguridad.html`: panel dinamico de seguridad por tipo de delito.
- `pulmon_oriente_mapa_v2.html`: mapa multivista (infraestructura, seguridad, equipamientos, ambiente).
- `pulmon_oriente_informe-v2.html`: analitica de inversiones.
- `intervenciones_v1.html`: vista distrital de intervenciones.

## Capa de datos en cliente

`assets/js/services/dataService.js` centraliza:

- carga de fuentes base de infraestructura
- cache en memoria y `sessionStorage`
- utilidades de filtrado espacial
- normalizacion de categorias y colores
- agregaciones para KPIs

## Scripts de mantenimiento

### 1) Conversion Excel -> JSON

Archivo: `scripts/excel_to_json.py`

Uso:

```bash
python scripts/excel_to_json.py
python scripts/excel_to_json.py data/excel/archivo.xlsx
```

Requiere:

```bash
pip install openpyxl
```

Salida esperada:

- `data/intervenciones/intervenciones.json`
- `data/intervenciones/intervenciones_meta.json`

### 2) Calculo ITT

Archivo: `scripts/calcular_itt.py`

Uso:

```bash
python scripts/calcular_itt.py
python scripts/calcular_itt.py --input data/excel/indicadores_itt.xlsx --periodo 2025-T4 --version preliminar
```

Salida esperada:

- `data/indices/itt_pulmon.json`

## Ejecucion local

Como es sitio estatico, levantar servidor local desde la raiz:

```bash
python -m http.server 8000
```

Abrir:

- `http://localhost:8000/`

## Flujo tecnico recomendado

1. Actualizar fuentes en `data/` o `data/excel/`.
2. Ejecutar scripts Python cuando aplique.
3. Verificar vistas clave: ITT, Seguridad, Mapa e Informe.
4. Confirmar consola sin errores JS.
5. Commit de cambios de codigo y artefactos permitidos.

## Notas de repositorio

- `.gitignore` excluye documentos locales de contexto que no deben versionarse.
- Si un archivo ya estaba trackeado antes de ignorarlo, debe retirarse del indice con `git rm --cached`.
