"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Player, Sponsor, Team, Tournament } from "@/lib/types";
import { useSession } from "./session-provider";
import { Avatar, Empty, ErrorMessage, Loading } from "./ui";
import { TeamForm } from "./entity-forms";
import { SponsorCard } from "./entity-cards";
import { ProfileHeader } from "./profile-header";
import { TournamentCard } from "./tournaments";
import { Icon } from "./icon";
import { rankFor } from "./game-ranks";
import { ReportButton } from "./report-button";

export function TeamPublicProfile({ id }: { id: string }) {
  const { user, requireAuth, toast } = useSession();
  const [team, setTeam] = useState<Team | null>(null); const [requests, setRequests] = useState<Player[]>([]);
  const [membership, setMembership] = useState({ member: false, requested: false });
  const [tournaments, setTournaments] = useState<Tournament[]>([]); const [sponsors, setSponsors] = useState<Sponsor[]>([]);
  const [edit, setEdit] = useState(false); const [gameView, setGameView] = useState(""); const [busy, setBusy] = useState(false); const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const load = useCallback(async () => {
    setError("");
    try {
      const [profile, allTournaments, allSponsors] = await Promise.all([api<Team>(`/teams/${id}`), api<Tournament[]>("/tournaments"), api<Sponsor[]>("/sponsors")]);
      setTeam(profile); setTournaments(allTournaments.filter(tournament => tournament.mode === "team" && tournament.participants.includes(id))); setSponsors(allSponsors.filter(sponsor => sponsor.team_ids.includes(id)));
      setRequests(user?.id === profile.owner_id ? await api<Player[]>(`/teams/${id}/requests`) : []);
      setMembership(user ? await api(`/teams/${id}/membership`) : { member: false, requested: false });
    } catch (error) { setError((error as Error).message); } finally { setLoading(false); }
  }, [id, user?.id]);
  useEffect(() => { void load(); }, [load]);
  async function mutate(path: string, method: string, body?: object) {
    setBusy(true); setError("");
    try { await api(`/teams/${id}/${path}`, { method, ...(body ? { body: JSON.stringify(body) } : {}) }); await load(); toast(path === "requests" ? "Solicitud enviada al capitán." : "La plantilla del equipo se actualizó."); } catch (error) { setError((error as Error).message); } finally { setBusy(false); }
  }
  if (loading) return <Loading />;
  if (!team) return <div className="container page-content"><ErrorMessage message={error || "No encontramos este equipo."} retry={load} /><Link href="/equipos" className="text-link">Volver a equipos</Link></div>;
  const competitionGame = team.games.includes(gameView) ? gameView : team.competition_game || team.games[0];
  const isOwner = user?.id === team.owner_id;
  const frozen = tournaments.some(tournament => tournament.status !== "finished");
  return <div className="container page-content"><Link href="/equipos" className="back-link">← Explorar equipos</Link><ProfileHeader {...team} label={`EQUIPO / ${team.tag}`} actions={isOwner ? <button className="button outline" onClick={() => setEdit(true)}><Icon name="edit" size={16} /> Editar equipo</button> : membership.member ? <button className="button outline" disabled={busy || frozen} onClick={() => void mutate(`members/${user?.id}`, "DELETE")}>Salir del equipo</button> : <button className="button primary" disabled={user?.account_type === "sponsor" || busy || membership.requested || !team.recruiting || team.members.length >= team.max_members} onClick={() => requireAuth(() => void mutate("requests", "POST"))}><Icon name="plus" size={16} />{user?.account_type === "sponsor" ? "Solo cuentas de jugadores" : membership.requested ? "Solicitud enviada" : "Solicitar unirme"}</button>}><span><Icon name="users" size={16} />{team.members.length}/{team.max_members} jugadores</span><span className={`availability ${team.recruiting ? "available" : ""}`}><i />{team.recruiting ? "Buscando jugadores" : "Plantilla cerrada"}</span></ProfileHeader><div className="profile-report-row"><ReportButton type="team" id={team.id} name={team.name} ownerId={team.owner_id} /></div>{error && <ErrorMessage message={error} />}<div className="profile-layout"><aside><div className="panel profile-about"><span className="eyebrow">IDENTIDAD DEL SQUAD</span><h3>Quiénes somos</h3><p className="preserve-lines">{team.bio}</p><h4>Preferencias de juego</h4><div className="player-tags">{team.games.map(game => <span className="tag" key={game}>{game}</span>)}</div><h4>Capitán</h4><Link href={`/jugadores/${team.captain.username}`} className="recommended-identity"><Avatar player={team.captain} small /><span><strong>{team.captain.name}</strong><small>@{team.captain.username}</small></span></Link></div>{frozen && <div className="panel roster-lock"><Icon name="shield" size={22} /><h3>Plantilla de competencia</h3><p>El equipo está inscrito en un torneo abierto o en juego. Su plantilla queda bloqueada hasta retirarse o terminar la competencia.</p></div>}</aside><section className="entity-sections"><div className="panel"><div className="entity-section-heading"><h2>La plantilla</h2><select className="roster-game-select" aria-label="Juego de competencia de la plantilla" value={competitionGame} onChange={event => setGameView(event.target.value)}>{team.games.map(game => <option key={game}>{game}</option>)}</select><span className="tag">{team.members.length} jugadores</span></div><div className="roster-list">{team.roster.map(member => <div className="roster-row" key={member.id}><Link href={`/jugadores/${member.username}`} className="recommended-identity"><Avatar player={member} small /><span><strong>{member.name}{member.id === team.owner_id ? " · Capitán" : ""}</strong><small>{competitionGame} · {rankFor(member, competitionGame)}</small></span></Link>{isOwner && member.id !== team.owner_id && <button className="icon-button" aria-label={`Retirar a ${member.name}`} disabled={busy || frozen} onClick={() => void mutate(`members/${member.id}`, "DELETE")}><Icon name="close" size={17} /></button>}</div>)}</div></div>{isOwner && <div className="panel"><span className="eyebrow">GESTIÓN DEL CAPITÁN</span><h2 className="entity-subheading">Solicitudes de ingreso ({requests.length})</h2>{requests.length ? requests.map(player => <div className="roster-row request-row" key={player.id}><Link className="recommended-identity" href={`/jugadores/${player.username}`}><Avatar player={player} small /><span><strong>{player.name}</strong><small>{competitionGame} · {rankFor(player, competitionGame)}</small></span></Link><div><button className="button soft" disabled={busy || frozen} aria-label={`Aceptar a ${player.name}`} onClick={() => void mutate(`requests/${player.id}`, "PUT", { decision: "accept" })}>Aceptar</button><button className="icon-button" disabled={busy} aria-label={`Rechazar a ${player.name}`} onClick={() => void mutate(`requests/${player.id}`, "PUT", { decision: "reject" })}><Icon name="close" size={17} /></button></div></div>) : <p className="muted">Las solicitudes de nuevos jugadores aparecerán aquí.</p>}</div>}<div><div className="entity-section-heading"><h2>Torneos del equipo</h2><Link href="/torneos" className="text-link">Ir a la arena <Icon name="arrow" size={16} /></Link></div>{tournaments.length ? <div className="tournament-grid profile-tournaments">{tournaments.map(tournament => <TournamentCard key={tournament.id} tournament={tournament} />)}</div> : <Empty title="El squad está listo para la arena." text="El capitán puede inscribir al equipo en un torneo compatible con sus juegos." />}</div>{sponsors.length > 0 && <div><h2 className="entity-subheading">Sponsors vinculados</h2><div className="compact-grid">{sponsors.map(sponsor => <SponsorCard key={sponsor.id} sponsor={sponsor} />)}</div></div>}</section></div>{edit && <TeamForm team={team} onClose={() => setEdit(false)} onSaved={updated => { setTeam(updated); setEdit(false); toast("El perfil del equipo está al día."); }} />}</div>;
}
