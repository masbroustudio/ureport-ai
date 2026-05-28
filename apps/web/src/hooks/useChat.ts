"use client";

import { useState, useCallback } from "react";
import { apiFetch } from "@/lib/api";

export interface Citation {
  id: string;
  doc_name: string;
  page: number | null;
  text: string;
  section: string | null;
}

export interface ChatMessage {
  id?: string;
  role: "user" | "assistant";
  content: string;
  isStreaming?: boolean;
  chartSpec?: { data: unknown[]; layout?: Record<string, unknown> };
  tableData?: { columns: string[]; rows: Record<string, unknown>[] };
  executedCode?: string;
  citations?: Citation[];
}

interface UseChatOptions {
  conversationId: string;
  initialMessages?: ChatMessage[];
}

export function useChat({ conversationId, initialMessages = [] }: UseChatOptions) {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [isStreaming, setIsStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const sendMessage = useCallback(
    async (content: string, model?: string, fileIds?: string[], kbDocumentIds?: string[]) => {
      setError(null);

      const userMessage: ChatMessage = { role: "user", content };
      const assistantMessage: ChatMessage = {
        role: "assistant",
        content: "",
        isStreaming: true,
      };

      setMessages((prev) => [...prev, userMessage, assistantMessage]);
      setIsStreaming(true);

      try {
        const body: Record<string, unknown> = { content };
        if (model) body.model = model;
        if (fileIds && fileIds.length > 0) body.file_ids = fileIds;
        if (kbDocumentIds && kbDocumentIds.length > 0) body.kb_document_ids = kbDocumentIds;

        const res = await apiFetch(
          `/api/v1/conversations/${conversationId}/messages`,
          {
            method: "POST",
            body: JSON.stringify(body),
            headers: {
              "Content-Type": "application/json",
              Accept: "text/event-stream",
            },
          }
        );

        const reader = res.body?.getReader();
        if (!reader) throw new Error("No response stream available");

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const events = buffer.split("\n\n");
          buffer = events.pop() || "";

          for (const event of events) {
            const lines = event.split("\n");
            let eventType = "";
            let eventData = "";

            for (const line of lines) {
              if (line.startsWith("event:")) {
                eventType = line.slice(6).trim();
              } else if (line.startsWith("data:")) {
                eventData = line.slice(5).trim();
              }
            }

            if (eventType === "token") {
              const parsed = JSON.parse(eventData);
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last && last.role === "assistant") {
                  updated[updated.length - 1] = {
                    ...last,
                    content: last.content + (parsed.text || parsed.token || ""),
                  };
                }
                return updated;
              });
            } else if (eventType === "chart") {
              const parsed = JSON.parse(eventData);
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last && last.role === "assistant") {
                  updated[updated.length - 1] = {
                    ...last,
                    chartSpec: parsed,
                  };
                }
                return updated;
              });
            } else if (eventType === "table") {
              const parsed = JSON.parse(eventData);
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last && last.role === "assistant") {
                  updated[updated.length - 1] = {
                    ...last,
                    tableData: parsed,
                  };
                }
                return updated;
              });
            } else if (eventType === "code") {
              const parsed = JSON.parse(eventData);
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last && last.role === "assistant") {
                  updated[updated.length - 1] = {
                    ...last,
                    executedCode: parsed.code || parsed.source || parsed,
                  };
                }
                return updated;
              });
            } else if (eventType === "citation") {
              const parsed = JSON.parse(eventData);
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last && last.role === "assistant") {
                  const existingCitations = last.citations || [];
                  updated[updated.length - 1] = {
                    ...last,
                    citations: [...existingCitations, parsed],
                  };
                }
                return updated;
              });
            } else if (eventType === "done") {
              const parsed = JSON.parse(eventData);
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last && last.role === "assistant") {
                  updated[updated.length - 1] = {
                    ...last,
                    id: parsed.message_id,
                    isStreaming: false,
                  };
                }
                return updated;
              });
            } else if (eventType === "error") {
              const parsed = JSON.parse(eventData);
              setError(parsed.detail || parsed.message || "An error occurred");
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last && last.role === "assistant") {
                  updated[updated.length - 1] = {
                    ...last,
                    content: "An error occurred while generating a response.",
                    isStreaming: false,
                  };
                }
                return updated;
              });
            }
          }
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to send message");
        setMessages((prev) => {
          const updated = [...prev];
          const last = updated[updated.length - 1];
          if (last && last.role === "assistant" && last.isStreaming) {
            updated[updated.length - 1] = {
              ...last,
              content: "Failed to get a response. Please try again.",
              isStreaming: false,
            };
          }
          return updated;
        });
      } finally {
        setIsStreaming(false);
      }
    },
    [conversationId]
  );

  return { messages, setMessages, isStreaming, error, sendMessage };
}
