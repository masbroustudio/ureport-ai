"use client";

import { useEffect, useState, useCallback } from "react";
import { useParams } from "next/navigation";
import { apiJson, apiFetch } from "@/lib/api";
import ReactMarkdown from "react-markdown";

interface OutlineSection {
  id: string;
  title: string;
  instruction: string;
  use_rag?: boolean;
  use_data?: boolean;
  target_words?: number;
}

interface OutlineChapter {
  number: string;
  title: string;
  sections: OutlineSection[];
}

interface Outline {
  chapters: OutlineChapter[];
}

interface Report {
  id: string;
  title: string;
  status: string;
  progress_pct: number;
  template_id: string;
  outline_json: Outline | null;
  error_message: string | null;
  pdf_path: string | null;
  created_at: string;
}

interface Section {
  id: string;
  report_id: string;
  chapter_number: string;
  chapter_title: string;
  section_order: number;
  section_title: string;
  content_markdown: string | null;
  status: string;
  word_count: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function ReportDetailPage() {
  const params = useParams();
  const reportId = params.id as string;

  const [report, setReport] = useState<Report | null>(null);
  const [sections, setSections] = useState<Section[]>([]);
  const [selectedSection, setSelectedSection] = useState<Section | null>(null);
  const [loading, setLoading] = useState(true);
  const [writing, setWriting] = useState(false);
  const [progressPct, setProgressPct] = useState(0);
  const [progressMessage, setProgressMessage] = useState("");
  const [error, setError] = useState("");

  // Outline editor state
  const [editableOutline, setEditableOutline] = useState<Outline | null>(null);
  const [saving, setSaving] = useState(false);

  const fetchReport = useCallback(async () => {
    try {
      const [reportData, sectionsData] = await Promise.all([
        apiJson<Report>(`/api/v1/reports/${reportId}`),
        apiJson<Section[]>(`/api/v1/reports/${reportId}/sections`),
      ]);
      setReport(reportData);
      setSections(sectionsData);
      if (reportData.outline_json) {
        setEditableOutline(reportData.outline_json);
      }
      if (sectionsData.length > 0 && !selectedSection) {
        setSelectedSection(sectionsData[0]);
      }
    } catch {
      setError("Failed to load report");
    } finally {
      setLoading(false);
    }
  }, [reportId, selectedSection]);

  useEffect(() => {
    fetchReport();
  }, [fetchReport]);

  const handleStartWriting = () => {
    if (!report) return;
    setWriting(true);
    setProgressPct(0);
    setProgressMessage("Starting...");

    const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
    const url = `${API_BASE}/api/v1/reports/${reportId}/start`;

    const eventSource = new EventSource(url);

    // Since EventSource doesn't support auth headers, use fetch with SSE parsing
    const startSSE = async () => {
      try {
        const res = await fetch(url, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            ...(token ? { Authorization: `Bearer ${token}` } : {}),
          },
        });

        if (!res.ok || !res.body) {
          setError("Failed to start report generation");
          setWriting(false);
          return;
        }

        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() || "";

          let currentEvent = "";
          for (const line of lines) {
            if (line.startsWith("event: ")) {
              currentEvent = line.slice(7);
            } else if (line.startsWith("data: ")) {
              const data = line.slice(6);
              try {
                const parsed = JSON.parse(data);
                if (currentEvent === "progress") {
                  setProgressPct(parsed.pct);
                  setProgressMessage(`Writing: ${parsed.section} (${parsed.completed}/${parsed.total})`);
                } else if (currentEvent === "render") {
                  setProgressPct(95);
                  setProgressMessage("Rendering PDF...");
                } else if (currentEvent === "done") {
                  setProgressPct(100);
                  setProgressMessage("Done!");
                  setWriting(false);
                  fetchReport();
                } else if (currentEvent === "error") {
                  setError(parsed.error || "Generation failed");
                  setWriting(false);
                  fetchReport();
                }
              } catch {
                // skip unparseable data
              }
            }
          }
        }
        setWriting(false);
        fetchReport();
      } catch {
        setError("Connection error during generation");
        setWriting(false);
      }
    };

    eventSource.close(); // close the unused EventSource
    startSSE();
  };

  const handleRegenerateSection = async () => {
    if (!report || !selectedSection) return;
    try {
      const updated = await apiJson<Section>(
        `/api/v1/reports/${reportId}/sections/${selectedSection.id}/regenerate`,
        { method: "POST" }
      );
      setSections((prev) =>
        prev.map((s) => (s.id === updated.id ? updated : s))
      );
      setSelectedSection(updated);
    } catch {
      setError("Failed to regenerate section");
    }
  };

  const handleSaveOutline = async () => {
    if (!editableOutline) return;
    setSaving(true);
    try {
      const updated = await apiJson<Report>(
        `/api/v1/reports/${reportId}/outline`,
        {
          method: "PUT",
          body: JSON.stringify({ outline_json: editableOutline }),
        }
      );
      setReport(updated);
      // Reload sections since they were recreated
      const newSections = await apiJson<Section[]>(`/api/v1/reports/${reportId}/sections`);
      setSections(newSections);
      if (newSections.length > 0) {
        setSelectedSection(newSections[0]);
      }
    } catch {
      setError("Failed to save outline");
    } finally {
      setSaving(false);
    }
  };

  const updateSectionTitle = (chapterIdx: number, sectionIdx: number, value: string) => {
    if (!editableOutline) return;
    const updated = { ...editableOutline };
    updated.chapters = [...updated.chapters];
    updated.chapters[chapterIdx] = { ...updated.chapters[chapterIdx] };
    updated.chapters[chapterIdx].sections = [...updated.chapters[chapterIdx].sections];
    updated.chapters[chapterIdx].sections[sectionIdx] = {
      ...updated.chapters[chapterIdx].sections[sectionIdx],
      title: value,
    };
    setEditableOutline(updated);
  };

  const updateSectionInstruction = (chapterIdx: number, sectionIdx: number, value: string) => {
    if (!editableOutline) return;
    const updated = { ...editableOutline };
    updated.chapters = [...updated.chapters];
    updated.chapters[chapterIdx] = { ...updated.chapters[chapterIdx] };
    updated.chapters[chapterIdx].sections = [...updated.chapters[chapterIdx].sections];
    updated.chapters[chapterIdx].sections[sectionIdx] = {
      ...updated.chapters[chapterIdx].sections[sectionIdx],
      instruction: value,
    };
    setEditableOutline(updated);
  };

  if (loading) {
    return (
      <div className="p-6">
        <p className="text-sm text-muted-foreground">Loading report...</p>
      </div>
    );
  }

  if (!report) {
    return (
      <div className="p-6">
        <p className="text-sm text-red-600">{error || "Report not found"}</p>
      </div>
    );
  }

  const isEditable = report.status === "created";
  const isDone = report.status === "done";
  const isWriting = report.status === "writing" || report.status === "rendering" || writing;

  return (
    <div className="flex h-full overflow-hidden">
      {/* Left sidebar - outline */}
      <div className="w-64 border-r border-border overflow-y-auto p-4 flex-shrink-0">
        <h2 className="font-semibold text-sm mb-3">Outline</h2>
        {editableOutline && isEditable ? (
          <div className="space-y-3">
            {editableOutline.chapters.map((chapter, ci) => (
              <div key={ci}>
                <p className="text-xs font-semibold text-muted-foreground mb-1">
                  {chapter.number} {chapter.title}
                </p>
                {chapter.sections.map((section, si) => (
                  <div key={si} className="mb-2 pl-2">
                    <input
                      type="text"
                      value={section.title}
                      onChange={(e) => updateSectionTitle(ci, si, e.target.value)}
                      className="w-full text-xs px-1.5 py-1 border border-border rounded bg-background mb-1"
                    />
                    <input
                      type="text"
                      value={section.instruction}
                      onChange={(e) => updateSectionInstruction(ci, si, e.target.value)}
                      placeholder="Instruction..."
                      className="w-full text-xs px-1.5 py-1 border border-border rounded bg-background text-muted-foreground"
                    />
                  </div>
                ))}
              </div>
            ))}
            <button
              onClick={handleSaveOutline}
              disabled={saving}
              className="w-full px-3 py-1.5 bg-primary text-primary-foreground rounded text-xs font-medium hover:opacity-90 disabled:opacity-50"
            >
              {saving ? "Saving..." : "Save Outline"}
            </button>
          </div>
        ) : (
          <div className="space-y-2">
            {report.outline_json?.chapters.map((chapter, ci) => (
              <div key={ci}>
                <p className="text-xs font-semibold text-muted-foreground mb-1">
                  {chapter.number} {chapter.title}
                </p>
                {sections
                  .filter((s) => s.chapter_number === chapter.number)
                  .map((section) => (
                    <button
                      key={section.id}
                      onClick={() => setSelectedSection(section)}
                      className={`block w-full text-left text-xs px-2 py-1 rounded mb-0.5 ${
                        selectedSection?.id === section.id
                          ? "bg-accent font-medium"
                          : "hover:bg-accent/50"
                      }`}
                    >
                      <span className="truncate block">{section.section_title}</span>
                      <span className="text-muted-foreground">
                        {section.status === "done" ? "done" : section.status === "writing" ? "writing..." : ""}
                      </span>
                    </button>
                  ))}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Center - content */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="max-w-3xl mx-auto">
          <h1 className="text-xl font-bold mb-2">{report.title}</h1>

          {error && (
            <p className="text-sm text-red-600 mb-4">{error}</p>
          )}

          {isWriting && (
            <div className="mb-4">
              <div className="w-full bg-gray-200 rounded-full h-2.5 mb-1">
                <div
                  className="bg-yellow-500 h-2.5 rounded-full transition-all"
                  style={{ width: `${progressPct}%` }}
                />
              </div>
              <p className="text-xs text-muted-foreground">{progressMessage}</p>
            </div>
          )}

          {selectedSection?.content_markdown ? (
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown>{selectedSection.content_markdown}</ReactMarkdown>
            </div>
          ) : selectedSection ? (
            <p className="text-sm text-muted-foreground">
              This section has not been written yet.
            </p>
          ) : (
            <p className="text-sm text-muted-foreground">
              Select a section from the outline to view its content.
            </p>
          )}
        </div>
      </div>

      {/* Right panel - actions */}
      <div className="w-48 border-l border-border p-4 flex-shrink-0">
        <h2 className="font-semibold text-sm mb-3">Actions</h2>
        <div className="space-y-2">
          {isEditable && (
            <button
              onClick={handleStartWriting}
              disabled={writing}
              className="w-full px-3 py-2 bg-primary text-primary-foreground rounded text-xs font-medium hover:opacity-90 disabled:opacity-50"
            >
              Start Writing
            </button>
          )}

          {isDone && (
            <button
              onClick={async () => {
                try {
                  const token = typeof window !== "undefined" ? localStorage.getItem("token") : null;
                  const res = await fetch(`${API_BASE}/api/v1/reports/${reportId}/pdf`, {
                    headers: {
                      ...(token ? { Authorization: `Bearer ${token}` } : {}),
                    },
                  });
                  if (!res.ok) {
                    setError("Failed to download file");
                    return;
                  }
                  const blob = await res.blob();
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = `${report.title}.pdf`;
                  a.click();
                  URL.revokeObjectURL(url);
                } catch {
                  setError("Failed to download file");
                }
              }}
              className="block w-full px-3 py-2 bg-green-600 text-white rounded text-xs font-medium text-center hover:opacity-90"
            >
              Download PDF
            </button>
          )}

          {selectedSection && !isEditable && (
            <button
              onClick={handleRegenerateSection}
              className="w-full px-3 py-2 border border-border rounded text-xs font-medium hover:bg-accent"
            >
              Regenerate Section
            </button>
          )}
        </div>

        {report.status === "failed" && report.error_message && (
          <div className="mt-4 p-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
            {report.error_message}
          </div>
        )}
      </div>
    </div>
  );
}
