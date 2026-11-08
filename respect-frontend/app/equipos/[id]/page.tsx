import { TeamPublicProfile } from "@/components/team-profile";
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <main id="contenido"><TeamPublicProfile id={id} /></main>;
}
