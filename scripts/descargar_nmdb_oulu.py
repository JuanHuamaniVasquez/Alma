"""M9 · FB-029: baja la serie horaria CORREGIDA POR PRESIÓN del monitor de neutrones de Oulu (NMDB) 2008–2025, un año por consulta, a data/externos/nmdb_oulu/ (ignorado por git).
Fuente S-34 (NMDB, interfaz NEST, `dtype=corr_for_pressure`). Reconocimiento obligatorio: ver `src/ingesta/entorno.py::ACK_NMDB`.
Guarda cada respuesta cruda (para su hash) y un CSV `ts_utc,cps`; los huecos quedan como huecos (no se rellenan). Uso: uv run python scripts/descargar_nmdb_oulu.py"""
import hashlib
import json
import re
import time
import urllib.request
from pathlib import Path

SAL = Path(__file__).resolve().parent.parent / "data/externos/nmdb_oulu"
URL = ("https://www.nmdb.eu/nest/draw_graph.php?formchk=1&stations%5B%5D=OULU&tabchoice=1h&dtype=corr_for_pressure&tresolution=60&force=1&yunits=0&date_choice=bydate"
       "&start_day=1&start_month=1&start_year={a}&start_hour=0&start_min=0&end_day=31&end_month=12&end_year={a}&end_hour=23&end_min=59&output=ascii")


def main() -> None:
    SAL.mkdir(parents=True, exist_ok=True)
    filas, man = [], {}
    for a in range(2008, 2026):
        raw = SAL / f"crudo_{a}.html"
        if not raw.exists():
            for intento in range(3):
                try:
                    with urllib.request.urlopen(urllib.request.Request(URL.format(a=a), headers={"User-Agent": "ALMA-TONO-LAB/0.1 (student project)"}), timeout=120) as r:
                        raw.write_bytes(r.read())
                    break
                except Exception as e:                                   # noqa: BLE001
                    print("reintento", a, e); time.sleep(5)
        cuerpo = raw.read_bytes()
        man[raw.name] = hashlib.sha256(cuerpo).hexdigest()
        b = re.search(r"<pre><code>(.*?)</code></pre>", cuerpo.decode("utf-8", "replace"), re.S).group(1)
        n = 0
        for l in b.splitlines():
            p = l.strip().split(";")
            if len(p) == 2 and re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d", p[0]):
                try:
                    filas.append((p[0].replace(" ", "T") + "Z", float(p[1]))); n += 1
                except ValueError:
                    pass
        print(a, n, "filas")
    csv = SAL / "oulu_1h_presion_2008_2025.csv"
    csv.write_text("ts_utc,cps\n" + "\n".join(f"{t},{v}" for t, v in filas) + "\n", encoding="utf-8")
    man[csv.name] = hashlib.sha256(csv.read_bytes()).hexdigest()
    (SAL / "MANIFIESTO.sha256.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    print(len(filas), "filas", csv.name, man[csv.name])


if __name__ == "__main__":
    main()
