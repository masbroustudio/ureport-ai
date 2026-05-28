"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { ChatSidebar } from "@/components/chat/ChatSidebar";
import { OnboardingModal } from "@/components/onboarding/OnboardingModal";
import { OfflineBanner } from "@/components/ui/OfflineBanner";

export default function AppLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { user, loading } = useAuth();
  const router = useRouter();
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  useEffect(() => {
    if (!loading && !user) {
      const token = localStorage.getItem("token");
      if (!token) {
        router.replace("/signin");
      }
    }
  }, [loading, user, router]);

  useEffect(() => {
    if (user && !localStorage.getItem("onboarding_done")) {
      setShowOnboarding(true);
    }
  }, [user]);

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
      <OfflineBanner />
      {showOnboarding && (
        <OnboardingModal onComplete={() => setShowOnboarding(false)} />
      )}
      <ChatSidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Mobile top bar */}
        <div className="md:hidden flex items-center border-b border-border px-4 py-2">
          <button
            onClick={() => setSidebarOpen(true)}
            className="p-1 text-muted-foreground hover:text-foreground"
            aria-label="Open sidebar"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 6.75h16.5M3.75 12h16.5m-16.5 5.25h16.5" />
            </svg>
          </button>
          <span className="ml-3 font-semibold text-sm">uReport AI</span>
        </div>
        <main className="flex-1 overflow-auto">{children}</main>
      </div>
    </div>
  );
}
