import { SponsorPublicProfile } from "@/components/sponsor-profile";
export default async function Page({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  return <main id="contenido"><SponsorPublicProfile id={id} /></main>;
}
