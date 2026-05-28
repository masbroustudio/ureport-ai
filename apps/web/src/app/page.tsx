import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <div className="relative min-h-screen flex flex-col">
      <main className="flex flex-1 flex-col items-center justify-center p-8">
        <div className="text-center space-y-6 max-w-2xl">
          <h1 className="text-4xl font-bold tracking-tight sm:text-6xl">
            uReport AI
          </h1>
          <p className="text-lg text-muted-foreground">
            Platform AI Assistant untuk Analisis Data dan Pembuatan Laporan
            Terstruktur. Upload data, tanyakan apa saja, dan dapatkan insight
            serta laporan profesional.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/chat">
              <Button size="lg">Mulai Chat</Button>
            </Link>
          </div>
        </div>
      </main>
      <footer className="border-t border-border px-6 py-4 text-center text-sm text-muted-foreground">
        <div className="flex items-center justify-center gap-4">
          <Link href="/privacy" className="hover:text-foreground transition-colors">
            Kebijakan Privasi
          </Link>
          <Link href="/terms" className="hover:text-foreground transition-colors">
            Syarat & Ketentuan
          </Link>
        </div>
        <p className="mt-2">&copy; 2025 uReport AI. All rights reserved.</p>
      </footer>
    </div>
  );
}
