export default function ContentArea({ children }: { children: React.ReactNode }) {
  return (
    <main className="flex-1 overflow-auto bg-background">
      <div className="h-full">
        {children}
      </div>
    </main>
  );
}
