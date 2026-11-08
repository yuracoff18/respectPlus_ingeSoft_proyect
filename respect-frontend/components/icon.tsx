import type { CSSProperties } from "react";

const paths: Record<string, React.ReactNode> = {
  flag: <><path d="M5 21V3m0 1c5-4 9 4 15 0v10c-6 4-10-4-15 0" /></>,
  arrow: <><path d="M4 12h15M13 5l7 7-7 7" /></>,
  diagonal: <><path d="M6 18 18 6M6 6h12v12" /></>,
  trophy: <><path d="M8 3h8v7a4 4 0 0 1-8 0V3ZM8 5H4v3a4 4 0 0 0 4 4m8-7h4v3a4 4 0 0 1-4 4M12 14v5m-4 2h8" /></>,
  users: <><circle cx="9" cy="8" r="3" /><path d="M3 21v-3a6 6 0 0 1 12 0v3M16 5a3 3 0 0 1 0 6m3 10v-3a6 6 0 0 0-3-5" /></>,
  game: <><path d="M8 7h8c3 0 4 2 5 7 1 5-2 6-4 3l-2-2H9l-2 2c-2 3-5 2-4-3 1-5 2-7 5-7Z" /><path d="M7 10v4m-2-2h4m6-1h.01m3 2h.01" /></>,
  spark: <><path d="m13 2-3 8H3l8 5-1 7 5-9h6l-8-5V2Z" /></>,
  shield: <><path d="m12 3 8 3v6c0 5-8 9-8 9s-8-4-8-9V6l8-3Z" /><path d="m8 12 3 3 5-6" /></>,
  check: <path d="m5 12 4 4L19 6" />,
  close: <path d="m6 6 12 12M6 18 18 6" />,
  menu: <path d="M4 6h16M4 12h16M4 18h16" />,
  search: <><circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 5 5" /></>,
  heart: <path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z" />,
  message: <path d="M21 11.5a8.5 8.5 0 0 1-8.5 8.5H3l2-5a8.5 8.5 0 1 1 16-3.5Z" />,
  calendar: <><rect x="3" y="5" width="18" height="16" rx="2" /><path d="M16 3v4M8 3v4M3 11h18" /></>,
  globe: <><circle cx="12" cy="12" r="9" /><ellipse cx="12" cy="12" rx="4" ry="9" /><path d="M3 12h18" /></>,
  plus: <path d="M12 5v14M5 12h14" />,
  clock: <><circle cx="12" cy="12" r="9" /><path d="M12 7v5l3 2" /></>,
  logout: <><path d="M9 4H4v16h5m5-13 5 5-5 5m-6-5h13" /></>,
  edit: <><path d="m15 4 5 5M4 20l5-1L21 7a2 2 0 0 0-5-5L4 14v6Z" /></>,
  play: <path d="m9 5 11 7-11 7V5Z" />,
};
export function Icon({ name, size = 20, className = "", style }: { name: string; size?: number; className?: string; style?: CSSProperties }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" className={className} style={style}>{paths[name] || paths.game}</svg>;
}
export function Logo() { return <span className="brand"><span className="brand-mark"><i /><i /><i /></span>respect<span className="brand-plus">+</span></span>; }
