import random
from datetime import date
from pathlib import Path

from src.motor.exposicion import contraste, estadisticos, exposicion, kp_max_por_dia, spearman


def test_kp_max_y_exposicion(tmp_path: Path):
    f = tmp_path / "kp.txt"
    f.write_text("# cabecera\n2021 04 08 0.0 1.5 1 1 1.000 4 1\n2021 04 08 3.0 4.5 1 1 5.333 56 1\n"
                "2021 04 09 0.0 1.5 1 1 2.000 7 1\n2021 04 09 3.0 4.5 1 1 -1.000 -1 1\n", encoding="utf-8")
    kp = kp_max_por_dia(f)
    assert kp == {date(2021, 4, 8): 5.333, date(2021, 4, 9): 2.0}      # Kp=-1 (ausente) se ignora
    assert exposicion([5.333, 2.0, 1.0]) == [5.333, 5.333, 2.0]


def test_spearman_empates_y_extremos():
    assert spearman([1, 2, 3, 4], [10, 20, 30, 40]) == 1.0
    assert spearman([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0
    assert spearman([1, 1, 1, 1], [1, 2, 3, 4]) is None


def test_contraste_detecta_efecto_plantado_y_no_en_ruido():
    rng = random.Random(20261113)
    expo = [float(rng.randint(0, 9)) for _ in range(120)]
    con = {f"p{i}": [(d, 2.0 * expo[d] + rng.gauss(0, 1)) for d in range(120)] for i in range(8)}
    sin = {f"p{i}": [(d, rng.gauss(0, 1)) for d in range(120)] for i in range(8)}
    assert contraste(con, expo, 20261113, n=300)["p_S1_bilateral"] < 0.01
    assert contraste(sin, expo, 20261113, n=300)["p_S1_bilateral"] > 0.05
    assert estadisticos({"a": [(0, 1.0)]}, expo) is None
