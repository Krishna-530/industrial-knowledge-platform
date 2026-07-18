export default function EmptyState({ title, description }: { title: string, description: string }) {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center bg-surface border border-border rounded-xl">
      <h3 className="text-lg font-semibold text-foreground mb-2">{title}</h3>
      <p className="text-muted text-sm max-w-md">{description}</p>
    </div>
  );
}
