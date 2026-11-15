"""M2.6 · IN-4: las tres clases de anomalía se inyectan y se detectan (o no) según diseño; banner y semilla pública en toda corrida."""
import subprocess
import sys
from pathlib import Path

import pytest

from src.motor.banco import ESCENARIOS, banner, deriva_coherente, flujo_no_contabilizado, fuga_fisica, modo_adversario, monte_carlo
from src.motor.adversario import calibrar_hv

RAIZ = Path(__file__).resolve().parent.parent


def test_banner_obligatorio_en_toda_corrida():
    assert banner(7, 20261113) == "UNIVERSO SIMULADO — DÍA 7 · semilla 20261113"
    for e, f in ESCENARIOS.items():
        r = f(20261113)
        assert r["banner"].startswith("UNIVERSO SIMULADO — DÍA") and "20261113" in r["banner"], e


def test_deriva_coherente_la_caza_el_cusum_y_antes_que_nada_mas_lento():
    m = monte_carlo("deriva_coherente", 20261113, 60)
    assert m["tasa_deteccion"] >= 0.95


def test_flujo_no_contabilizado_manifiesto_ciego_ley_alarma():
    r = flujo_no_contabilizado(20261113)
    assert r["manifiesto_alarma"] is False and r["ley_veredicto"] == "NO CIERRA" and r["detecta"]


def test_fuga_fisica_se_clasifica_como_mundo():
    assert monte_carlo("fuga_fisica", 20261113, 60)["tasa_deteccion"] >= 0.9
    assert fuga_fisica(20261113)["diagnostico"] == "mundo"


def test_modo_adversario_zigzag_evade():
    r = modo_adversario("zigzag", 2.0, 20261113, 80, calibrar_hv(n=2000))
    assert r["media"] <= 0.10 and r["banner"].startswith("UNIVERSO SIMULADO")


def test_cli_rechaza_semilla_no_publica():
    p = subprocess.run([sys.executable, "scripts/banco.py", "fuga_fisica", "--semilla", "7"], cwd=RAIZ, capture_output=True, text=True)
    assert p.returncode != 0 and "semilla" in (p.stderr + p.stdout)


def test_cli_imprime_el_banner():
    p = subprocess.run([sys.executable, "scripts/banco.py", "fuga_fisica", "--n", "5"], cwd=RAIZ, capture_output=True, text=True)
    assert p.returncode == 0 and "UNIVERSO SIMULADO" in p.stdout
