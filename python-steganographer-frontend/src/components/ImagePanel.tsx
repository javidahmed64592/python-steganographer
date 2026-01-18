"use client";

import Image from "next/image";
import { useRef } from "react";

interface ImagePanelProps {
  imageData: string | null;
  imageFormat: string;
  onImageUpload: (base64: string, format: string, filename: string) => void;
  onClear: () => void;
}

export default function ImagePanel({
  imageData,
  imageFormat,
  onImageUpload,
  onClear,
}: ImagePanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = async (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file = event.target.files?.[0];
    if (!file) return;

    // Check if it's an image
    if (!file.type.startsWith("image/")) {
      alert("Please upload an image file");
      return;
    }

    // Read file as base64
    const reader = new FileReader();
    reader.onload = e => {
      const result = e.target?.result as string;
      // Extract base64 data without the data:image/xxx;base64, prefix
      const base64 = result.split(",")[1];
      if (!base64) {
        alert("Failed to process image data");
        return;
      }
      // Extract format from file type (e.g., "image/png" -> "png", "image/jpeg" -> "jpg")
      let format = (file.type.split("/")[1] || "png").toLowerCase();
      // Normalize jpeg to jpg
      if (format === "jpeg") {
        format = "jpg";
      }
      // Get original filename without extension
      const filename = file.name.replace(/\.[^/.]+$/, "");
      onImageUpload(base64, format, filename);
    };
    reader.readAsDataURL(file);
  };

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleClear = () => {
    onClear();
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  return (
    <div className="w-full rounded-lg border border-terminal-border bg-terminal-bg p-6">
      <h2 className="mb-4 text-lg font-semibold text-neon-green">
        Image Upload
      </h2>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        className="hidden"
      />

      {!imageData ? (
        <div
          onClick={handleClick}
          className="flex h-64 cursor-pointer flex-col items-center justify-center rounded border-2 border-dashed border-border-accent bg-background-secondary transition-colors hover:bg-background-tertiary"
        >
          <svg
            className="mb-3 h-12 w-12 text-text-muted"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>
          <p className="mb-2 text-sm text-text-secondary">
            <span className="font-semibold text-neon-green">
              Click to upload
            </span>{" "}
            or drag and drop
          </p>
          <p className="text-xs text-text-muted">PNG, JPG, JPEG, or GIF</p>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="relative rounded border border-border bg-background-secondary p-2">
            <Image
              src={`data:image/${imageFormat};base64,${imageData}`}
              alt="Uploaded preview"
              className="mx-auto w-full max-h-64 rounded object-contain"
              width={800}
              height={256}
              unoptimized
            />
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleClick}
              className="flex-1 rounded bg-background-tertiary px-4 py-2 text-sm text-text-secondary transition-colors hover:bg-border hover:text-neon-green"
            >
              Change Image
            </button>
            <button
              onClick={handleClear}
              className="flex-1 rounded bg-background-tertiary px-4 py-2 text-sm text-text-secondary transition-colors hover:bg-border hover:text-neon-red"
            >
              Clear
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
