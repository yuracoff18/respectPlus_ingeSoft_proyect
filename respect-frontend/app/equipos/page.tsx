"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { GAMES, type Team } from "@/lib/types";
import { Icon } from "@/components/icon";
import { Empty, ErrorMessage, Loading } from "@/components/ui";
import { TeamCard } from "@/components/entity-cards";
import { TeamForm } from "@/components/entity-forms";
import { useSession } from "@/components/session-provider";

export default function TeamsPage() {
  const [teams, setTeams] = useState<Team[]>([]);
  const [query, setQuery] = useState(""); const [game, setGame] = useState(""); const [rank, setRank] = useState("");
  const [recruiting, setRecruiting] = useState(false); const [mine, setMine] = useState(false); const [create, setCreate] = useState(false);
  const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const { user, requireAuth, toast } = useSession(); const router = useRouter();
  async function load() { setLoading(true); setError(""); try { setTeams(await api<Team[]>("/teams")); } catch (error) { setError((error as Error).message); } finally { setLoading(false); } }
  useEffect(() => { void load(); }, []);
  const rankValues = (team: Team) => team.roster.map(player => player.game_profiles[game || team.competition_game]?.current_rank).filter((value): value is string => !!value);
  const ranks = [...new Set(teams.filter(team => !game || team.games.includes(game)).flatMap(rankValues))].sort();
  const filtered = teams.filter(team => (!game || team.games.includes(game)) && (!rank || rankValues(team).includes(rank)) && (!recruiting || team.recruiting) && (!mine || team.members.includes(user?.id || "")) && `${team.name} ${team.tag} ${team.headline}`.toLocaleLowerCase().includes(query.toLocaleLowerCase()));
  return <main id="contenido" className="container page-content"><div className="page-heading"><div><span className="eyebrow">RESPECT+ / EQUIPOS</span><h1>Un squad. <span className="muted-text">Un mismo objetivo.</span></h1><p>Encuentra un equipo por sus juegos y rango, solicita unirte o construye el tuyo.</p></div><button className="button primary" onClick={() => requireAuth(account => account.account_type === "sponsor" ? toast("Los equipos se crean desde una cuenta de jugador. Puedes vincular equipos a tu empresa desde su perfil.") : setCreate(true))}><Icon name="plus" size={18} /> Crear equipo</button></div><div className="filter-bar"><label className="search-field"><Icon name="search" size={18} /><input aria-label="Buscar equipos" placeholder="Nombre, tag u objetivo del equipo" value={query} onChange={event => setQuery(event.target.value)} /></label><select aria-label="Filtrar equipos por juego" value={game} onChange={event => { setGame(event.target.value); setRank(""); }}><option value="">Todos los juegos</option>{GAMES.map(value => <option key={value}>{value}</option>)}</select><select aria-label="Filtrar equipos por rango" value={rank} onChange={event => setRank(event.target.value)}><option value="">Todos los rangos</option>{ranks.map(value => <option key={value}>{value}</option>)}</select><label className="checkbox-label filter-check"><input type="checkbox" checked={recruiting} onChange={event => setRecruiting(event.target.checked)} /> Buscando jugadores</label>{user && <label className="checkbox-label filter-check"><input type="checkbox" checked={mine} onChange={event => setMine(event.target.checked)} /> Mis equipos</label>}</div><div className="results-caption"><span>{filtered.length} equipos en tu radar</span><span>ESTRATEGIA, TALENTO Y RESPETO.</span></div>{loading ? <Loading /> : error ? <ErrorMessage message={error} retry={load} /> : filtered.length ? <div className="players-grid">{filtered.map(team => <TeamCard key={team.id} team={team} />)}</div> : <Empty title="Tu próximo equipo está por formarse." text="Cambia los filtros o crea tu propio squad." />}{create && <TeamForm onClose={() => setCreate(false)} onSaved={team => { setCreate(false); toast("Tu equipo ya tiene su propio espacio."); router.push(`/equipos/${team.id}`); }} />}</main>;
}
