"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiJson } from "@/lib/api";
import { ChatComposer } from "@/components/chat/ChatComposer";

const PROMPT_SUGGESTIONS = [
  "Upload Excel & minta saya analisa",
  "Bikin laporan penjualan dari data ini",
  "Bandingkan 2 dataset",
  "Eksplorasi statistik dasar",
];

export default function ChatPage() {
  const router = useRouter();
  const [isCreating, setIsCreating] = useState(false);

  const handleSend = async (content: string, model?: string) => {
    if (isCreating) return;
    setIsCreating(true);
    try {
      const data = await apiJson<{ id: string }>(
        "/api/v1/conversations",
        {
          method: "POST",
          body: JSON.stringify({ title: content.slice(0, 50) }),
        }
      );
      const id = data.id;
      const params = new URLSearchParams({ message: content });
      if (model) params.set("model", model);
      router.push(`/chat/${id}?${params.toString()}`);
    } catch {
      setIsCreating(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 flex flex-col items-center justify-center p-6">
        <h1 className="text-2xl font-bold mb-2">Selamat datang di uReport AI</h1>
        <p className="text-muted-foreground mb-6">
          Mulai percakapan dengan asisten AI Anda.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 max-w-lg w-full">
          {PROMPT_SUGGESTIONS.map((prompt) => (
            <button
              key={prompt}
              onClick={() => handleSend(prompt)}
              disabled={isCreating}
              className="text-left text-sm p-3 border border-border rounded-md hover:bg-accent transition-colors disabled:opacity-50"
            >
              {prompt}
            </button>
          ))}
        </div>
      </div>
      <ChatComposer onSend={handleSend} disabled={isCreating} />
    </div>
  );
}
