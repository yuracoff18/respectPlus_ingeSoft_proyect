import { NextRequest } from "next/server";

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  const { path } = await context.params;
  const target = new URL(`/api/${path.map(encodeURIComponent).join("/")}${request.nextUrl.search}`, process.env.BACKEND_URL || "http://127.0.0.1:8000");
  try {
    const headers = new Headers();
    for (const name of ["content-type", "cookie", "origin"]) {
      const value = request.headers.get(name);
      if (value) headers.set(name, value);
    }
    const upstream = await fetch(target, { method: request.method, headers, body: ["GET", "HEAD"].includes(request.method) ? undefined : await request.arrayBuffer(), cache: "no-store", signal: AbortSignal.timeout(20000), redirect: "manual" });
    const output = new Headers({ "Content-Type": upstream.headers.get("content-type") || "application/json", "Cache-Control": "no-store" });
    for (const cookie of upstream.headers.getSetCookie()) output.append("Set-Cookie", cookie);
    return new Response(upstream.body, { status: upstream.status, headers: output });
  } catch { return Response.json({ detail: "El servidor no está disponible. Inicia el backend para continuar." }, { status: 503 }); }
}
export { proxy as GET, proxy as POST, proxy as PUT, proxy as PATCH, proxy as DELETE };
