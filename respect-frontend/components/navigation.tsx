"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Icon, Logo } from "./icon";
import { useSession } from "./session-provider";
import { Avatar } from "./ui";

export function Navbar() {
  const { user, ready, openAuth, logout } = useSession();
  const pathname = usePathname();
  const [menu, setMenu] = useState(false);
  const links = [["/comunidad", "Comunidad", "message"], ["/torneos", "Torneos", "trophy"], ["/jugadores", "Jugadores", "game"], ["/equipos", "Equipos", "users"], ["/sponsors", "Sponsors", "shield"]];
  if (user?.role === "admin") links.push(["/admin", "Administración", "shield"]);
  return (
    <header className="site-header">
      <div className="container nav-inner">
        <Link href="/" aria-label="Respect+ inicio" onClick={() => setMenu(false)}><Logo /></Link>
        <nav className={`main-nav ${menu ? "nav-open" : ""}`} aria-label="Navegación principal">
          {links.map(([href, label, icon]) => <Link key={href} href={href} className={pathname.startsWith(href) ? "active" : ""} onClick={() => setMenu(false)}><Icon name={icon} size={18} /><span>{label}</span></Link>)}
        </nav>
        <div className="nav-actions">
          {!ready ? <span className="nav-loading" role="status" aria-label="Recuperando sesión"><span className="loader" /></span> : user ? <>
            <Link className="nav-profile" aria-label={user.role === "admin" ? "Administración" : user.account_type === "sponsor" ? "Mi empresa" : "Mi perfil"} href={user.role === "admin" ? "/admin" : user.account_type === "sponsor" ? user.profile_href : "/perfil"} onClick={() => setMenu(false)}><Avatar player={user} small /><span>{user.role === "admin" ? "Admin" : user.account_type === "sponsor" ? "Mi empresa" : user.name}</span></Link>
            <button className="icon-button signout" onClick={logout} aria-label="Cerrar sesión"><Icon name="logout" size={18} /></button>
          </> : <>
            <button className="login-button" onClick={() => openAuth("login")}>Iniciar sesión</button>
            <button className="button primary nav-cta" onClick={() => openAuth("register")}>Únete al juego <Icon name="diagonal" size={16} /></button>
          </>}
          <button className="icon-button menu-toggle" aria-label={menu ? "Cerrar menú" : "Abrir menú"} aria-expanded={menu} onClick={() => setMenu(!menu)}><Icon name={menu ? "close" : "menu"} /></button>
        </div>
      </div>
    </header>
  );
}
export function Footer() {
  return <footer className="site-footer"><div className="container footer-top"><Link href="/" aria-label="Respect+ inicio"><Logo /></Link><p>El talento se juega. El respeto se gana.</p><div className="footer-links"><Link href="/comunidad">Comunidad</Link><Link href="/torneos">Torneos</Link><Link href="/jugadores">Jugadores</Link><Link href="/equipos">Equipos</Link><Link href="/sponsors">Sponsors</Link></div></div><div className="container footer-bottom"><span>© {new Date().getFullYear()} Respect+. Hecho para quienes juegan en serio.</span><span className="footer-status"><i /> TODOS LOS ESTILOS. UNA COMUNIDAD.</span></div></footer>;
}
