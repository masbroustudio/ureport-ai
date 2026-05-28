import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
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
  );
}
