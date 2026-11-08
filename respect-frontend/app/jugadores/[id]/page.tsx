import { PlayerPublicProfile } from "@/components/player-profile";
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <main id="contenido"><PlayerPublicProfile id={id} /></main>;
}
