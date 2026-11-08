"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import { GAMES, type Player, type Team, type Tournament, type Match } from "@/lib/types";
import { useSession } from "./session-provider";
import { dateLabel, ErrorMessage, Loading, Modal } from "./ui";
import { Icon } from "./icon";

const statusLabel = { open: "Inscripciones abiertas", live: "En juego", finished: "Finalizado" };
export function gameClass(game: string) {
  return game === "League of Legends" ? "game-league" : game === "Counter-Strike 2" ? "game-cs" : game === "Rocket League" ? "game-rocket" : "game-valorant";
}

export function TournamentCard({ tournament: t }: { tournament: Tournament }) {
  const teamMode = t.mode === "team";
  return <Link href={`/torneos/${t.id}`} className="tournament-card" data-game={t.game}>
    <div className={`tournament-cover ${gameClass(t.game)}`}><div className="cover-noise" /><span className={`status-badge ${t.status}`}><i />{statusLabel[t.status]}</span><span className="cover-corner">R+ / ARENA</span><div className="cover-symbol"><Icon name={t.game === "League of Legends" ? "shield" : t.game === "Counter-Strike 2" ? "spark" : "trophy"} size={74} /></div><div className="cover-title"><span>{t.game.toUpperCase()}</span><strong>{t.title}</strong></div>{t.demo && <span className="demo-ribbon">DEMO</span>}</div>
    <div className="tournament-info">
      <div className="tournament-game-row"><span><Icon name="game" size={16} />{t.game}</span><span className="mode-chip">{teamMode ? `${t.team_size}v${t.team_size} · Equipos` : "Individual"}</span></div>
      <div className="tournament-meta"><span><Icon name="calendar" size={14} />{dateLabel(t.starts_at)}</span><span><Icon name="globe" size={14} />{t.region}</span></div><h3>{t.title}</h3>
      <div className="tournament-prize"><Icon name="trophy" size={16} /><strong>{t.prize}</strong><span>{t.demo ? "Premio ilustrativo" : "Premio anunciado"}</span></div>
      <div className="capacity-bar"><span style={{ width: `${Math.min(100, t.participants.length / t.capacity * 100)}%` }} /></div><div className="tournament-card-bottom"><span><Icon name="users" size={15} /><strong>{t.participants.length}</strong> / {t.capacity} {teamMode ? "equipos" : "jugadores"}</span><span>Ver torneo <Icon name="arrow" size={15} /></span></div>
    </div>
  </Link>;
}

export function CreateTournament({ onClose, onCreated }: { onClose: () => void; onCreated: (t: Tournament) => void }) {
  const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  const [mode, setMode] = useState("solo"); const [teamSize, setTeamSize] = useState(5);
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); const data = Object.fromEntries(new FormData(event.currentTarget)); setBusy(true); setError("");
    try {
      onCreated(await api<Tournament>("/tournaments", { method: "POST", body: JSON.stringify({ ...data, mode, team_size: mode === "team" ? teamSize : 1, capacity: Number(data.capacity), starts_at: new Date(String(data.starts_at)).toISOString() }) }));
    } catch (error) { setError((error as Error).message); } finally { setBusy(false); }
  }
  const tomorrow = new Date(Date.now() + 86400000);
  const localDate = new Date(tomorrow.getTime() - tomorrow.getTimezoneOffset() * 60000).toISOString().slice(0, 16);
  return <Modal title="Tu comunidad. Tus reglas." onClose={onClose} wide><p className="muted">Organiza una competencia individual o por equipos. Tú coordinas las partidas y registras los resultados.</p><form className="form-stack" onSubmit={submit}>
    <label>Nombre del torneo<input name="title" minLength={4} maxLength={80} required placeholder="Ej. Friday Night Clutch" /></label>
    <div className="form-grid"><label>Juego<select name="game">{GAMES.map(game => <option key={game}>{game}</option>)}</select></label><label>Modalidad<select value={mode} onChange={event => setMode(event.target.value)}><option value="solo">Individual</option><option value="team">Por equipos</option></select></label>
      <label>{mode === "team" ? "Cupos de equipos" : "Cupos"}<select name="capacity">{[4, 8, 16, 32, 64].map(number => <option value={number} key={number}>{number} {mode === "team" ? "equipos" : "jugadores"}</option>)}</select></label>
      {mode === "team" && <label>Jugadores por equipo<input type="number" min={2} max={10} value={teamSize} onChange={event => setTeamSize(Number(event.target.value))} required /></label>}
      <label>Fecha y hora (tu hora local)<input name="starts_at" type="datetime-local" required defaultValue={localDate} /></label><label>Región<input name="region" required minLength={2} maxLength={60} defaultValue="Latinoamérica" /></label>
    </div><label>Premio anunciado<input name="prize" maxLength={60} required defaultValue="Por la gloria" /></label><label>Descripción y reglas<textarea name="description" required minLength={20} maxLength={2000} rows={4} placeholder="Reglas, formato de las partidas y cómo coordinar los encuentros…" /></label>
    <p className="form-hint">{mode === "team" ? "Cada capitán selecciona su equipo y la plantilla que competirá. Un jugador no puede representar a dos equipos en el mismo torneo. " : ""}Respect+ gestiona inscripciones y llaves de eliminación directa. Las partidas y los premios los coordina el organizador.</p>
    {error && <p className="form-error" role="alert">{error}</p>}<button className="button primary" disabled={busy}>{busy ? "Creando torneo…" : "Crear torneo"}<Icon name="trophy" size={18} /></button>
  </form></Modal>;
}

export function TournamentDetail({ id }: { id: string }) {
  const { user, requireAuth, toast } = useSession();
  const [tournament, setTournament] = useState<Tournament | null>(null); const [players, setPlayers] = useState<Player[]>([]); const [teams, setTeams] = useState<Team[]>([]);
  const [teamId, setTeamId] = useState(""); const [rosterChoices, setRosterChoices] = useState<Record<string, string[]>>({});
  const [error, setError] = useState(""); const [busy, setBusy] = useState(false); const [scoreMatch, setScoreMatch] = useState<Match | null>(null); const [confirmStart, setConfirmStart] = useState(false);
  const load = useCallback(async () => {
    setError("");
    try { const [t, p, allTeams] = await Promise.all([api<Tournament>(`/tournaments/${id}`), api<Player[]>("/users"), api<Team[]>("/teams")]); setTournament(t); setPlayers(p); setTeams(allTeams); } catch (error) { setError((error as Error).message); }
  }, [id]);
  useEffect(() => { void load(); }, [load]);
  if (error && !tournament) return <div className="container page-content"><ErrorMessage message={error} retry={load} /></div>;
  if (!tournament) return <Loading />;
  const t = tournament;
  const teamMode = t.mode === "team";
  const unit = teamMode ? "equipos" : "jugadores";
  const isOwner = user?.id === t.owner_id;
  const ownTeams = teams.filter(team => team.owner_id === user?.id && team.games.includes(t.game));
  const selectedTeam = ownTeams.find(team => team.id === teamId) || ownTeams[0];
  const selectedRoster = selectedTeam ? rosterChoices[selectedTeam.id] || selectedTeam.members.slice(0, t.team_size) : [];
  const joined = teamMode ? !!selectedTeam && t.participants.includes(selectedTeam.id) : !!user && t.participants.includes(user.id);
  const participantName = (identifier: string | null) => identifier ? t.participant_details.find(participant => participant.id === identifier)?.name || "Por definir" : "Por definir";
  const playerName = (identifier: string) => players.find(player => player.id === identifier)?.name || "Jugador";

  async function action(path: string, method = "POST", body?: object) {
    setBusy(true); setError("");
    try {
      setTournament(await api<Tournament>(`/tournaments/${t.id}/${path}`, { method, ...(body ? { body: JSON.stringify(body) } : {}) }));
      setScoreMatch(null); setConfirmStart(false);
      toast(path === "join" ? method === "DELETE" ? "Inscripción retirada." : teamMode ? "¡Equipo inscrito! La plantilla está confirmada." : "¡Estás dentro! Prepárate para competir." : path === "start" ? "Las llaves ya están listas." : "Resultado guardado. La llave se actualizó.");
    } catch (error) { setError((error as Error).message); } finally { setBusy(false); }
  }
  function join() {
    if (teamMode && !user) { requireAuth(() => toast("Selecciona tu equipo y confirma la plantilla para inscribirlo.")); return; }
    requireAuth(() => void action("join", joined ? "DELETE" : "POST", teamMode ? { team_id: selectedTeam?.id, roster: selectedRoster } : undefined));
  }
  const disabledJoin = busy || (!joined && (t.participants.length >= t.capacity || new Date(t.starts_at).getTime() <= Date.now() || (teamMode && !!user && (!selectedTeam || selectedRoster.length !== t.team_size))));

  return <div className="container page-content tournament-detail"><Link className="back-link" href="/torneos">← Volver a torneos</Link>
    <div className={`detail-banner ${gameClass(t.game)}`}><div className="cover-symbol"><Icon name="trophy" size={145} /></div><span className={`status-badge ${t.status}`}><i />{statusLabel[t.status]}</span><span className="eyebrow">{t.game} / ELIMINACIÓN DIRECTA / {teamMode ? `EQUIPOS ${t.team_size}v${t.team_size}` : "INDIVIDUAL"}</span><h1>{t.title}</h1><p>Organizado por {t.owner_href ? <Link href={t.owner_href}>{t.owner_name}</Link> : t.owner_name}{t.demo ? " · Torneo de demostración" : ""}</p></div>
    <div className="detail-grid"><section className="detail-main panel"><span className="eyebrow">EL PLAN DE JUEGO</span><h2>Todo listo para competir.</h2><div className="detail-game"><Icon name="game" size={22} /><strong>{t.game}</strong><span className="tag">{teamMode ? `Por equipos · ${t.team_size}v${t.team_size}` : "Individual"}</span></div><p className="preserve-lines">{t.description}</p><div className="detail-facts"><div><Icon name="calendar" /><span>Comienza<strong>{new Intl.DateTimeFormat("es-CO", { dateStyle: "medium", timeStyle: "short", timeZone: "America/Bogota" }).format(new Date(t.starts_at))} (Bogotá)</strong></span></div><div><Icon name="globe" /><span>Región<strong>{t.region}</strong></span></div><div><Icon name="trophy" /><span>{t.demo ? "Premio ilustrativo" : "Premio anunciado"}<strong>{t.prize}</strong></span></div></div>
      <h3>{teamMode ? "Equipos inscritos" : "Participantes"} · {t.participants.length}/{t.capacity}</h3><div className={teamMode ? "registered-teams" : "participant-list"}>{t.participant_details.length ? t.participant_details.map(participant => <div className={teamMode ? "registered-team" : "participant"} key={participant.id}>{participant.href ? <Link href={participant.href} className="tag">{teamMode && <Icon name="users" size={14} />}{participant.name}<Icon name="diagonal" size={12} /></Link> : <span className="tag">{participant.name}</span>}{teamMode && <div className="registered-roster">{(t.rosters[participant.id] || []).map(member => <Link key={member} href={`/jugadores/${member}`}>{playerName(member)}</Link>)}</div>}</div>) : <p className="muted">El lobby está esperando a su primer {teamMode ? "equipo" : "jugador"}.</p>}</div>
    </section><aside className="panel join-panel"><Icon name={teamMode ? "users" : "game"} size={32} /><h3>{joined ? teamMode ? "Tu squad ya está dentro." : "Ya eres parte de la partida." : "Tu próximo GG empieza aquí."}</h3><p>{t.capacity - t.participants.length} cupos de {unit} disponibles.</p><div className="capacity-bar"><span style={{ width: `${t.participants.length / t.capacity * 100}%` }} /></div>
      {user?.account_type === "sponsor" ? <p className="form-hint">Tu cuenta de empresa puede organizar torneos. Los jugadores y equipos participan desde sus propias cuentas.</p> : t.status === "open" ? <>
        {teamMode && user && <div className="team-entry-form">{ownTeams.length ? <><label>Equipo a inscribir<select aria-label="Equipo a inscribir" value={selectedTeam?.id || ""} onChange={event => setTeamId(event.target.value)}>{ownTeams.map(team => <option value={team.id} key={team.id}>{team.name} ({team.members.length} jugadores)</option>)}</select></label>{selectedTeam && !joined && <fieldset className="entry-roster"><legend>Plantilla: {selectedRoster.length}/{t.team_size} jugadores</legend>{selectedTeam.roster.map(member => <label className="checkbox-label" key={member.id}><input type="checkbox" value={member.id} checked={selectedRoster.includes(member.id)} onChange={event => setRosterChoices(previous => ({ ...previous, [selectedTeam.id]: event.target.checked ? [...selectedRoster, member.id] : selectedRoster.filter(identifier => identifier !== member.id) }))} />{member.name}</label>)}</fieldset>}</> : <p className="form-hint">Necesitas ser capitán de un equipo con {t.game} entre sus preferencias. <Link className="text-link" href="/equipos">Crear o ver equipos</Link></p>}</div>}
        <button className={`button ${joined ? "outline" : "primary"} full`} disabled={disabledJoin} onClick={join}>{busy ? "Guardando…" : teamMode ? joined ? "Retirar equipo" : "Inscribir equipo" : joined ? "Retirarme del torneo" : "Inscribirme gratis"}<Icon name={joined ? "close" : "arrow"} size={18} /></button>
      </> : <span className="tag">Inscripciones cerradas</span>}
      {isOwner && t.status === "open" && <button className="button outline full" disabled={busy || t.participants.length < 2} onClick={() => setConfirmStart(true)}>Iniciar torneo <Icon name="play" size={15} /></button>}
      <p className="form-hint">{isOwner && t.status === "open" ? `Se necesitan al menos 2 ${unit}. Al iniciar se cierran las inscripciones y se sortean las llaves.` : teamMode ? "El capitán confirma la plantilla. No se permite representar a dos equipos en el mismo torneo." : "Juega con respeto. Los encuentros y premios se coordinan con el organizador."}</p>{error && <ErrorMessage message={error} />}
    </aside></div>
    <section className="bracket-section"><div className="section-heading"><div><span className="eyebrow">EL CAMINO A LA VICTORIA</span><h2>Llaves del torneo</h2></div><button className="text-link" onClick={load}>Actualizar <Icon name="arrow" size={16} /></button></div>
      {t.rounds.length ? <div className="bracket">{t.rounds.map((round, roundIndex) => <div className="bracket-round" key={roundIndex}><span className="eyebrow">{roundIndex === t.rounds.length - 1 ? "FINAL" : `RONDA ${roundIndex + 1}`}</span>{round.map(match => <div className="match" key={match.id}>{(["a", "b"] as const).map(side => <div key={side} className={match.winner && match.winner === match[side] ? "winner" : ""}><span>{participantName(match[side])}</span><strong>{match[`score_${side}`] ?? "—"}</strong></div>)}{isOwner && match.a && match.b && !match.winner && t.status === "live" && <button className="text-link" disabled={busy} onClick={() => setScoreMatch(match)}>Registrar resultado</button>}{match.winner && <small>{match.a && match.b ? "Resultado final" : "Avanza por pase libre"}</small>}</div>)}</div>)}</div> : <div className="empty-state"><Icon name="trophy" size={32} /><h3>El camino se dibuja al empezar.</h3><p>Las llaves se generan cuando el organizador inicia el torneo.</p></div>}
      {t.status === "finished" && <div className="champion"><Icon name="trophy" size={32} /><div><span className="eyebrow">{teamMode ? "EQUIPO CAMPEÓN" : "CAMPEÓN DEL TORNEO"}</span><h2>{participantName(t.rounds.at(-1)?.[0].winner || null)}</h2></div></div>}
    </section>
    {confirmStart && <Modal title="¿Todo listo para empezar?" onClose={() => setConfirmStart(false)}><p className="muted">Se cerrarán las inscripciones y se sortearán las llaves para {t.participants.length} {unit}. El torneo no podrá volver al estado de inscripciones.</p><button className="button primary full" disabled={busy} onClick={() => void action("start")}>{busy ? "Iniciando…" : "Confirmar e iniciar torneo"}<Icon name="play" size={16} /></button>{error && <p className="form-error" role="alert">{error}</p>}</Modal>}
    {scoreMatch && <Modal title="Cada partida cuenta." onClose={() => setScoreMatch(null)}><form className="form-stack" onSubmit={event => { event.preventDefault(); const data = new FormData(event.currentTarget); void action(`matches/${scoreMatch.id}`, "PUT", { score_a: Number(data.get("score_a")), score_b: Number(data.get("score_b")) }); }}><p className="muted">Registra el marcador definitivo. {teamMode ? "El equipo ganador" : "El ganador"} avanzará automáticamente y el resultado no se podrá editar.</p><div className="form-grid"><label>{participantName(scoreMatch.a)}<input type="number" min="0" max="999" name="score_a" required defaultValue="0" /></label><label>{participantName(scoreMatch.b)}<input type="number" min="0" max="999" name="score_b" required defaultValue="0" /></label></div>{error && <p className="form-error" role="alert">{error}</p>}<button className="button primary" disabled={busy}>{busy ? "Guardando…" : "Confirmar resultado"}</button></form></Modal>}
  </div>;
}
