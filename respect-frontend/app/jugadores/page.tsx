"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { GAMES, type Player } from "@/lib/types";
import { Icon } from "@/components/icon";
import { Empty, ErrorMessage, Loading } from "@/components/ui";
import { PlayerCard } from "@/components/players";
import { useSession } from "@/components/session-provider";

export default function PlayersPage() {
  const [players, setPlayers] = useState<Player[]>([]);
  const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const [query, setQuery] = useState(""); const [game, setGame] = useState(""); const [rank, setRank] = useState(""); const [available, setAvailable] = useState(false); const [connections, setConnections] = useState(false);
  const { user } = useSession();
  async function load() { setLoading(true); setError(""); try { setPlayers(await api<Player[]>("/users")); } catch (e) { setError((e as Error).message); } finally { setLoading(false); } }
  useEffect(() => { void load(); }, []);
  const rankValues = (p: Player) => Object.entries(p.game_profiles).filter(([name]) => !game || name === game).map(([, value]) => value.current_rank).filter((value): value is string => !!value);
  const ranks = [...new Set(players.flatMap(rankValues))].sort();
  const filtered = players.filter(p => (!game || p.games.includes(game)) && (!rank || rankValues(p).includes(rank)) && (!available || p.available) && (!connections || user?.connections.includes(p.id)) && `${p.name} ${p.username} ${p.headline}`.toLowerCase().includes(query.toLowerCase()));
  return <main id="contenido" className="container page-content"><div className="page-heading"><div><span className="eyebrow">RESPECT+ / TU RED</span><h1>El talento conecta.<br /><span className="muted-text">El squad se construye.</span></h1><p>Busca por preferencias de juego y rango. Cada jugador tiene su propia historia y su propio perfil.</p></div><div className="page-emblem"><Icon name="users" size={56} /></div></div><div className="filter-bar"><label className="search-field"><Icon name="search" size={18} /><input aria-label="Buscar jugadores" value={query} onChange={e => setQuery(e.target.value)} placeholder="Busca por nombre, gamertag o rol" /></label><select aria-label="Filtrar por juego" value={game} onChange={e => { setGame(e.target.value); setRank(""); }}><option value="">Todos los juegos</option>{GAMES.map(g => <option key={g}>{g}</option>)}</select><select aria-label="Filtrar jugadores por rango" value={rank} onChange={e => setRank(e.target.value)}><option value="">Todos los rangos</option>{ranks.map(value => <option key={value}>{value}</option>)}</select><label className="checkbox-label filter-check"><input type="checkbox" checked={available} onChange={e => setAvailable(e.target.checked)} /> Buscando equipo</label>{user && <label className="checkbox-label filter-check"><input type="checkbox" checked={connections} onChange={e => setConnections(e.target.checked)} /> Mis conexiones</label>}</div><div className="results-caption"><span>{filtered.length} jugadores en tu radar</span><span>RANGOS CONSULTADOS POR JUEGO.</span></div>{loading ? <Loading /> : error ? <ErrorMessage message={error} retry={load} /> : filtered.length ? <div className="players-grid">{filtered.map(p => <PlayerCard key={p.id} player={p} />)}</div> : <Empty title="Tu squad está en otra búsqueda." text="Cambia los filtros y descubre más jugadores." />}</main>;
}
