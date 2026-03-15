"""
calcular_itt.py  v2
===================
Motor de cálculo del ITT — Pulmón de Oriente — Cali 2024-2027.

Lee directamente los GeoJSON de data/ y genera data/indices/itt_pulmon.json.

Fuentes automáticas (GeoJSON):
  data/seguridad/hurtos/        → hurtos por período (FECHA_HECH)
  data/seguridad/homicidios/    → homicidios por período (FECHA_HECH)
  data/seguridad/violencia/     → VIF por período · VBG total 2025
  data/seguridad/institucional/ → CAI activos (conteo)
  data/infraestructura/         → polígonos obra (conteo) · tramos viales (km Haversine)
  data/equipamientos/           → sedes educativas (conteo)
  data/ambiente/                → árboles vivos (conteo)
  data/vivienda/                → polígonos AHDI (conteo+ha) · viviendas mejoramiento (suma)

Fuentes manuales (JSON):
  data/indices/indicadores_manuales.json
    → riñas, siniestralidad, lesionados, muertes en vía, velocidad,
      NDVI, área verde, déficit habitacional,
      matrícula, deserción, repitencia, estudiantes/docente, aforo,
      concentración de vulnerabilidad y barrios (ranking ITT estimado por barrio)

Uso:
  python scripts/calcular_itt.py                                 # período actual
  python scripts/calcular_itt.py --periodo 2025-T4               # período específico
  python scripts/calcular_itt.py --periodo 2025-T4 --version oficial
  python scripts/calcular_itt.py --generar-manuales              # crea/actualiza manuales.json
"""

import json
import math
import argparse
from pathlib import Path
from datetime import datetime, date
from collections import defaultdict

# ── RUTAS BASE ────────────────────────────────────────────────────────────────
ROOT  = Path(__file__).resolve().parent.parent
DATA  = ROOT / "data"
OUT   = DATA / "indices" / "itt_pulmon.json"
HIST  = DATA / "indices" / "itt_historico.json"
MAN   = DATA / "indices" / "indicadores_manuales.json"


# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE DIMENSIONES
# ══════════════════════════════════════════════════════════════════════════════

DIMENSIONES = {
    "seguridad": {
        "nombre": "Seguridad",
        "icono": "shield",
        "peso": 0.30,
        "color": "#C1272D",
        "indicadores": [
            {
                "id": "homicidios", "oficial": True, "inverso": True,
                "nombre": "Homicidios en polígono (trimestral)",
                "unidad": "casos",
                "fuente": "Observatorio de Seguridad y Justicia / SIEDCO",
                "ref_min": 5, "ref_max": 50,   # anclado a serie real C13-C14: min=9 max=38 (2023-2025)
                "gis_dir": "seguridad/homicidios", "gis_tipo": "conteo_periodo",
                "gis_campo_fecha": "FECHA_HECH",
            },
            {
                "id": "hurtos", "oficial": True, "inverso": True,
                "nombre": "Hurtos en polígono (trimestral)",
                "unidad": "casos",
                "fuente": "Observatorio de Seguridad y Justicia / SIEDCO",
                "ref_min": 200, "ref_max": 450,  # anclado a serie real C13-C14: min=259 max=434 (2023-2025)
                "gis_dir": "seguridad/hurtos", "gis_tipo": "conteo_periodo",
                "gis_campo_fecha": "FECHA_HECH",
            },
        ],
    },
    "movilidad": {
        "nombre": "Movilidad",
        "icono": "route",
        "peso": 0.25,
        "color": "#00796B",
        "indicadores": [
            {
                "id": "siniestralidad_vial", "oficial": True, "inverso": True,
                "nombre": "Siniestralidad vial (accidentes)",
                "unidad": "eventos",
                "fuente": "Secretaría de Movilidad · verificado GIS",
                "ref_min": 30, "ref_max": 80,   # anclado a serie real C13-C14: min=47 max=68 (2023-2025)
                "gis_dir": "movilidad", "gis_tipo": "conteo_periodo",
                "gis_patron": "SINIESTROS", "gis_campo_fecha": "Fecha",
            },
            {
                "id": "accidentes_lesionados", "oficial": True, "inverso": True,
                "nombre": "Accidentes con lesionados",
                "unidad": "eventos",
                "fuente": "Secretaría de Movilidad · verificado GIS",
                "ref_min": 20, "ref_max": 65,   # anclado a serie real C13-C14: min=42 max=56 (2023-2025)
                "gis_dir": "movilidad", "gis_tipo": "conteo_periodo",
                "gis_patron": "SINIESTROS", "gis_campo_fecha": "Fecha",
                "gis_filtro": {"Tipo_Confi": "Lesiones"},
            },
            {
                "id": "muertes_via", "oficial": True, "inverso": True,
                "nombre": "Muertes en vía",
                "unidad": "casos",
                "fuente": "Secretaría de Movilidad · verificado GIS",
                "ref_min": 1, "ref_max": 10,    # anclado a serie real C13-C14: min=2 max=6 (2023-2025)
                "gis_dir": "movilidad", "gis_tipo": "conteo_periodo",
                "gis_patron": "SINIESTROS", "gis_campo_fecha": "Fecha",
                "gis_filtro": {"Tipo_Confi": "Mortal"},
            },
            {
                "id": "velocidad_corredor", "oficial": True, "inverso": False,
                "nombre": "Velocidad promedio del corredor",
                "unidad": "km/h",
                "fuente": "Secretaría de Movilidad / Waze for Cities 2025",
                "ref_min": 12.0, "ref_max": 32.0,
            },
        ],
    },
    "entorno_urbano": {
        "nombre": "Entorno Urbano",
        "icono": "city",
        "peso": 0.20,
        "color": "#1565C0",
        "indicadores": [
            {
                "id": "ndvi_cobertura_vegetal", "oficial": True, "inverso": False,
                "nombre": "NDVI / cobertura vegetal",
                "unidad": "índice",
                "fuente": "Copernicus / Sentinel-2 · TIF procesado",
                "ref_min": 0.15, "ref_max": 0.65,
            },
            {
                "id": "area_verde_neta", "oficial": True, "inverso": False,
                "nombre": "Área verde neta",
                "unidad": "m²",
                "fuente": "Copernicus / Sentinel-2 · NDVI ≥ 0.20",
                "ref_min": 500000, "ref_max": 3000000,  # ref_max = 25% del poligono (12km2); anterior 300k era irreal
            },
            {
                "id": "deficit_habitacional_cualitativo", "oficial": True, "inverso": True,
                "nombre": "Déficit habitacional cualitativo",
                "unidad": "% pendiente",
                "fuente": "Secretaría de Vivienda / AHDI 2024-2026",
                "ref_min": 10.0, "ref_max": 100.0,
            },
        ],
    },
    "educacion_desarrollo": {
        "nombre": "Educación y Desarrollo",
        "icono": "school",
        "peso": 0.13,
        "color": "#6A1B9A",
        "indicadores": [
            {
                "id": "matricula_escolar", "oficial": True, "inverso": False,
                "nombre": "Matrícula escolar · Territorio Pulmón",
                "unidad": "estudiantes",
                "fuente": "Secretaría de Educación / Indicadores Sectoriales",
                "ref_min": 40000, "ref_max": 58000,
                "gis_tipo": "excel_edu", "edu_campo": "matricula",
                # edu_sector omitido → usa EDU_SECTOR global ("total")
            },
            {
                "id": "desercion_escolar", "oficial": True, "inverso": True,
                "nombre": "Deserción escolar · Territorio Pulmón",
                "unidad": "%",
                "fuente": "Secretaría de Educación / Indicadores Sectoriales",
                "ref_min": 1.0, "ref_max": 10.0,
                "gis_tipo": "excel_edu", "edu_campo": "tasa_desercion",
            },
            {
                "id": "repitencia_escolar", "oficial": True, "inverso": True,
                "nombre": "Repitencia escolar · Territorio Pulmón",
                "unidad": "%",
                "fuente": "Secretaría de Educación / Indicadores Sectoriales",
                "ref_min": 1.0, "ref_max": 15.0,
                "gis_tipo": "excel_edu", "edu_campo": "tasa_repitencia",
            },
            {
                "id": "estudiantes_por_docente", "oficial": True, "inverso": True,
                "nombre": "Estudiantes por docente · Territorio Pulmón",
                "unidad": "ratio",
                "fuente": "Secretaría de Educación / Indicadores Sectoriales",
                "ref_min": 18.0, "ref_max": 40.0,
                "gis_tipo": "excel_edu", "edu_campo": "rad",
            },
            {
                "id": "aforo_villa_lago", "oficial": False, "inverso": False,
                "nombre": "Aforo polideportivo Villa del Lago",
                "unidad": "personas/mes",
                "fuente": "Secretaría de Deportes",
                "ref_min": 1000, "ref_max": 7000,
                # Sin gis_tipo → cae a manuales.json hasta recibir el dato
            },
        ],
    },
    "cohesion_social": {
        "nombre": "Cohesión Social",
        "icono": "people",
        "peso": 0.12,
        "color": "#8E24AA",
        "indicadores": [
            {
                "id": "vif", "oficial": True, "inverso": True,
                "nombre": "Violencia intrafamiliar (VIF) trimestral",
                "unidad": "casos",
                "fuente": "Observatorio de Seguridad y Justicia / SIEDCO",
                "ref_min": 60, "ref_max": 200,  # anclado a serie real C13-C14: min=88 max=189 (2023-2025)
                "gis_dir": "seguridad/violencia", "gis_tipo": "conteo_periodo",
                "gis_campo_fecha": "FECHA_HECH",
                "gis_patron": "VIOLENCIA_INTRAFAMILIAR",
            },
            {
                "id": "rinas_conflictividad", "oficial": True, "inverso": True,
                "nombre": "Riñas / conflictividad (trimestral)",
                "unidad": "casos",
                "fuente": "Observatorio de Seguridad y Justicia / Comparendos",
                "ref_min": 20, "ref_max": 160,  # anclado a serie real C13-C14: min=38 max=144 (2023-2025)
                "gis_dir": "seguridad/comparendos", "gis_tipo": "conteo_periodo",
                "gis_campo_fecha": "fecha_hech",
                "gis_filtro": {"agrupado": "RIÑAS"},
            },
            {
                "id": "concentracion_vulnerabilidad_activa", "oficial": True, "inverso": True,
                "nombre": "Concentración de vulnerabilidad activa",
                "unidad": "personas por 1.000 hab",
                "fuente": "Secretaría de Bienestar Social / Caracterización Sub PyE 2025 · C13-C14",
                "ref_min": 30.0, "ref_max": 160.0,
            },
        ],
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# UTILIDADES DE FECHA Y PERÍODO
# ══════════════════════════════════════════════════════════════════════════════

def parsear_periodo(periodo_str):
    """
    Parsea un período y devuelve (year, mes_inicio, mes_fin, lapso, periodo_anterior).

    Formatos soportados:
      '2025-T4' → trimestral: (2025, 10, 12, 'trimestral', '2025-T3')
      '2025-S2' → semestral:  (2025,  7, 12, 'semestral',  '2025-S1')
      '2025'    → anual:      (2025,  1, 12, 'anual',      '2024')
    """
    s = periodo_str.upper().strip()
    if '-T' in s:
        parts = s.split('-T')
        year, trim = int(parts[0]), int(parts[1])
        mes_inicio = (trim - 1) * 3 + 1
        mes_fin    = trim * 3
        ant = f"{year}-T{trim-1}" if trim > 1 else f"{year-1}-T4"
        return year, mes_inicio, mes_fin, 'trimestral', ant
    elif '-S' in s:
        parts = s.split('-S')
        year, sem = int(parts[0]), int(parts[1])
        mes_inicio = 1 if sem == 1 else 7
        mes_fin    = 6 if sem == 1 else 12
        ant = f"{year}-S1" if sem == 2 else f"{year-1}-S2"
        return year, mes_inicio, mes_fin, 'semestral', ant
    else:
        year = int(s)
        return year, 1, 12, 'anual', str(year - 1)


def en_rango(fecha_val, year, mes_inicio, mes_fin):
    """True si fecha_val (str YYYY-MM-DD) cae en el año y rango de meses."""
    if not fecha_val:
        return False
    s = str(fecha_val)[:10]
    try:
        d = datetime.strptime(s, "%Y-%m-%d").date()
        return d.year == year and mes_inicio <= d.month <= mes_fin
    except Exception:
        return False


def en_anio(fecha_val, year):
    if not fecha_val:
        return False
    try:
        return int(str(fecha_val)[:4]) == year
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════════════════
# LECTURA DE ARCHIVOS
# ══════════════════════════════════════════════════════════════════════════════

def leer_geojson(ruta):
    """Lee un GeoJSON y devuelve lista de features."""
    path = ROOT / ruta if not Path(ruta).is_absolute() else Path(ruta)
    if not path.exists():
        print(f"  [WARN] No encontrado: {path}")
        return []
    try:
        return json.loads(path.read_text(encoding="utf-8-sig")).get("features", [])
    except Exception as e:
        print(f"  [WARN] Error leyendo {path.name}: {e}")
        return []


def leer_geojsons_dir(subdir, patron=None):
    """Lee todos los GeoJSON en data/subdir, filtrando por patrón en el nombre."""
    features = []
    path = DATA / subdir
    if not path.exists():
        return features
    for archivo in path.glob("*.geojson"):
        if patron and patron.upper() not in archivo.name.upper():
            continue
        features.extend(leer_geojson(archivo))
    return features


def leer_json(ruta, default=None):
    path = ROOT / ruta if not Path(ruta).is_absolute() else Path(ruta)
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return default


def leer_ndvi_tif():
    """
    Lee data/NVDI/ndvi_resultado.tif.
    Devuelve dict con:
      - ndvi_medio   : float — media NDVI válida
      - area_verde_m2: int   — m² con NDVI > 0.20 (vegetación activa)
    Requiere tifffile + imagecodecs-lite (pip install tifffile imagecodecs-lite).
    Retorna None si el archivo no existe o hay error.
    """
    tif_path = DATA / "NVDI" / "ndvi_resultado.tif"
    if not tif_path.exists():
        return None
    try:
        import tifffile
        import numpy as np

        arr = tifffile.imread(str(tif_path)).astype(float)

        # Georeferencia: escala de píxel en grados (leída del TIF en sesión anterior)
        # ModelPixelScaleTag: ~8.98e-5 grados/píxel en x e y
        # A lat ~3.43°: 1° lat ≈ 111 320 m, 1° lon ≈ cos(3.43°)×111 320 ≈ 111 121 m
        pixel_scale_deg = 8.98e-5
        lat_centro_rad  = math.radians(3.43)
        metro_por_grado_lat = 111_320.0
        metro_por_grado_lon = math.cos(lat_centro_rad) * 111_320.0
        pixel_area_m2 = pixel_scale_deg * metro_por_grado_lon * pixel_scale_deg * metro_por_grado_lat

        # Píxeles válidos (rango NDVI [-1, 1] sin NoData)
        validos_mask = (arr >= -1.0) & (arr <= 1.0)
        validos       = arr[validos_mask]
        if validos.size == 0:
            return None

        # Área verde: píxeles con NDVI ≥ 0.20 (vegetación activa / cobertura real)
        verde_mask   = (arr >= 0.20) & (arr <= 1.0)
        n_verde      = int(np.count_nonzero(verde_mask))
        area_verde   = round(n_verde * pixel_area_m2)

        return {
            "ndvi_medio":    round(float(validos.mean()), 4),
            "area_verde_m2": area_verde,
        }
    except ImportError:
        print("  [WARN] tifffile no instalado — usando valores manuales. pip install tifffile imagecodecs-lite")
        return None
    except Exception as e:
        print(f"  [WARN] Error leyendo NDVI TIF: {e}")
        return None


def leer_deficit_ahdi_excel(year):
    """
    Lee data/excel/vivienda/INTERVENCION_AHDI_AÑOS_24_25_26.xlsx.
    Calcula el % de avance ponderado por etapa procesal:

      avance = Σ(ha × peso_etapa)  /  Σ(ha totales con AÑO_INTERV ≤ year)

    Pesos por etapa (supuesto metodológico explícito v7):
      Escriturado / Resuelto       → 1.00  (déficit realmente resuelto)
      Proceso de Legalización      → 0.75  (expediente en etapa final)
      Con Radicación               → 0.40  (expediente iniciado y radicado)
      A Intervenir                 → 0.05  (solo planificado, sin trámite)
      Estado desconocido           → 0.00  (conservador)

    Retorna dict con avance y trazabilidad o None si no se puede leer:
      {
        "avance_pct": float,   # % de avance ponderado
        "activo_ha": float,    # ha-equivalente ponderadas
        "total_ha": float,     # ha totales consideradas
        "corte": str           # regla de corte aplicada
      }
    """
    xlsx_path = DATA / "excel" / "vivienda" / "INTERVENCION_AHDI_AÑOS_24_25_26.xlsx"
    if not xlsx_path.exists():
        return None
    try:
        import zipfile
        import xml.etree.ElementTree as ET

        ns_ss  = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        ns_pkg = "http://schemas.openxmlformats.org/package/2006/relationships"

        with zipfile.ZipFile(xlsx_path) as z:
            # Shared strings
            try:
                shared = [t.text or "" for t in ET.parse(z.open("xl/sharedStrings.xml")).findall(f".//{{{ns_ss}}}t")]
            except Exception:
                shared = []

            # Primera hoja
            try:
                rels_tree = ET.parse(z.open("xl/_rels/workbook.xml.rels"))
                targets = [
                    "xl/" + r.get("Target", "").lstrip("/")
                    for r in rels_tree.findall(f"{{{ns_pkg}}}Relationship")
                    if "worksheet" in r.get("Type", "").lower()
                ]
            except Exception:
                targets = ["xl/worksheets/sheet1.xml"]

            if not targets:
                return None
            sf = targets[0].replace("xl/xl/", "xl/")
            if sf not in z.namelist():
                return None

            def cell_val(c):
                t = c.get("t", "")
                v = c.find(f"{{{ns_ss}}}v")
                if v is None:
                    return ""
                return shared[int(v.text)] if t == "s" else (v.text or "")

            rows = []
            for row in ET.parse(z.open(sf)).findall(f".//{{{ns_ss}}}row"):
                rows.append([cell_val(c) for c in row.findall(f"{{{ns_ss}}}c")])

        if not rows:
            return None

        # Detectar columnas por cabecera (fila 0)
        header = [str(h).strip().upper() for h in rows[0]]
        def col(nombre):
            for kw in nombre:
                for i, h in enumerate(header):
                    if kw in h:
                        return i
            return None

        idx_area   = col(["AREA_HA", "AREA HA", "HA"])
        idx_año    = col(["AÑO_INTERV", "AÑO INTERV", "AÑO"])
        idx_estado = col(["PROCESO", "ESTADO"])

        if idx_area is None or idx_año is None or idx_estado is None:
            print("  [WARN] AHDI Excel: no se encontraron columnas esperadas")
            return None

        # Pesos por etapa de avance procesal (supuesto metodológico explícito v7)
        PESOS_ETAPA = [
            ("ESCRITURADO",            1.00),
            ("RESUELTO",               1.00),
            ("PROCESO DE LEGALIZ",     0.75),
            ("LEGALIZ",                0.75),
            ("CON RADICACI",           0.40),
            ("CON RADICACION",         0.40),
            ("A INTERVENIR",           0.05),
        ]

        total_ha = 0.0
        pond_ha  = 0.0

        for fila in rows[1:]:
            def get(i):
                return fila[i].strip() if i < len(fila) else ""

            try:
                año_fila = int(float(get(idx_año))) if get(idx_año) else 9999
            except Exception:
                continue
            if año_fila > year:
                continue  # Solo asentamientos cuyo año de intervención ≤ período actual

            try:
                ha = float(get(idx_area)) if get(idx_area) else 0.0
            except Exception:
                ha = 0.0

            estado = get(idx_estado).upper()
            peso = 0.0
            for kw, w in PESOS_ETAPA:
                if kw in estado:
                    peso = w
                    break

            total_ha += ha
            pond_ha  += ha * peso

        if total_ha == 0:
            return None

        pct = round(pond_ha / total_ha * 100, 1)
        print(f"  [AHDI] {year}: avance ponderado {pct}% ({pond_ha:.2f} ha-equiv / {total_ha:.2f} ha totales)")
        return {
            "avance_pct": pct,
            "activo_ha": round(pond_ha, 2),
            "total_ha":  round(total_ha, 2),
            "corte": f"AÑO_INTERV <= {year}, ponderado por etapa",
        }

    except Exception as e:
        print(f"  [WARN] Error leyendo AHDI Excel: {e}")
        return None


def leer_velocidad_excel():
    """
    Lee data/excel/movilidad/Velocidades*.xlsx, hoja "Velocidades Jornadas".
    Devuelve la velocidad promedio general del corredor Pulmon de Oriente (km/h).

    Estructura de la hoja (fila 2 = cabecera real):
      Etiquetas de fila | am | pm | noche | General | Nota
    Fila total: la ultima fila con label 'General' en col 0.
    Dato acumulado 2025-YTD2026 — se aplica como referencia fija para todos los lapsos.
    Retorna float o None.
    """
    xlsx_dir = DATA / "excel" / "movilidad"
    candidatos = list(xlsx_dir.glob("Velocidades*.xlsx"))
    if not candidatos:
        return None
    xlsx_path = candidatos[0]
    try:
        rows = _leer_xlsx_sheet(xlsx_path, "Velocidades Jornadas")
        if not rows:
            return None

        # Fila 2 (indice 2) es la cabecera real: Etiquetas de fila | am | pm | noche | General | ...
        header_row = rows[2] if len(rows) > 2 else rows[0]
        header = [str(h).strip().upper() for h in header_row]
        idx_general = next((i for i, h in enumerate(header) if h == "GENERAL"), None)
        if idx_general is None:
            return None

        # Buscar fila total 'General' desde el final
        for fila in reversed(rows):
            label = str(fila[0]).strip().upper() if fila else ""
            if label == "GENERAL":
                try:
                    vel = round(float(fila[idx_general]), 1)
                    print(f"  [VEL] Excel leido: velocidad corredor = {vel} km/h")
                    return vel
                except (ValueError, IndexError):
                    continue
        return None

    except Exception as e:
        print(f"  [WARN] Error leyendo Excel velocidad: {e}")
        return None


def leer_vulnerabilidad_excel(comunas=None, poblacion=88400):
    """
    Lee data/excel/bienestar/Caracterizacion Personas Sub PyE*.xlsx
    y calcula la concentración de vulnerabilidad activa (personas / 1.000 hab)
    filtrando por las comunas del Pulmón de Oriente.

    comunas: set de strings con el formato 'Comuna 13', 'Comuna 14', etc.
             Por defecto {'Comuna 13', 'Comuna 14'} — núcleo del Pulmón.
    poblacion: población de referencia del territorio (denominador).
    Retorna float (p/1000 hab) o None.
    """
    if comunas is None:
        comunas = {"Comuna 13", "Comuna 14"}

    xlsx_dir = DATA / "excel" / "bienestar"
    candidatos = list(xlsx_dir.glob("Caracterizaci*.xlsx"))
    if not candidatos:
        return None
    xlsx_path = candidatos[0]

    import zipfile
    import xml.etree.ElementTree as ET

    ns = {"s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    try:
        with zipfile.ZipFile(xlsx_path) as z:
            with z.open("xl/sharedStrings.xml") as f:
                ss = [t.text or "" for t in ET.parse(f).findall(".//s:t", ns)]
            with z.open("xl/worksheets/sheet1.xml") as f:
                ws = ET.parse(f)

        def cv(c):
            v = c.find("s:v", ns)
            t = c.get("t", "")
            if v is None:
                return ""
            if t == "s":
                return ss[int(v.text)]
            return v.text

        rows = ws.findall(".//s:row", ns)
        total = 0
        for row in rows[1:]:  # saltar cabecera
            cells = row.findall("s:c", ns)
            if len(cells) > 10 and cv(cells[10]) in comunas:
                total += 1

        rate = round(total / poblacion * 1000, 1)
        print(
            f"  [VULN] Bienestar Excel: {total} personas en {sorted(comunas)} "
            f"=> {rate} p/1000 hab (pob={poblacion})"
        )
        return rate

    except Exception as e:
        print(f"  [WARN] Error leyendo Excel bienestar: {e}")
        return None


# ══════════════════════════════════════════════════════════════════════════════
# EXTRACCIÓN DE INDICADORES DESDE GIS
# ══════════════════════════════════════════════════════════════════════════════

def haversine(lon1, lat1, lon2, lat2):
    R = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    return R * 2 * math.asin(math.sqrt(min(1.0, a)))


def calcular_longitud_linea(coords):
    total = 0.0
    for i in range(1, len(coords)):
        c0, c1 = coords[i - 1], coords[i]
        if len(c0) >= 2 and len(c1) >= 2:
            total += haversine(c0[0], c0[1], c1[0], c1[1])
    return total


def extraer_gis(ind_cfg, year, mes_inicio, mes_fin):
    """
    Extrae el valor de un indicador según su configuración GIS.
    Devuelve None si no tiene fuente GIS.
    """
    tipo = ind_cfg.get("gis_tipo")
    if not tipo:
        return None

    def _cumple_filtro(props):
        filtro = ind_cfg.get("gis_filtro")
        if not filtro:
            return True
        try:
            return all(props.get(k) == v for k, v in filtro.items())
        except Exception:
            return False

    # ── conteo_periodo: cuenta features cuya fecha cae en el período ──────
    if tipo == "conteo_periodo":
        feats = leer_geojsons_dir(ind_cfg["gis_dir"], ind_cfg.get("gis_patron"))
        campo = ind_cfg.get("gis_campo_fecha", "FECHA_HECH")
        return sum(
            1 for f in feats
            if en_rango(f["properties"].get(campo), year, mes_inicio, mes_fin)
            and _cumple_filtro(f.get("properties", {}))
        )

    # ── conteo_total: cuenta todos los features (sin filtro de fecha) ─────
    if tipo == "conteo_total":
        feats = leer_geojsons_dir(ind_cfg["gis_dir"], ind_cfg.get("gis_patron"))
        return len(feats)

    # ── conteo_archivo: cuenta features de un archivo (con filtro opcional) ─
    if tipo == "conteo_archivo":
        feats = leer_geojson(ind_cfg["gis_archivo"])
        filtro = ind_cfg.get("gis_filtro")
        if filtro:
            feats = [f for f in feats if all(f["properties"].get(k) == v for k, v in filtro.items())]
        return len(feats)

    # ── suma_campo: suma el valor de un campo numérico ────────────────────
    if tipo == "suma_campo":
        feats  = leer_geojson(ind_cfg["gis_archivo"])
        campo  = ind_cfg.get("gis_campo", "")
        total  = 0
        for f in feats:
            try:
                total += int(f["properties"].get(campo) or 0)
            except (ValueError, TypeError):
                pass
        return total

    # ── longitud_lineas: suma longitud Haversine de LineStrings ──────────
    if tipo == "longitud_lineas":
        feats  = leer_geojson(ind_cfg["gis_archivo"])
        total  = 0.0
        for f in feats:
            geom  = f.get("geometry", {}) or {}
            gtype = geom.get("type", "")
            coords = geom.get("coordinates", [])
            if gtype == "LineString":
                total += calcular_longitud_linea(coords)
            elif gtype == "MultiLineString":
                for seg in coords:
                    total += calcular_longitud_linea(seg)
        return round(total, 2)

    # ── excel_edu: lee indicadores educativos desde Excel de Sec. Educación ──
    if tipo == "excel_edu":
        # year es el año del período; los Excel son anuales (no trimestrales)
        datos = leer_indicadores_educacion(year, sector=ind_cfg.get("edu_sector"))
        if datos is None:
            return None
        campo = ind_cfg.get("edu_campo")
        return datos.get(campo)

    return None


# ══════════════════════════════════════════════════════════════════════════════
# EXTRACCIÓN DESDE EXCEL EDUCACIÓN
# ══════════════════════════════════════════════════════════════════════════════

# Comunas que forman el polígono Pulmón de Oriente
COMUNAS_PULMON_EDU = {13, 14}

# Sector configurable: "total" | "oficial" | "no_oficial"
# Cambiar aquí para alternar la base del cálculo educativo
EDU_SECTOR = "total"


def _leer_xlsx_sheet(path, sheet_name):
    """Lee una hoja de un .xlsx y devuelve lista de listas de strings."""
    import zipfile
    import xml.etree.ElementTree as ET

    ns_ss  = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    ns_rel = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    ns_pkg = "http://schemas.openxmlformats.org/package/2006/relationships"

    with zipfile.ZipFile(path) as z:
        # Shared strings
        try:
            shared = [t.text or "" for t in ET.parse(z.open("xl/sharedStrings.xml")).findall(f".//{{{ns_ss}}}t")]
        except Exception:
            shared = []

        # Leer relaciones del workbook para mapear rId → ruta de hoja
        try:
            rels_tree = ET.parse(z.open("xl/_rels/workbook.xml.rels"))
            rid_to_target = {
                r.get("Id"): "xl/" + r.get("Target", "").lstrip("/")
                for r in rels_tree.findall(f"{{{ns_pkg}}}Relationship")
                if "worksheet" in r.get("Type", "").lower()
            }
        except Exception:
            rid_to_target = {}

        # Mapear nombre de hoja → ruta real usando rId
        wb_tree = ET.parse(z.open("xl/workbook.xml"))
        sheet_map = {}
        for s in wb_tree.findall(f".//{{{ns_ss}}}sheet"):
            name = s.get(f"{{{ns_ss}}}name") or s.get("name", "")
            rid  = s.get(f"{{{ns_rel}}}id") or s.get("r:id", "")
            target = rid_to_target.get(rid)
            if name and target:
                # normalizar ruta: xl/worksheets/sheet1.xml
                target = target.replace("xl/xl/", "xl/")
                sheet_map[name] = target

        sf = sheet_map.get(sheet_name)
        if not sf or sf not in z.namelist():
            return []

        rows = []
        for row in ET.parse(z.open(sf)).findall(f".//{{{ns_ss}}}row"):
            cells = []
            for c in row.findall(f"{{{ns_ss}}}c"):
                t = c.get("t", "")
                v = c.find(f"{{{ns_ss}}}v")
                if v is not None:
                    cells.append(shared[int(v.text)] if t == "s" else (v.text or ""))
                else:
                    cells.append("")
            rows.append(cells)
        return rows


def _edu_excel_path(year):
    """Devuelve la ruta del Excel de educación para el año dado, o None."""
    base = DATA / "excel" / "educacion"
    for fname in [f"Indicadores_Sectoriales_{year}.xlsx"]:
        p = base / fname
        if p.exists():
            return p
    return None


def leer_indicadores_educacion(year, sector=None):
    """
    Lee los indicadores educativos desde el Excel de Secretaría de Educación.
    Retorna dict: {matricula, tasa_repitencia, tasa_desercion, rad}
    Si el archivo no existe, retorna None.

    sector: "total" | "oficial" | "no_oficial"
            Si es None, usa EDU_SECTOR global.

    Mapa de hojas (por contenido real, independiente del nombre en workbook):
      sheet7  – Matrícula por sector (Contratada/No Oficial/Oficial) y comuna
                idx ignorado; fila de datos: [COMUNA, Cont_F, Cont_M, NoOf_F, NoOf_M, Of_F, Of_M, TOTAL]
      sheet14 – Repitencia total: [idx, COMUNA, MAT, REP_abs, TASA_%]
      sheet16 – Deserción sector oficial: [idx, COMUNA, DESERTORES, MAT_of, TASA_%]
      sheet18 – Deserción sector no oficial: [idx, COMUNA, DESERTORES, MAT_noOf, TASA_%]
      sheet20 – RAD sector oficial: [idx, COMUNA, MAT_of, DOCENTES_of, RAD_of]
    """
    sector = sector or EDU_SECTOR
    path = _edu_excel_path(year)
    if not path:
        return None

    COMUNAS = {f"Comuna {c}" for c in COMUNAS_PULMON_EDU}

    def _f(x):
        try:
            return float(x) if x else 0.0
        except (ValueError, TypeError):
            return 0.0

    def _read_file(fname):
        """Lee un archivo de hoja directamente por nombre de archivo dentro del zip."""
        import zipfile
        import xml.etree.ElementTree as ET
        ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        rows = []
        with zipfile.ZipFile(path) as z:
            try:
                shared = [t.text or "" for t in ET.parse(z.open("xl/sharedStrings.xml")).findall(f".//{{{ns}}}t")]
            except Exception:
                shared = []
            sf = f"xl/worksheets/{fname}"
            if sf not in z.namelist():
                return []
            for row in ET.parse(z.open(sf)).findall(f".//{{{ns}}}row"):
                cells = []
                for c in row.findall(f"{{{ns}}}c"):
                    t = c.get("t", "")
                    v = c.find(f"{{{ns}}}v")
                    if v is not None:
                        cells.append(shared[int(v.text)] if t == "s" else (v.text or ""))
                    else:
                        cells.append("")
                rows.append(cells)
        return rows

    # ── Matrícula por sector (sheet7) ─────────────────────────────────────────
    # Filas: [COMUNA, Cont_F, Cont_M, NoOf_F, NoOf_M, Of_F, Of_M, TOTAL]
    # (hay 3 filas de header antes de los datos de comunas)
    mat_total, mat_oficial, mat_no_oficial = 0.0, 0.0, 0.0
    for r in _read_file("sheet7.xml"):
        if len(r) >= 8 and r[0] in COMUNAS:
            mat_total      += _f(r[7])
            mat_oficial    += _f(r[5]) + _f(r[6])
            mat_no_oficial += _f(r[3]) + _f(r[4])

    if sector == "oficial":
        mat_base = mat_oficial
    elif sector == "no_oficial":
        mat_base = mat_no_oficial
    else:
        mat_base = mat_total

    if not mat_base:
        return None

    # ── Repitencia total (sheet14: idx | COMUNA | MAT | REP_abs | TASA_%) ────
    rep_abs = 0.0
    for r in _read_file("sheet14.xml"):
        if len(r) >= 4 and r[1] in COMUNAS:
            rep_abs += _f(r[3])
    # Escalar proporcionalmente si sector != total
    if mat_total and sector != "total":
        rep_abs *= mat_base / mat_total
    tasa_rep = round(rep_abs / mat_base * 100, 1) if mat_base else 0.0

    # ── Deserción por sector ──────────────────────────────────────────────────
    # sheet16 = oficial  (idx | COMUNA | DESERTORES | MAT_of | TASA_%)
    # sheet18 = no oficial (misma estructura)
    if sector == "oficial":
        des_rows = _read_file("sheet16.xml")
    elif sector == "no_oficial":
        des_rows = _read_file("sheet18.xml")
    else:
        # total = oficial + no oficial
        des_rows = _read_file("sheet16.xml") + _read_file("sheet18.xml")

    des_abs, des_mat_sector = 0.0, 0.0
    for r in des_rows:
        if len(r) >= 5 and r[1] in COMUNAS:
            des_abs        += _f(r[2])
            des_mat_sector += _f(r[3])
    tasa_des = round(des_abs / des_mat_sector * 100, 1) if des_mat_sector else 0.0

    # ── RAD (sheet20: idx | COMUNA | MAT_of | DOCENTES_of | RAD_of) ──────────
    # sheet20 contiene solo sector oficial; el RAD (~27-29) es el más significativo
    # Para total/no_oficial se usa el mismo valor (no hay hoja equivalente para otros sectores)
    rad_c, rad_w = 0.0, 0.0
    for r in _read_file("sheet20.xml"):
        if len(r) >= 5 and r[1] in COMUNAS:
            mat_c = _f(r[2])
            rad_c += _f(r[4]) * mat_c   # promedio ponderado
            rad_w += mat_c
    rad = round(rad_c / rad_w, 1) if rad_w else 0.0

    return {
        "matricula":       int(mat_base),
        "tasa_repitencia": tasa_rep,
        "tasa_desercion":  tasa_des,
        "rad":             rad,
        "sector_usado":    sector,
    }


# ══════════════════════════════════════════════════════════════════════════════
# GENERACIÓN DE NOTAS REALES
# ══════════════════════════════════════════════════════════════════════════════

def _conteos_anuales(features, campo_fecha):
    """Devuelve {year: count} para los años en el dataset."""
    c = defaultdict(int)
    for f in features:
        val = f["properties"].get(campo_fecha)
        if val:
            try:
                c[int(str(val)[:4])] += 1
            except Exception:
                pass
    return dict(c)


def _conteos_trimestrales(features, campo_fecha):
    """Devuelve {'YYYY-Tn': count} para todos los trimestres con datos."""
    c = defaultdict(int)
    for f in features:
        val = f["properties"].get(campo_fecha)
        if val:
            try:
                s = str(val)[:7]
                y, m = int(s[:4]), int(s[5:7])
                t = (m - 1) // 3 + 1
                c[f"{y}-T{t}"] += 1
            except Exception:
                pass
    return dict(c)


def nota_hurtos(year, mes_inicio, mes_fin, periodo_str):
    feats = leer_geojsons_dir("seguridad/hurtos")
    if not feats:
        return None
    trims = _conteos_trimestrales(feats, "FECHA_HECH")
    if not trims:
        return None
    max_p = max(trims, key=trims.get)
    max_v = trims[max_p]
    # Sumar todos los trimestres que caen dentro del rango
    cur = sum(v for k, v in trims.items() if _trim_en_rango(k, year, mes_inicio, mes_fin))
    if max_v and cur:
        if mes_fin - mes_inicio < 6:  # trimestral
            pct = round((max_v - cur) / max_v * 100)
            return f"Pico {max_v} ({max_p}) → {cur} ({periodo_str}) — reducción {pct}%"
        else:
            return f"Acumulado {periodo_str}: {cur} hurtos · Pico trimestral: {max_v} ({max_p})"
    return None


def _trim_en_rango(trim_key, year, mes_inicio, mes_fin):
    """'2025-T3' → True si ese trimestre cae dentro del rango año/meses."""
    try:
        y, t = int(trim_key[:4]), int(trim_key[-1])
        t_ini = (t - 1) * 3 + 1
        t_fin = t * 3
        return y == year and t_ini >= mes_inicio and t_fin <= mes_fin
    except Exception:
        return False


def nota_homicidios(year):
    feats = leer_geojsons_dir("seguridad/homicidios")
    if not feats:
        return None
    anual = _conteos_anuales(feats, "FECHA_HECH")
    if not anual:
        return None
    partes = " · ".join(f"{y}={anual.get(y,0)}" for y in sorted(anual))
    primero = min(anual.values())
    ultimo  = anual.get(year, 0)
    if primero and ultimo < primero:
        pct = round((primero - ultimo) / primero * 100)
        return f"{partes} — reducción {pct}%"
    return partes


def nota_vif(year):
    feats = leer_geojsons_dir("seguridad/violencia", "VIOLENCIA_INTRAFAMILIAR")
    if not feats:
        return None
    anual   = _conteos_anuales(feats, "FECHA_HECH")
    partes  = " · ".join(f"{y}={anual.get(y,0)}" for y in sorted(anual))
    anios   = sorted(anual.keys())
    if len(anios) >= 2:
        primero = anual[anios[0]]
        ultimo  = anual.get(year, anual[anios[-1]])
        if ultimo > primero:
            pct = round((ultimo - primero) / primero * 100)
            return f"ALERTA: {partes} — incremento +{pct}%"
    return partes


def nota_vbg():
    feats = leer_geojsons_dir("seguridad/violencia", "VBG")
    if not feats:
        return None
    comunas = defaultdict(int)
    for f in feats:
        c = f["properties"].get("COMUNA") or f["properties"].get("COD_COMUNA")
        if c:
            comunas[f"C{c}"] += 1
    top = sorted(comunas.items(), key=lambda x: x[1], reverse=True)[:3]
    detalle = " · ".join(f"{k}={v}" for k, v in top)
    return f"{detalle} — solo período 2025"


def nota_cai():
    feats = leer_geojson("data/seguridad/institucional/CAI_MECAL_CALI_PULMON.geojson")
    cais  = [f for f in feats if f["properties"].get("TIPO") == "CAI"]
    nombres = [f["properties"].get("UNIDAD", "") for f in cais]
    return " + ".join(n.title() for n in nombres if n) or None


def nota_ahdi():
    feats = leer_geojson("data/vivienda/INTERV_AHDI_LEG_URBA_PULMON.geojson")
    if not feats:
        return None
    n        = len(feats)
    total_ha = sum(f["properties"].get("AREA_HA", 0) or 0 for f in feats)
    pcts     = [f["properties"].get("PORC_URBAN", 0) for f in feats if f["properties"].get("PORC_URBAN")]
    avg_pct  = round(sum(pcts) / len(pcts), 1) if pcts else 0
    barrios  = list({f["properties"].get("BARRIOS_SE", "") for f in feats if f["properties"].get("BARRIOS_SE")})
    bar_str  = ", ".join(list(barrios)[:4])
    return f"{n} polígonos priorizados LU 2024-2027 · {total_ha:.2f} ha urbanizadas ({avg_pct}% prom.) · Barrios: {bar_str}"


def nota_viviendas():
    feats = leer_geojson("data/vivienda/INTERV_MEJOR_VIV_25_26_PULMON.geojson")
    if not feats:
        return None
    total    = sum(int(f["properties"].get("CANT_MEJOR") or 0) for f in feats)
    n_sec    = len(feats)
    estados  = defaultdict(int)
    for f in feats:
        est = f["properties"].get("ESTADO", "")
        if "EJECUTADO" in est and "EJECUCI" not in est:
            estados["ejecutado"] += 1
        elif "EJECUCI" in est:
            estados["ejecucion"] += 1
        else:
            estados["asignado"] += 1
    top3 = sorted(feats, key=lambda f: int(f["properties"].get("CANT_MEJOR") or 0), reverse=True)[:3]
    detalle = ", ".join(f"{f['properties'].get('NOMBRE_LOC','?')}={f['properties'].get('CANT_MEJOR','?')}" for f in top3)
    return (f"{n_sec} sectores · {total} viviendas · {detalle} · "
            f"{estados['ejecutado']} ejecutado, {estados['ejecucion']} en ejecución, {estados['asignado']} asignados")


# ══════════════════════════════════════════════════════════════════════════════
# SERIE TEMPORAL DE HURTOS
# ══════════════════════════════════════════════════════════════════════════════

def generar_hurtos_series():
    feats = leer_geojsons_dir("seguridad/hurtos")
    if not feats:
        return None
    trims  = _conteos_trimestrales(feats, "FECHA_HECH")
    serie  = [{"periodo": k, "n": v} for k, v in sorted(trims.items()) if v > 0]
    if not serie:
        return None
    return {
        "fuente":  "Policía Nacional / SIEDCO",
        "unidad":  "casos por trimestre",
        "nota":    f"Datos reales {serie[0]['periodo'][:4]}–{serie[-1]['periodo'][:4]}. Área del Pulmón de Oriente.",
        "serie":   serie,
    }


# ══════════════════════════════════════════════════════════════════════════════
# NORMALIZACIÓN
# ══════════════════════════════════════════════════════════════════════════════

def normalizar(valor, ref_min, ref_max, inverso=False):
    """Min-Max → [0, 100]. inverso=True → menor valor = mayor score."""
    if ref_max == ref_min:
        return 0.0
    score = (valor - ref_min) / (ref_max - ref_min) * 100
    if inverso:
        score = 100 - score
    return round(max(0.0, min(100.0, score)), 2)


# ══════════════════════════════════════════════════════════════════════════════
# CLASIFICACIÓN ITT
# ══════════════════════════════════════════════════════════════════════════════

NIVELES = [
    (0,  40, "Nivel 1 · Emergencia"),
    (40, 60, "Nivel 2 · Consolidación"),
    (60, 80, "Nivel 3 · Avance"),
    (80, 100,"Nivel 4 · Transformación"),
]

def clasificar(score):
    for lo, hi, label in NIVELES:
        if lo <= score < hi:
            return label, [lo, hi]
    return NIVELES[-1][2], [80, 100]


# ══════════════════════════════════════════════════════════════════════════════
# TENDENCIA POR INDICADOR
# ══════════════════════════════════════════════════════════════════════════════

def tendencia(valor, ind_id, vals_previos_dim):
    """Compara con período anterior para determinar alza/baja/estable."""
    if not vals_previos_dim:
        return "estable"
    prev = vals_previos_dim.get(ind_id)
    if prev is None:
        return "estable"
    try:
        diff = float(valor) - float(prev)
        umbral = abs(float(prev)) * 0.03 if prev != 0 else 0.5
        if abs(diff) <= umbral:
            return "estable"
        return "alza" if diff > 0 else "baja"
    except Exception:
        return "estable"


# ══════════════════════════════════════════════════════════════════════════════
# HISTORICO
# ══════════════════════════════════════════════════════════════════════════════

def _lapso_de_periodo(periodo_str):
    """Devuelve el lapso inferido del string de período."""
    s = periodo_str.upper()
    if '-T' in s:   return 'trimestral'
    if '-S' in s:   return 'semestral'
    return 'anual'


def _periodo_sort_key(periodo_str):
    """
    Clave de orden cronológico real para periodos mixtos (A/S/T).
    """
    try:
        year, mes_inicio, mes_fin, _, _ = parsear_periodo(str(periodo_str).strip())
        dur = mes_fin - mes_inicio + 1
        return (year, mes_inicio, mes_fin, dur)
    except Exception:
        return (9999, 99, 99, 99)


def leer_historico(periodo_actual=None, lapso=None):
    """Lee itt_historico.json y devuelve el último período del mismo lapso distinto al actual."""
    hist = leer_json(HIST, default={"periodos": []})
    periodos = hist.get("periodos", [])
    if not periodos:
        return None

    def mismo_lapso(p):
        if lapso is None:
            return True
        return _lapso_de_periodo(p.get("periodo", "")) == lapso

    candidatos = [p for p in periodos if mismo_lapso(p)]
    candidatos.sort(key=lambda p: _periodo_sort_key(p.get("periodo", "")))
    if not candidatos:
        return None

    if periodo_actual:
        candidatos = [p for p in candidatos if p.get("periodo") != periodo_actual]
        return candidatos[-1] if candidatos else None
    return candidatos[-1]


def guardar_historico(nuevo):
    """Agrega el período calculado al histórico si no existe ya."""
    hist = leer_json(HIST, default={"periodos": []})
    periodos = hist.get("periodos", [])
    # Reemplazar si ya existe el mismo período
    periodos = [p for p in periodos if p.get("periodo") != nuevo["periodo"]]
    periodos.append(nuevo)
    # Mantener orden cronológico
    periodos.sort(key=lambda p: _periodo_sort_key(p.get("periodo", "")))
    hist["periodos"] = periodos
    HIST.write_text(json.dumps(hist, ensure_ascii=False, indent=2), encoding="utf-8")


def leer_manuales(periodo_str):
    """
    Lee indicadores_manuales.json.
    Busca primero el bloque del período específico, luego 'default'.
    """
    data = leer_json(MAN, default={})
    if not data:
        return {}
    especifico = data.get(periodo_str, {})
    default    = data.get("default", {})
    # Merge: específico sobreescribe default
    resultado = {}
    for dim in set(list(especifico.keys()) + list(default.keys())):
        d_val = default.get(dim, {})
        e_val = especifico.get(dim, {})
        # _barrios y otras listas: específico reemplaza, no mergea
        if isinstance(d_val, list) or isinstance(e_val, list):
            resultado[dim] = e_val if e_val else d_val
        else:
            resultado[dim] = {**d_val, **e_val}
    return resultado


# ══════════════════════════════════════════════════════════════════════════════
# CÁLCULO PRINCIPAL
# ══════════════════════════════════════════════════════════════════════════════

def calcular_itt(periodo_str, version="preliminar"):
    year, mes_inicio, mes_fin, lapso, _ = parsear_periodo(periodo_str)
    # Factor para escalar refs de indicadores de conteo (1=trimestral, 2=semestral, 4=anual)
    n_trim = (mes_fin - mes_inicio + 1) // 3
    historico  = leer_historico(periodo_str, lapso=lapso)
    manuales   = leer_manuales(periodo_str)
    tiene_prev = historico is not None

    prev_vals   = historico.get("valores_crudos", {})     if historico else {}
    prev_dim_s  = historico.get("dimensiones_scores", {}) if historico else {}
    prev_period = historico.get("periodo", "N/A")          if historico else "N/A"

    print(f"\n  Período: {periodo_str}  |  Lapso: {lapso}  |  Comparación vs: {prev_period}")

    # ── Entorno Urbano: fuentes automáticas desde TIF y Excel ─────────────
    eu = manuales.setdefault("entorno_urbano", {})

    ndvi_result = leer_ndvi_tif()
    if ndvi_result is not None:
        eu["ndvi_cobertura_vegetal"] = ndvi_result["ndvi_medio"]
        eu["area_verde_neta"]        = ndvi_result["area_verde_m2"]
        print(f"  [NDVI] TIF leído: NDVI medio={ndvi_result['ndvi_medio']}  "
              f"Área verde={ndvi_result['area_verde_m2']:,} m²")
    else:
        print("  [NDVI] Usando valores manuales de indicadores_manuales.json")

    # ── Movilidad: velocidad corredor desde Excel ─────────────────────────
    vel_excel = leer_velocidad_excel()
    if vel_excel is not None:
        manuales.setdefault("movilidad", {})["velocidad_corredor"] = vel_excel
    else:
        print("  [VEL] Usando velocidad manual de indicadores_manuales.json")

    deficit_ahdi = leer_deficit_ahdi_excel(year)
    nota_deficit = None
    if deficit_ahdi is not None:
        # El indicador mide % avance en resolución: mayor avance = menor déficit pendiente
        # Lo invertimos: deficit_restante = 100 - avance (mayor → peor situación)
        avance = deficit_ahdi["avance_pct"]
        deficit_restante = round(100 - avance, 1)
        eu["deficit_habitacional_cualitativo"] = deficit_restante
        nota_deficit = (
            f"Corte {periodo_str}: {deficit_restante}% pendiente "
            f"(avance ponderado {avance}% = {deficit_ahdi['activo_ha']:.2f} ha-equiv / "
            f"{deficit_ahdi['total_ha']:.2f} ha totales; {deficit_ahdi['corte']})."
        )
    else:
        print("  [AHDI] Usando déficit manual de indicadores_manuales.json")

    # ── Cohesión Social: concentración vulnerabilidad desde Excel Bienestar ──
    vuln_excel = leer_vulnerabilidad_excel(
        comunas={"Comuna 13", "Comuna 14"},
        poblacion=88400,
    )
    if vuln_excel is not None:
        manuales.setdefault("cohesion_social", {})["concentracion_vulnerabilidad_activa"] = vuln_excel
    else:
        print("  [VULN] Usando concentración manual de indicadores_manuales.json")


    resultado_dims = []
    itt_global     = 0.0
    vals_actuales  = {}   # Para guardar en histórico

    # ── Notas reales por dimensión (se calculan una vez) ──────────────────
    notas_seg = {
        "hurtos": nota_hurtos(year, mes_inicio, mes_fin, periodo_str),
        "homicidios": nota_homicidios(year),
    }
    notas_coh = {
        "vif": nota_vif(year),
    }
    notas_ent = {
        "deficit_habitacional_cualitativo": nota_deficit,
    }
    NOTAS_EXTRA = {
        "seguridad": notas_seg,
        "entorno_urbano": notas_ent,
        "cohesion_social": notas_coh,
    }

    for dim_id, dim_cfg in DIMENSIONES.items():
        man_dim   = manuales.get(dim_id, {})
        prev_vals_dim = prev_vals.get(dim_id, {})
        scores_ind = []
        inds_out   = []
        vals_dim   = {}

        for ind in dim_cfg["indicadores"]:
            ind_id = ind["id"]

            # 1. Intentar obtener valor GIS
            valor = extraer_gis(ind, year, mes_inicio, mes_fin)

            # 2. Si no hay GIS, usar manual
            if valor is None:
                valor = man_dim.get(ind_id)

            if valor is None:
                inds_out.append({
                    "nombre":    ind["nombre"], "valor": None,
                    "unidad":    ind["unidad"], "tendencia": "sin_dato",
                    "fuente":    ind["fuente"], "oficial":   ind["oficial"],
                })
                continue

            vals_dim[ind_id] = valor
            # Escalar refs para indicadores de conteo en períodos > 1 trimestre
            ref_factor = n_trim if ind.get("gis_tipo") == "conteo_periodo" else 1
            score = normalizar(valor, ind["ref_min"] * ref_factor, ind["ref_max"] * ref_factor, ind["inverso"])
            scores_ind.append(score)

            ind_out = {
                "nombre":    ind["nombre"],
                "valor":     round(valor, 2) if isinstance(valor, float) else valor,
                "unidad":    ind["unidad"],
                "tendencia": tendencia(valor, ind_id, prev_vals_dim),
                "fuente":    ind["fuente"],
                "oficial":   ind["oficial"],
            }

            # Nota real si existe
            nota = NOTAS_EXTRA.get(dim_id, {}).get(ind_id)
            if nota:
                ind_out["nota_real"] = nota

            inds_out.append(ind_out)

        vals_actuales[dim_id] = vals_dim

        score_dim = round(sum(scores_ind) / len(scores_ind), 1) if scores_ind else 0.0
        cobertura = round(len(scores_ind) / len(dim_cfg["indicadores"]) * 100)
        score_prev = round(prev_dim_s.get(dim_id, score_dim), 1) if tiene_prev else score_dim
        variacion  = round(score_dim - score_prev, 1)

        dim_out = {
            "id":            dim_id,
            "nombre":        dim_cfg["nombre"],
            "icono":         dim_cfg["icono"],
            "peso":          dim_cfg["peso"],
            "score":         score_dim,
            "score_anterior": score_prev,
            "variacion":     variacion,
            "color":         dim_cfg["color"],
            "calidad_dato":  "oficial" if all(i["oficial"] for i in dim_cfg["indicadores"]) and cobertura >= 80 else "preliminar",
            "cobertura":     cobertura,
            "indicadores":   inds_out,
        }

        if dim_id == "seguridad":
            hs = generar_hurtos_series()
            if hs:
                dim_out["hurtos_series"] = hs

        resultado_dims.append(dim_out)
        itt_global += score_dim * dim_cfg["peso"]
        print(f"  {dim_cfg['nombre']:20s} score={score_dim:5.1f}  cobertura={cobertura}%")

    itt_global  = round(itt_global, 1)
    prev_global = round(historico.get("itt_score", itt_global), 1) if historico else itt_global
    variacion_g = round(itt_global - prev_global, 1)

    total_inds  = sum(len(d["indicadores"]) for d in DIMENSIONES.values())
    con_valor   = sum(len(v) for v in vals_actuales.values())
    cobertura_g = round(con_valor / total_inds * 100)
    oficiales_g = sum(1 for d in resultado_dims for i in d["indicadores"] if i["oficial"] and i["valor"] is not None)
    clasif, rango = clasificar(itt_global)

    # Serie temporal (historico + actual)
    hist_data   = leer_json(HIST, default={"periodos": []})
    serie_temp  = []
    for p in hist_data.get("periodos", []):
        if _lapso_de_periodo(p.get("periodo", "")) != lapso:
            continue
        row = {"periodo": p["periodo"], "itt": p.get("itt_score", 0)}
        for d in DIMENSIONES:
            row[d] = p.get("dimensiones_scores", {}).get(d, 0)
        serie_temp.append(row)
    # Agregar/reemplazar período actual (siempre usa el valor recién calculado)
    serie_temp = [r for r in serie_temp if r["periodo"] != periodo_str]
    row_actual = {"periodo": periodo_str, "itt": itt_global}
    for d_out in resultado_dims:
        row_actual[d_out["id"]] = d_out["score"]
    serie_temp.append(row_actual)
    serie_temp.sort(key=lambda r: _periodo_sort_key(r.get("periodo", "")))

    # Barrios desde manuales
    barrios = manuales.get("_barrios", [])

    resultado = {
        "meta": {
            "territorio":      "Pulmón de Oriente",
            "version":         version,
            "periodo":         periodo_str,
            "lapso":           lapso,
            "fecha_calculo":   datetime.today().strftime("%Y-%m-%d"),
            "cobertura_datos": cobertura_g,
            "fuentes_activas": con_valor,
            "fuentes_total":   total_inds,
            "nota": (
                f"ITT {version}. "
                f"Fuentes GIS verificadas: {oficiales_g} indicadores oficiales. "
                f"Manuales pendientes de actualización: {total_inds - con_valor} indicadores."
            ),
        },
        "itt_global": {
            "score":              itt_global,
            "score_anterior":     prev_global,
            "variacion":          variacion_g,
            "clasificacion":      clasif,
            "rango":              rango,
            "periodo_comparacion": prev_period,
        },
        "dimensiones":   resultado_dims,
        "serie_temporal": serie_temp,
        "barrios":        barrios,
    }

    # Guardar en histórico
    guardar_historico({
        "periodo":            periodo_str,
        "itt_score":          itt_global,
        "dimensiones_scores": {d["id"]: d["score"] for d in resultado_dims},
        "valores_crudos":     vals_actuales,
    })

    return resultado


# ══════════════════════════════════════════════════════════════════════════════
# GENERAR indicadores_manuales.json
# ══════════════════════════════════════════════════════════════════════════════

MANUALES_DEFAULT = {
    "_nota": (
        "Valores manuales para indicadores sin fuente GeoJSON directa. "
        "Actualizar cada trimestre antes de ejecutar calcular_itt.py. "
        "Bloque 'default' se usa si no existe el bloque del período específico."
    ),
    "default": {
        "seguridad": {
            "rinas_conflictividad": 74
        },
        "movilidad": {
            "siniestralidad_vial": 118,
            "accidentes_lesionados": 83,
            "muertes_via": 11,
            "velocidad_corredor": 18.5
        },
        "entorno_urbano": {
            "ndvi_cobertura_vegetal": 0.38,
            "area_verde_neta": 148000,
            "deficit_habitacional_cualitativo": 29.0
        },
        "educacion_desarrollo": {
            "matricula_escolar": 12350,
            "desercion_escolar": 3.8,
            "repitencia_escolar": 4.7,
            "estudiantes_por_docente": 29.0,
            "aforo_villa_lago": 4200
        },
        "cohesion_social": {
            "concentracion_vulnerabilidad_activa": 78.0
        },
        "_barrios": [
            {"nombre": "Alfonso López",   "itt": 65.2, "poblacion": 18400, "proyectos": 12},
            {"nombre": "El Vergel",       "itt": 61.8, "poblacion":  9200, "proyectos":  8},
            {"nombre": "Mojica",          "itt": 59.4, "poblacion": 21300, "proyectos": 15},
            {"nombre": "Pízamos I",       "itt": 57.1, "poblacion":  7800, "proyectos":  6},
            {"nombre": "Manuela Beltrán", "itt": 54.9, "poblacion": 11200, "proyectos":  9},
            {"nombre": "Cauquita",        "itt": 52.3, "poblacion":  6400, "proyectos":  5},
            {"nombre": "Nueva Floresta",  "itt": 50.8, "poblacion":  8900, "proyectos":  7},
            {"nombre": "Sena",            "itt": 48.5, "poblacion":  5200, "proyectos":  4}
        ]
    }
}


def generar_manuales():
    if MAN.exists():
        print(f"  El archivo ya existe: {MAN}")
        print("  Para regenerarlo, elimínalo primero.")
        return
    MAN.parent.mkdir(parents=True, exist_ok=True)
    MAN.write_text(json.dumps(MANUALES_DEFAULT, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  OK Creado: {MAN}")
    print("  Edita los valores del bloque 'default' o agrega bloques por periodo (ej. '2025-T4').")


# ══════════════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════════════

LAPSO_OUT = {
    'trimestral': DATA / 'indices' / 'itt_pulmon_trimestral.json',
    'semestral':  DATA / 'indices' / 'itt_pulmon_semestral.json',
    'anual':      DATA / 'indices' / 'itt_pulmon_anual.json',
}


def main():
    parser = argparse.ArgumentParser(
        description="Calcula el ITT del Pulmón de Oriente desde fuentes GeoJSON.")
    parser.add_argument("--periodo",          default=None,
                        help="Período (ej. 2025-T4, 2025-S2, 2025). Default: período actual según lapso.")
    parser.add_argument("--lapso",            default="trimestral",
                        choices=["trimestral", "semestral", "anual"],
                        help="Granularidad temporal (default: trimestral)")
    parser.add_argument("--version",          default="preliminar",
                        help="'preliminar' u 'oficial'")
    parser.add_argument("--output",           default=None,
                        help="Ruta de salida del JSON (default: según --lapso)")
    parser.add_argument("--generar-manuales", action="store_true",
                        help="Crea data/indices/indicadores_manuales.json con valores por defecto")
    args = parser.parse_args()

    if args.generar_manuales:
        print("\nGenerando indicadores_manuales.json...")
        generar_manuales()
        return

    # Período por defecto según lapso
    if not args.periodo:
        hoy = datetime.today()
        if args.lapso == 'trimestral':
            trim = (hoy.month - 1) // 3 + 1
            args.periodo = f"{hoy.year}-T{trim}"
        elif args.lapso == 'semestral':
            sem = 1 if hoy.month <= 6 else 2
            args.periodo = f"{hoy.year}-S{sem}"
        else:
            args.periodo = str(hoy.year)

    # Verificar que existen los manuales
    if not MAN.exists():
        print(f"\n  [WARN] No existe {MAN}")
        print("  Ejecuta primero:  python scripts/calcular_itt.py --generar-manuales")
        return

    print(f"\n{'='*60}")
    print(f"  ITT Pulmón de Oriente  ·  {args.periodo}  ·  {args.version}")
    print(f"{'='*60}")

    resultado = calcular_itt(args.periodo, args.version)

    # Determinar archivo de salida
    if args.output:
        out_paths = [Path(args.output)]
    else:
        lapso_det = resultado['meta'].get('lapso', args.lapso)
        out_paths = [LAPSO_OUT[lapso_det]]
        # Para trimestral también actualiza el JSON genérico (compatibilidad)
        if lapso_det == 'trimestral':
            out_paths.append(OUT)

    for out_path in out_paths:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    g = resultado["itt_global"]
    print(f"\n{'='*60}")
    print(f"  ITT Global: {g['score']}/100  ->  {g['clasificacion']}")
    print(f"  Variación:  {g['variacion']:+.1f} pts vs {g['periodo_comparacion']}")
    print(f"  Cobertura:  {resultado['meta']['cobertura_datos']}%  "
          f"({resultado['meta']['fuentes_activas']}/{resultado['meta']['fuentes_total']} indicadores)")
    for p in out_paths:
        print(f"  Guardado:   {p}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
