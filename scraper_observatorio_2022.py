#!/usr/bin/env python3
"""
Scraper – Resultados Presidenciales Colombia 2022 (Primera Vuelta)
Fuente: Observatorio Electoral / Estadísticas Electorales Registraduría
https://estadisticaselectorales.registraduria.gov.co
"""

import json
import logging
import time
from pathlib import Path

import pandas as pd
import requests
from tqdm import tqdm

BASE_URL   = "https://estadisticaselectorales.registraduria.gov.co"
DELAY      = 0.4
MAX_RETRY  = 3
OUTPUT_DIR = Path("resultados")
OUTPUT_CSV  = str(OUTPUT_DIR / "resultados_presidenciales_2022_municipios.csv")
OUTPUT_XLSX = str(OUTPUT_DIR / "resultados_presidenciales_2022_municipios.xlsx")
RESUMEN_CSV = str(OUTPUT_DIR / "resumen_nacional_2022.csv")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                    datefmt="%H:%M:%S")
log = logging.getLogger(__name__)


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update({
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Referer": BASE_URL + "/",
    })
    return s


def fetch(url: str, session: requests.Session, params: dict | None = None):
    for attempt in range(1, MAX_RETRY + 1):
        try:
            r = session.get(url, params=params, timeout=30)
            if r.status_code == 404:
                return None
            r.raise_for_status()
            ct = r.headers.get("content-type", "")
            if "json" in ct:
                return r.json()
            return r.text
        except Exception as e:
            if attempt == MAX_RETRY:
                log.warning(f"Error definitivo {url}: {e}")
                return None
            time.sleep(2 ** attempt)
    return None


def explore_api(session: requests.Session):
    """Explora los endpoints disponibles en el Observatorio Electoral."""
    print("\n=== EXPLORANDO API DEL OBSERVATORIO ELECTORAL ===")

    # Endpoints conocidos para estadísticas electorales
    endpoints = [
        "/api/elecciones",
        "/api/resultados",
        "/api/candidatos",
        "/api/municipios",
        "/unit",
        "/api/v1/elecciones",
        "/historicos",
        "/views/electoral/historicos-resultados.php",
    ]

    found = []
    for ep in endpoints:
        url = BASE_URL + ep
        result = fetch(url, session)
        status = "ENCONTRADO" if result else "sin respuesta"
        if result:
            preview = str(result)[:120] if result else ""
            print(f"  {ep}: {status} → {preview}")
            found.append((ep, result))
        else:
            print(f"  {ep}: {status}")
        time.sleep(DELAY)

    return found


def try_direct_api(session: requests.Session):
    """
    Intenta los endpoints específicos de estadísticas electorales 2022.
    """
    print("\n=== PROBANDO ENDPOINTS ESPECÍFICOS 2022 ===")

    # Parámetros observados en la URL del observatorio:
    # str_opc=Elecciones+Presidenciales+Primera+Vuelta
    # idFilter=1, filter=PRESIDENCIALES, t=NACIONALES, y1=2022
    candidates_endpoints = [
        # API REST típica
        f"{BASE_URL}/api/resultados?year=2022&tipo=PRESIDENCIALES&vuelta=1",
        f"{BASE_URL}/api/elecciones/2022/presidente/primera-vuelta",
        # Endpoint de datos del observatorio
        f"{BASE_URL}/views/electoral/historicos-resultados.php",
        # Posible endpoint de descarga CSV
        f"{BASE_URL}/download/2022/presidente/primera-vuelta/municipios.csv",
        f"{BASE_URL}/api/data?y1=2022&filter=PRESIDENCIALES&t=MUNICIPIOS",
        # Alternativas de la Registraduría
        "https://wapp.registraduria.gov.co/electoral/Elecciones-presidente-2022/resultados/",
        "https://wapp.registraduria.gov.co/api/resultados/2022/presidente",
    ]

    found_data = {}
    for url in candidates_endpoints:
        print(f"\nProbando: {url}")
        result = fetch(url, session)
        if result:
            snippet = str(result)[:300]
            print(f"  → RESPUESTA: {snippet}")
            found_data[url] = result
        else:
            print(f"  → Sin respuesta")
        time.sleep(DELAY)

    return found_data


def try_datos_gov(session: requests.Session):
    """Busca datasets en datos.gov.co (portal de datos abiertos de Colombia)."""
    print("\n=== BUSCANDO EN DATOS.GOV.CO ===")

    search_url = "https://www.datos.gov.co/api/views"
    params = {
        "q": "elecciones presidente 2022 municipio",
        "limit": 10,
        "type": "dataset",
    }

    result = fetch(search_url, session, params=params)
    if result:
        if isinstance(result, list):
            print(f"Encontrados {len(result)} datasets:")
            for ds in result[:5]:
                name = ds.get("name", ds.get("n", "?"))
                uid  = ds.get("id",   ds.get("i", "?"))
                print(f"  [{uid}] {name}")
            return result
        else:
            print(f"Respuesta: {str(result)[:400]}")
            return result
    else:
        print("Sin respuesta del portal de datos abiertos")
        return None


def try_moe(session: requests.Session):
    """Intenta obtener datos de la MOE (Misión de Observación Electoral)."""
    print("\n=== PROBANDO MOE ===")

    moe_endpoints = [
        "https://moe.org.co/api/resultados/2022",
        "https://moe.org.co/herramienta/elecciones/2022/presidente",
        "https://datasketch.co/api/resultados/2022/presidente",
        "https://cedae.datasketch.co/api/elecciones/2022",
    ]

    for url in moe_endpoints:
        print(f"Probando: {url}")
        result = fetch(url, session)
        if result:
            print(f"  → ENCONTRADO: {str(result)[:200]}")
            return result
        time.sleep(DELAY)

    return None


def save_findings(data: dict, path: str = "resultados/exploracion_2022.json"):
    """Guarda los hallazgos de la exploración."""
    Path(path).parent.mkdir(exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)
    print(f"\nHallazgos guardados en {path}")


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    session = _session()

    findings = {}

    # 1. Explorar API del Observatorio Electoral
    found_ep = explore_api(session)
    findings["observatorio"] = {ep: str(data)[:500] for ep, data in found_ep}

    # 2. Endpoints directos 2022
    direct = try_direct_api(session)
    findings["direct_2022"] = {url: str(data)[:500] for url, data in direct.items()}

    # 3. Portal datos.gov.co
    datos = try_datos_gov(session)
    findings["datos_gov"] = str(datos)[:1000] if datos else None

    # 4. MOE
    moe = try_moe(session)
    findings["moe"] = str(moe)[:500] if moe else None

    # Guardar todo lo encontrado
    save_findings(findings)

    print("\n=== RESUMEN ===")
    print("Endpoints con respuesta:")
    for source, data in findings.items():
        if data and data != "None":
            print(f"  [{source}] → tiene datos")
        else:
            print(f"  [{source}] → sin datos")

    print("""
Próximos pasos según resultado:
  - Si datos.gov.co devolvió datasets → bajar CSV con:
      https://www.datos.gov.co/api/views/{UID}/rows.csv?accessType=DOWNLOAD
  - Si Observatorio devolvió JSON → adaptar el scraper a esa estructura
  - Si todo falla → bajar manual desde:
      https://estadisticaselectorales.registraduria.gov.co
      (Presidenciales Primera Vuelta 2022 → Exportar CSV)
""")


if __name__ == "__main__":
    main()
