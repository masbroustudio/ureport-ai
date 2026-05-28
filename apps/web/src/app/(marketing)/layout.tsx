import Link from "next/link";

export default function MarketingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-border px-6 py-4">
        <Link href="/" className="text-lg font-bold">
          uReport AI
        </Link>
      </header>
      <main className="flex-1">{children}</main>
      <footer className="border-t border-border px-6 py-4 text-center text-sm text-muted-foreground">
        <div className="flex items-center justify-center gap-4">
          <Link href="/privacy" className="hover:text-foreground transition-colors">
            Kebijakan Privasi
          </Link>
          <Link href="/terms" className="hover:text-foreground transition-colors">
            Syarat & Ketentuan
          </Link>
        </div>
        <p className="mt-2">&copy; {new Date().getFullYear()} uReport AI. All rights reserved.</p>
      </footer>
    </div>
  );
}
