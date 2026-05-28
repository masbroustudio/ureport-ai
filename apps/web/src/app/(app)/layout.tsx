export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen">
      <aside className="w-64 border-r border-border p-4 hidden md:block">
        <div className="font-semibold text-lg mb-4">uReport AI</div>
        <nav className="space-y-2">
          <a
            href="/chat"
            className="block px-3 py-2 rounded-md hover:bg-accent text-sm"
          >
            Chat
          </a>
        </nav>
      </aside>
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
