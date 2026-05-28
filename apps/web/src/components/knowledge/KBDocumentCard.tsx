"use client";

import { Trash2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface KBDocument {
  id: string;
  name: string;
  status: string;
  chunk_count: number;
  tags: string[];
  created_at: string;
}

interface KBDocumentCardProps {
  document: KBDocument;
  onDelete: (id: string) => void;
}

function formatRelativeTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffMins = Math.floor(diffMs / 60000);
  if (diffMins < 1) return "just now";
  if (diffMins < 60) return `${diffMins}m ago`;
  const diffHours = Math.floor(diffMins / 60);
  if (diffHours < 24) return `${diffHours}h ago`;
  const diffDays = Math.floor(diffHours / 24);
  return `${diffDays}d ago`;
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    processing: "bg-yellow-100 text-yellow-800",
    ready: "bg-green-100 text-green-800",
    failed: "bg-red-100 text-red-800",
  };
  return (
    <span
      className={cn(
        "inline-block px-2 py-0.5 rounded-full text-xs font-medium",
        colors[status] || "bg-gray-100 text-gray-800"
      )}
    >
      {status}
    </span>
  );
}

export function KBDocumentCard({ document, onDelete }: KBDocumentCardProps) {
  const handleDelete = () => {
    if (confirm(`Delete "${document.name}"?`)) {
      onDelete(document.id);
    }
  };

  return (
    <div className="border border-border rounded-lg p-4 bg-card text-card-foreground">
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-sm font-medium truncate flex-1" title={document.name}>
          {document.name}
        </h3>
        <button
          onClick={handleDelete}
          className="text-muted-foreground hover:text-destructive transition-colors flex-shrink-0"
          aria-label={`Delete ${document.name}`}
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
      <div className="mt-2 flex items-center gap-2">
        <StatusBadge status={document.status} />
        <span className="text-xs text-muted-foreground">
          {document.chunk_count} chunks
        </span>
      </div>
      {document.tags.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {document.tags.map((tag) => (
            <span
              key={tag}
              className="inline-block px-1.5 py-0.5 rounded text-xs bg-secondary text-secondary-foreground"
            >
              {tag}
            </span>
          ))}
        </div>
      )}
      <div className="mt-2 text-xs text-muted-foreground">
        Uploaded {formatRelativeTime(document.created_at)}
      </div>
    </div>
  );
}

export type { KBDocument };
