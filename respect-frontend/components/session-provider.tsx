"use client";

import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { api } from "@/lib/api";
import type { AccountType, User } from "@/lib/types";
import { Icon } from "./icon";
import { AuthForm } from "./auth-form";

type Session = { user: User | null; ready: boolean; setUser: (user: User | null) => void; openAuth: (mode?: "login" | "register", accountType?: AccountType) => void; requireAuth: (action: (user: User) => void) => void; logout: () => Promise<void>; toast: (message: string) => void };
const Context = createContext<Session | null>(null);
export function useSession() { const value = useContext(Context); if (!value) throw new Error("SessionProvider missing"); return value; }

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [ready, setReady] = useState(false);
  const [auth, setAuth] = useState<"login" | "register" | null>(null);
  const [registrationType, setRegistrationType] = useState<AccountType>("player");
  const router = useRouter();
  const [notice, setNotice] = useState("");
  const pending = useRef<((user: User) => void) | null>(null);
  const sessionRequest = useRef<Promise<User | null> | null>(null);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);
  useEffect(() => {
    const request = api<User>("/auth/me").catch(() => null);
    sessionRequest.current = request;
    let active = true;
    void request.then(value => { if (active) { setUser(value); setReady(true); } });
    return () => { active = false; if (timer.current) clearTimeout(timer.current); };
  }, []);
  const toast = useCallback((message: string) => { setNotice(message); if (timer.current) clearTimeout(timer.current); timer.current = setTimeout(() => setNotice(""), 4500); }, []);
  const openAuth = (mode: "login" | "register" = "register", accountType: AccountType = "player") => { pending.current = null; setRegistrationType(accountType); setAuth(mode); };
  const requireAuth = (action: (user: User) => void) => {
    if (user) { action(user); return; }
    const resolve = (value: User | null) => { if (value) action(value); else { pending.current = action; setRegistrationType("player"); setAuth("register"); } };
    if (!ready && sessionRequest.current) void sessionRequest.current.then(resolve);
    else resolve(null);
  };
  const logout = async () => { try { await api("/auth/logout", { method: "POST" }); setUser(null); toast("Sesión cerrada. ¡Nos vemos en la siguiente partida!"); } catch (e) { toast((e as Error).message); } };
  return <Context.Provider value={{ user, ready, setUser, openAuth, requireAuth, logout, toast }}>{children}{auth && <AuthForm key={registrationType} mode={auth} initialAccountType={registrationType} changeMode={setAuth} onClose={() => { setAuth(null); pending.current = null; }} onSuccess={value => { setUser(value); setAuth(null); toast(`¡Bienvenido a Respect+, ${value.name}!`); const action = pending.current; pending.current = null; if (action) action(value); else if (value.account_type === "sponsor") router.push(value.profile_href); }} />}{notice && <div className="toast" role="status"><span className="toast-check"><Icon name="check" size={16} /></span>{notice}<button className="icon-button" onClick={() => setNotice("")} aria-label="Cerrar notificación"><Icon name="close" size={16} /></button></div>}</Context.Provider>;
}
