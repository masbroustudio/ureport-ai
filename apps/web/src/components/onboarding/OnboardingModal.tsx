"use client";

import { useState, useCallback } from "react";
import { Button } from "@/components/ui/button";
import { API_BASE } from "@/lib/api";

const AVAILABLE_MODELS = [
  { id: "groq/llama-3.3-70b-versatile", label: "Llama 3.3 70B (Groq)" },
  { id: "cerebras/llama-3.3-70b", label: "Llama 3.3 70B (Cerebras)" },
  { id: "gemini/gemini-2.0-flash", label: "Gemini 2.0 Flash" },
  { id: "openai/sumopod-default", label: "Sumopod Pro" },
];

interface OnboardingModalProps {
  onComplete: () => void;
}

export function OnboardingModal({ onComplete }: OnboardingModalProps) {
  const [step, setStep] = useState(0);
  const [selectedModel, setSelectedModel] = useState(AVAILABLE_MODELS[0].id);
  const [uploading, setUploading] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<string | null>(null);

  const handleFinish = useCallback(() => {
    localStorage.setItem("onboarding_done", "true");
    localStorage.setItem("default_model", selectedModel);
    onComplete();
  }, [selectedModel, onComplete]);

  const handleFileUpload = useCallback(
    async (file: File) => {
      setUploading(true);
      try {
        const token = localStorage.getItem("token");
        const formData = new FormData();
        formData.append("file", file);

        const res = await fetch(`${API_BASE}/api/v1/files`, {
          method: "POST",
          headers: token ? { Authorization: `Bearer ${token}` } : {},
          body: formData,
        });

        if (res.ok) {
          setUploadedFile(file.name);
        }
      } catch {
        // Upload failed silently
      } finally {
        setUploading(false);
      }
    },
    []
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      const file = e.dataTransfer.files[0];
      if (file) handleFileUpload(file);
    },
    [handleFileUpload]
  );

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const nextStep = () => {
    if (step === 0) {
      localStorage.setItem("default_model", selectedModel);
    }
    if (step < 2) {
      setStep(step + 1);
    } else {
      handleFinish();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      <div className="absolute inset-0 bg-black/50" />
      <div className="relative bg-background border border-border rounded-lg shadow-xl w-full max-w-md mx-4 p-6">
        {/* Step indicators */}
        <div className="flex justify-center gap-2 mb-6">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={`w-2.5 h-2.5 rounded-full transition-colors ${
                i === step ? "bg-primary" : "bg-muted"
              }`}
            />
          ))}
        </div>

        {/* Step 1: Welcome + model selection */}
        {step === 0 && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-center">
              Selamat datang di uReport AI!
            </h2>
            <p className="text-sm text-muted-foreground text-center">
              Platform AI Assistant untuk analisis data dan pembuatan laporan.
              Pilih model AI default Anda untuk memulai.
            </p>
            <div>
              <label className="block text-sm font-medium mb-1">
                Model AI Default
              </label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="w-full px-3 py-2 border border-border rounded-md bg-background text-foreground text-sm"
              >
                {AVAILABLE_MODELS.map((m) => (
                  <option key={m.id} value={m.id}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        )}

        {/* Step 2: Upload file */}
        {step === 1 && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-center">
              Upload file pertama Anda
            </h2>
            <p className="text-sm text-muted-foreground text-center">
              Drag & drop file CSV atau Excel untuk mulai menganalisis data.
            </p>
            <div
              onDrop={handleDrop}
              onDragOver={handleDragOver}
              className="border-2 border-dashed border-border rounded-lg p-8 text-center hover:border-primary/50 transition-colors"
            >
              {uploading ? (
                <p className="text-sm text-muted-foreground animate-pulse">
                  Mengupload...
                </p>
              ) : uploadedFile ? (
                <p className="text-sm text-green-600">
                  Berhasil upload: {uploadedFile}
                </p>
              ) : (
                <>
                  <div className="text-3xl mb-2">📄</div>
                  <p className="text-sm text-muted-foreground">
                    Drag & drop file di sini
                  </p>
                  <p className="text-xs text-muted-foreground mt-1">
                    CSV, XLSX, XLS
                  </p>
                </>
              )}
            </div>
          </div>
        )}

        {/* Step 3: Try a sample prompt */}
        {step === 2 && (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-center">
              Coba prompt contoh
            </h2>
            <p className="text-sm text-muted-foreground text-center">
              Mulai dengan prompt contoh atau langsung buat chat baru.
            </p>
            <div className="border border-border rounded-md p-3 bg-muted/30">
              <p className="text-sm">
                &ldquo;Analisa data penjualan Q4 2024&rdquo;
              </p>
            </div>
          </div>
        )}

        {/* Navigation buttons */}
        <div className="flex justify-between mt-6">
          {step < 2 ? (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={nextStep}
              >
                Lewati
              </Button>
              <Button size="sm" onClick={nextStep}>
                Lanjut
              </Button>
            </>
          ) : (
            <>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleFinish}
              >
                Lewati
              </Button>
              <Button size="sm" onClick={handleFinish}>
                Mulai Chat
              </Button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
