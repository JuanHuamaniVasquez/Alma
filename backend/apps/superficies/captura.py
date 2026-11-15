"""IN-2 · Captura del autorreporte de ánimo (DC-02) — la ÚNICA escritura de la API.

Reglas: el contrato valida antes de guardar (escala declarada, valor 1–5, duración medida en pantalla); el `persona_id` es un pseudónimo generado en
el navegador (nunca un nombre); un mismo pseudónimo no puede reportar más de una vez cada MIN_ENTRE_REPORTES_S; el banner es REAL (lo escribe
una persona real, que NO es astronauta) y el agregado que se lee después no expone ids.
"""
from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pydantic import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ingesta.models import Autorreporte
from apps.ingesta.repositorio import guardar_autorreporte
from src.contratos.comunes import Banner
from src.contratos.dc02_autorreporte import DC02Autorreporte, TipoAutorreporte

ESCALA = "Likert 1-5 (1 = very low, 5 = very good)"
MIN_ENTRE_REPORTES_S = 10


class Animo(APIView):
    """POST {persona_id, valor (1-5), duracion_respuesta_s} → guarda un DC-02. No lee ni devuelve nada individual."""
    http_method_names = ["post", "options"]

    def post(self, request):
        d = request.data if isinstance(request.data, dict) else {}
        ahora = datetime.now(UTC)
        pid = d.get("persona_id")
        if isinstance(pid, str) and Autorreporte.objects.filter(persona_id=pid, ts_utc__gt=ahora - timedelta(seconds=MIN_ENTRE_REPORTES_S)).exists():
            return Response({"error": "too soon: one report per pseudonym every 10 s"}, status=429)
        try:
            r = DC02Autorreporte.model_validate(dict(persona_id=pid, ts_utc=ahora, banner=Banner.REAL, tipo=TipoAutorreporte.ANIMO, escala=ESCALA,
                                                     valor=d.get("valor"), duracion_respuesta_s=d.get("duracion_respuesta_s"), registro_ausencia=False))
            if not 1 <= r.valor <= 5:
                raise ValueError("valor fuera de la escala 1-5")
        except (ValidationError, ValueError, TypeError) as e:
            return Response({"error": str(e)[:200]}, status=400)
        guardar_autorreporte(r)
        return Response({"ok": True}, status=201)
