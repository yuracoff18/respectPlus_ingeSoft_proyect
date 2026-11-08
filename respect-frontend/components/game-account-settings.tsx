"use client";

import { useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { User } from "@/lib/types";
import { useSession } from "./session-provider";
import { GameRanks } from "./game-ranks";
import { ErrorMessage, Modal } from "./ui";
import { Icon } from "./icon";

type Provider = { game: string; provider: string | null; supported: boolean; configured: boolean; message: string };
const LOL_REGIONS = [["la1", "LAN"], ["la2", "LAS"], ["na1", "Norteamérica"], ["br1", "Brasil"], ["euw1", "Europa Oeste"], ["eun1", "Europa Nórdica"], ["kr", "Corea"], ["jp1", "Japón"], ["oc1", "Oceanía"], ["tr1", "Turquía"], ["ru", "Rusia"]];

export function GameAccountSettings() {
  const { user, setUser, toast } = useSession();
  const [providers, setProviders] = useState<Provider[]>([]); const [selected, setSelected] = useState<string | null>(null);
  const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  useEffect(() => { api<Provider[]>("/game-accounts/providers").then(setProviders).catch(error => setError(error.message)); }, []);
  if (!user || user.role === "admin") return null;
  const currentUser = user;
  const provider = providers.find(value => value.game === selected);
  async function sync(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); const form = new FormData(event.currentTarget); setBusy(true); setError("");
    try {
      const updated = await api<User>("/game-accounts/sync", { method: "POST", body: JSON.stringify({ game: selected, identifier: form.get("identifier"), region: form.get("region") || "global", platform: form.get("platform") || "pc", queue: form.get("queue") || "competitive", consent: form.get("consent") === "on" }) });
      setUser(updated); const status = updated.game_profiles[selected!]?.status;
      toast(status === "synced" || status === "unranked" ? "Estadísticas actualizadas desde el proveedor." : updated.game_profiles[selected!]?.note || "La consulta no está disponible."); setSelected(null);
    } catch (error) { setError((error as Error).message); } finally { setBusy(false); }
  }
  async function unlink(game: string) {
    setBusy(true); setError("");
    try { setUser(await api<User>(`/game-accounts/${encodeURIComponent(game)}`, { method: "DELETE" })); toast("La cuenta y sus estadísticas se desvincularon."); } catch (error) { setError((error as Error).message); } finally { setBusy(false); }
  }
  return <section className="panel account-settings"><span className="eyebrow">TUS JUEGOS, TUS ESTADÍSTICAS</span><h2>Cuentas de juego</h2><p>Consulta tus rangos por juego. El pico se muestra cuando el proveedor lo entrega; las cuentas declaradas no verifican tu identidad como propietario.</p>{error && !selected && <ErrorMessage message={error} />}{!user.games.length && <p className="muted">Añade juegos a tu perfil para consultar sus rangos.</p>}{user.games.map(game => <div className="account-setting-row" key={game}><GameRanks player={user} onlyGame={game} /><div className="account-setting-actions"><button className="button outline" onClick={() => { setError(""); setSelected(game); }}>Configurar cuenta <Icon name="game" size={15} /></button>{user.game_profiles[game] && <button className="text-link" disabled={busy} onClick={() => void unlink(game)}>Desvincular</button>}</div><p className="form-hint">{user.game_profiles[game]?.note || providers.find(value => value.game === game)?.message}</p></div>)}{selected && <Modal title={`Tu cuenta de ${selected}`} onClose={() => setSelected(null)}><p className="muted">{provider?.provider ? `Consulta mediante ${provider.provider}.` : "Este juego requiere acceso de partner a una fuente de rangos."}</p>{provider && !provider.supported ? <p className="error-box">{provider.message} Los rangos estarán disponibles cuando se configure un proveedor autorizado.</p> : <form className="form-stack" onSubmit={sync}><label>Cuenta del juego<input name="identifier" required minLength={3} maxLength={100} defaultValue={currentUser.game_profiles[selected]?.account_name || ""} placeholder={selected === "Valorant" || selected === "League of Legends" ? "Nombre#TAG" : selected === "Counter-Strike 2" ? "SteamID64 o nickname de FACEIT" : "Nombre de Epic o Epic Account ID"} /></label>{selected === "League of Legends" && <><label>Servidor<select name="region" defaultValue={currentUser.game_profiles[selected]?.region || "la1"}>{LOL_REGIONS.map(([value, label]) => <option value={value} key={value}>{label}</option>)}</select></label><label>Cola<select name="queue"><option value="solo">Solo/Duo</option><option value="flex">Flex</option></select></label></>}{selected === "Counter-Strike 2" && <label>Proveedor de Counter-Strike 2<select name="platform"><option value="steam">Steam / SteamID64 de 17 digitos</option><option value="faceit">FACEIT / Nickname (clave independiente)</option></select></label>}{selected === "Valorant" && <><label>Región<select name="region" defaultValue="latam">{["latam", "na", "eu", "br", "ap", "kr"].map(region => <option key={region}>{region}</option>)}</select></label><label>Plataforma<select name="platform"><option value="pc">PC</option><option value="console">Consola</option></select></label></>}{selected === "Fortnite" && <label>Modo competitivo<select name="queue"><option value="ranked-br">Battle Royale</option><option value="ranked-zb">Cero construcción</option></select></label>}{provider && !provider.configured && <p className="form-hint">{provider.message} Puedes guardar tu cuenta; el rango permanecerá sin sincronizar hasta activar el proveedor.</p>}<label className="checkbox-label"><input name="consent" type="checkbox" required /> Esta es mi cuenta y autorizo consultar y mostrar sus estadísticas.</label>{error && <p className="form-error" role="alert">{error}</p>}<button className="button primary" disabled={busy}>{busy ? "Consultando…" : provider?.configured ? "Consultar rangos" : "Guardar cuenta"}</button></form>}</Modal>}</section>;
}
