"use client";

import { useEffect, useId, useRef } from "react";
import { createPortal } from "react-dom";
import type { Player } from "@/lib/types";
import { Icon } from "./icon";

export function Avatar({ player, small = false }: { player: Pick<Player, "name" | "color">; small?: boolean }) {
  return <span className={`avatar ${small ? "avatar-small" : ""}`} style={{ "--avatar-color": player.color } as React.CSSProperties}>{player.name.slice(0, 2).toUpperCase()}</span>;
}
export function Modal({ title, children, onClose, wide = false }: { title: string; children: React.ReactNode; onClose: () => void; wide?: boolean }) {
  const ref = useRef<HTMLDivElement>(null);
  const id = useId();
  const closeRef = useRef(onClose);
  closeRef.current = onClose;
  useEffect(() => {
    const prior = document.activeElement as HTMLElement | null;
    const overflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    ref.current?.focus();
    function keydown(e: KeyboardEvent) {
      if (e.key === "Escape") closeRef.current();
      if (e.key !== "Tab") return;
      const elements = ref.current?.querySelectorAll<HTMLElement>('button:not(:disabled), a[href], input:not(:disabled), select, textarea, [tabindex="0"]');
      if (!elements?.length) return;
      const first = elements[0], last = elements[elements.length - 1];
      if (e.shiftKey && (document.activeElement === first || document.activeElement === ref.current)) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && (document.activeElement === last || document.activeElement === ref.current)) { e.preventDefault(); first.focus(); }
    }
    document.addEventListener("keydown", keydown);
    return () => { document.body.style.overflow = overflow; document.removeEventListener("keydown", keydown); prior?.focus(); };
  }, []);
  return createPortal(<div className="modal-backdrop" onMouseDown={e => { if (e.target === e.currentTarget) onClose(); }}><div className={`modal ${wide ? "modal-wide" : ""}`} role="dialog" aria-modal="true" aria-labelledby={id} ref={ref} tabIndex={-1}><button className="icon-button modal-close" onClick={onClose} aria-label="Cerrar ventana"><Icon name="close" /></button><span className="eyebrow">RESPECT+ / PLAYER ZONE</span><h2 id={id}>{title}</h2>{children}</div></div>, document.body);
}
export function ErrorMessage({ message, retry }: { message: string; retry?: () => void }) { return <div className="error-box" role="alert"><p>{message}</p>{retry && <button className="text-link" onClick={retry}>Volver a intentar <Icon name="arrow" size={16} /></button>}</div>; }
export function Empty({ title, text }: { title: string; text: string }) { return <div className="empty-state"><Icon name="game" size={36} /><h3>{title}</h3><p>{text}</p></div>; }
export function Loading() { return <div className="loading-state" role="status"><span className="loader" /> Cargando la siguiente partida…</div>; }
export function Reveal({ children, className = "" }: { children: React.ReactNode; className?: string }) {
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const node = ref.current;
    if (!node || !window.IntersectionObserver || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;
    node.classList.add("reveal-ready");
    const observer = new IntersectionObserver(entries => { if (entries[0].isIntersecting) { node.classList.add("revealed"); observer.disconnect(); } }, { threshold: 0.08 });
    observer.observe(node);
    return () => observer.disconnect();
  }, []);
  return <div className={`reveal ${className}`} ref={ref}>{children}</div>;
}
export function dateLabel(date: string) { return new Intl.DateTimeFormat("es-CO", { day: "numeric", month: "short", timeZone: "America/Bogota" }).format(new Date(date)); }
