"use client";

import { useEffect, useRef } from "react";
import { useParams, useSearchParams } from "next/navigation";
import { apiJson } from "@/lib/api";
import { useChat, type ChatMessage } from "@/hooks/useChat";
import { ChatComposer } from "@/components/chat/ChatComposer";
import { MessageBubble } from "@/components/chat/MessageBubble";

interface ApiMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
}

export default function ChatConversationPage() {
  const params = useParams();
  const searchParams = useSearchParams();
  const conversationId = params.id as string;
  const initialMessageSent = useRef(false);

  const { messages, setMessages, isStreaming, error, sendMessage } = useChat({
    conversationId,
  });

  useEffect(() => {
    apiJson<ApiMessage[]>(
      `/api/v1/conversations/${conversationId}/messages`
    )
      .then((data) => {
        const mapped: ChatMessage[] = data.map((m) => ({
          id: m.id,
          role: m.role,
          content: m.content,
        }));
        setMessages(mapped);
      })
      .catch(() => {});
  }, [conversationId, setMessages]);

  useEffect(() => {
    const message = searchParams.get("message");
    const model = searchParams.get("model");
    if (message && !initialMessageSent.current) {
      initialMessageSent.current = true;
      sendMessage(message, model || undefined);
    }
  }, [searchParams, sendMessage]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full">
            <p className="text-muted-foreground">No messages yet.</p>
          </div>
        )}
        {messages.map((msg, idx) => (
          <MessageBubble
            key={msg.id || idx}
            role={msg.role}
            content={msg.content}
            isStreaming={msg.isStreaming}
          />
        ))}
        {error && (
          <div className="text-sm text-destructive text-center py-2">
            {error}
          </div>
        )}
      </div>
      <ChatComposer onSend={sendMessage} disabled={isStreaming} />
    </div>
  );
}
