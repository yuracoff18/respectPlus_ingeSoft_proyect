"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { AccountType, User } from "@/lib/types";
import { Modal } from "./ui";
import { Icon, Logo } from "./icon";

export function AuthForm({ mode, initialAccountType, changeMode, onClose, onSuccess }: {
  mode: "login" | "register";
  initialAccountType: AccountType;
  changeMode: (mode: "login" | "register") => void;
  onClose: () => void;
  onSuccess: (user: User) => void;
}) {
  const [accountType, setAccountType] = useState<AccountType>(initialAccountType);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const registering = mode === "register";
  const company = accountType === "sponsor";

  async function submit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault(); setBusy(true); setError("");
    const data = Object.fromEntries(new FormData(event.currentTarget));
    try {
      onSuccess(await api<User>(`/auth/${mode}`, { method: "POST", body: JSON.stringify(data) }));
    } catch (error) { setError((error as Error).message); }
    finally { setBusy(false); }
  }

  return <Modal title={registering ? "Tu próxima historia empieza aquí." : "De vuelta a tu zona."} onClose={onClose}>
    <div className="auth-logo"><Logo /></div>
    <p className="muted">{registering ? "Elige cómo quieres formar parte de la comunidad." : "Entra con tu cuenta de jugador o de empresa."}</p>
    <form onSubmit={submit} className="form-stack" key={mode}>
      {registering && <>
        <fieldset className="account-type-picker">
          <legend>Tipo de cuenta</legend>
          <div className="account-type-options">
            <label className={company ? "" : "selected"}>
              <input type="radio" name="account_type" value="player" aria-label="Jugador" checked={!company} onChange={() => { setAccountType("player"); setError(""); }} />
              <Icon name="game" size={22} /><span><strong>Jugador</strong><small>Tu identidad y tus juegos</small></span>
            </label>
            <label className={company ? "selected" : ""}>
              <input type="radio" name="account_type" value="sponsor" aria-label="Empresa / sponsor" checked={company} onChange={() => { setAccountType("sponsor"); setError(""); }} />
              <Icon name="shield" size={22} /><span><strong>Empresa / sponsor</strong><small>El espacio de tu organización</small></span>
            </label>
          </div>
        </fieldset>
        <p className="form-hint account-type-hint">{company ? "La empresa tendrá su propio acceso y perfil. Podrás completar sus datos después." : "No necesitas pertenecer a un equipo ni crear uno para registrarte."}</p>
        <label>{company ? "Nombre de la empresa" : "Nombre o alias"}<input name="name" required minLength={company ? 3 : 2} maxLength={40} placeholder={company ? "Nombre de tu organización" : "Tu nombre o alias de jugador"} autoComplete={company ? "organization" : "nickname"} /></label>
        <label>Usuario<input name="username" required pattern="[A-Za-z0-9_]{3,24}" title="Entre 3 y 24 letras, números o guiones bajos" minLength={3} maxLength={24} placeholder={company ? "usuario_de_la_empresa" : "tu_gamertag"} autoComplete="username" /></label>
      </>}
      {registering ? <label>Correo electrónico<input name="email" type="email" required placeholder={company ? "contacto@empresa.com" : "player@ejemplo.com"} autoComplete="email" /></label> : <label>Usuario o correo electrónico<input name="identifier" type="text" required placeholder="tu_usuario o correo@ejemplo.com" autoComplete="username" /></label>}
      <label>Contraseña<input name="password" type="password" minLength={8} maxLength={128} required placeholder="Mínimo 8 caracteres" autoComplete={registering ? "new-password" : "current-password"} /></label>
      {error && <p className="form-error" role="alert">{error}</p>}
      <button className="button primary full" disabled={busy}>{busy ? "Conectando…" : registering ? company ? "Crear cuenta de empresa" : "Crear mi perfil" : "Entrar a mi cuenta"}<Icon name="arrow" size={18} /></button>
    </form>
    <p className="auth-switch">{registering ? "¿Ya tienes una cuenta?" : "¿Primera vez por aquí?"} <button className="text-link" onClick={() => { setError(""); changeMode(registering ? "login" : "register"); }}>{registering ? "Inicia sesión" : "Crea tu cuenta"}</button></p>
  </Modal>;
}
