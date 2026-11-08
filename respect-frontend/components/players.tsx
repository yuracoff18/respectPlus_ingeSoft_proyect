"use client";

import { useState } from "react";
import Link from "next/link";
import { GamePreferences } from "./game-preferences";
import { GameRanks } from "./game-ranks";
import { api } from "@/lib/api";
import { GAMES, type Player, type User } from "@/lib/types";
import { Icon } from "./icon";
import { useSession } from "./session-provider";
import { Avatar, Modal } from "./ui";

export function ConnectButton({ player }: { player: Player }) {
  const { user, setUser, requireAuth, toast } = useSession();
  const [busy, setBusy] = useState(false);
  const connected = user?.connections.includes(player.id);
  if (user?.id === player.id) return <span className="tag">Este es tu perfil</span>;
  const connect = async () => { setBusy(true); try { const updated = await api<User>(`/users/${player.id}/connect`, { method: "POST" }); setUser(updated); toast(connected ? "Conexión eliminada." : `Ahora tú y ${player.name} están conectados.`); } catch (e) { toast((e as Error).message); } finally { setBusy(false); } };
  return <button className={`button ${connected ? "outline" : "soft"}`} disabled={busy} onClick={() => requireAuth(() => void connect())}><Icon name={connected ? "check" : "plus"} size={16} />{busy ? "Conectando…" : connected ? "Conectados" : "Conectar"}</button>;
}
export function PlayerCard({ player }: { player: Player }) {
  return <article className="player-card"><div className="player-cover" style={{ "--avatar-color": player.color } as React.CSSProperties}><span>R+ / PLAYER</span></div><div className="player-info"><Avatar player={player} /><span className={`availability ${player.available ? "available" : ""}`}><i />{player.available ? "Buscando equipo" : "En su propia partida"}</span><Link className="player-name-button" href={`/jugadores/${player.username}`}><h3>{player.name}</h3><Icon name="diagonal" size={16} /></Link><span className="player-handle">@{player.username}</span><p>{player.headline}</p><GameRanks player={player} compact /><div className="player-location"><Icon name="globe" size={14} /> {player.country}</div><ConnectButton player={player} /></div></article>;
}
export function EditProfile({ user, onClose, onSaved }: { user: User; onClose: () => void; onSaved: (user: User) => void }) {
  const [busy, setBusy] = useState(false); const [error, setError] = useState("");
  async function submit(e: React.FormEvent<HTMLFormElement>) { e.preventDefault(); const form = new FormData(e.currentTarget); setBusy(true); setError(""); try { onSaved(await api<User>("/users/me", { method: "PUT", body: JSON.stringify({ ...Object.fromEntries(form), games: form.getAll("games"), available: form.get("available") === "on" }) })); } catch (e) { setError((e as Error).message); } finally { setBusy(false); } }
  return <Modal title="Haz que tu perfil hable de ti." onClose={onClose} wide><form onSubmit={submit} className="form-stack"><div className="form-grid"><label>Nombre de jugador<input name="name" required minLength={2} maxLength={40} defaultValue={user.name} /></label><label>País<input name="country" minLength={2} required maxLength={60} defaultValue={user.country} /></label></div><label>Tu presentación<input name="headline" maxLength={120} defaultValue={user.headline} placeholder="Tu rol, tu estilo o lo que te mueve" /></label><label>Tu historia<textarea name="bio" maxLength={1000} rows={4} defaultValue={user.bio} placeholder="Cuéntanos qué juegas, qué has logrado y hacia dónde vas…" /></label><GamePreferences selected={user.games} /><div className="form-grid"><label>Juego principal<select name="game" defaultValue={user.game}>{GAMES.map(g => <option key={g}>{g}</option>)}</select></label><p className="form-hint">Los rangos se consultan desde Cuentas de juego; no se editan manualmente.</p></div><label className="checkbox-label"><input type="checkbox" name="available" defaultChecked={user.available} /> Estoy buscando equipo o nuevos compañeros</label>{error && <p className="form-error" role="alert">{error}</p>}<button className="button primary" disabled={busy}>{busy ? "Guardando…" : "Guardar mi perfil"}<Icon name="check" size={18} /></button></form></Modal>;
}
