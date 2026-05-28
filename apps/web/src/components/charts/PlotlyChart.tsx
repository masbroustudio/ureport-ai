"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";

const Plot = dynamic(() => import("react-plotly.js"), {
  ssr: false,
  loading: () => (
    <div className="min-h-[300px] w-full flex items-center justify-center text-muted-foreground">
      Loading chart...
    </div>
  ),
});

interface PlotlyChartProps {
  spec: {
    data: unknown[];
    layout?: Record<string, unknown>;
  };
}

export function PlotlyChart({ spec }: PlotlyChartProps) {
  const [isDark, setIsDark] = useState(false);

  useEffect(() => {
    setIsDark(document.documentElement.classList.contains("dark"));
  }, []);

  const layout = {
    autosize: true,
    paper_bgcolor: "transparent",
    plot_bgcolor: "transparent",
    font: {
      family: "inherit",
      ...(isDark ? { color: "#e2e8f0" } : {}),
    },
    ...(isDark
      ? {
          xaxis: { color: "#94a3b8", gridcolor: "#334155" },
          yaxis: { color: "#94a3b8", gridcolor: "#334155" },
        }
      : {}),
    ...(spec.layout || {}),
  };

  const config = {
    responsive: true,
    displayModeBar: false,
  };

  return (
    <div className="min-h-[300px] w-full">
      <Plot
        data={spec.data as Array<Record<string, unknown>>}
        layout={layout}
        config={config}
        style={{ width: "100%", height: "100%" }}
        useResizeHandler={true}
      />
    </div>
  );
}
