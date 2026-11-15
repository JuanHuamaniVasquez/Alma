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
