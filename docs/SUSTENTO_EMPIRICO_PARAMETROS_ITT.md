# Sustento empírico para parámetros ref_min y ref_max
## Consolidado técnico de indicadores y evidencia de soporte para la calibración del ITT

**Última actualización:** 2026-03-16
**Versión ITT de referencia:** v7 · ITT 2025-T4 = 46.9

---

## Propósito

Ordenar la evidencia disponible que sustenta los valores de referencia usados en la normalización de indicadores del ITT.

## Conclusión clave

El 54% del peso del ITT descansa sobre referencias sin serie histórica suficiente, por lo que el principal riesgo metodológico del modelo sigue estando en la debilidad del anclaje empírico de una parte importante de los indicadores.

---

## Alcance del documento

Este anexo reorganiza la información del archivo base y la presenta con una estructura metodológica más clara. Los datos, rangos y observaciones se conservan; únicamente se mejora su jerarquía, lectura y presentación para revisión académica y técnica.

## Criterios de lectura

| Etiqueta | Descripción |
|---|---|
| **Serie real** | Indicadores con soporte en series históricas trimestrales completas y comparables. |
| **Serie anual por diseño** | Indicadores medidos a frecuencia anual por la naturaleza de su fuente (año lectivo, corte institucional). No es una debilidad — es la granularidad disponible y metodológicamente apropiada. |
| **Dato débil** | Indicadores apoyados en un único corte, dato manual o supuesto de diseño. |

---

## 1. Indicadores con serie histórica real

Serie GeoJSON de 12 trimestres (2023-T1 a 2025-T4). En este grupo, los parámetros de referencia muestran el mejor sustento empírico disponible.

| Indicador | Dim | Val T4-25 | ref_min | ref_max | Obs. min (trim) | Obs. max (trim) | Sustento |
|---|---|---:|---:|---:|---|---|---|
| Homicidios | Seguridad | 36 | 5 | 50 | 9 (2025-T3) | 38 (2023-T3) | Serie real 12 trim. Refs dan margen operacional sobre el rango observado. |
| Hurtos | Seguridad | 260 | 200 | 450 | 259 (2023-T4) | 434 (2023-T1) | Serie real 12 trim. Refs prácticamente pegados al rango observado. |
| Siniestralidad vial | Movilidad | 63 | 30 | 80 | 47 (2024-T2) | 68 (2023-T3) | Serie real 12 trim. ref_min=30 da margen aspiracional; ref_max=80 supera el histórico. |
| Accidentes c/lesionados | Movilidad | 53 | 20 | 65 | 42 (2024-T2) | 56 (2023-T3) | Serie real 12 trim. ref_max=65 supera el observado (56), da margen. |
| Muertes en vía | Movilidad | 6 | 1 | 10 | 2 (2024-T1) | 6 (varios) | Serie real 12 trim. ref_max=10 supera histórico; ref_min=1 es aspiracional. |
| VIF | Cohesión | 105 | 60 | 200 | 88 (2023-T4) | 189 (2025-T3) | Serie real 12 trim. Refs casi exactos al rango observado. |
| Riñas | Cohesión | 127 | 20 | 160 | 38 (2023-T4) | 144 (2025-T3) | Serie real 12 trim. ref_min=20 aspiracional; ref_max=160 sobre el histórico. |

---

## 2. Indicadores con serie anual por diseño

Indicadores con tres cortes anuales (2023, 2024, 2025). La frecuencia anual es inherente a la fuente — el sistema educativo reporta por año lectivo, no por trimestre. Esta clasificación **no constituye una debilidad metodológica**, sino el reflejo de la granularidad disponible y apropiada para estos fenómenos. Tres cortes anuales son suficientes para observar tendencia general, aunque no permiten validar extremos de referencia con la misma solidez que una serie trimestral.

| Indicador | Dim | Val 2025 | ref_min | ref_max | Obs. min | Obs. max | Sustento |
|---|---|---:|---:|---:|---|---|---|
| Matrícula escolar | Educ. | 50,336 | 40,000 | 58,000 | 50,336 (2025) | 53,746 (2023) | Serie anual 3 cortes (año lectivo). Toda la serie cae en rango medio (50K–54K). Refs fuera del rango observado — dan margen para crecimiento y contracción estructural. |
| Deserción escolar | Educ. | 4.3% | 1.0 | 10.0 | 4.3% (2025) | 5.3% (2024) | Serie anual 3 cortes. Rango observado estrecho (4.3–5.3). ref_min=1.0 es aspiracional (no observado). |
| Repitencia escolar | Educ. | 8.4% | 1.0 | 15.0 | 8.4% (2025) | 9.4% (2023) | Serie anual 3 cortes. Rango observado (8.4–9.4) está en el centro del rango de refs. |
| Estudiantes/docente | Educ. | 27.1 | 18 | 40 | 26.7 (2024) | 28.3 (2023) | Serie anual 3 cortes. Rango observado (26.7–28.3) muy estrecho respecto a los refs — margen para variación estructural. |

---

## 3. Indicadores con un solo punto de datos o dato manual

Este grupo concentra la evidencia más débil. Los valores de referencia dependen de juicio experto, rangos conceptuales o supuestos de diseño, más que de series observadas.

| Indicador | Dim | Valor | ref_min | ref_max | Sustento |
|---|---|---:|---:|---:|---|
| ~~Velocidad corredor~~ | ~~Movilidad~~ | ~~26.8 km/h~~ | ~~12~~ | ~~32~~ | **Retirada del modelo v7.** Dato único sin serie histórica generaba score 74/100 inflando Movilidad. Queda como dato de contexto. |
| NDVI cobertura vegetal | Entorno | 0.20 | 0.15 | 0.65 | Un solo TIF (imagen 2025). ref_max=0.65 es muy aspiracional para zona urbana densa. En v8 se recalculará sobre sub-polígono ambiental. |
| Área verde neta | Entorno | 1,699,769 m² | 500,000 | 3,000,000 | Un solo TIF. ref_max=3M equivale al ~25% del polígono — supuesto de diseño. Misma limitación v7 que NDVI. |
| Déficit AHDI | Entorno | 46.4% pend. | 10 | 100 | Escala conceptual 0–100, no anclada a observación histórica del polígono. |
| Conc. vulnerabilidad | Cohesión | 54.1 p/1K | 30 | 160 | Un solo corte (2025). Refs son rangos sectoriales sin historia local. |
| Cobertura deportiva activa | Educ. | 3,877 reg. | 1,000 | 7,000 | **Dato proxy.** 3,877 personas registradas activas en 25 escenarios deportivos de la Comuna 14 (formulario oficial Sec. Deportes, marzo 2024). No es conteo directo de asistencia — es lo que cada escenario reportó tener activo. Referencias visuales de contexto: polideportivo Villa San Marcos y cancha múltiple Los Lagos. Aforo directo Villa del Lago pendiente. |

---

## 4. Lectura ejecutiva para el equipo

Resumen del peso metodológico de cada grupo dentro del ITT.

| Estado | Indicadores | Peso acumulado en el ITT |
|---|---:|---:|
| Serie real — refs anclados a serie trimestral 12 cortes | 7 | ~35% |
| Serie anual por diseño — 3 cortes anuales (apropiado para la fuente) | 4 | ~11% |
| Dato débil — juicio experto / único dato / proxy | 6 | ~54% |

### Implicación para la lectura del ITT

El ITT es un índice de seguimiento territorial operativo, no un modelo econométrico de precisión. Los indicadores de "dato débil" no invalidan el índice — lo contextualizan. La lectura correcta es:

- Los movimientos del ITT explicados principalmente por los **7 indicadores de serie real** (35% de peso, 12 trimestres de datos) son los más confiables y deben jerarquizarse en la narrativa.
- Los **4 indicadores de educación** (11% del peso) son estables por diseño y se actualizan anualmente — su variación es estructuralmente lenta.
- Los **6 indicadores de dato débil** (54% del peso) son los que más se beneficiarán de la mejora continua de fuentes: NDVI sub-polígono v8, serie histórica de velocidad, aforo deportivo directo.

---

## 5. Hoja de ruta de fortalecimiento empírico

| Indicador | Acción de mejora | Prioridad |
|---|---|---|
| NDVI / Área verde | Recalcular sobre sub-polígono ambiental (Charco Azul + El Pondaje) — v8 | Alta |
| Cobertura deportiva activa | Obtener aforo directo Villa del Lago (Sec. Deportes) | Media |
| Velocidad corredor | Acumular cortes trimestrales Waze for Cities · reintegrar al modelo cuando haya serie | Media |
| Conc. vulnerabilidad | Acumular cortes anuales de caracterización Sub PyE | Baja |
| Matrícula / Deserción / Repitencia / Ratio docente | Continuar actualización anual — granularidad apropiada por diseño | Baja |
