"use client";

import { useRef, useState, useEffect } from "react";
import { Button } from "@/components/ui/button";

const AVAILABLE_MODELS = [
  { id: "groq/llama-3.3-70b-versatile", label: "Llama 3.3 70B (Groq)" },
  { id: "cerebras/llama-3.3-70b", label: "Llama 3.3 70B (Cerebras)" },
  { id: "gemini/gemini-2.0-flash", label: "Gemini 2.0 Flash" },
  { id: "openai/sumopod-default", label: "Sumopod Pro" },
];

interface ChatComposerProps {
  onSend: (content: string, model?: string) => void;
  disabled?: boolean;
}

export function ChatComposer({ onSend, disabled }: ChatComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const [content, setContent] = useState("");
  const [model, setModel] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("default_model") || AVAILABLE_MODELS[0].id;
    }
    return AVAILABLE_MODELS[0].id;
  });

  const adjustHeight = () => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = "auto";
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  };

  useEffect(() => {
    adjustHeight();
  }, [content]);

  const handleSubmit = () => {
    const trimmed = content.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed, model);
    setContent("");
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-border p-4">
      <div className="flex items-end gap-2">
        <div className="flex-1">
          <textarea
            ref={textareaRef}
            value={content}
            onChange={(e) => setContent(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type a message..."
            disabled={disabled}
            rows={1}
            className="w-full resize-none px-3 py-2 border border-border rounded-md bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-ring disabled:opacity-50"
          />
        </div>
        <Button
          onClick={handleSubmit}
          disabled={disabled || !content.trim()}
          size="default"
        >
          Send
        </Button>
      </div>
      <div className="mt-2">
        <select
          value={model}
          onChange={(e) => setModel(e.target.value)}
          className="text-xs px-2 py-1 border border-border rounded-md bg-background text-muted-foreground"
        >
          {AVAILABLE_MODELS.map((m) => (
            <option key={m.id} value={m.id}>
              {m.label}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
}

export { AVAILABLE_MODELS };
