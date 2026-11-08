"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { GAMES, type Sponsor, type Team, type TeamSummary } from "@/lib/types";
import { Modal } from "./ui";
import { GamePreferences } from "./game-preferences";
import { Icon } from "./icon";

export function TeamForm({ team, onClose, onSaved }: { team?: Team; onClose: () => void; onSaved: (value: Team) => void }) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setBusy(true); setError("");
    try {
      const data = { ...Object.fromEntries(form), games: form.getAll("games"), recruiting: form.get("recruiting") === "on", max_members: Number(form.get("max_members")) };
      onSaved(await api<Team>(team ? `/teams/${team.id}` : "/teams", { method: team ? "PUT" : "POST", body: JSON.stringify(data) }));
    } catch (error) { setError((error as Error).message); } finally { setBusy(false); }
  }
  return <Modal title={team ? "Prepara a tu squad." : "Un buen equipo empieza contigo."} onClose={onClose} wide><p className="muted">Serás el capitán. Los jugadores podrán solicitar unirse y tú gestionarás la plantilla desde la página del equipo.</p><form className="form-stack" onSubmit={submit}><div className="form-grid"><label>Nombre del equipo<input name="name" defaultValue={team?.name} required minLength={3} maxLength={60} placeholder="Nombre de tu squad" /></label><label>Tag del equipo<input name="tag" defaultValue={team?.tag} required pattern="[A-Za-z0-9]{2,8}" minLength={2} maxLength={8} placeholder="Ej. RSP" /></label></div><label>Presentación<input name="headline" defaultValue={team?.headline} required minLength={3} maxLength={120} placeholder="Qué define a tu squad" /></label><label>Historia y objetivos<textarea name="bio" defaultValue={team?.bio} required minLength={10} maxLength={2000} rows={3} /></label><GamePreferences selected={team?.games || ["Valorant"]} /><div className="form-grid"><label>Juego de competencia<select name="competition_game" defaultValue={team?.competition_game || "Valorant"}>{GAMES.map(game => <option key={game}>{game}</option>)}</select></label><label>País<input name="country" defaultValue={team?.country || "Colombia"} required minLength={2} maxLength={60} /></label><label>Tamaño máximo de plantilla<input name="max_members" type="number" min={2} max={16} required defaultValue={team?.max_members || 5} /></label></div><label className="checkbox-label"><input name="recruiting" type="checkbox" defaultChecked={team?.recruiting ?? true} /> Recibir solicitudes de jugadores</label>{error && <p className="form-error" role="alert">{error}</p>}<button className="button primary" disabled={busy}>{busy ? "Guardando…" : team ? "Guardar equipo" : "Crear equipo"}<Icon name="users" size={18} /></button></form></Modal>;
}

export function SponsorForm({ sponsor, onClose, onSaved }: { sponsor?: Sponsor; onClose: () => void; onSaved: (value: Sponsor) => void }) {
  const [teams, setTeams] = useState<TeamSummary[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => { api<TeamSummary[]>("/teams").then(setTeams).catch(error => setError(error.message)); }, []);
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = new FormData(event.currentTarget); setBusy(true); setError("");
    try { onSaved(await api<Sponsor>(sponsor ? `/sponsors/${sponsor.id}` : "/sponsors", { method: sponsor ? "PUT" : "POST", body: JSON.stringify({ ...Object.fromEntries(form), games: form.getAll("games"), team_ids: form.getAll("team_ids") }) })); } catch (error) { setError((error as Error).message); } finally { setBusy(false); }
  }
  return <Modal title={sponsor ? "Actualiza tu propuesta." : "Dale un espacio a tu organización."} onClose={onClose} wide><form className="form-stack" onSubmit={submit}><label>Nombre del sponsor<input name="name" defaultValue={sponsor?.name} required minLength={3} maxLength={60} /></label><label>Presentación<input name="headline" defaultValue={sponsor?.headline} required minLength={3} maxLength={120} /></label><label>Acerca de la organización<textarea name="bio" defaultValue={sponsor?.bio} required minLength={10} maxLength={2000} rows={4} /></label><div className="form-grid"><label>País<input name="country" defaultValue={sponsor?.country || "Colombia"} required minLength={2} maxLength={60} /></label><label>Sitio web<input name="website" type="url" defaultValue={sponsor?.website} maxLength={300} placeholder="https://" /></label></div><GamePreferences selected={sponsor?.games || ["Valorant"]} /><fieldset className="game-preferences"><legend>Equipos vinculados</legend><p className="form-hint">Vínculos declarados por la organización. No representan pagos gestionados por Respect+.</p><div className="game-checks">{teams.map(team => <label key={team.id} className="checkbox-label"><input type="checkbox" name="team_ids" value={team.id} defaultChecked={sponsor?.team_ids.includes(team.id)} />{team.name}</label>)}</div></fieldset>{error && <p className="form-error" role="alert">{error}</p>}<button className="button primary" disabled={busy}>{busy ? "Guardando…" : sponsor ? "Guardar sponsor" : "Crear sponsor"}<Icon name="shield" size={18} /></button></form></Modal>;
}
