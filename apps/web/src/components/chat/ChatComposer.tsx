"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import { Paperclip, X, BookOpen } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { apiJson } from "@/lib/api";

const AVAILABLE_MODELS = [
  { id: "groq/llama-3.3-70b-versatile", label: "Llama 3.3 70B (Groq)" },
  { id: "cerebras/llama-3.3-70b", label: "Llama 3.3 70B (Cerebras)" },
  { id: "gemini/gemini-2.0-flash", label: "Gemini 2.0 Flash" },
  { id: "openai/sumopod-default", label: "Sumopod Pro" },
];

interface AttachedFile {
  id: string;
  name: string;
}

interface ChatComposerProps {
  onSend: (content: string, model?: string, fileIds?: string[], kbDocumentIds?: string[]) => void;
  disabled?: boolean;
}

interface KBDoc {
  id: string;
  name: string;
  status: string;
}

export function ChatComposer({ onSend, disabled }: ChatComposerProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [content, setContent] = useState("");
  const [attachedFiles, setAttachedFiles] = useState<AttachedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [kbDocs, setKbDocs] = useState<KBDoc[]>([]);
  const [selectedKbDocs, setSelectedKbDocs] = useState<string[]>([]);
  const [showKbPanel, setShowKbPanel] = useState(false);
  const [model, setModel] = useState(() => {
    if (typeof window !== "undefined") {
      return localStorage.getItem("default_model") || AVAILABLE_MODELS[0].id;
    }
    return AVAILABLE_MODELS[0].id;
  });

  useEffect(() => {
    apiJson<KBDoc[]>("/api/v1/kb/documents")
      .then((data) => setKbDocs(data.filter((d) => d.status === "ready")))
      .catch(() => {});
  }, []);

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

  const handleFileUpload = useCallback(async (file: File) => {
    setUploading(true);
    try {
      const token =
        typeof window !== "undefined" ? localStorage.getItem("token") : null;
      const formData = new FormData();
      formData.append("file", file);

      const API_BASE =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${API_BASE}/api/v1/files`, {
        method: "POST",
        headers: token ? { Authorization: `Bearer ${token}` } : {},
        body: formData,
      });

      if (!res.ok) {
        throw new Error("Upload failed");
      }

      const data = await res.json();
      setAttachedFiles((prev) => [
        ...prev,
        { id: data.id, name: data.name || file.name },
      ]);
    } catch {
      // Upload failed silently - user can try again
    } finally {
      setUploading(false);
    }
  }, []);

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) handleFileUpload(file);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const removeFile = (id: string) => {
    setAttachedFiles((prev) => prev.filter((f) => f.id !== id));
  };

  const handleSubmit = () => {
    const trimmed = content.trim();
    if (!trimmed || disabled) return;
    const fileIds = attachedFiles.map((f) => f.id);
    onSend(
      trimmed,
      model,
      fileIds.length > 0 ? fileIds : undefined,
      selectedKbDocs.length > 0 ? selectedKbDocs : undefined
    );
    setContent("");
    setAttachedFiles([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="border-t border-border p-4">
      {selectedKbDocs.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-2">
          {selectedKbDocs.map((docId) => {
            const doc = kbDocs.find((d) => d.id === docId);
            return (
              <div
                key={docId}
                className={cn(
                  "inline-flex items-center gap-1 px-2 py-0.5 rounded-full",
                  "bg-primary/10 text-primary text-xs"
                )}
              >
                <BookOpen className="h-3 w-3" />
                <span className="truncate max-w-[120px]">{doc?.name || docId}</span>
                <button
                  onClick={() =>
                    setSelectedKbDocs((prev) => prev.filter((id) => id !== docId))
                  }
                  className="hover:text-destructive transition-colors"
                  aria-label="Remove KB document"
                >
                  <X className="h-3 w-3" />
                </button>
              </div>
            );
          })}
        </div>
      )}
      {attachedFiles.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-2">
          {attachedFiles.map((file) => (
            <div
              key={file.id}
              className={cn(
                "inline-flex items-center gap-1 px-2 py-0.5 rounded-full",
                "bg-secondary text-secondary-foreground text-xs"
              )}
            >
              <span>{file.name}</span>
              <button
                onClick={() => removeFile(file.id)}
                className="hover:text-destructive transition-colors"
                aria-label={`Remove ${file.name}`}
              >
                <X className="h-3 w-3" />
              </button>
            </div>
          ))}
        </div>
      )}
      {showKbPanel && kbDocs.length > 0 && (
        <div className="mb-2 border border-border rounded-md p-2 bg-background max-h-32 overflow-y-auto">
          <p className="text-xs text-muted-foreground mb-1">Select knowledge base documents:</p>
          {kbDocs.map((doc) => (
            <label
              key={doc.id}
              className="flex items-center gap-2 px-2 py-1 rounded hover:bg-accent text-sm cursor-pointer"
            >
              <input
                type="checkbox"
                checked={selectedKbDocs.includes(doc.id)}
                onChange={(e) => {
                  if (e.target.checked) {
                    setSelectedKbDocs((prev) => [...prev, doc.id]);
                  } else {
                    setSelectedKbDocs((prev) => prev.filter((id) => id !== doc.id));
                  }
                }}
                className="rounded border-border"
              />
              <span className="truncate">{doc.name}</span>
            </label>
          ))}
        </div>
      )}
      <div className="flex items-end gap-2">
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={disabled || uploading}
          className="flex-shrink-0 p-2 text-muted-foreground hover:text-foreground transition-colors disabled:opacity-50"
          aria-label="Attach file"
        >
          <Paperclip className={cn("h-5 w-5", uploading && "animate-pulse")} />
        </button>
        <button
          type="button"
          onClick={() => setShowKbPanel(!showKbPanel)}
          disabled={disabled}
          className={cn(
            "flex-shrink-0 p-2 transition-colors disabled:opacity-50",
            selectedKbDocs.length > 0 || showKbPanel
              ? "text-primary"
              : "text-muted-foreground hover:text-foreground"
          )}
          aria-label="Use Knowledge Base"
        >
          <BookOpen className="h-5 w-5" />
        </button>
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.xlsx,.xls"
          onChange={handleFileSelect}
          className="hidden"
        />
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
