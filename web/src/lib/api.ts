// Cliente de LECTURA del backend (DRF, solo GET). Lo que no llega, no se dibuja: la ausencia es dato.
export type Banner = "REAL" | "SIMULADO";
export const BANNER_EN: Record<Banner, string> = { REAL: "REAL DATA", SIMULADO: "SIMULATED UNIVERSE" };

export type HabitatLine = {
  presupuesto_id: string; emision_esperada: number; incertidumbre_del_manifiesto: number;
  emision_observada: number; residuo_contable: number; estado_linea: string; cierra: boolean;
};
export type LedgerDay = {
  banner: Banner; dia_habitat: number; cierra: boolean;
  presupuestos: Record<string, { lineas: number; abiertas: number; cierra: boolean }>;
  habitat: HabitatLine[];
};
export type LedgerDays = { banner: Banner; dias: number[]; ultimo: number | null };

export async function get<T>(url: string): Promise<T | null> {
  try { const r = await fetch(url, { cache: "no-store" }); return r.ok ? ((await r.json()) as T) : null; } catch { return null; }
}

/** Los 9 presupuestos del libro (DC-04), en el orden fijo del anillo. */
export const BUDGETS = [
  ["aire", "Air"], ["agua", "Water"], ["energia", "Energy"], ["dosis", "Dose"], ["ritmo", "Rhythm"],
  ["carga", "Load"], ["inmunidad", "Immunity"], ["conducta", "Conduct"], ["tiempo", "Time"],
] as const;

/** Veredictos del backend (español) → inglés de la vitrina. Lo desconocido se muestra tal cual: no se adivina. */
const WORDS: Record<string, string> = {
  SOSTENIDA: "SUSTAINED", REFUTADA: "REFUTED", "NO CONCLUYENTE": "INCONCLUSIVE", "NO REFUTADA": "NOT REFUTED", "NO SOSTENIDA": "NOT SUSTAINED", PARCIAL: "PARTIAL", "NO REPLICADA": "NOT REPLICATED",
  sostenida: "SUSTAINED", refutada: "REFUTED", en_prueba: "IN TEST", sin_datos: "NO DATA", vivero: "NURSERY", preregistrada: "PREREGISTERED",
};
export const word = (s: string) => WORDS[s] ?? s;

export type DemoKill = {
  acta: string; hash_acta: string; acta_registrada_utc: string; ts_ejecucion_utc: string; semilla: number; banner: string;
  control: DKDay; fuga: DKDay; prediccion_confirmada: boolean;
};
export type DKDay = { fuga_kg: number; A_manifiesto: { z: number; alarma: boolean }; B_ley: { residuo_kg: number; sigma_propagada_kg: number; veredicto: string } };

export type Acta = { acta: string; hash_sha256: string; registrada_utc: string; semillas: number[]; estado: string; ejecutada: boolean; veredictos: unknown; banner: string | null;
  en: { title: string; summary: string; outcome: string; data: string; tags: string[] } | null };
export type Tarjeta = {
  tarjeta_id: string; estado: string; preregistro_hash: string; fuentes: unknown[];
  en: { title: string; prediction: string; refuter: string; mechanism: string; result: string } | null;
};
export type Fundicion = {
  tablero: { nacidas: number; refutada: number; sostenida: number; en_prueba: number; sin_datos: number; detectores_nuevos: number };
  tarjetas: Tarjeta[]; detectores: { tarjeta_id: string; detector: string; hash_preregistro: string; en: { title: string; rule: string; limit: string } | null }[];
  faro: { id: string; probabilidad: number; fecha_limite: string; sha256: string; emitida_utc: string; en: { statement: string; grading: string } | null }[];
};

export type ResidualPoint = {
  ts_utc: string; presupuesto_id: string; observado: number; predicho: number; residuo: number;
  sigma_efectiva: number; cusum_acumulado: number; bandera: string; banner: Banner;
};
export type Residuals = { banner: Banner; habitat: ResidualPoint[] };

export type SpaceEvent = { evento_id: string; ts_utc_inicio: string; tipo: string; fuente: string; parametros: { kp?: number }; hash_lectura_cruda: string; banner: Banner };

export type Scenario = { banner: Banner; aviso: string; dia_habitat: number; escala: string; semilla: number; receta: string; receta_en: string; paso_horas: number; pico_kp: number; eventos: SpaceEvent[] };

export type Capsule = {
  version: string; banner: Banner; hipotesis: string; prueba_protocolo: string; preregistro: { hash: string; semilla: number };
  numeros: Record<string, number | string>; senal_refutadora: string; veredicto: string; limites: string;
};

export type Indicator = {
  indicador: string; bloqueado: string | null; personas_con_linea_base?: number; verde?: number; sin_datos_suficientes?: number; alarma?: number;
  cobertura_media?: number | null; mde_sigma_mediana?: number | null; unidad?: string | null; potencia_declarada?: number | null; banner?: Banner; fuente?: string;
  crew?: "verde" | "alarma" | "sin_datos_suficientes";   // estado del SUSTITUTO del tripulante elegido (solo se rellena en la vista de tripulante)
  canal?: string; reportes?: number; personas?: number; distribucion?: Record<string, number>; duracion_mediana_s?: number | null; escala?: string;
};
export const INDICATOR_NAMES: Record<string, string> = { fc: "Heart rate", "sueño": "Sleep", "presión": "Blood pressure", glucosa: "Glucose", temperatura: "Temperature", "ánimo": "Mood" };

/** Pseudónimo de este navegador para el autorreporte (nunca un nombre). */
export function crewId(): string {
  try {
    let id = localStorage.getItem("alma-crew-id");
    if (!id) { id = "crew-" + Array.from(crypto.getRandomValues(new Uint8Array(4)), (b) => b.toString(16).padStart(2, "0")).join(""); localStorage.setItem("alma-crew-id", id); }
    return id;
  } catch { return "crew-" + Math.random().toString(16).slice(2, 10); }
}

export type CrewMember = { indicativo: string; rol: string; color: string; piel: string; pelo: string; peinado: string; complexion: number; estado: { fc: string; "sueño": string } | null };
export type CrewPayload = { banner: Banner; aviso: string; tripulacion: CrewMember[] };
export const CREW_STATE_EN: Record<string, string> = { verde: "a green with a receipt", alarma: "an alarm with a receipt — a question, not a verdict", sin_datos_suficientes: "too few days to say" };

export type PrivacyBook = { banner: Banner; n_tripulacion: number; epsilon_total: number; epsilon_gastado: number; epsilon_restante: number; cierra: boolean; nota: string;
  asientos: { etiqueta: string; epsilon: number; mecanismo: string; sensibilidad: number; n: number; valor_publicado: number }[] };

export type NilmBook = { banner: Banner; ejecutada: boolean; hash_acta?: string; azar?: number; sigma_rel?: number; n_por_celda?: number;
  curvas?: Record<string, { paso_h: number; exactitud: number }[]>; veredictos?: Record<string, string | number | null> };

export type EProcess = { banner: Banner; alfa: number; umbral: number; s: number; curva: number[]; escalon_dia: number; ejecutada: boolean; hash_acta?: string | null;
  entrenamiento?: Record<string, { k: number; n: number; fpr_entrenamiento: number; potencia_h2: number; apto: boolean }> | null; veredictos?: Record<string, string> | null };

export type Entorno = { banner: Banner; aviso: string;
  iss: { disponible: boolean; lat?: number; lon?: number; alt_km?: number; vel_kms?: number; visibilidad?: string; sol_lat?: number; sol_lon?: number; ts_utc?: string; a_la_luz?: boolean };
  protones: { disponible: boolean; pfu?: number; max_ventana_pfu?: number; tormenta_s1_o_mas?: boolean; umbral_s1_pfu?: number; ts_utc?: string; serie?: number[] };
  rayosx: { disponible: boolean; clase?: string; max_ventana?: string; ts_utc?: string } };
export type Astronautas = { banner: Banner; ejecutada: boolean; hash_acta?: string; fuente?: string; n_personas?: number; tiempos?: string[]; aviso?: string;
  conciliacion?: { valores: number; filas: number; de_filas: number };
  tabla?: Record<string, { dentro: number; arriba: number; abajo: number; sin_datos: number; sospechoso: number; mediana_cambio_pct: number | null; n: number }>; veredictos?: Record<string, string | number | { valores: number; filas: number }> };
export type Osdr = { capturado_utc: string; n: number; n_crew: number; nota: string; estudios: { accession: string; titulo: string; liberado: string | null; ensayos: string[]; mision: string | null; tipo: "crew" | "cells"; url: string }[] };

export type Frontera = { banner: Banner; regla_color: string; fichas: { id: string; verdict: "held" | "failed" | "mixed" | "measured" | "open"; hash: string | null; numeros: Record<string, number> }[] };
