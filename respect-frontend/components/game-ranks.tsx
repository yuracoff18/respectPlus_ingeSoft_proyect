import type { Player } from "@/lib/types";
import { Icon } from "./icon";

export function rankFor(player: Player, game: string) {
  const profile = player.game_profiles?.[game];
  return profile?.current_rank || (profile?.status === "unavailable" ? "Rango no disponible" : "Sin sincronizar");
}

export function GameRanks({ player, onlyGame, compact = false }: { player: Player; onlyGame?: string; compact?: boolean }) {
  const games = onlyGame ? [onlyGame] : player.games;
  if (!games.length) return <p className="muted small">Sin juegos preferidos.</p>;
  if (compact) return <div className="game-rank-tags">{games.map(game => <span key={game} className="tag"><Icon name="game" size={13} /><span>{game} <strong>· {rankFor(player, game)}</strong></span></span>)}</div>;
  return <div className="game-ranks">{games.map(game => {
    const profile = player.game_profiles?.[game];
    return <div key={game} className="game-rank-card"><div className="game-rank-heading"><Icon name="game" size={19} /><strong>{game}</strong></div><div className="rank-values"><span>{profile?.status === "stale" ? "Último rango conocido" : "Rango actual"}<strong>{rankFor(player, game)}</strong></span>{profile?.peak_rank && <span>Pico{profile.peak_scope ? ` · ${profile.peak_scope}` : ""}<strong>{profile.peak_rank}</strong></span>}</div>{profile?.queue && <span className="rank-queue">{profile.queue}{profile.rank_points != null ? ` · ${profile.rank_points} puntos` : ""}</span>}{profile?.provider && <span className="rank-provider">Fuente: {profile.provider}{profile.status === "stale" ? " · Dato anterior" : ""}</span>}{profile?.synced_at && <time className="rank-updated" dateTime={profile.synced_at}>Consultado: {new Intl.DateTimeFormat("es-CO", { dateStyle: "short", timeStyle: "short", timeZone: "America/Bogota" }).format(new Date(profile.synced_at))}</time>}{profile?.account_name && <span className="rank-account">Cuenta declarada: {profile.account_name}</span>}</div>;
  })}</div>;
}
