import Link from "next/link";
import type { Sponsor, TeamSummary } from "@/lib/types";
import { Avatar } from "./ui";
import { Icon } from "./icon";

export function TeamCard({ team }: { team: TeamSummary }) {
  return <article className="panel entity-card"><div className="entity-card-top"><Avatar player={team} /><span className="tag">EQUIPO / {team.tag}</span></div><Link href={`/equipos/${team.id}`} className="entity-title"><h3>{team.name}</h3><Icon name="diagonal" size={18} /></Link><p>{team.headline}</p><div className="player-tags">{team.games.map(game => <span className="tag" key={game}>{game}</span>)}<span className="tag competition-tag"><Icon name="trophy" size={12} />Compite en {team.competition_game || team.games[0]}</span></div><div className="entity-card-meta"><span><Icon name="users" size={15} />{team.members.length}/{team.max_members} jugadores</span><span><Icon name="globe" size={15} />{team.country}</span></div><div className="entity-card-bottom"><span className={`availability ${team.recruiting ? "available" : ""}`}><i />{team.recruiting ? "Buscando jugadores" : "Plantilla cerrada"}</span><Link href={`/equipos/${team.id}`} className="text-link">Ver equipo <Icon name="arrow" size={15} /></Link></div></article>;
}

export function SponsorCard({ sponsor }: { sponsor: Sponsor }) {
  return <article className="panel entity-card"><div className="entity-card-top"><Avatar player={sponsor} /><span className="tag"><Icon name="shield" size={13} /> SPONSOR</span></div><Link href={`/sponsors/${sponsor.id}`} className="entity-title"><h3>{sponsor.name}</h3><Icon name="diagonal" size={18} /></Link><p>{sponsor.headline}</p><div className="player-tags">{sponsor.games.map(game => <span className="tag" key={game}>{game}</span>)}</div><div className="entity-card-meta"><span><Icon name="globe" size={15} />{sponsor.country}</span><span>{sponsor.team_ids.length} equipos vinculados</span></div><Link className="text-link" href={`/sponsors/${sponsor.id}`}>Ver sponsor <Icon name="arrow" size={15} /></Link></article>;
}
