import React, { useState, useRef } from 'react';
import { Upload, Trash2, ArrowLeft, AlertCircle, Terminal } from 'lucide-react';
import type { Observation } from '../types/diagnostic';

interface ScreenshotUploadStepProps {
  screenshotBase64: string | null;
  onScreenshotChange: (base64: string | null) => void;
  onParseScreenshot: (base64: string) => Promise<void>;
  screenshotObservations: Observation[];
  isLoading: boolean;
  error: string | null;
  onBack: () => void;
  onRunDiagnosis: () => void;
}

export const ScreenshotUploadStep: React.FC<ScreenshotUploadStepProps> = ({
  screenshotBase64,
  onScreenshotChange,
  isLoading,
  error,
  onBack,
  onRunDiagnosis
}) => {
  const [fileName, setFileName] = useState<string | null>(null);
  const [fileSize, setFileSize] = useState<number | null>(null);
  const [localError, setLocalError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (file: File) => {
    setLocalError(null);

    // Validate size <= 5MB
    if (file.size > 5 * 1024 * 1024) {
      setLocalError('File size exceeds maximum limit of 5 MB.');
      return;
    }

    // Validate type
    const allowed = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp'];
    if (!allowed.includes(file.type)) {
      setLocalError('Invalid format. Please upload a PNG, JPEG, or WEBP image.');
      return;
    }

    setFileName(file.name);
    setFileSize(file.size);

    const reader = new FileReader();
    reader.onloadend = () => {
      const base64Str = reader.result as string;
      onScreenshotChange(base64Str);
    };
    reader.readAsDataURL(file);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileChange(e.dataTransfer.files[0]);
    }
  };

  const handleRemove = () => {
    onScreenshotChange(null);
    setFileName(null);
    setFileSize(null);
    setLocalError(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-6 shadow-sm max-w-3xl mx-auto transition-colors">
      {/* Header */}
      <div className="flex items-center gap-3 mb-5 pb-4 border-b border-slate-100 dark:border-zinc-800">
        <div className="p-2 rounded-lg bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 border border-slate-200 dark:border-zinc-700">
          <Terminal className="w-5 h-5" />
        </div>
        <div>
          <h2 className="text-base font-semibold text-slate-900 dark:text-zinc-100">
            Task Manager Screenshot (Optional)
          </h2>
          <p className="text-xs text-slate-500 dark:text-zinc-400">
            Upload a Windows Task Manager screenshot for automated resource analysis.
          </p>
        </div>
      </div>

      {/* Upload Drop Zone / Preview */}
      {!screenshotBase64 ? (
        <div
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className="border-2 border-dashed border-slate-300 dark:border-zinc-800 hover:border-indigo-500/50 bg-slate-50/70 dark:bg-zinc-950/60 rounded-xl p-8 text-center cursor-pointer transition-all group mb-6"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/png,image/jpeg,image/webp"
            className="hidden"
            onChange={(e) => e.target.files?.[0] && handleFileChange(e.target.files[0])}
          />
          <div className="w-10 h-10 rounded-full bg-slate-100 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 flex items-center justify-center mx-auto mb-3 group-hover:scale-105 transition-all">
            <Upload className="w-5 h-5 text-slate-500 dark:text-zinc-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400" />
          </div>
          <p className="text-sm font-medium text-slate-800 dark:text-zinc-200 mb-1">
            Click to upload or drag & drop Task Manager screenshot
          </p>
          <p className="text-xs text-slate-500 dark:text-zinc-500">Supports PNG, JPEG, WEBP (Max 5 MB)</p>
        </div>
      ) : (
        <div className="mb-6 p-4 rounded-lg bg-slate-50 dark:bg-zinc-950 border border-slate-200 dark:border-zinc-800 flex flex-col sm:flex-row items-center gap-4">
          <img
            src={screenshotBase64}
            alt="Task Manager Preview"
            className="w-32 h-24 object-cover rounded-md border border-slate-200 dark:border-zinc-800 shadow-sm"
          />
          <div className="flex-1 text-center sm:text-left">
            <p className="text-xs font-semibold text-slate-900 dark:text-zinc-100 truncate max-w-[240px]">
              {fileName || 'Task_Manager_Screenshot.png'}
            </p>
            {fileSize && (
              <p className="text-[11px] text-slate-500 dark:text-zinc-500 font-mono mt-0.5">
                {(fileSize / 1024).toFixed(1)} KB
              </p>
            )}
            <span className="inline-block mt-2 px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-50 dark:bg-zinc-800 text-indigo-700 dark:text-indigo-300 border border-indigo-200 dark:border-zinc-700">
              Attached to session payload
            </span>
          </div>

          <button
            onClick={handleRemove}
            className="px-3 py-1.5 rounded-md bg-slate-200/80 dark:bg-zinc-800 hover:bg-rose-500/10 text-slate-700 dark:text-zinc-300 hover:text-rose-600 dark:hover:text-rose-400 text-xs font-medium flex items-center gap-1.5 transition-all border border-slate-300 dark:border-zinc-700"
          >
            <Trash2 className="w-3.5 h-3.5" />
            Remove
          </button>
        </div>
      )}

      {/* Error Alert */}
      {(localError || error) && (
        <div className="mb-4 p-3.5 rounded-lg bg-rose-50 dark:bg-rose-950/40 border border-rose-200 dark:border-rose-900/60 flex items-start gap-2.5 text-xs text-rose-800 dark:text-rose-300">
          <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-rose-600 dark:text-rose-400" />
          <div>
            <p className="font-semibold">Screenshot Processing Error</p>
            <p className="mt-0.5 text-rose-700/90 dark:text-rose-300/90">{localError || error}</p>
          </div>
        </div>
      )}

      {/* Navigation */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-zinc-800">
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-md bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 text-xs font-medium flex items-center gap-2 transition-all border border-slate-200 dark:border-zinc-700"
        >
          <ArrowLeft className="w-4 h-4" />
          Back: Questions
        </button>

        <button
          onClick={onRunDiagnosis}
          disabled={isLoading}
          className="px-6 py-2.5 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-sm flex items-center gap-2 transition-all disabled:opacity-60"
        >
          {isLoading ? (
            <>
              <div className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Evaluating Expert Rules...
            </>
          ) : (
            <>
              Run Expert Diagnosis Engine
            </>
          )}
        </button>
      </div>
    </div>
  );
};
