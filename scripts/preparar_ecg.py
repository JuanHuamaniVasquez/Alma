"""Descarga el ECG público S-20 y exige los hashes ya registrados en el lector."""
from pathlib import Path
import hashlib
import sys
from urllib.request import urlopen

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.ingesta.ecg_mitbih import SHA256


def preparar():
    destino = RAIZ / "data" / "externos" / "mitdb"
    destino.mkdir(parents=True, exist_ok=True)
    for nombre, esperado in SHA256.items():
        ruta = destino / nombre
        if ruta.exists() and hashlib.sha256(ruta.read_bytes()).hexdigest() == esperado:
            continue
        with urlopen(f"https://physionet.org/files/mitdb/1.0.0/{nombre}", timeout=60) as respuesta:
            contenido = respuesta.read()
        if hashlib.sha256(contenido).hexdigest() != esperado:
            raise ValueError(f"PhysioNet: hash inesperado para {nombre}; no se instala")
        ruta.write_bytes(contenido)
        print(f"ECG REAL verificado: {nombre}")


if __name__ == "__main__":
    preparar()
