from pathlib import Path

from src.contratos.comunes import Banner, IndicadorSensor
from src.contratos.dc01_sensores import CalidadDato
from src.ingesta.fatiga_zenodo import cargar, sanos

CAB = "user_id,date,heart_rate__mean,sleep__total_asleep_minutes\n"


def test_solo_sanos_y_ausencia_es_dato(tmp_path: Path):
    (tmp_path / "s.csv").write_text("user_id,diagnosis\nFS1,none\nFS2,sle\n", encoding="utf-8")
    (tmp_path / "d.csv").write_text(CAB + "FS1,2020-08-18,70.5,420\nFS1,2020-08-19,,\nFS2,2020-08-18,80,300\n", encoding="utf-8")
    regs = cargar(tmp_path / "d.csv", sanos(tmp_path / "s.csv"))
    assert {r.persona_id for r in regs} == {"FS1"} and len(regs) == 4
    assert all(r.banner is Banner.REAL for r in regs)
    aus = [r for r in regs if r.calidad is CalidadDato.AUSENTE]
    assert len(aus) == 2 and all(r.valor is None for r in aus)
    ok = {r.indicador: r.valor for r in regs if r.calidad is CalidadDato.OK}
    assert ok == {IndicadorSensor.FC: 70.5, IndicadorSensor.SUENO: 420.0}


def test_valor_imposible_es_sospechoso(tmp_path: Path):
    (tmp_path / "d.csv").write_text(CAB + "FS1,2020-08-18,0,2000\n", encoding="utf-8")
    regs = cargar(tmp_path / "d.csv", {"FS1"})
    assert all(r.calidad is CalidadDato.SOSPECHOSO for r in regs)
