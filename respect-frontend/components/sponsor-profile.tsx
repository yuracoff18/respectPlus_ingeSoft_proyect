"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { Post, Sponsor, Tournament } from "@/lib/types";
import { useSession } from "./session-provider";
import { Avatar, Empty, ErrorMessage, Loading } from "./ui";
import { SponsorForm } from "./entity-forms";
import { TeamCard } from "./entity-cards";
import { PostCard } from "./posts";
import { TournamentCard } from "./tournaments";
import { ProfileHeader } from "./profile-header";
import { Icon } from "./icon";
import { ReportButton } from "./report-button";

export function SponsorPublicProfile({ id }: { id: string }) {
  const { user, setUser, toast } = useSession();
  const [sponsor, setSponsor] = useState<Sponsor | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [loading, setLoading] = useState(true); const [error, setError] = useState(""); const [edit, setEdit] = useState(false);
  const load = useCallback(async () => {
    setLoading(true); setError("");
    try {
      const [profile, publications, events] = await Promise.all([api<Sponsor>(`/sponsors/${id}`), api<Post[]>("/posts"), api<Tournament[]>("/tournaments")]);
      setSponsor(profile);
      setPosts(publications.filter(post => post.publisher.type === "sponsor" && post.publisher.id === id));
      setTournaments(profile.owner.account_type === "sponsor" ? events.filter(event => event.owner_id === profile.owner_id) : []);
    } catch (error) { setError((error as Error).message); }
    finally { setLoading(false); }
  }, [id]);
  useEffect(() => { void load(); }, [load]);
  if (loading) return <Loading />;
  if (!sponsor) return <div className="container page-content"><ErrorMessage message={error || "No encontramos este sponsor."} retry={load} /><Link className="text-link" href="/sponsors">Volver a sponsors</Link></div>;
  const own = user?.id === sponsor.owner_id;

  return <div className="container page-content">
    <Link href="/sponsors" className="back-link">← Explorar sponsors</Link>
    <ProfileHeader {...sponsor} label="ORGANIZACIÓN / SPONSOR" actions={own && <button className="button outline" onClick={() => setEdit(true)}><Icon name="edit" size={16} /> Editar empresa</button>}>
      <span><Icon name="shield" size={16} />{sponsor.team_ids.length} equipos vinculados</span>
      {sponsor.website && <a href={sponsor.website} target="_blank" rel="noopener noreferrer" className="text-link">Visitar sitio web <Icon name="diagonal" size={15} /></a>}
    </ProfileHeader>
    <div className="profile-report-row"><ReportButton type="sponsor" id={sponsor.id} name={sponsor.name} ownerId={sponsor.owner_id} /></div>
    {own && <div className="company-actions"><Link className="button outline" href="/comunidad"><Icon name="message" size={16} /> Publicar como empresa</Link><Link className="button outline" href="/torneos"><Icon name="trophy" size={16} /> Organizar un torneo</Link></div>}
    {error && <ErrorMessage message={error} retry={load} />}
    <div className="profile-layout">
      <aside className="panel profile-about"><span className="eyebrow">NUESTRA PROPUESTA</span><h3>Acerca de la empresa</h3>
        <p className="preserve-lines">{sponsor.bio || (own ? "Completa la descripción para presentar tu empresa a la comunidad." : "Esta empresa todavía no ha añadido una descripción.")}</p>
        <h4>Juegos de interés</h4><div className="player-tags">{sponsor.games.length ? sponsor.games.map(game => <span className="tag" key={game}>{game}</span>) : <p className="muted small">Todavía no se han añadido juegos de interés.</p>}</div>
        <div className="sponsor-account-info">{sponsor.owner.account_type === "sponsor" ? <><span className="eyebrow">CUENTA DE EMPRESA</span><p>@{sponsor.owner.username}</p></> : <><h4>Administrado por</h4><Link href={sponsor.owner.profile_href} className="recommended-identity"><Avatar player={sponsor.owner} small /><span><strong>{sponsor.owner.name}</strong><small>Ver perfil</small></span></Link></>}</div>
      </aside>
      <section className="sponsor-sections">
        <section><div className="entity-section-heading"><h2>Equipos vinculados</h2></div><p className="section-note">Relaciones declaradas por la organización. Respect+ no verifica ni gestiona sus acuerdos económicos.</p>{sponsor.supported_teams.length ? <div className="compact-grid">{sponsor.supported_teams.map(team => <TeamCard key={team.id} team={team} />)}</div> : <Empty title="Aquí empiezan las próximas alianzas." text="Vincular equipos es opcional. La empresa puede participar en la comunidad desde su propia cuenta." />}</section>
        <section><div className="entity-section-heading"><h2>Publicaciones de la empresa</h2></div>{posts.length ? posts.map(post => <PostCard key={post.id} post={post} onUpdated={updated => setPosts(previous => previous.map(item => item.id === updated.id ? updated : item))} />) : <Empty title="La primera conversación está por empezar." text="Las publicaciones de esta organización aparecerán aquí." />}</section>
        <section><div className="entity-section-heading"><h2>Torneos organizados</h2></div>{tournaments.length ? <div className="tournament-grid profile-tournaments">{tournaments.map(tournament => <TournamentCard key={tournament.id} tournament={tournament} />)}</div> : <Empty title="Hay espacio para una nueva competencia." text="Los torneos organizados por esta cuenta aparecerán aquí." />}</section>
      </section>
    </div>
    {edit && <SponsorForm sponsor={sponsor} onClose={() => setEdit(false)} onSaved={value => {
      setSponsor(value); setEdit(false);
      if (user?.account_type === "sponsor" && user.sponsor_id === value.id) setUser({ ...user, name: value.name, headline: value.headline, bio: value.bio, country: value.country, games: value.games });
      toast("El perfil de la organización está al día."); void load();
    }} />}
  </div>;
}
