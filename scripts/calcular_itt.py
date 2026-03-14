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
    → luminarias, espacio público, parques, percepción seguridad,
      accesibilidad MIO, tiempo desplazamiento, ciclorutas,
      niños programas, acceso salud, familias subsidio,
      negocios formalizados, empleos obra, inversión privada, emprendimientos,
      barrios (ranking ITT estimado por barrio)

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
        "icono":  "shield",
        "peso":   0.20,
        "color":  "#C1272D",
        "indicadores": [
            {
                "id": "homicidios", "oficial": True, "inverso": True,
                "nombre": "Homicidios (trimestral)",
                "unidad": "casos",
                "fuente": "Policía Nacional / SIEDCO",
                "ref_min": 10, "ref_max": 130,
                "gis_dir": "seguridad/homicidios", "gis_tipo": "conteo_periodo",
                "gis_campo_fecha": "FECHA_HECH",
            },
            {
                "id": "hurtos", "oficial": True, "inverso": True,
                "nombre": "Hurtos reportados (trimestral)",
                "unidad": "casos",
                "fuente": "Policía Nacional / SIEDCO",
                "ref_min": 150, "ref_max": 500,
                "gis_dir": "seguridad/hurtos", "gis_tipo": "conteo_periodo",
                "gis_campo_fecha": "FECHA_HECH",
            },
            {
                "id": "vif", "oficial": True, "inverso": True,
                "nombre": "Violencia Intrafamiliar (trimestral)",
                "unidad": "casos",
                "fuente": "Policía Nacional / SIEDCO",
                "ref_min": 80, "ref_max": 200,
                "gis_dir": "seguridad/violencia", "gis_tipo": "conteo_periodo",
                "gis_campo_fecha": "FECHA_HECH",
                "gis_patron": "VIOLENCIA_INTRAFAMILIAR",
            },
            {
                "id": "vbg", "oficial": True, "inverso": True,
                "nombre": "VBG reportadas (anual)",
                "unidad": "casos",
                "fuente": "Policía Nacional / SIEDCO",
                "ref_min": 20, "ref_max": 150,
                "gis_dir": "seguridad/violencia", "gis_tipo": "conteo_total",
                "gis_patron": "VBG",
            },
            {
                "id": "percepcion_seguridad", "oficial": False, "inverso": False,
                "nombre": "Percepción de seguridad",
                "unidad": "%",
                "fuente": "Encuesta ITT (estimado)",
                "ref_min": 20.0, "ref_max": 75.0,
            },
            {
                "id": "presencia_institucional", "oficial": True, "inverso": False,
                "nombre": "Presencia institucional",
                "unidad": "CAI activos",
                "fuente": "Secretaría de Seguridad / MECAL · verificado GIS",
                "ref_min": 1, "ref_max": 6,
                "gis_archivo": "data/seguridad/institucional/CAI_MECAL_CALI_PULMON.geojson",
                "gis_tipo": "conteo_archivo",
                "gis_filtro": {"TIPO": "CAI"},
            },
        ],
    },

    "entorno_urbano": {
        "nombre": "Entorno Urbano",
        "icono":  "city",
        "peso":   0.30,
        "color":  "#1565C0",
        "indicadores": [
            {
                "id": "espacio_publico", "oficial": True, "inverso": False,
                "nombre": "Espacio público recuperado",
                "unidad": "ha",
                "fuente": "Secretaría de Vivienda",
                "ref_min": 0.0, "ref_max": 10.0,
            },
            {
                "id": "frentes_obra", "oficial": True, "inverso": False,
                "nombre": "Obras de infraestructura activas",
                "unidad": "frentes",
                "fuente": "UP Secretarías",
                "ref_min": 0, "ref_max": 60,
                "gis_archivo": "data/infraestructura/poligonos.geojson",
                "gis_tipo": "conteo_archivo",
            },
            {
                "id": "luminarias", "oficial": True, "inverso": False,
                "nombre": "Luminarias instaladas",
                "unidad": "unidades",
                "fuente": "Emcali / Alumbrado",
                "ref_min": 0, "ref_max": 400,
            },
            {
                "id": "parques", "oficial": True, "inverso": False,
                "nombre": "Parques y zonas verdes intervenidos",
                "unidad": "equipamientos",
                "fuente": "Secretaría de Deporte",
                "ref_min": 0, "ref_max": 15,
            },
            {
                "id": "poligonos_ahdi", "oficial": True, "inverso": False,
                "nombre": "Polígonos en legalización urbanística (AHDI)",
                "unidad": "polígonos / ha",
                "fuente": "Secretaría de Vivienda AHDI · verificado GIS",
                "ref_min": 0, "ref_max": 12,
                "gis_archivo": "data/vivienda/INTERV_AHDI_LEG_URBA_PULMON.geojson",
                "gis_tipo": "conteo_archivo",
            },
            {
                "id": "viviendas_mejoramiento", "oficial": True, "inverso": False,
                "nombre": "Viviendas en mejoramiento (2025-2026)",
                "unidad": "viviendas",
                "fuente": "Secretaría de Vivienda / Convenio Ministerio · verificado GIS",
                "ref_min": 0, "ref_max": 400,
                "gis_archivo": "data/vivienda/INTERV_MEJOR_VIV_25_26_PULMON.geojson",
                "gis_tipo": "suma_campo",
                "gis_campo": "CANT_MEJOR",
            },
        ],
    },

    "movilidad": {
        "nombre": "Movilidad",
        "icono":  "route",
        "peso":   0.20,
        "color":  "#00796B",
        "indicadores": [
            {
                "id": "tramos_viales", "oficial": True, "inverso": False,
                "nombre": "Tramos viales mejorados",
                "unidad": "km",
                "fuente": "Infraestructura Vial · verificado GIS",
                "ref_min": 0.0, "ref_max": 8.0,
                "gis_archivo": "data/infraestructura/tramos_oriente.geojson",
                "gis_tipo": "longitud_lineas",
            },
            {
                "id": "accesibilidad_mio", "oficial": True, "inverso": False,
                "nombre": "Accesibilidad a MIO (500m)",
                "unidad": "%",
                "fuente": "MIO / Metrocali",
                "ref_min": 60.0, "ref_max": 90.0,
            },
            {
                "id": "tiempo_desplazamiento", "oficial": False, "inverso": True,
                "nombre": "Tiempo promedio de desplazamiento",
                "unidad": "min",
                "fuente": "Encuesta estimada",
                "ref_min": 25.0, "ref_max": 55.0,
            },
            {
                "id": "ciclorutas", "oficial": True, "inverso": False,
                "nombre": "Ciclorutas activas en el área",
                "unidad": "km",
                "fuente": "Secretaría de Movilidad",
                "ref_min": 0.0, "ref_max": 5.0,
            },
        ],
    },

    "desarrollo_social": {
        "nombre": "Desarrollo Social",
        "icono":  "people",
        "peso":   0.15,
        "color":  "#6A1B9A",
        "indicadores": [
            {
                "id": "ninos_programas", "oficial": True, "inverso": False,
                "nombre": "Niños en programas de atención",
                "unidad": "beneficiarios",
                "fuente": "Secretaría de Bienestar",
                "ref_min": 0, "ref_max": 4000,
            },
            {
                "id": "sedes_educativas", "oficial": True, "inverso": False,
                "nombre": "Sedes educativas oficiales activas",
                "unidad": "sedes",
                "fuente": "Secretaría de Educación · verificado GIS",
                "ref_min": 40, "ref_max": 100,
                "gis_archivo": "data/equipamientos/Sedes_educativas_oficiales_PULMON_1K.geojson",
                "gis_tipo": "conteo_archivo",
            },
            {
                "id": "acceso_salud", "oficial": True, "inverso": False,
                "nombre": "Acceso a servicios de salud",
                "unidad": "%",
                "fuente": "Secretaría de Salud",
                "ref_min": 50.0, "ref_max": 100.0,
            },
            {
                "id": "familias_subsidio", "oficial": True, "inverso": False,
                "nombre": "Familias en programas de subsidio",
                "unidad": "familias",
                "fuente": "Secretaría de Bienestar",
                "ref_min": 0, "ref_max": 1200,
            },
        ],
    },

    "actividad_economica": {
        "nombre": "Actividad Económica",
        "icono":  "store",
        "peso":   0.15,
        "color":  "#E65100",
        "indicadores": [
            {
                "id": "negocios_formalizados", "oficial": False, "inverso": False,
                "nombre": "Negocios formalizados en el área",
                "unidad": "establecimientos",
                "fuente": "Cámara de Comercio (estimado)",
                "ref_min": 0, "ref_max": 250,
            },
            {
                "id": "empleos_obra", "oficial": True, "inverso": False,
                "nombre": "Empleos generados por obras",
                "unidad": "empleos",
                "fuente": "UP Secretarías",
                "ref_min": 0, "ref_max": 800,
            },
            {
                "id": "inversion_privada", "oficial": False, "inverso": False,
                "nombre": "Inversión privada atraída",
                "unidad": "millones COP",
                "fuente": "Cámara de Comercio (estimado)",
                "ref_min": 0, "ref_max": 15000,
            },
            {
                "id": "emprendimientos", "oficial": False, "inverso": False,
                "nombre": "Iniciativas de emprendimiento apoyadas",
                "unidad": "unidades",
                "fuente": "Secretaría de Desarrollo",
                "ref_min": 0, "ref_max": 80,
            },
        ],
    },
}


# ══════════════════════════════════════════════════════════════════════════════
# UTILIDADES DE FECHA Y PERÍODO
# ══════════════════════════════════════════════════════════════════════════════

def parsear_periodo(periodo_str):
    """'2025-T4' → (2025, 4)"""
    partes = periodo_str.upper().split("-T")
    return int(partes[0]), int(partes[1])


def en_periodo(fecha_val, year, trim):
    """True si fecha_val (str YYYY-MM-DD) cae en el año/trimestre."""
    if not fecha_val:
        return False
    s = str(fecha_val)[:10]
    try:
        d = datetime.strptime(s, "%Y-%m-%d").date()
        inicio = (trim - 1) * 3 + 1
        fin    = trim * 3
        return d.year == year and inicio <= d.month <= fin
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


def extraer_gis(ind_cfg, year, trim):
    """
    Extrae el valor de un indicador según su configuración GIS.
    Devuelve None si no tiene fuente GIS.
    """
    tipo = ind_cfg.get("gis_tipo")
    if not tipo:
        return None

    # ── conteo_periodo: cuenta features cuya fecha cae en el período ──────
    if tipo == "conteo_periodo":
        feats = leer_geojsons_dir(ind_cfg["gis_dir"], ind_cfg.get("gis_patron"))
        campo = ind_cfg.get("gis_campo_fecha", "FECHA_HECH")
        return sum(1 for f in feats if en_periodo(f["properties"].get(campo), year, trim))

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

    return None


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


def nota_hurtos(year, trim):
    feats = leer_geojsons_dir("seguridad/hurtos")
    if not feats:
        return None
    trims = _conteos_trimestrales(feats, "FECHA_HECH")
    if not trims:
        return None
    max_p = max(trims, key=trims.get)
    max_v = trims[max_p]
    cur   = trims.get(f"{year}-T{trim}", 0)
    if max_v and cur:
        pct = round((max_v - cur) / max_v * 100)
        return f"Pico {max_v} ({max_p}) → {cur} ({year}-T{trim}) — reducción {pct}%"
    return None


def nota_homicidios(year, trim):
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

def leer_historico(periodo_actual=None):
    """Lee itt_historico.json y devuelve el último período distinto al actual."""
    hist = leer_json(HIST, default={"periodos": []})
    periodos = hist.get("periodos", [])
    if not periodos:
        return None
    if periodo_actual:
        for p in reversed(periodos):
            if p.get("periodo") != periodo_actual:
                return p
        return None
    return periodos[-1]


def guardar_historico(nuevo):
    """Agrega el período calculado al histórico si no existe ya."""
    hist = leer_json(HIST, default={"periodos": []})
    periodos = hist.get("periodos", [])
    # Reemplazar si ya existe el mismo período
    periodos = [p for p in periodos if p.get("periodo") != nuevo["periodo"]]
    periodos.append(nuevo)
    # Mantener orden cronológico
    periodos.sort(key=lambda p: p.get("periodo", ""))
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
    year, trim = parsear_periodo(periodo_str)
    historico  = leer_historico(periodo_str)
    manuales   = leer_manuales(periodo_str)

    prev_vals  = historico.get("valores_crudos", {})      if historico else {}
    prev_dim_s = historico.get("dimensiones_scores", {})   if historico else {}
    prev_period = historico.get("periodo", "N/A")           if historico else "N/A"

    print(f"\n  Período: {periodo_str}  |  Comparación vs: {prev_period}")

    resultado_dims = []
    itt_global     = 0.0
    vals_actuales  = {}   # Para guardar en histórico

    # ── Notas reales de seguridad (se calculan una vez) ───────────────────
    notas_seg = {
        "hurtos":                nota_hurtos(year, trim),
        "homicidios":            nota_homicidios(year, trim),
        "vif":                   nota_vif(year),
        "vbg":                   nota_vbg(),
        "presencia_institucional": nota_cai(),
    }
    notas_ent = {
        "poligonos_ahdi":       nota_ahdi(),
        "viviendas_mejoramiento": nota_viviendas(),
    }
    NOTAS_EXTRA = {"seguridad": notas_seg, "entorno_urbano": notas_ent}

    for dim_id, dim_cfg in DIMENSIONES.items():
        man_dim   = manuales.get(dim_id, {})
        prev_vals_dim = prev_vals.get(dim_id, {})
        scores_ind = []
        inds_out   = []
        vals_dim   = {}

        for ind in dim_cfg["indicadores"]:
            ind_id = ind["id"]

            # 1. Intentar obtener valor GIS
            valor = extraer_gis(ind, year, trim)

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
            score = normalizar(valor, ind["ref_min"], ind["ref_max"], ind["inverso"])
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
        score_prev = round(prev_dim_s.get(dim_id, 0.0), 1)
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
    prev_global = round(historico.get("itt_score", 0.0), 1) if historico else 0.0
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
        row = {"periodo": p["periodo"], "itt": p.get("itt_score", 0)}
        for d in DIMENSIONES:
            row[d] = p.get("dimensiones_scores", {}).get(d, 0)
        serie_temp.append(row)
    # Agregar período actual si no está
    if not any(r["periodo"] == periodo_str for r in serie_temp):
        row_actual = {"periodo": periodo_str, "itt": itt_global}
        for d_out in resultado_dims:
            row_actual[d_out["id"]] = d_out["score"]
        serie_temp.append(row_actual)

    # Barrios desde manuales
    barrios = manuales.get("_barrios", [])

    resultado = {
        "meta": {
            "territorio":      "Pulmón de Oriente",
            "version":         version,
            "periodo":         periodo_str,
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
            "percepcion_seguridad": 38
        },
        "entorno_urbano": {
            "espacio_publico": 4.2,
            "luminarias":      210,
            "parques":         6
        },
        "movilidad": {
            "accesibilidad_mio":       72,
            "tiempo_desplazamiento":   38,
            "ciclorutas":              1.2
        },
        "desarrollo_social": {
            "ninos_programas":   1840,
            "acceso_salud":       76,
            "familias_subsidio":  520
        },
        "actividad_economica": {
            "negocios_formalizados": 87,
            "empleos_obra":          340,
            "inversion_privada":     4200,
            "emprendimientos":       23
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

def main():
    parser = argparse.ArgumentParser(
        description="Calcula el ITT del Pulmón de Oriente desde fuentes GeoJSON.")
    parser.add_argument("--periodo",          default=None,
                        help="Período (ej. 2025-T4). Default: trimestre actual.")
    parser.add_argument("--version",          default="preliminar",
                        help="'preliminar' u 'oficial'")
    parser.add_argument("--output",           default=None,
                        help="Ruta de salida del JSON (default: data/indices/itt_pulmon.json)")
    parser.add_argument("--generar-manuales", action="store_true",
                        help="Crea data/indices/indicadores_manuales.json con valores por defecto")
    args = parser.parse_args()

    if args.generar_manuales:
        print("\nGenerando indicadores_manuales.json...")
        generar_manuales()
        return

    # Período por defecto: trimestre actual
    if not args.periodo:
        hoy = datetime.today()
        trim = (hoy.month - 1) // 3 + 1
        args.periodo = f"{hoy.year}-T{trim}"

    # Verificar que existen los manuales
    if not MAN.exists():
        print(f"\n  [WARN] No existe {MAN}")
        print("  Ejecuta primero:  python scripts/calcular_itt.py --generar-manuales")
        return

    print(f"\n{'='*60}")
    print(f"  ITT Pulmón de Oriente  ·  {args.periodo}  ·  {args.version}")
    print(f"{'='*60}")

    resultado = calcular_itt(args.periodo, args.version)

    # Guardar JSON
    out_path = Path(args.output) if args.output else OUT
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(resultado, ensure_ascii=False, indent=2), encoding="utf-8")

    g = resultado["itt_global"]
    print(f"\n{'='*60}")
    print(f"  ITT Global: {g['score']}/100  ->  {g['clasificacion']}")
    print(f"  Variación:  {g['variacion']:+.1f} pts vs {g['periodo_comparacion']}")
    print(f"  Cobertura:  {resultado['meta']['cobertura_datos']}%  "
          f"({resultado['meta']['fuentes_activas']}/{resultado['meta']['fuentes_total']} indicadores)")
    print(f"  Guardado:   {out_path}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
