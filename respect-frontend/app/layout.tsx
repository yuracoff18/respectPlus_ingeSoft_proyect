import type { Metadata } from "next";
import { SessionProvider } from "@/components/session-provider";
import { Navbar, Footer } from "@/components/navigation";
import "./globals.css";
import "./community-updates.css";

export const metadata: Metadata = {
  title: { default: "Respect+ | Tu juego. Tu gente. Tu próximo nivel.", template: "%s | Respect+" },
  description: "Tu red gamer: conecta con jugadores, comparte tus logros y crea o compite en torneos. El siguiente nivel empieza contigo.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body><SessionProvider><a className="skip-link" href="#contenido">Saltar al contenido</a><Navbar />{children}<Footer /></SessionProvider></body>
    </html>
  );
}
