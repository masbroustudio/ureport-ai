"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiJson } from "@/lib/api";

interface Report {
  id: string;
  title: string;
  status: string;
  progress_pct: number;
  template_id: string;
  created_at: string;
  updated_at: string;
}

const STATUS_COLORS: Record<string, string> = {
  created: "bg-blue-100 text-blue-800",
  planning: "bg-blue-100 text-blue-800",
  writing: "bg-yellow-100 text-yellow-800",
  rendering: "bg-yellow-100 text-yellow-800",
  done: "bg-green-100 text-green-800",
  failed: "bg-red-100 text-red-800",
};

function StatusBadge({ status }: { status: string }) {
  const color = STATUS_COLORS[status] || "bg-gray-100 text-gray-800";
  return (
    <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>
      {status}
    </span>
  );
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString("id-ID", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiJson<Report[]>("/api/v1/reports/")
      .then(setReports)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-5xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">Reports</h1>
        <Link
          href="/reports/new"
          className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:opacity-90"
        >
          New Report
        </Link>
      </div>

      {loading && (
        <p className="text-sm text-muted-foreground">Loading reports...</p>
      )}

      {!loading && reports.length === 0 && (
        <div className="text-center py-12">
          <p className="text-muted-foreground mb-4">No reports yet. Create your first report to get started.</p>
          <Link
            href="/reports/new"
            className="px-4 py-2 bg-primary text-primary-foreground rounded-md text-sm font-medium hover:opacity-90"
          >
            New Report
          </Link>
        </div>
      )}

      {reports.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {reports.map((report) => (
            <Link
              key={report.id}
              href={`/reports/${report.id}`}
              className="block border border-border rounded-lg p-4 hover:bg-accent transition-colors"
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-medium text-sm truncate flex-1 mr-2">
                  {report.title}
                </h3>
                <StatusBadge status={report.status} />
              </div>
              <p className="text-xs text-muted-foreground mb-2">
                {report.template_id === "business_report_v1"
                  ? "Laporan Bisnis"
                  : report.template_id}
              </p>
              {(report.status === "writing" || report.status === "rendering") && (
                <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
                  <div
                    className="bg-yellow-500 h-2 rounded-full transition-all"
                    style={{ width: `${report.progress_pct}%` }}
                  />
                </div>
              )}
              <p className="text-xs text-muted-foreground">
                {formatDate(report.created_at)}
              </p>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
