import { AdminCaseReview, AdminGate } from "@/components/admin-panel";
export default async function Page({ params }: { params: Promise<{ kind: string; id: string }> }) {
  const { kind, id } = await params;
  return <main id="contenido"><AdminGate><AdminCaseReview kind={kind} id={id} /></AdminGate></main>;
}
