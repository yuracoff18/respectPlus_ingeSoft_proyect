import { Avatar } from "./ui";
import { Icon } from "./icon";

export function ProfileHeader({ name, color, label, headline, country, actions, children }: { name: string; color: string; label: string; headline: string; country: string; actions?: React.ReactNode; children?: React.ReactNode }) {
  return <div className="profile-header public-profile-header"><div className="profile-banner"><span>YOUR GAME. YOUR STORY.</span><span className="profile-banner-mark">R+</span></div><div className="profile-header-content"><Avatar player={{ name, color }} /><div className="public-profile-actions">{actions}</div><span className="eyebrow">{label}</span><h1>{name}</h1><p>{headline}</p><div className="profile-meta"><span><Icon name="globe" size={16} />{country}</span>{children}</div></div></div>;
}
