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
          <p className="text-sm text-muted-foreground">
            No documents uploaded yet. Upload a PDF, DOCX, or TXT file to get started.
          </p>
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
