"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import { GAMES, type Tournament } from "@/lib/types";
import { useSession } from "@/components/session-provider";
import { Icon } from "@/components/icon";
import { CreateTournament, TournamentCard } from "@/components/tournaments";
import { Empty, ErrorMessage, Loading } from "@/components/ui";

export default function TournamentsPage() {
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [error, setError] = useState(""); const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState(""); const [game, setGame] = useState(""); const [mode, setMode] = useState(""); const [status, setStatus] = useState(""); const [create, setCreate] = useState(false);
  const { requireAuth, toast, user } = useSession(); const router = useRouter();
  async function load() { setLoading(true); setError(""); try { setTournaments(await api<Tournament[]>("/tournaments")); } catch (e) { setError((e as Error).message); } finally { setLoading(false); } }
  useEffect(() => { void load(); }, []);
  const filtered = tournaments.filter(t => (!game || t.game === game) && (!mode || t.mode === mode) && (!status || (status === "mine" ? t.owner_id === user?.id : t.status === status)) && t.title.toLowerCase().includes(query.toLowerCase()));
  return <main id="contenido" className="container page-content"><div className="page-heading"><div><span className="eyebrow">RESPECT+ / ARENA</span><h1>El próximo GG <span className="muted-text">te espera.</span></h1><p>Encuentra tu competencia. O crea la que tu comunidad necesita.</p></div><button className="button primary" onClick={() => requireAuth(() => setCreate(true))}><Icon name="plus" size={18} /> Crear torneo</button></div><div className="filter-bar"><label className="search-field"><Icon name="search" size={18} /><input aria-label="Buscar torneo" placeholder="Busca tu próxima competencia" value={query} onChange={e => setQuery(e.target.value)} /></label><select aria-label="Filtrar por juego" value={game} onChange={e => setGame(e.target.value)}><option value="">Todos los juegos</option>{GAMES.map(g => <option key={g}>{g}</option>)}</select><select aria-label="Filtrar por modalidad" value={mode} onChange={e => setMode(e.target.value)}><option value="">Todas las modalidades</option><option value="solo">Individual</option><option value="team">Por equipos</option></select><select aria-label="Filtrar por estado" value={status} onChange={e => setStatus(e.target.value)}><option value="">Todos los estados</option><option value="open">Inscripciones abiertas</option><option value="live">En juego</option><option value="finished">Finalizados</option>{user && <option value="mine">Mis torneos</option>}</select></div><div className="results-caption"><span>{filtered.length} competencias para darlo todo</span><span>JUEGA CON TALENTO. COMPITE CON RESPETO.</span></div>{loading ? <Loading /> : error ? <ErrorMessage message={error} retry={load} /> : filtered.length ? <div className="tournament-grid">{filtered.map(t => <TournamentCard key={t.id} tournament={t} />)}</div> : <Empty title="Todavía no hay una partida aquí." text="Prueba con otro filtro o crea el primer torneo de tu comunidad." />}{create && <CreateTournament onClose={() => setCreate(false)} onCreated={t => { setCreate(false); toast("Tu torneo está listo. ¡Invita a tu comunidad!"); router.push(`/torneos/${t.id}`); }} />}</main>;
}
