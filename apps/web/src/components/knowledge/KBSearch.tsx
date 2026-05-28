"use client";

import { useState } from "react";
import { Search } from "lucide-react";
import { Button } from "@/components/ui/button";
import { apiJson } from "@/lib/api";

interface SearchResult {
  text: string;
  score: number;
  doc_name: string;
  page: number | null;
}

export function KBSearch() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    const trimmed = query.trim();
    if (!trimmed) return;
    setLoading(true);
    try {
      const data = await apiJson<SearchResult[]>("/api/v1/kb/search", {
        method: "POST",
        body: JSON.stringify({ query: trimmed, top_k: 5 }),
      });
      setResults(data);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSearch();
    }
  };

  return (
    <div className="border border-border rounded-lg p-4 bg-card">
      <h3 className="text-sm font-medium mb-2">Test RAG Search</h3>
      <div className="flex items-center gap-2">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Search your knowledge base..."
          className="flex-1 px-3 py-1.5 border border-border rounded-md bg-background text-sm focus:outline-none focus:ring-2 focus:ring-ring"
        />
        <Button onClick={handleSearch} disabled={loading || !query.trim()} size="sm">
          <Search className="h-4 w-4" />
        </Button>
      </div>
      {results.length > 0 && (
        <div className="mt-3 space-y-2">
          {results.map((result, idx) => (
            <div
              key={idx}
              className="border border-border rounded-md p-3 bg-background"
            >
              <div className="flex items-center justify-between text-xs text-muted-foreground mb-1">
                <span className="font-medium">{result.doc_name}</span>
                <span>{Math.round(result.score * 100)}% match</span>
              </div>
              {result.page !== null && (
                <div className="text-xs text-muted-foreground mb-1">
                  Page {result.page}
                </div>
              )}
              <p className="text-sm line-clamp-3">{result.text}</p>
            </div>
          ))}
        </div>
      )}
      {loading && (
        <p className="text-sm text-muted-foreground mt-2">Searching...</p>
      )}
    </div>
  );
}
