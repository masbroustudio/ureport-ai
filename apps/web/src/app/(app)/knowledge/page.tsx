"use client";

import { useEffect, useState, useCallback } from "react";
import { apiJson, apiFetch } from "@/lib/api";
import { KBDocumentCard, type KBDocument } from "@/components/knowledge/KBDocumentCard";
import { KBUpload } from "@/components/knowledge/KBUpload";
import { KBSearch } from "@/components/knowledge/KBSearch";

export default function KnowledgeBasePage() {
  const [documents, setDocuments] = useState<KBDocument[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDocuments = useCallback(async () => {
    try {
      const data = await apiJson<KBDocument[]>("/api/v1/kb/documents");
      setDocuments(data);
    } catch {
      // Failed to load documents
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleDelete = async (id: string) => {
    try {
      await apiFetch(`/api/v1/kb/documents/${id}`, { method: "DELETE" });
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch {
      // Delete failed
    }
  };

  const handleUpload = () => {
    fetchDocuments();
  };

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <h1 className="text-2xl font-bold">Knowledge Base</h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <KBUpload onUpload={handleUpload} />
        <KBSearch />
      </div>

      <div>
        <h2 className="text-lg font-semibold mb-3">Documents</h2>
        {loading && (
          <p className="text-sm text-muted-foreground">Loading documents...</p>
        )}
        {!loading && documents.length === 0 && (
          <div className="flex flex-col items-center justify-center py-12 text-center">
            <svg
              className="h-16 w-16 text-muted-foreground/50 mb-4"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 0 0-3.375-3.375h-1.5A1.125 1.125 0 0 1 13.5 7.125v-1.5a3.375 3.375 0 0 0-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 0 0-9-9Z"
              />
            </svg>
            <h3 className="text-lg font-semibold mb-1">Belum ada dokumen</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Upload dokumen pertama Anda untuk memulai
            </p>
            <button
              onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
              className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:opacity-90"
            >
              Upload Dokumen
            </button>
          </div>
        )}
        {documents.length > 0 && (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {documents.map((doc) => (
              <KBDocumentCard
                key={doc.id}
                document={doc}
                onDelete={handleDelete}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
