"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { ChatSidebar } from "@/components/chat/ChatSidebar";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) {
      const token = localStorage.getItem("token");
      if (!token) {
        router.replace("/signin");
      }
    }
  }, [loading, user, router]);

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <p className="text-muted-foreground">Loading...</p>
      </div>
    );
  }

  if (!user && typeof window !== "undefined" && !localStorage.getItem("token")) {
    return null;
  }

  return (
    <div className="flex h-screen">
      <ChatSidebar />
      <main className="flex-1 overflow-auto">{children}</main>
    </div>
  );
}
