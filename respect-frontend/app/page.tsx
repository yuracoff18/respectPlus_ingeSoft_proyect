"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { Icon } from "@/components/icon";
import { useSession } from "@/components/session-provider";
import { Reveal } from "@/components/ui";
import { TournamentCard } from "@/components/tournaments";
import { api } from "@/lib/api";
import type { Tournament } from "@/lib/types";

export default function Home() {
  const { requireAuth } = useSession();
  const router = useRouter();
  const [tournaments, setTournaments] = useState<Tournament[]>([]);
  const [game, setGame] = useState("Todos");
  const [error, setError] = useState(""); const [loading, setLoading] = useState(true);
  useEffect(() => { api<Tournament[]>("/tournaments").then(setTournaments).catch(e => setError(e.message)).finally(() => setLoading(false)); }, []);
  const join = () => requireAuth(current => router.push(current.role === "admin" ? "/admin" : "/perfil"));
  const visibleTournaments = tournaments.filter(t => game === "Todos" || t.game === game).slice(0, 3);
  return <main id="contenido">
    <section className="hero">
      <div className="hero-art" role="img" aria-label="Jugador futurista frente a una arena iluminada en rojo" />
      <div className="hero-grid" />
      <div className="container hero-inner">
        <div className="hero-copy">
          <span className="hero-badge"><i /> TU TALENTO MERECE SU PROPIO LUGAR <span>↗</span></span>
          <h1>Tu juego.<br />Tu gente.<br /><span>Tu próximo nivel.</span></h1>
          <p>Conecta con quienes comparten tu pasión.<br className="desktop-break" /> Haz equipo, muestra tu talento y compite por más.<br className="desktop-break" /> Tu historia gamer empieza aquí.</p>
          <div className="hero-actions"><button className="button primary" onClick={join}>Crea tu perfil gratis <Icon name="arrow" size={18} /></button><Link className="button outline" href="/torneos"><Icon name="trophy" size={18} /> Explorar torneos</Link></div>
          <div className="hero-community"><div className="avatar-stack"><span><Icon name="game" size={12} /></span><span><Icon name="users" size={12} /></span><span><Icon name="trophy" size={12} /></span></div><div><strong>Tu próximo squad está aquí.</strong><span>Todos los niveles. La misma pasión.</span></div></div>
        </div>
        <div className="hero-player-card"><div className="player-card-top"><span className="status-dot" /> TU SIGUIENTE NIVEL</div><div className="player-card-body"><span className="spotlight-avatar"><Icon name="game" size={24} /></span><div><strong>Tu identidad gamer</strong><span>Perfiles · Equipos · Torneos</span></div></div><div className="player-card-bottom"><span>JUEGA CONECTADO</span><Link href="/jugadores">Explorar <Icon name="arrow" size={12} /></Link></div></div>
        <div className="hero-coordinate">R+ NETWORK <span>EST. 2026</span></div>
      </div>
      <div className="container hero-bottom"><span>NO ES SOLO JUGAR. ES LLEGAR MÁS LEJOS.</span><a href="#explorar" className="scroll-cue">DESCUBRE TU SIGUIENTE NIVEL <span>↓</span></a></div>
    </section>
    <div className="game-strip"><div className="container game-strip-inner"><span className="game-strip-label">TU JUEGO.<br /><strong>TU COMUNIDAD.</strong></span><span className="game-wordmark valorant-word">VALORANT</span><span className="game-wordmark league-word">LEAGUE <small>OF</small> LEGENDS</span><span className="game-wordmark cs-word">COUNTER-STRIKE <b>2</b></span><span className="game-wordmark rocket-word">ROCKET<br />LEAGUE</span><span className="game-wordmark fortnite-word">FORTNITE</span></div></div>
    <section className="section container tournaments-section" id="explorar"><Reveal><div className="section-heading"><div><span className="eyebrow"><span className="tiny-line" /> COMPITE. CONECTA. REPITE.</span><h2>La próxima partida<br />puede <span className="muted-text">cambiarlo todo.</span></h2></div><Link href="/torneos" className="text-link section-more">Todos los torneos <Icon name="diagonal" size={17} /></Link></div><div className="tournament-toolbar"><div className="tabs" aria-label="Filtrar torneos por juego">{["Todos", "Valorant", "League of Legends", "Counter-Strike 2"].map(g => <button key={g} onClick={() => setGame(g)} className={game === g ? "selected" : ""} aria-pressed={game === g}>{g === "Todos" && <Icon name="game" size={16} />}{g}</button>)}</div><span className="small-note">COMPETENCIAS DE LA COMUNIDAD</span></div><div className="tournament-grid">{visibleTournaments.map(t => <TournamentCard key={t.id} tournament={t} />)}</div>{!visibleTournaments.length && <div className="landing-empty">{error ? <><p>{error}</p><Link className="text-link" href="/torneos">Ir a torneos <Icon name="arrow" size={16} /></Link></> : <p>{loading ? "Buscando tu siguiente competencia…" : "Aún no hay torneos para este juego. Tu comunidad puede crear la primera competencia."}</p>}</div>}</Reveal></section>
    <section className="community-section"><div className="container community-layout"><Reveal className="community-visual"><div className="network-orbit orbit-one" /><div className="network-orbit orbit-two" /><div className="network-core"><Icon name="game" size={45} /></div><div className="network-node node-one">N<span>VALORANT</span></div><div className="network-node node-two">L<span>LEAGUE OF LEGENDS</span></div><div className="network-node node-three">G<span>COUNTER-STRIKE 2</span></div><div className="connection-chip"><span className="status-dot" /><span>Una buena conexión lo cambia todo.</span><Icon name="spark" size={15} /></div><div className="visual-caption">DIFERENTES JUEGOS. EL MISMO ADN.</div></Reveal><Reveal className="community-copy"><span className="eyebrow">MÁS QUE UN GAMERTAG</span><h2>Tu talento se ve.<br />Tu equipo <span className="muted-text">te encuentra.</span></h2><p>Hay una historia detrás de cada jugador. Crea un perfil que hable de la tuya y conecta con personas que quieran llegar tan lejos como tú.</p><ul className="feature-list"><li><span><Icon name="users" size={18} /></span><div><strong>Encuentra a tu gente</strong><p>Jugadores con tu juego, tu mentalidad y tus ganas.</p></div></li><li><span><Icon name="spark" size={18} /></span><div><strong>Haz que tus logros cuenten</strong><p>Comparte tus mejores momentos con la comunidad.</p></div></li><li><span><Icon name="trophy" size={18} /></span><div><strong>De la conexión a la competencia</strong><p>Organiza un torneo y lleva a tu squad a la arena.</p></div></li></ul><Link className="text-link" href="/comunidad">Conoce la comunidad <Icon name="arrow" size={17} /></Link></Reveal></div></section>
    <section className="section container how-section" id="como-funciona"><Reveal><div className="section-heading"><div><span className="eyebrow">DEL LOBBY A TU PRÓXIMO NIVEL</span><h2>Tres pasos. <span className="muted-text">Infinitas partidas.</span></h2></div><span className="how-label">SIN COMPLICACIONES.<br />CON TODA LA ACTITUD.</span></div><div className="steps-grid">{[{n:"01",icon:"game",title:"Crea tu identidad",text:"Tu gamertag, tus juegos y tu historia. Un perfil que muestra quién eres dentro de la partida."},{n:"02",icon:"users",title:"Encuentra tu squad",text:"Conecta con jugadores, comparte lo que te mueve y construye tu red dentro del gaming."},{n:"03",icon:"trophy",title:"Entra a la arena",text:"Inscríbete en una competencia o crea tu propio torneo. El próximo GG puede ser tuyo."}].map(step => <div className="step" key={step.n}><div className="step-top"><span>{step.n}</span><Icon name={step.icon} size={28} /></div><h3>{step.title}</h3><p>{step.text}</p></div>)}</div></Reveal></section>
    <section className="container cta-wrap"><Reveal className="bottom-cta"><div className="cta-art">+</div><div><span className="eyebrow">EL SIGUIENTE MOVIMIENTO ES TUYO</span><h2>Juegas bien.<br /><span>Ahora, juega conectado.</span></h2><p>Tu talento merece más que una partida. Dale una comunidad.</p></div><button className="button primary" onClick={join}>Soy parte del juego <Icon name="diagonal" size={18} /></button></Reveal></section>
  </main>;
}
