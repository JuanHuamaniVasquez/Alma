"""SU · Vocabulario HABLADO del buscador de La Bóveda. ALMA no sintetiza frases libres: compone su respuesta encadenando clips cortos
pre-generados (frases fijas, números, ids de acta, veredictos, salas), así suena con su voz, al instante y sin poder decir nada que no esté en el vocabulario.
Las claves son contrato con la vitrina (`web/src/lib/search.ts`): cambiarlas aquí exige cambiarlas allí."""
from __future__ import annotations

import re

_NUM = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen", "twenty", "twenty-one", "twenty-two", "twenty-three", "twenty-four", "twenty-five"]
_DIG = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]

RESULTADOS = {"refuted": "refuted", "sustained": "sustained", "mixed": "mixed results", "inconclusive": "inconclusive", "partial": "partial",
              "not_replicated": "not replicated", "not_run": "sealed, not yet run", "no_data": "no data"}
SALAS = {"medical": "the Medical Module", "machine": "the Machine Room", "kill": "the Leak", "vault": "the Vault", "foundry": "the Foundry",
         "storm": "the Storm", "budget": "the Budget", "capsule": "the Capsule"}
FRASES = {
    "i_found": "I found", "experiment": "experiment.", "experiments": "experiments.", "best": "The best match is", "then": "Then",
    "none": "I found nothing like that in the vault.", "closest": "The closest are", "try": "Try a topic, a verdict, or an experiment number.",
    "opening": "Opening", "no_id": "There is no experiment with that number.", "going": "Going to", "verifying": "Recomputing every hash in your browser.",
    "cleared": "Showing the whole vault.", "showing": "Showing", "heard_nothing": "I did not catch that. You can type instead.",
    "help": "You can say: show refuted experiments, find solar storms, open F B zero two zero, verify everything, or go to the foundry.",
    "and": "and",
}


def hablar_id(acta: str) -> str:
    """FB-005-D1 → «F B zero zero five, D one»; FB-020-v2 → «F B zero two zero, version two»; FB-003R → «F B zero zero three R»."""
    m = re.fullmatch(r"FB-(\d+)(?:-(D1|v2)|(R))?", acta)
    if not m:
        raise ValueError(f"id de acta no hablable: {acta}")
    digitos = " ".join(_DIG[int(c)] for c in m.group(1))
    sufijo = {"D1": ", D one", "v2": ", version two"}.get(m.group(2) or "", "") + (" R" if m.group(3) else "")
    return f"F B {digitos}{sufijo}"


def clips(ids: list[str]) -> dict[str, str]:
    """{clave: texto} de todo lo que el buscador puede decir."""
    out = dict(FRASES)
    out.update({f"n_{i}": _NUM[i] for i in range(len(_NUM))})
    out.update({f"o_{k}": v for k, v in RESULTADOS.items()})
    out.update({f"room_{k}": v for k, v in SALAS.items()})
    out.update({f"id_{a}": hablar_id(a) for a in ids})
    return out
