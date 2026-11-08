export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`/api${path}`, { ...init, credentials: "same-origin", cache: "no-store", headers: { "Content-Type": "application/json", ...init?.headers } });
  } catch { throw new Error("No pudimos conectar. Revisa tu conexión e inténtalo de nuevo."); }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail;
    throw new Error(typeof detail === "string" ? detail : response.status === 503 ? "El servidor no está disponible. Inicia el backend para continuar." : "Revisa los campos e inténtalo de nuevo.");
  }
  return data as T;
}
