"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { apiJson } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

interface Conversation {
  id: string;
  title: string;
  updated_at: string;
}

interface ChatSidebarProps {
  isOpen?: boolean;
  onClose?: () => void;
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

function SidebarContent({
  conversations,
  loading,
  pathname,
  onDelete,
  onClose,
}: {
  conversations: Conversation[];
  loading: boolean;
  pathname: string;
  onDelete: (id: string) => void;
  onClose?: () => void;
}) {
  return (
    <>
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          <div className="font-semibold text-lg">uReport AI</div>
          {onClose && (
            <button
              onClick={onClose}
              className="md:hidden p-1 text-muted-foreground hover:text-foreground"
              aria-label="Close sidebar"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
        <Link href="/chat" onClick={onClose}>
          <Button variant="outline" className="w-full mt-3" size="sm">
            + New Chat
          </Button>
        </Link>
      </div>
      <nav className="flex-1 overflow-y-auto p-2 space-y-1">
        {loading && (
          <p className="text-sm text-muted-foreground px-2 py-1">Loading...</p>
        )}
        {!loading && conversations.length === 0 && (
          <div className="px-2 py-4 text-center">
            <p className="text-sm text-muted-foreground">
              Mulai chat baru
            </p>
          </div>
        )}
        {conversations.map((conv) => (
          <div
            key={conv.id}
            className={cn(
              "group flex items-center justify-between rounded-md px-2 py-1.5 text-sm hover:bg-accent",
              pathname === `/chat/${conv.id}` && "bg-accent"
            )}
          >
            <Link
              href={`/chat/${conv.id}`}
              className="flex-1 truncate mr-2"
              onClick={onClose}
            >
              <span className="block truncate">{conv.title}</span>
              <span className="text-xs text-muted-foreground">
                {formatRelativeTime(conv.updated_at)}
              </span>
            </Link>
            <button
              onClick={() => onDelete(conv.id)}
              className="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive text-xs px-1"
              title="Delete"
            >
              &times;
            </button>
          </div>
        ))}
      </nav>
      <div className="p-2 border-t border-border">
        <Link
          href="/knowledge"
          className="block px-3 py-2 rounded-md hover:bg-accent text-sm text-muted-foreground"
          onClick={onClose}
        >
          Knowledge Base
        </Link>
        <Link
          href="/reports"
          className="block px-3 py-2 rounded-md hover:bg-accent text-sm text-muted-foreground"
          onClick={onClose}
        >
          Reports
        </Link>
        <Link
          href="/settings"
          className="block px-3 py-2 rounded-md hover:bg-accent text-sm text-muted-foreground"
          onClick={onClose}
        >
          Settings
        </Link>
      </div>
    </>
  );
}

export function ChatSidebar({ isOpen, onClose }: ChatSidebarProps) {
  const pathname = usePathname();
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiJson<Conversation[]>("/api/v1/conversations")
      .then((data) => setConversations(data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const handleDelete = async (id: string) => {
    try {
      await apiJson(`/api/v1/conversations/${id}`, { method: "DELETE" });
      setConversations((prev) => prev.filter((c) => c.id !== id));
    } catch {
      // ignore
    }
  };

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="w-64 border-r border-border flex-col h-full hidden md:flex">
        <SidebarContent
          conversations={conversations}
          loading={loading}
          pathname={pathname}
          onDelete={handleDelete}
        />
      </aside>

      {/* Mobile sidebar overlay */}
      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-40 bg-black/50 md:hidden"
            onClick={onClose}
          />
          <aside className="fixed inset-y-0 left-0 z-40 w-64 bg-background border-r border-border flex flex-col md:hidden">
            <SidebarContent
              conversations={conversations}
              loading={loading}
              pathname={pathname}
              onDelete={handleDelete}
              onClose={onClose}
            />
          </aside>
        </>
      )}
    </>
  );
}
