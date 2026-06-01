#!/usr/bin/env python3
"""
Scraper - Resultados Presidenciales Colombia 2026
Fuente: https://resultados.registraduria.gov.co
"""

import json
import logging
import time
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

BASE_URL = "https://resultados.registraduria.gov.co"
DELAY = 0.3
MAX_RETRIES = 3
OUTPUT_DIR = Path("resultados")
OUTPUT_CSV = str(OUTPUT_DIR / "resultados_presidenciales_2026_municipios.csv")
OUTPUT_XLSX = str(OUTPUT_DIR / "resultados_presidenciales_2026_municipios.xlsx")
ERROR_LOG = str(OUTPUT_DIR / "errores.log")
RESUMEN_CSV = str(OUTPUT_DIR / "resumen_nacional.csv")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)


def parse_pct(s: str) -> float:
    """'56,08%' → 56.08"""
    if not s:
        return 0.0
    return float(s.strip().rstrip("%").replace(",", "."))


def parse_int(s: str | int) -> int:
    """'4.191' o '4191' → 4191"""
    if s is None:
        return 0
    if isinstance(s, int):
        return s
    cleaned = str(s).replace(".", "").replace(",", "").strip()
    return int(cleaned) if cleaned.isdigit() else 0


def fetch_json(url: str, session: requests.Session) -> dict | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            r = session.get(url, timeout=20)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            return r.json()
        except (requests.RequestException, json.JSONDecodeError) as e:
            if attempt == MAX_RETRIES:
                log.warning(f"Error definitivo {url}: {e}")
                return None
            wait = 2 ** attempt
            time.sleep(wait)
    return None


def get_nomenclator(session: requests.Session) -> dict:
    print("Descargando nomenclator...")
    data = fetch_json(f"{BASE_URL}/json/nomenclator.json", session)
    if not data:
        raise RuntimeError("No se pudo descargar el nomenclator")
    return data


def build_territory_list(nomenclator: dict) -> list[dict]:
    """
    Extrae todos los ámbitos de nivel 3 (municipios) con su departamento padre.
    Los ámbitos de nivel 2 sin hijos de nivel 3 (ej. CONSULADOS) se incluyen
    como territorios únicos.
    """
    ambitos_raw = nomenclator["amb"][0]["ambitos"]
    by_index = {a["i"]: a for a in ambitos_raw}

    territories = []

    for amb in ambitos_raw:
        level = amb.get("l")

        if level == 3:
            # Buscar departamento padre
            dept = None
            for p_entry in amb.get("p", []):
                if p_entry.get("l") == 2:
                    parent_indices = p_entry.get("p", [])
                    if parent_indices:
                        dept = by_index.get(parent_indices[0])
                    break

            territories.append({
                "muni_co": amb["co"],
                "muni_nombre": amb["n"],
                "dept_co": dept["co"] if dept else "??",
                "dept_nombre": dept["n"] if dept else "DESCONOCIDO",
                "level": 3,
            })

        elif level == 2:
            # Solo incluir si NO tiene hijos nivel 3
            has_muni_children = any(
                h.get("l") == 3 for h in amb.get("h", [])
            )
            if not has_muni_children:
                territories.append({
                    "muni_co": amb["co"],
                    "muni_nombre": amb["n"],
                    "dept_co": amb["co"],
                    "dept_nombre": amb["n"],
                    "level": 2,
                })

    return territories


def extract_candidates(result_json: dict, territory: dict) -> list[dict]:
    """Retorna una fila por candidato en el JSON de resultados del ámbito."""
    rows = []

    act = result_json.get("totales", {}).get("act", {})
    mesas_total = parse_int(act.get("metota", 0))
    mesas_escrutadas = parse_int(act.get("mesesc", 0))
    pct_mesas = parse_pct(act.get("pmesesc", "0%"))
    total_votantes = parse_int(act.get("votant", 0))
    pct_participacion = parse_pct(act.get("pvotant", "0%"))
    total_abstencion = parse_int(act.get("absten", 0))
    votos_nulos = parse_int(act.get("votnul", 0))
    votos_no_marcados = parse_int(act.get("votnma", 0))
    votos_blancos = parse_int(act.get("votblan", 0))
    votos_validos = parse_int(act.get("votval", 0))

    camaras = result_json.get("camaras", [])
    if not camaras:
        return rows

    partotabla = camaras[0].get("partotabla", [])

    for partido_entry in partotabla:
        p_act = partido_entry.get("act", {})
        codpar = str(p_act.get("codpar", ""))

        cantotabla = p_act.get("cantotabla", [])
        if not cantotabla:
            continue

        for cand in cantotabla:
            nomcan = cand.get("nomcan", "").strip()
            apecan = cand.get("apecan", "").strip()
            nomcan2 = cand.get("nomcan2", "").strip()
            apecan2 = cand.get("apecan2", "").strip()

            rows.append({
                "dept_co": territory["dept_co"],
                "dept_nombre": territory["dept_nombre"],
                "muni_co": territory["muni_co"],
                "muni_nombre": territory["muni_nombre"],
                "mesas_total": mesas_total,
                "mesas_escrutadas": mesas_escrutadas,
                "pct_mesas_escrutadas": pct_mesas,
                "total_votantes": total_votantes,
                "pct_participacion": pct_participacion,
                "total_abstencion": total_abstencion,
                "votos_nulos": votos_nulos,
                "votos_no_marcados": votos_no_marcados,
                "votos_blancos": votos_blancos,
                "votos_validos": votos_validos,
                "codcan": str(cand.get("codcan", "")),
                "codpar": codpar,
                "candidato_presidente": f"{nomcan} {apecan}".strip(),
                "candidato_vicepresidente": f"{nomcan2} {apecan2}".strip(),
                "votos_candidato": parse_int(cand.get("vot", 0)),
                "pct_votos_candidato": parse_pct(cand.get("pvot", "0%")),
            })

    return rows


def scrape_nacional(session: requests.Session) -> list[dict]:
    data = fetch_json(f"{BASE_URL}/json/ACT/PR/00.json", session)
    if not data:
        log.warning("No se pudo descargar resumen nacional")
        return []
    return extract_candidates(data, {
        "muni_co": "00",
        "muni_nombre": "COLOMBIA",
        "dept_co": "00",
        "dept_nombre": "COLOMBIA",
        "level": 1,
    })


def save_excel(df: pd.DataFrame, path: str) -> None:
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Resultados")
        ws = writer.sheets["Resultados"]
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 2, 40)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    session = requests.Session()
    session.headers.update({
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Referer": "https://resultados.registraduria.gov.co/",
        "Origin": "https://resultados.registraduria.gov.co",
    })

    # 1. Descargar nomenclator y construir lista de territorios
    nomenclator = get_nomenclator(session)
    territories = build_territory_list(nomenclator)

    n_depts = len({t["dept_co"] for t in territories if t["level"] == 3})
    n_munis = sum(1 for t in territories if t["level"] == 3)
    n_especiales = sum(1 for t in territories if t["level"] == 2)
    print(f"Encontrados {n_depts} departamentos y {n_munis} municipios"
          + (f" + {n_especiales} territorio(s) especial(es)" if n_especiales else ""))

    # 2. Resumen nacional
    time.sleep(DELAY)
    nacional_rows = scrape_nacional(session)

    # 3. Iterar territorios
    all_rows: list[dict] = []
    errors: list[str] = []

    with open(ERROR_LOG, "w", encoding="utf-8") as err_file:
        for territory in tqdm(territories, desc="Procesando municipios"):
            time.sleep(DELAY)
            co = territory["muni_co"]
            data = fetch_json(f"{BASE_URL}/json/ACT/PR/{co}.json", session)

            if data is None:
                msg = (f"ERROR {co} - {territory['muni_nombre']} "
                       f"({territory['dept_nombre']})")
                err_file.write(msg + "\n")
                errors.append(co)
                continue

            all_rows.extend(extract_candidates(data, territory))

    # 4. Construir DataFrame y coercer tipos
    print("\nGuardando archivos...")
    df = pd.DataFrame(all_rows)

    int_cols = [
        "mesas_total", "mesas_escrutadas", "total_votantes",
        "total_abstencion", "votos_nulos", "votos_no_marcados",
        "votos_blancos", "votos_validos", "votos_candidato",
    ]
    float_cols = ["pct_mesas_escrutadas", "pct_participacion", "pct_votos_candidato"]

    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    for col in float_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"✓ {OUTPUT_CSV} ({len(df):,} filas)")

    save_excel(df, OUTPUT_XLSX)
    print(f"✓ {OUTPUT_XLSX}")

    # 5. Resumen nacional
    if nacional_rows:
        df_nac = pd.DataFrame(nacional_rows)
        for col in int_cols:
            if col in df_nac.columns:
                df_nac[col] = pd.to_numeric(df_nac[col], errors="coerce").fillna(0).astype(int)
        df_nac.to_csv(RESUMEN_CSV, index=False, encoding="utf-8-sig")
        print(f"✓ {RESUMEN_CSV}")

    # 6. Validación cruzada
    print("\n=== VALIDACIÓN ===")
    total_procesados = len(territories) - len(errors)
    print(f"Municipios procesados: {total_procesados} / {len(territories)}")

    if not df.empty:
        avg_cands = df.groupby("muni_co")["codcan"].count().mean()
        print(f"Candidatos por municipio (promedio): {avg_cands:.1f}")

        # Referencia cruzada con totales nacionales
        ref = {}
        if nacional_rows:
            for row in nacional_rows:
                ref[row["codcan"]] = (row["candidato_presidente"], row["votos_candidato"])

        for codcan, nombre_ref in [("4", "De La Espriella"), ("1", "Cepeda Castro")]:
            total_sum = int(df[df["codcan"] == codcan]["votos_candidato"].sum())
            nac = ref.get(codcan)
            nac_str = f"  (nacional directo: {nac[1]:,})" if nac else ""
            print(f"Votos {nombre_ref} (sum municipios): {total_sum:,}{nac_str}")

    print(f"Municipios sin datos: {len(errors)}")
    if errors:
        print(f"  → Ver {ERROR_LOG} para detalle")


if __name__ == "__main__":
    main()
