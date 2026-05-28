"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeHighlight from "rehype-highlight";
import { ChevronDown, ChevronRight } from "lucide-react";
import { cn } from "@/lib/utils";
import { PlotlyChart } from "@/components/charts/PlotlyChart";
import { DataTable } from "@/components/tables/DataTable";

interface MessageBubbleProps {
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
  chartSpec?: { data: unknown[]; layout?: Record<string, unknown> };
  tableData?: { columns: string[]; rows: Record<string, unknown>[] };
  executedCode?: string;
}

export function MessageBubble({
  role,
  content,
  isStreaming,
  chartSpec,
  tableData,
  executedCode,
}: MessageBubbleProps) {
  const [showCode, setShowCode] = useState(false);

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
      </div>
    </div>
  );
}
