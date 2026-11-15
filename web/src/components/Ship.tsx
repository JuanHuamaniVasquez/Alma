"use client";
import { createContext, useContext, useState } from "react";

/** Estado compartido de la nave: el día del libro que se está mirando (la barra superior y la sala deben coincidir). */
const ShipCtx = createContext<{ day: number | null; setDay: (d: number | null) => void }>({ day: null, setDay() {} });
export const useShip = () => useContext(ShipCtx);
export function ShipProvider({ children }: { children: React.ReactNode }) {
  const [day, setDay] = useState<number | null>(null);
  return <ShipCtx.Provider value={{ day, setDay }}>{children}</ShipCtx.Provider>;
}
