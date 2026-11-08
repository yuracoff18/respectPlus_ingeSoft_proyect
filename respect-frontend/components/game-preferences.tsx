"use client";

import { GAMES } from "@/lib/types";

export function GamePreferences({ selected, legend = "Preferencias de juego" }: { selected: string[]; legend?: string }) {
  return <fieldset className="game-preferences"><legend>{legend}</legend><div className="game-checks">{GAMES.map(game => <label key={game} className="checkbox-label"><input type="checkbox" name="games" value={game} defaultChecked={selected.includes(game)} />{game}</label>)}</div></fieldset>;
}
