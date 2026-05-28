"use client";

import { useState, useRef, useCallback } from "react";
import { Upload } from "lucide-react";
import { cn } from "@/lib/utils";
import { API_BASE } from "@/lib/api";

interface FileInfo {
  id: string;
  name: string;
  profile_json: Record<string, unknown>;
}

interface FileUploadProps {
  onFileUploaded: (file: FileInfo) => void;
}

type UploadState = "idle" | "uploading" | "done" | "error";

export function FileUpload({ onFileUploaded }: FileUploadProps) {
  const [state, setState] = useState<UploadState>("idle");
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState("");
  const [fileProfile, setFileProfile] = useState<Record<string, unknown> | null>(null);
  const [errorMessage, setErrorMessage] = useState("");
  const inputRef = useRef<HTMLInputElement>(null);

  const uploadFile = useCallback(
    async (file: File) => {
      setState("uploading");
      setFileName(file.name);
      setErrorMessage("");

      try {
        const token =
          typeof window !== "undefined" ? localStorage.getItem("token") : null;
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch(`${API_BASE}/api/v1/files`, {
          method: "POST",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          body: formData,
        });

        if (!res.ok) {
          const err = await res.json().catch(() => ({ message: "Upload failed" }));
          throw new Error(err.message || "Upload failed");
        }

        const data = await res.json();
        setState("done");
        setFileProfile(data.profile_json);
        onFileUploaded({
          id: data.id,
          name: data.name || file.name,
          profile_json: data.profile_json,
        });
      } catch (err) {
        setState("error");
        setErrorMessage(err instanceof Error ? err.message : "Upload failed");
      }
    },
    [onFileUploaded]
  );

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) uploadFile(file);
    if (inputRef.current) inputRef.current.value = "";
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files?.[0];
    if (file) uploadFile(file);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const nRows = fileProfile ? (fileProfile.n_rows as number) : null;
  const nCols = fileProfile ? (fileProfile.n_cols as number) : null;

  return (
    <div
      onClick={() => inputRef.current?.click()}
      onDrop={handleDrop}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      className={cn(
        "border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors",
        dragOver
          ? "border-primary bg-primary/5"
          : "border-border hover:border-primary/50",
        state === "error" && "border-destructive"
      )}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.xlsx,.xls"
        onChange={handleFileSelect}
        className="hidden"
      />

      {state === "idle" && (
        <div className="flex flex-col items-center gap-2 text-muted-foreground">
          <Upload className="h-8 w-8" />
          <p className="text-sm">
            Drop a file here or click to upload
          </p>
          <p className="text-xs">CSV, XLSX, XLS</p>
        </div>
      )}

      {state === "uploading" && (
        <div className="flex flex-col items-center gap-2 text-muted-foreground">
          <Upload className="h-8 w-8 animate-pulse" />
          <p className="text-sm">Uploading...</p>
          <p className="text-xs">{fileName}</p>
        </div>
      )}

      {state === "done" && (
        <div className="flex flex-col items-center gap-2 text-muted-foreground">
          <Upload className="h-8 w-8 text-green-600" />
          <p className="text-sm font-medium">{fileName}</p>
          {nRows != null && nCols != null && (
            <p className="text-xs">
              {nRows} rows x {nCols} cols
            </p>
          )}
        </div>
      )}

      {state === "error" && (
        <div className="flex flex-col items-center gap-2">
          <Upload className="h-8 w-8 text-destructive" />
          <p className="text-sm text-destructive">{errorMessage}</p>
          <p className="text-xs text-muted-foreground">Click to try again</p>
        </div>
      )}
    </div>
  );
}
