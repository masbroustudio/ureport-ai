"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { ChevronDown, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { PlotlyChart } from "@/components/charts/PlotlyChart";
import { DataTable } from "@/components/tables/DataTable";
import type { Citation } from "@/hooks/useChat";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
  chartSpec?: { data: unknown[]; layout?: Record<string, unknown> };
  tableData?: { columns: string[]; rows: Record<string, unknown>[] };
  executedCode?: string;
  citations?: Citation[];
}

export function MessageBubble({
  role,
  content,
  isStreaming,
  chartSpec,
  tableData,
  executedCode,
  citations,
}: MessageBubbleProps) {
  const [showCode, setShowCode] = useState(false);
  const [activeCitation, setActiveCitation] = useState<string | null>(null);

  if (role === "user") {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[80%] px-4 py-2 rounded-lg bg-primary text-primary-foreground">
          <p className="whitespace-pre-wrap">{content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[80%] px-4 py-2 rounded-lg bg-secondary text-secondary-foreground">
        {!content && isStreaming ? (
          <span className="inline-block animate-pulse">...</span>
        ) : (
          <div className={cn("prose prose-sm max-w-none dark:prose-invert")}>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              rehypePlugins={[rehypeHighlight]}
            >
              {content}
            </ReactMarkdown>
            {isStreaming && (
              <span className="inline-block w-1.5 h-4 bg-foreground/70 animate-pulse ml-0.5" />
            )}
          </div>
        )}

        {chartSpec && (
          <div className="mt-3">
            <PlotlyChart spec={chartSpec} />
          </div>
        )}

        {tableData && (
          <div className="mt-3">
            <DataTable columns={tableData.columns} rows={tableData.rows} />
          </div>
        )}

        {executedCode && (
          <div className="mt-3">
            <button
              onClick={() => setShowCode(!showCode)}
              className="inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground transition-colors"
            >
              {showCode ? (
                <ChevronDown className="h-3 w-3" />
              ) : (
                <ChevronRight className="h-3 w-3" />
              )}
              Show code
            </button>
            {showCode && (
              <pre className="mt-2 p-3 rounded-md bg-muted text-xs overflow-x-auto">
                <code>{executedCode}</code>
              </pre>
            )}
          </div>
        )}

        {citations && citations.length > 0 && (
          <div className="mt-3 border-t border-border pt-2">
            <p className="text-xs text-muted-foreground mb-1">Sources:</p>
            <div className="flex flex-wrap gap-1">
              {citations.map((citation, idx) => (
                <span key={citation.id} className="relative inline-block">
                  <button
                    onClick={() =>
                      setActiveCitation(
                        activeCitation === citation.id ? null : citation.id
                      )
                    }
                    className="inline-flex items-center justify-center h-5 min-w-5 px-1 rounded-full bg-primary/10 text-primary text-xs font-medium hover:bg-primary/20 transition-colors"
                  >
                    {idx + 1}
                  </button>
                  {activeCitation === citation.id && (
                    <div className="absolute bottom-full left-0 mb-1 w-64 p-2 rounded-md border border-border bg-popover text-popover-foreground shadow-md z-10">
                      <p className="text-xs font-medium">{citation.doc_name}</p>
                      {citation.page !== null && (
                        <p className="text-xs text-muted-foreground">
                          Page {citation.page}
                        </p>
                      )}
                      {citation.section && (
                        <p className="text-xs text-muted-foreground">
                          {citation.section}
                        </p>
                      )}
                      <p className="text-xs mt-1 line-clamp-3">{citation.text}</p>
                    </div>
                  )}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
