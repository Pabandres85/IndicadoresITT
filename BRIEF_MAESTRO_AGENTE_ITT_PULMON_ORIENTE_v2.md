# Brief maestro para agente — Sitio ITT Pulmón de Oriente (v2)

## 1. Objetivo
Construir un **nuevo sitio web** para **Pulmón de Oriente** usando como base la estructura visual y técnica del sitio actual (`page.zip`), pero cambiando el enfoque desde el **seguimiento de intervenciones** hacia la **medición territorial por dimensiones** y el **cálculo del ITT (Índice de Transformación Territorial)**.

El nuevo sitio **no debe cargar data cruda masiva en el frontend**. Debe consumir **JSON y GeoJSON precalculados**, livianos y optimizados por propósito:
- KPIs
- series temporales
- rankings territoriales
- capas geográficas ligeras
- cálculo del ITT
- metadatos y trazabilidad

---

## 2. Contexto funcional

### 2.1 Qué existe hoy
Hay un sitio estático funcional con una base útil para reutilizar:
- `index.html`
- `paginas/pulmon_oriente_informe-v2.html`
- `paginas/pulmon_oriente_mapa_v2.html`
- `paginas/intervenciones_v1.html`
- `paginas/pulmon_oriente_impacto_v2.html` (placeholder)
- JS estático con **Leaflet**, **Turf.js**, **Chart.js** y pipeline simple **Python → JSON**.

### 2.2 Qué debe pasar ahora
Se debe crear un **sitio nuevo** o una **nueva rama funcional del sitio** donde el foco sea:
1. **ITT general de Pulmón de Oriente**
2. **5 dimensiones del ITT**
3. **Indicadores núcleo por dimensión**
4. **Indicadores operativos/complementarios**
5. **Mapa y análisis territorial**
6. **Metodología, trazabilidad y estado de calidad de los datos**

### 2.3 Principio narrativo del sitio
El sitio debe explicar la transformación territorial de Pulmón de Oriente desde dos perspectivas que deben convivir:
- **Infraestructura / intervenciones**
- **Resultados territoriales por dimensión**

Por eso el mapa y el frontend deben poder **alternar dinámicamente** entre:
- capas de infraestructura ya existentes
- capas de seguridad
- capas de movilidad
- capas de entorno urbano
- capas de desarrollo social
- capas de actividad económica

---

## 3. Perfil ITT para Pulmón de Oriente
Usar este perfil de ponderación:

- **Seguridad:** 0.20
- **Entorno urbano:** 0.30
- **Movilidad:** 0.20
- **Desarrollo social:** 0.15
- **Actividad económica:** 0.15

> Nota importante: para Pulmón de Oriente, el peso mayor está en **entorno urbano**.

### 3.1 Niveles interpretativos del ITT
El sitio debe mostrar también el nivel interpretativo:
- **Nivel 1 – Activación:** 0–40
- **Nivel 2 – Consolidación:** 41–60
- **Nivel 3 – Transformación:** 61–80
- **Nivel 4 – Escala:** 81–100

### 3.2 ITT oficial vs ITT preliminar
El sitio debe distinguir explícitamente entre:

#### ITT oficial
Solo puede mostrarse como oficial cuando existan datos suficientes, trazables y metodológicamente válidos para las **5 dimensiones**.

#### ITT preliminar
Debe mostrarse como **preliminar** o **en construcción** cuando:
- falten dimensiones núcleo
- existan dimensiones con datos parciales
- el score use proxies temporales
- una fuente relevante esté en validación o depuración

### 3.3 Regla de visualización de madurez
Si no existen datos suficientes para todas las dimensiones, el sitio debe mostrar:
- `ITT preliminar`
- qué dimensiones están completas
- cuáles están parciales
- cuáles están pendientes
- nivel de confianza del cálculo

---

## 4. Principio arquitectónico clave

### 4.1 Qué NO hacer
No cargar en frontend:
- Excel crudos
- CSV completos muy pesados
- eventos georreferenciados masivos sin filtrar
- toda la historia completa para cada interacción
- cálculos espaciales pesados sobre cientos de miles de registros

### 4.2 Qué SÍ hacer
El frontend debe consumir solo productos derivados:
- JSON de KPIs
- JSON de series mensuales
- JSON de rankings
- GeoJSON de puntos ya filtrados o muestreados
- GeoJSON de agregación territorial (barrios, comunas, polígonos)
- JSON del ITT ya calculado o casi calculado

### 4.3 Regla de oro
**El dashboard es la vitrina, no la bodega de datos.**

### 4.4 Arquitectura conceptual recomendada
La solución debe tener tres capas:

#### Capa 1. Recepción de datos
Recibe y almacena fuentes como:
- Excel
- CSV
- GeoJSON
- Shapefile convertido a GeoJSON
- JSON estructurados
- capas de intervención existentes

#### Capa 2. Preparación / normalización
Realiza:
- homologación de campos
- validación territorial
- filtrado a Pulmón de Oriente
- agregaciones por período y dimensión
- construcción de indicadores
- generación de GeoJSON livianos

#### Capa 3. Visualización
Consume solo:
- KPIs
- series
- rankings
- GeoJSON filtrados
- metadatos
- score del ITT

---

## 5. Fuentes y estado actual de disponibilidad

### 5.1 Fuentes ya identificadas

#### Seguridad / convivencia
Disponibles o parcialmente disponibles a partir de los archivos revisados:
- comparendos
- homicidios
- hurtos
- violencia intrafamiliar
- VBG

#### Sitio actual / intervenciones
Disponibles en `page.zip`:
- `data/Total_secretarias.geojson`
- `data/poligonos.geojson`
- `data/tramos_oriente.geojson`
- `data/intervenciones.json`
- `data/intervenciones_meta.json`

### 5.2 Fuentes que faltan o están pendientes
Para completar Pulmón de Oriente se requieren nuevas fuentes:
- siniestralidad vial
- lesionados y muertes por tránsito
- velocidad promedio / tiempos de viaje
- inventario de luminarias funcionales
- km de vía intervenida / m de andenes
- NDVI / cobertura vegetal
- uso del espacio público / aforos
- acceso a servicios sociales
- negocios activos
- licencias / actividad comercial
- valor catastral promedio

### 5.3 Estado actual por dimensión
- **Seguridad:** alta disponibilidad
- **Entorno urbano:** disponibilidad parcial
- **Movilidad:** baja disponibilidad
- **Desarrollo social:** baja disponibilidad
- **Actividad económica:** baja disponibilidad

### 5.4 Advertencia crítica conocida
La fuente de **hurtos 2025** presenta inconsistencias territoriales derivadas de un **corrimiento de columnas** en la fuente original. Aunque la geometría del punto puede servir para exploración visual, **no debe entrar al cálculo oficial** hasta que se depure.

### 5.5 Regla para nuevas fuentes similares
Así como llegó la capa de hurtos, pueden llegar otras capas similares en formato **GeoJSON/JSON** ya recortadas a Pulmón o a otro territorio. El agente debe asumir que:
- pueden venir con buena geometría pero mala calidad atributiva
- pueden requerir homologación de nombres de campos
- pueden requerir validación de comuna/barrio/territorio
- pueden traer años o bloques temporales parcialmente dañados

Por tanto, **ninguna fuente nueva debe consumirse directa en frontend sin pasar por la capa de preparación**.

---

## 6. Matriz de indicadores para el sitio

## 6.1 Seguridad
### Indicadores núcleo ITT
- Homicidios
- Hurtos
- Violencia intrafamiliar

### Indicadores de apoyo
- Riñas / conflictividad
- VBG
- Comparendos de convivencia

> Regla: **comparendos de convivencia** se muestran como indicador complementario de contexto y **no** hacen parte del subíndice núcleo de seguridad, salvo decisión metodológica explícita.

### Fórmulas sugeridas
- `homicidios = conteo de eventos dentro del polígono y período`
- `hurtos = conteo de eventos dentro del polígono y período`
- `violencia_intrafamiliar = conteo de eventos dentro del polígono y período`
- `variacion_pct = ((valor_actual - valor_periodo_prev) / valor_periodo_prev) * 100`

### Subíndice sugerido
- 40% homicidios
- 35% hurtos
- 25% violencia intrafamiliar

---

## 6.2 Movilidad
### Indicadores núcleo ITT
- Siniestralidad vial
- Accidentes con lesionados
- Velocidad promedio del corredor

### Indicadores de apoyo
- Muertes por accidente de tránsito
- Accesibilidad peatonal / continuidad de andenes

### Fórmulas sugeridas
- `siniestralidad_vial = conteo de siniestros en el polígono/corredor`
- `lesionados = conteo de siniestros con lesionados`
- `velocidad_promedio = promedio de velocidad en corredor priorizado`

### Subíndice sugerido
- 40% siniestralidad vial
- 30% lesionados
- 30% velocidad promedio

---

## 6.3 Entorno urbano
### Indicadores núcleo ITT
- km de vía intervenida
- m de andenes construidos o recuperados
- luminarias funcionales
- área efectiva de espacio público recuperado
- NDVI / cobertura vegetal

### Indicadores de apoyo
- parques o espacios públicos intervenidos
- inversión asociada
- estado de vía

### Fórmulas sugeridas
- `km_via = suma de km ejecutados/entregados`
- `andenes_m = suma de metros intervenidos`
- `luminarias_funcionales = numero o porcentaje operativo`
- `espacio_publico_recuperado_m2 = suma de m2`
- `ndvi = promedio NDVI del polígono`

### Subíndice sugerido
- 25% km de vía
- 20% andenes
- 20% luminarias funcionales
- 15% espacio público recuperado
- 20% NDVI

### Regla conceptual
Distinguir entre:
- **indicadores de ejecución física (output)**
- **indicadores de transformación territorial (outcome)**

El ITT debe priorizar outcomes cuando existan. Si en fase 1 solo existen outputs confiables, la dimensión debe marcarse como **parcial**.

---

## 6.4 Desarrollo social
### Indicadores núcleo ITT
- Uso del espacio público
- Uso de canchas, parques y equipamientos
- Acceso a servicios sociales

### Indicadores de apoyo
- Asistencia a actividades comunitarias
- Percepción de seguridad
- Confianza institucional
- Permanencia escolar

### Fórmulas sugeridas
- `uso_espacio_publico = aforo promedio o proxy de uso`
- `uso_equipamientos = visitas/aforo`
- `acceso_servicios = cobertura % o beneficiarios en territorio`

### Subíndice sugerido
- 35% uso del espacio público
- 35% uso de equipamientos
- 30% acceso a servicios sociales

---

## 6.5 Actividad económica
### Indicadores núcleo ITT
- Negocios activos en el área
- Licencias / actividad comercial
- Valor catastral promedio

### Indicadores de apoyo
- Dinámica predial o inmobiliaria
- Formalización de negocios
- Aforo peatonal en corredores

### Fórmulas sugeridas
- `negocios_activos = conteo de establecimientos activos`
- `licencias = conteo de licencias/actividad formal`
- `valor_catastral_prom = promedio COP/m2`

### Subíndice sugerido
- 35% negocios activos
- 25% licencias
- 40% valor catastral promedio

---

## 7. Qué mostrar en el sitio

## 7.1 Inicio / dashboard ejecutivo
Debe mostrar:
- ITT general de Pulmón de Oriente
- puntaje por dimensión
- nivel interpretativo (Activación / Consolidación / Transformación / Escala)
- fecha de corte
- radar por dimensiones
- resumen ejecutivo de hallazgos
- estado del cálculo: oficial o preliminar
- nivel de confianza

## 7.2 Página Seguridad
Debe mostrar:
- tarjetas KPI: homicidios, hurtos, VIF, VBG, comparendos
- variación frente a período anterior
- serie mensual
- top 5 barrios
- mapa de eventos / clusters / heatmap

## 7.3 Página Movilidad
Debe mostrar:
- siniestralidad vial
- lesionados
- velocidad promedio
- tendencia temporal
- mapa de corredores o puntos

## 7.4 Página Entorno urbano
Debe mostrar:
- km de vía
- andenes
- luminarias
- espacio público recuperado
- NDVI
- mapa de intervenciones y tramos

## 7.5 Página Desarrollo social
Debe mostrar:
- uso del espacio público
- uso de equipamientos
- acceso a servicios
- actividades comunitarias
- series o comparativos territoriales

## 7.6 Página Actividad económica
Debe mostrar:
- negocios activos
- licencias
- valor catastral promedio
- dinámica comercial/predial
- mapas o rankings por microzona

## 7.7 Página Metodología
Debe incluir:
- fórmula del ITT
- ponderaciones de Pulmón
- definición de cada indicador
- fuente, frecuencia y fecha de corte
- reglas de calidad de datos
- advertencias metodológicas
- estado de disponibilidad por dimensión

## 7.8 Página Mapa integrado / explorador territorial
Debe permitir cambiar dinámicamente entre capas de:
- infraestructura / intervenciones
- seguridad
- movilidad
- entorno urbano
- desarrollo social
- actividad económica

Funciones mínimas esperadas:
- activar y desactivar capas
- leyenda dinámica
- filtro por período
- filtros por dimensión o fuente
- popups con atributos clave
- mantener el polígono de Pulmón de Oriente como referencia

---

## 8. Contratos de datos que debe consumir el frontend
El agente debe generar o pedir estos archivos:

### 8.1 Resumen ITT
`data/itt/itt_resumen_pulmon.json`
```json
{
  "territorio": "Pulmón de Oriente",
  "fecha_corte": "2026-03-31",
  "itt_total": 58.4,
  "nivel": "Consolidación",
  "estado_calculo": "preliminar",
  "nivel_confianza": "medio",
  "dimensiones_completas": ["seguridad"],
  "dimensiones_parciales": ["entorno_urbano"],
  "dimensiones_pendientes": ["movilidad", "desarrollo_social", "actividad_economica"],
  "dimensiones": {
    "seguridad": 52.1,
    "entorno_urbano": 68.7,
    "movilidad": 41.5,
    "desarrollo_social": 46.2,
    "actividad_economica": 33.8
  },
  "ponderaciones": {
    "seguridad": 0.20,
    "entorno_urbano": 0.30,
    "movilidad": 0.20,
    "desarrollo_social": 0.15,
    "actividad_economica": 0.15
  }
}
```

### 8.2 Catálogo de indicadores
`data/itt/catalogo_indicadores.json`
```json
[
  {
    "id": "homicidios",
    "dimension": "seguridad",
    "nombre": "Homicidios",
    "rol": "nucleo_itt",
    "unidad": "casos",
    "frecuencia": "mensual",
    "sentido": "menor_es_mejor",
    "fuente": "Seguridad y Justicia",
    "metodo_normalizacion": "benchmark_historico",
    "estado_disponibilidad": "completo"
  }
]
```

### 8.3 KPIs por dimensión
Archivos sugeridos:
- `data/itt/seguridad_kpis.json`
- `data/itt/movilidad_kpis.json`
- `data/itt/entorno_urbano_kpis.json`
- `data/itt/desarrollo_social_kpis.json`
- `data/itt/actividad_economica_kpis.json`

Estructura sugerida:
```json
{
  "fecha_corte": "2026-03-31",
  "estado_calculo": "preliminar",
  "kpis": [
    {
      "id": "homicidios",
      "nombre": "Homicidios",
      "valor": 14,
      "unidad": "casos",
      "variacion_pct": -12.5,
      "sentido": "menor_es_mejor",
      "fuente": "Seguridad y Justicia",
      "metodologia": "conteo de eventos dentro del polígono"
    }
  ]
}
```

### 8.4 Series temporales
`data/itt/series_mensuales.json`
```json
{
  "seguridad": {
    "homicidios": [{"periodo":"2025-01","valor":4}],
    "hurtos": [{"periodo":"2025-01","valor":72}]
  }
}
```

### 8.5 Rankings territoriales
`data/itt/rankings_barrios.json`
```json
{
  "seguridad": {
    "hurtos_top": [
      {"barrio":"X","valor":31},
      {"barrio":"Y","valor":25}
    ]
  }
}
```

### 8.6 Capas geográficas
Archivos sugeridos:
- `data/geo/pulmon_oriente_poligono.geojson`
- `data/geo/mapa_infraestructura.geojson`
- `data/geo/mapa_seguridad.geojson`
- `data/geo/mapa_movilidad.geojson`
- `data/geo/mapa_entorno_urbano.geojson`
- `data/geo/mapa_desarrollo_social.geojson`
- `data/geo/mapa_actividad_economica.geojson`
- `data/geo/microzonas.geojson`
- `data/geo/barrios_pulmon.geojson`

### 8.7 Metadatos
`data/itt/meta.json`
```json
{
  "fecha_corte": "2026-03-31",
  "version": "1.0.0",
  "estado_calculo": "preliminar",
  "fuentes": [
    "Seguridad y Justicia",
    "Infraestructura",
    "Movilidad"
  ],
  "observaciones": [
    "Hurtos 2025 requiere depuración antes de entrar al cálculo oficial"
  ]
}
```

---

## 9. Reglas para acomodar la data entrante

### 9.1 Supuesto de entrada
El agente debe asumir que pueden llegar archivos como:
- `...GeoJson.geojson`
- `...Json.json`
- capas recortadas a Pulmón
- capas por dimensión
- capas de puntos o polígonos
- insumos por año o consolidado 2023–2025

### 9.2 Pipeline mínimo de preparación
Toda nueva fuente debe pasar por este proceso:
1. **Lectura de campos**
2. **Homologación de nombres**
3. **Validación de geometría**
4. **Validación territorial**
5. **Validación temporal**
6. **Clasificación por dimensión**
7. **Filtrado a Pulmón de Oriente**
8. **Construcción de productos derivados para frontend**

### 9.3 Homologación mínima de campos
Cuando lleguen capas similares a hurtos u otras capas geo, el pipeline debe acomodar como mínimo a este esquema lógico cuando aplique:
- `fuente`
- `dimension`
- `categoria_principal`
- `subcategoria`
- `tipo_evento`
- `fecha_evento`
- `hora_evento`
- `anio`
- `mes`
- `periodo`
- `direccion`
- `cod_barrio`
- `nom_barrio`
- `cod_territorio_raw`
- `nom_territorio_raw`
- `cod_territorio_norm`
- `nom_territorio_norm`
- `tipo_territorio`
- `territorio_proyecto`
- `estado_calidad`
- `score_calidad`

### 9.4 Regla de control de calidad
Si una capa trae:
- comuna en cero
- barrio numérico donde debería haber nombre
- inconsistencias comuna/barrio
- fecha o período mal interpretado
- columnas corridas

entonces esa fuente debe quedar en estado:
- `revision`
- `parcial`
- o `excluida del ITT oficial`

### 9.5 Regla para geometría válida
Las capas geográficas del sitio deben salir en:
- **EPSG:4326**
- GeoJSON válido
- coordenadas en orden `[longitud, latitud]`

---

## 10. Fórmula de cálculo del ITT

## 10.1 Regla general
Cada indicador debe transformarse a escala **0–100**.

### Si el indicador es positivo (más alto = mejor)
Usar normalización directa.

### Si el indicador es negativo (más alto = peor)
Usar normalización inversa.
Ejemplo:
- homicidios
- hurtos
- siniestralidad vial
- violencia intrafamiliar

## 10.2 Regla de normalización
Cada indicador debe normalizarse usando una referencia explícita y declarada en metadatos. No se deben asumir rangos arbitrarios.

Referencias válidas:
- línea base histórica
- meta definida por política pública
- benchmark de ciudad
- territorio comparable
- rango técnico validado por el equipo

## 10.3 Fórmula sugerida
```text
score_dimension = suma(score_indicador_normalizado * peso_indicador)
```

```text
ITT_Pulmon =
  (Seguridad * 0.20) +
  (Entorno_urbano * 0.30) +
  (Movilidad * 0.20) +
  (Desarrollo_social * 0.15) +
  (Actividad_economica * 0.15)
```

## 10.4 Reglas metodológicas mínimas
- no mezclar comparendos con delitos en un mismo indicador núcleo
- no usar indicadores de apoyo dentro del ITT oficial salvo decisión explícita
- registrar fecha de corte en cada JSON
- separar siempre `valor`, `variacion_pct`, `unidad`, `fuente`, `metodologia`
- permitir recalcular el ITT cuando entren nuevas fuentes

---

## 11. Reglas de calidad de datos

### 11.1 Reglas obligatorias
- toda fila debe tener fuente
- todo KPI debe tener fecha de corte
- todo indicador debe declarar unidad y frecuencia
- toda capa geográfica debe usar CRS consistente
- toda serie temporal debe estar normalizada por período (`YYYY-MM` o `YYYY-Qn`)

### 11.2 Reglas específicas ya conocidas
- **hurtos 2025** no debe entrar al cálculo oficial hasta depuración
- registros malformados deben aislarse en dataset de revisión, no mezclarse con la vista principal
- el frontend no debe calcular point-in-polygon masivo sobre cientos de miles de eventos crudos

### 11.3 Regla de fragmentación de capas
Las capas de eventos deben entregarse:
- filtradas a Pulmón de Oriente
- por período o por fuente si superan tamaño razonable
- con propiedades mínimas necesarias para filtros y popups

Ejemplos válidos:
- `hurtos_pulmon_2023.geojson`
- `hurtos_pulmon_2024.geojson`
- `homicidios_pulmon.geojson`
- `comparendos_pulmon.geojson`

---

## 12. Recomendación técnica para el agente

## 12.1 Se puede reutilizar del sitio actual
- estructura estática HTML/CSS
- patrón visual de landing + páginas internas
- Leaflet para mapa
- Chart.js para gráficas
- lógica de cache y carga modular
- componentes de infraestructura ya existentes

## 12.2 Lo que sí debe cambiar
- crear nuevo `DataService` orientado a ITT
- dejar de pensar solo en “proyectos/intervenciones”
- consumir JSON por dimensión
- consumir GeoJSON optimizados
- tener una página de metodología
- tener un motor claro para el score del ITT
- tener un controlador de capas para mapa dinámico

## 12.3 Librerías permitidas / recomendadas
- Leaflet
- Turf.js (solo para operaciones ligeras o ya filtradas)
- Chart.js
- opcional: Tabulator o grid liviano para tablas
- opcional: noUiSlider para filtros temporales

## 12.4 No recomendado
- cargar 500k+ eventos en cliente
- recalcular todo el ITT en el navegador con raw data
- depender del HTML como almacenamiento de indicadores

---

## 13. Estructura sugerida del nuevo proyecto
Se debe reutilizar la base visual y de navegación del sitio actual de Pulmón de Oriente, pero reorganizando el proyecto para consumir productos de datos por dimensión del ITT.

```text
/src
  /assets
    /css
    /img
  /data
    /itt
      itt_resumen_pulmon.json
      catalogo_indicadores.json
      seguridad_kpis.json
      movilidad_kpis.json
      entorno_urbano_kpis.json
      desarrollo_social_kpis.json
      actividad_economica_kpis.json
      series_mensuales.json
      rankings_barrios.json
      meta.json
    /geo
      pulmon_oriente_poligono.geojson
      barrios_pulmon.geojson
      microzonas.geojson
      mapa_infraestructura.geojson
      mapa_seguridad.geojson
      mapa_movilidad.geojson
      mapa_entorno_urbano.geojson
      mapa_desarrollo_social.geojson
      mapa_actividad_economica.geojson
  /js
    data-service-itt.js
    itt-engine.js
    charts.js
    maps.js
    layers-controller.js
    ui.js
  /paginas
    index.html
    seguridad.html
    movilidad.html
    entorno_urbano.html
    desarrollo_social.html
    actividad_economica.html
    metodologia.html
    mapa_integrado.html
```

---

## 14. Comportamiento esperado del mapa dinámico
El mapa debe poder trabajar en dos modos principales:

### Modo A. Infraestructura
Reutiliza lo que hoy ya existe en Pulmón de Oriente:
- tramos
- intervenciones
- puntos de infraestructura
- polígonos de actuación

### Modo B. Dimensiones / ITT
Permite cambiar a capas como:
- seguridad
- movilidad
- entorno urbano
- desarrollo social
- actividad económica

### Requisitos funcionales mínimos
- selector de dimensión o capa activa
- posibilidad de superponer infraestructura + una dimensión
- leyenda según capa activa
- popup con atributos resumidos
- filtro temporal cuando aplique
- posibilidad de apagar / encender capas
- mantener el perímetro de Pulmón visible

### Requisito narrativo
El mapa no debe verse como dos productos separados. Debe poder mostrar cómo la **infraestructura existente** se relaciona con las **capas analíticas por dimensión**.

---

## 15. Criterios de aceptación para el agente
El trabajo se considera correcto si:
1. El sitio muestra ITT total y puntaje por dimensión.
2. Cada dimensión tiene KPIs, serie temporal y explicación metodológica.
3. El frontend consume JSON livianos y no data cruda masiva.
4. El mapa funciona con capas filtradas para Pulmón de Oriente.
5. El cálculo del ITT es trazable y reproducible.
6. Cada indicador tiene fuente, fecha de corte y frecuencia.
7. El sitio permite crecer por fases cuando entren nuevas fuentes.
8. El mapa puede alternar entre infraestructura y otras capas temáticas.
9. Las fuentes problemáticas quedan marcadas como preliminares o en revisión.

---

## 16. Resultado esperado de fase 1
Fase 1 debe quedar con:
- sitio funcional
- ITT preliminar de Pulmón
- Seguridad sólida
- Entorno urbano parcial
- páginas estructuradas por dimensión
- metodología visible
- pipeline de JSONs listo para recibir más datos
- mapa dinámico con infraestructura + seguridad como mínimo

---

## 17. Mensaje guía para el agente
**No construyas un dashboard que intente absorber toda la data cruda. Construye una vitrina de indicadores territoriales para Pulmón de Oriente, con un modelo de datos preprocesado, trazable y escalable, donde el ITT sea el eje narrativo principal. Reutiliza la base visual de infraestructura existente, pero permite alternar dinámicamente entre infraestructura y las capas analíticas de las demás dimensiones.**
