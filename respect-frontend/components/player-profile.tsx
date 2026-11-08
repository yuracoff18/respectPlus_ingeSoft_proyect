"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Player, Post, Sponsor, Team, Tournament } from "@/lib/types";
import { useSession } from "./session-provider";
import { ConnectButton } from "./players";
import { Empty, ErrorMessage, Loading } from "./ui";
import { ProfileHeader } from "./profile-header";
import { PostCard } from "./posts";
import { SponsorCard, TeamCard } from "./entity-cards";
import { TournamentCard } from "./tournaments";
import { Icon } from "./icon";
import { GameRanks } from "./game-ranks";
import { ReportButton } from "./report-button";

export function PlayerPublicProfile({ id }: { id: string }) {
  const { user } = useSession();
  const [player, setPlayer] = useState<Player | null>(null);
  const [posts, setPosts] = useState<Post[]>([]); const [teams, setTeams] = useState<Team[]>([]);
  const [sponsors, setSponsors] = useState<Sponsor[]>([]); const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [tab, setTab] = useState("posts"); const [error, setError] = useState(""); const [loading, setLoading] = useState(true);
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const profile = await api<Player>(`/users/${encodeURIComponent(id)}`);
      const [publications, allTeams, allSponsors, allTournaments] = await Promise.all([api<Post[]>(`/posts?author=${encodeURIComponent(profile.id)}`), api<Team[]>("/teams"), api<Sponsor[]>("/sponsors"), api<Tournament[]>("/tournaments")]);
      setPlayer(profile); setPosts(publications);
      setTeams(allTeams.filter(team => team.members.includes(profile.id)));
      setSponsors(allSponsors.filter(sponsor => sponsor.owner_id === profile.id));
      setTournaments(allTournaments.filter(tournament => tournament.owner_id === profile.id || tournament.participants.includes(profile.id) || Object.values(tournament.rosters).some(roster => roster.includes(profile.id))));
    } catch (error) { setError((error as Error).message); } finally { setLoading(false); }
  }, [id]);
  useEffect(() => { void load(); }, [load]);
  if (loading) return <Loading />;
  if (!player) return <div className="container page-content"><ErrorMessage message={error || "No encontramos este jugador."} retry={load} /><Link href="/jugadores" className="text-link">Volver a jugadores</Link></div>;
  return <div className="container page-content"><Link href="/jugadores" className="back-link">← Explorar jugadores</Link><ProfileHeader {...player} label={`JUGADOR / @${player.username}`} actions={user?.id === player.id ? <Link href="/perfil" className="button outline"><Icon name="edit" size={16} /> Editar mi perfil</Link> : <ConnectButton player={player} />}><span><Icon name="users" size={16} />{player.connections.length} conexiones</span><span className={`availability ${player.available ? "available" : ""}`}><i />{player.available ? "Buscando equipo" : "No busca equipo"}</span></ProfileHeader><div className="profile-report-row"><ReportButton type="player" id={player.id} name={player.name} /></div><div className="profile-layout"><aside className="panel profile-about"><span className="eyebrow">DETRÁS DEL GAMERTAG</span><h3>Mi historia</h3><p className="preserve-lines">{player.bio || "Esta historia todavía se está escribiendo."}</p><h4>Juegos preferidos</h4><GameRanks player={player} /></aside><section><div className="tabs profile-tabs">{[["posts", "Publicaciones", posts.length], ["teams", "Equipos", teams.length], ["tournaments", "Torneos", tournaments.length], ["sponsors", "Sponsors", sponsors.length]].map(([value, label, count]) => <button key={value} className={tab === value ? "selected" : ""} onClick={() => setTab(String(value))}>{label} <span>{count}</span></button>)}</div>{tab === "posts" && (posts.length ? posts.map(post => <PostCard key={post.id} post={post} onUpdated={updated => setPosts(previous => previous.map(value => value.id === updated.id ? updated : value))} />) : <Empty title="Su próxima historia está por compartirse." text="Aquí aparecerán las publicaciones de este jugador." />)}{tab === "teams" && (teams.length ? <div className="compact-grid">{teams.map(team => <TeamCard key={team.id} team={team} />)}</div> : <Empty title="El próximo squad está por llegar." text="Este jugador todavía no forma parte de un equipo." />)}{tab === "tournaments" && (tournaments.length ? <div className="tournament-grid profile-tournaments">{tournaments.map(tournament => <TournamentCard key={tournament.id} tournament={tournament} />)}</div> : <Empty title="La arena todavía lo espera." text="Aquí se muestran sus torneos e inscripciones." />)}{tab === "sponsors" && (sponsors.length ? <div className="compact-grid">{sponsors.map(sponsor => <SponsorCard key={sponsor.id} sponsor={sponsor} />)}</div> : <Empty title="Sin organizaciones vinculadas." text="Este jugador todavía no administra un sponsor." />)}</section></div></div>;
}
