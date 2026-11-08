"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { useSession } from "./session-provider";
import { Modal } from "./ui";
import { Icon } from "./icon";

export function ReportButton({ type, id, name, ownerId, publicationId }: { type: "player" | "team" | "sponsor"; id: string; name: string; ownerId?: string; publicationId?: string }) {
  const { user, requireAuth, toast } = useSession(); const [open, setOpen] = useState(false); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  if (user?.id === ownerId || (type === "player" && user?.id === id)) return null;
  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError(""); const form = new FormData(event.currentTarget);
    try { await api("/reports", { method: "POST", body: JSON.stringify({ target_type: type, target_id: id, publication_id: publicationId || null, category: form.get("category"), reason: form.get("reason") }) }); setOpen(false); toast("Reporte enviado. El equipo de moderación podrá revisar la evidencia."); } catch (error) { setError((error as Error).message); } finally { setBusy(false); }
  }
  return <><button className="report-button" aria-label={publicationId ? "Reportar publicación" : "Reportar perfil"} onClick={() => requireAuth(() => { setError(""); setOpen(true); })}><Icon name="flag" size={15} /><span>Reportar</span></button>{open && <Modal title={publicationId ? "Reportar esta publicación" : `Reportar a ${name}`} onClose={() => setOpen(false)}><p className="muted">Describe qué ocurrió. Guardaremos el motivo y {publicationId ? "una copia de la publicación" : "el perfil señalado"} para revisión.</p><form onSubmit={submit} className="form-stack"><label>Motivo<select name="category"><option value="acoso">Acoso o comportamiento abusivo</option><option value="odio">Contenido de odio</option><option value="spam">Spam o publicidad engañosa</option><option value="suplantacion">Suplantación de identidad</option><option value="trampas">Trampas o fraude</option><option value="otro">Otro</option></select></label><label>Razón del reporte<textarea name="reason" required minLength={10} maxLength={1500} rows={4} placeholder="Explica el problema y aporta el contexto que ayude a revisarlo." /></label><p className="form-hint">Solo puedes tener un reporte pendiente por perfil. La identidad de quien reporta es visible únicamente para administración.</p>{error && <p className="form-error" role="alert">{error}</p>}<button className="button primary" disabled={busy}>{busy ? "Enviando…" : "Enviar reporte"}<Icon name="flag" size={16} /></button></form></Modal>}</>;
}
