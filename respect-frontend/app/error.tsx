"use client";
export default function ErrorPage({ reset }: { reset: () => void }) { return <main id="contenido" className="container page-content signed-out"><span className="eyebrow">CONEXIÓN INTERRUMPIDA</span><h1>Necesitamos una nueva ronda.</h1><p>Ocurrió un error al cargar esta página.</p><button className="button primary" onClick={reset}>Volver a intentar</button></main>; }
