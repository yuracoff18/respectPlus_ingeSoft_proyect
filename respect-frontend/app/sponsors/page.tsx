"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { api } from "@/lib/api";
import { GAMES, type Sponsor } from "@/lib/types";
import { Icon } from "@/components/icon";
import { Empty, ErrorMessage, Loading } from "@/components/ui";
import { SponsorCard } from "@/components/entity-cards";
import { useSession } from "@/components/session-provider";

export default function SponsorsPage() {
  const [sponsors, setSponsors] = useState<Sponsor[]>([]); const [query, setQuery] = useState(""); const [game, setGame] = useState("");
  const [loading, setLoading] = useState(true); const [error, setError] = useState("");
  const { user, openAuth } = useSession();
  async function load() { setLoading(true); setError(""); try { setSponsors(await api<Sponsor[]>("/sponsors")); } catch (error) { setError((error as Error).message); } finally { setLoading(false); } }
  useEffect(() => { void load(); }, []);
  const filtered = sponsors.filter(sponsor => (!game || sponsor.games.includes(game)) && `${sponsor.name} ${sponsor.headline}`.toLowerCase().includes(query.toLowerCase()));
  return <main id="contenido" className="container page-content"><div className="page-heading"><div><span className="eyebrow">RESPECT+ / SPONSORS</span><h1>El talento merece <span className="muted-text">buenas conexiones.</span></h1><p>Descubre organizaciones, sus juegos y los equipos con los que se vinculan. Cada empresa dispone de su propia cuenta.</p></div>{user?.account_type === "sponsor" ? <Link className="button primary" href={user.profile_href}><Icon name="shield" size={18} /> Mi empresa</Link> : <button className="button primary" onClick={() => openAuth("register", "sponsor")}><Icon name="plus" size={18} /> Registrar empresa</button>}</div><div className="filter-bar"><label className="search-field"><Icon name="search" size={18} /><input value={query} onChange={event => setQuery(event.target.value)} aria-label="Buscar sponsors" placeholder="Busca una organización" /></label><select value={game} onChange={event => setGame(event.target.value)} aria-label="Filtrar sponsors por juego"><option value="">Todos los juegos</option>{GAMES.map(value => <option key={value}>{value}</option>)}</select></div><div className="results-caption"><span>{filtered.length} organizaciones</span><span>UN ESPACIO PROPIO PARA CADA SPONSOR.</span></div>{loading ? <Loading /> : error ? <ErrorMessage message={error} retry={load} /> : filtered.length ? <div className="players-grid">{filtered.map(sponsor => <SponsorCard key={sponsor.id} sponsor={sponsor} />)}</div> : <Empty title="Hay espacio para nuevas conexiones." text="Cambia los filtros o registra la cuenta de tu organización." />}</main>;
}
