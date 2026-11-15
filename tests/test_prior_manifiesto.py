import random

from src.motor.prior_manifiesto import cargar, cocientes, cuantil, muestrear_log

D = cargar()


def test_cifras_del_paper_se_reproducen():
    upa = {f["acronimo"]: f["mtbf_mads_h"] / f["mtbf_vuelo_h"] for f in D["filas"] if f["sistema"] == "UPA"}
    # Jones 2019 dice «de 7,5 a 22 veces»: DA = 7,5; FCPA ≈ 22,8 (el paper redondea a 22)
    assert round(upa["DA"], 1) == 7.5 and 22.0 <= upa["FCPA"] <= 23.0
    wpa = [f["mtbf_mads_h"] / f["mtbf_vuelo_h"] for f in D["filas"] if f["sistema"] == "WPA" and f["acronimo"] in {"CR", "MCV", "RHS", "S"}]
    assert 1.9 <= min(wpa) < 2.0 and 2.5 <= max(wpa) <= 2.7   # «de 1,9 a 2,6»


def test_censuradas_separadas_de_medidas():
    med, cen = cocientes(D, medidas=True), cocientes(D, medidas=False)
    assert len(med) >= 8 and len(cen) >= 10
    assert all(f["mtbf_vuelo_h"] == 70000 for f in D["filas"] if f["vuelo_censurado"])
    assert cuantil(med, 0.5) > 1.0          # el manifiesto fue optimista en la mediana de las medidas


def test_muestreo_reproducible():
    a = [muestrear_log(D, random.Random(20261113)) for _ in range(3)]
    b = [muestrear_log(D, random.Random(20261113)) for _ in range(3)]
    assert a == b
