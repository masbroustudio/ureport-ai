"use client";

import { X } from "lucide-react";
import { cn } from "@/lib/utils";

interface FileInfo {
  id: string;
  name: string;
  profile_json: Record<string, unknown>;
}

interface FilePanelProps {
  files: FileInfo[];
  onRemove: (id: string) => void;
}

export function FilePanel({ files, onRemove }: FilePanelProps) {
  if (files.length === 0) return null;

  return (
    <div className="flex flex-wrap gap-2 px-4 py-2">
      {files.map((file) => {
        const nRows = file.profile_json?.n_rows as number | undefined;
        const nCols = file.profile_json?.n_cols as number | undefined;

        return (
          <div
            key={file.id}
            className={cn(
              "inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full",
              "bg-secondary text-secondary-foreground text-xs"
            )}
          >
            <span className="font-medium">{file.name}</span>
            {nRows != null && nCols != null && (
              <span className="text-muted-foreground">
                ({nRows} x {nCols})
              </span>
            )}
            <button
              onClick={() => onRemove(file.id)}
              className="ml-1 hover:text-destructive transition-colors"
              aria-label={`Remove ${file.name}`}
            >
              <X className="h-3 w-3" />
            </button>
          </div>
        );
      })}
    </div>
  );
}
