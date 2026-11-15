"""MP-11 · CUSUM sobre residuos blanqueados AR(1). Implementación VALIDADA CON SIMULACIÓN (X-06, semillas públicas);
no usa los datos de la evaluación FB-010. Verifica que φ = 0 no cambia nada y que φ = ρ devuelve el FPR al nominal."""
import random
from datetime import date, timedelta

import pytest

from src.contratos import SEMILLAS_PUBLICAS
from src.contratos.comunes import Indicador
from src.contratos.dc05_alarma import EstadoAlarma
from src.motor.alertas import a_dc05, reevaluar
from src.motor.cusum import calibrar_h, ejecutar_regla, regla_exacta
from src.motor.evaluacion import PHI_MAX, ejecutar_unidad, estimar_phi, lag1, particion
from src.motor.modelo_nulo import ModeloNulo

F0 = date(2026, 1, 1)
H = calibrar_h()


def ar1(rng, n, rho, media=0.0):
    x, out = rng.gauss(0, 1), []
    for _ in range(n):
        x = rho * x + (1 - rho * rho) ** 0.5 * rng.gauss(0, 1)
        out.append(media + x)
    return [(F0 + timedelta(days=i), v) for i, v in enumerate(out)]


def fpr(rho, phi, n=2500, semilla=SEMILLAS_PUBLICAS[0], delta=0.0):
    rng, alarmas = random.Random(semilla), 0
    for _ in range(n):
        s = ar1(rng, 28, rho)
        alarmas += ejecutar_unidad("sim", Indicador.SUENO, 0.0, s[:14], s[14:], H, delta=delta, phi=phi).alarma
    return alarmas / n


def test_phi_cero_no_cambia_nada():
    rng = random.Random(SEMILLAS_PUBLICAS[1])
    s = ar1(rng, 28, 0.3)
    a = ejecutar_unidad("sim", Indicador.SUENO, 0.0, s[:14], s[14:], H, delta=2.0)
    b = ejecutar_unidad("sim", Indicador.SUENO, 0.0, s[:14], s[14:], H, delta=2.0, phi=0.0)
    assert a == b


def test_con_autocorrelacion_el_cusum_sin_blanquear_se_descalibra_y_el_blanqueado_la_corrige():
    sin, con = fpr(0.4, 0.0), fpr(0.4, 0.4)
    assert sin > 0.05               # sin blanquear: ≈7-8 % en vez de 1 %
    assert con < 0.025              # blanqueado con φ = ρ: vuelve hacia el 1 %
    assert con < sin / 2


def test_con_ruido_independiente_blanquear_con_phi_pequeno_apenas_cambia_el_fpr():
    assert abs(fpr(0.0, 0.0) - fpr(0.0, 0.2)) < 0.03


def test_el_blanqueado_conserva_potencia_a_dos_sigma():
    # con φ = ρ = 0.3 la señal de un cambio sostenido se atenúa por √((1−φ)/(1+φ)) pero sigue siendo detectable
    rng = random.Random(SEMILLAS_PUBLICAS[2])
    n, detectadas = 800, 0
    for _ in range(n):
        s = ar1(rng, 28, 0.3)
        detectadas += ejecutar_unidad("sim", Indicador.SUENO, 0.0, s[:14], s[14:], H, delta=3.0, phi=0.3).alarma
    assert detectadas / n >= 0.9


def test_el_modelo_con_phi_emite_dc06_validos_y_su_recibo_se_reproduce():
    rng = random.Random(SEMILLAS_PUBLICAS[0])
    m = ModeloNulo("p-sim", Indicador.SUENO, 0.0, h=3.0, phi=0.3)
    s = ar1(rng, 14, 0.3, media=500.0)
    for d, v in s:
        m.observar(d, v * 10)
    alarma = None
    for i in range(30):
        o = m.observar(F0 + timedelta(days=14 + i), m.linea_base.media - 2.0 * m.linea_base.sigma_efectiva)
        assert o.residuo is None or o.residuo.residuo == pytest.approx(o.residuo.observado - o.residuo.predicho)
        if o.alarma:
            alarma = o.alarma
            break
    assert alarma and "phi=0.3" in alarma.regla_exacta and "x0=" in alarma.regla_exacta
    dc05 = a_dc05(alarma, indicador=Indicador.SUENO, alarma_id="al-1", semilla=SEMILLAS_PUBLICAS[0], hash_preregistro="a" * 64)
    r = ejecutar_regla(dc05.regla_exacta, list(alarma.valores))
    assert r.alarma and r.indice == len(alarma.valores) - 1
    assert reevaluar(dc05, list(alarma.valores)).estado is EstadoAlarma.ACTIVA
    assert reevaluar(dc05, [x + 500 for x in alarma.valores]).estado is EstadoAlarma.RETIRADA


def test_la_regla_con_phi_exige_x0_y_phi_invalido_se_rechaza():
    with pytest.raises(ValueError, match="x0"):
        regla_exacta(0.5, 4.0, 0.0, 1.0, phi=0.3)
    with pytest.raises(ValueError, match="phi"):
        ModeloNulo("p-sim", Indicador.SUENO, 0.0, phi=1.2)


def test_la_particion_es_determinista_y_reparte_aproximadamente_la_mitad():
    ids = [f"persona-{i:03d}" for i in range(400)]
    partes = [particion(i) for i in ids]
    assert partes == [particion(i) for i in ids]
    assert 0.4 < partes.count("prueba") / len(ids) < 0.6


def test_estimar_phi_recupera_la_autocorrelacion_y_se_acota():
    rng = random.Random(SEMILLAS_PUBLICAS[0])
    series = {f"p{i}": ar1(rng, 56, 0.4) for i in range(60)}
    phi = estimar_phi(series, filtro_personas=lambda p: True)
    # el estimador lag-1 sobre solo 28 puntos tiene sesgo A LA BAJA conocido: estima ≈0.28 cuando la verdad es 0.4
    assert 0.2 < phi < 0.4
    assert estimar_phi({}, filtro_personas=lambda p: True) == 0.0
    chorro = {"x": [(F0 + timedelta(days=i), float(i)) for i in range(28)]}  # tendencia pura: autocorr ≈ 1
    assert estimar_phi(chorro, filtro_personas=lambda p: True) == PHI_MAX
    assert lag1([1.0] * 10) == 0.0
