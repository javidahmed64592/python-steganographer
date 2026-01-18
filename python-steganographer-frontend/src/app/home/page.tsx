"use client";

import Image from "next/image";
import { useState } from "react";

import DecodePanel from "@/components/DecodePanel";
import EncodePanel from "@/components/EncodePanel";
import ImagePanel from "@/components/ImagePanel";

type Mode = "encode" | "decode";

export default function Home() {
  const [mode, setMode] = useState<Mode>("encode");
  const [originalImageData, setOriginalImageData] = useState<string | null>(
    null
  );
  const [originalImageFormat, setOriginalImageFormat] = useState<string>("png");
  const [originalImageFilename, setOriginalImageFilename] =
    useState<string>("image");
  const [encodedImageData, setEncodedImageData] = useState<string | null>(null);
  const [encodedImageFormat, setEncodedImageFormat] = useState<string>("png");

  const handleImageUpload = (
    base64: string,
    format: string,
    filename: string
  ) => {
    setOriginalImageData(base64);
    setOriginalImageFormat(format);
    setOriginalImageFilename(filename);
    setEncodedImageData(null); // Clear encoded image when new image is uploaded
  };

  const handleClearImage = () => {
    setOriginalImageData(null);
    setEncodedImageData(null);
  };

  const handleEncodedImage = (base64: string, format: string) => {
    setEncodedImageData(base64);
    setEncodedImageFormat(format);
  };

  const handleDownloadEncodedImage = () => {
    if (!encodedImageData) return;

    const link = document.createElement("a");
    link.href = `data:image/${encodedImageFormat};base64,${encodedImageData}`;
    link.download = `encoded_${originalImageFilename}.${encodedImageFormat}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="bg-background py-4 px-4">
      <div className="mx-auto max-w-6xl">
        {/* Header */}
        <div className="mb-4 text-center">
          <h1 className="mb-1 text-3xl font-bold text-neon-green">
            Steganography Lab
          </h1>
          <p className="text-sm text-text-muted">
            Hide secret messages in images using advanced steganography
            algorithms
          </p>
        </div>

        {/* Mode Toggle */}
        <div className="mb-4 flex justify-center">
          <div className="inline-flex rounded-lg border border-terminal-border bg-terminal-bg p-1">
            <button
              onClick={() => setMode("encode")}
              className={`rounded px-6 py-2 text-sm font-medium transition-all ${
                mode === "encode"
                  ? "bg-neon-green text-background shadow-neon"
                  : "text-text-muted hover:text-text-secondary"
              }`}
            >
              Encode
            </button>
            <button
              onClick={() => setMode("decode")}
              className={`rounded px-6 py-2 text-sm font-medium transition-all ${
                mode === "decode"
                  ? "bg-neon-green text-background shadow-neon"
                  : "text-text-muted hover:text-text-secondary"
              }`}
            >
              Decode
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid gap-4 md:grid-cols-2">
          {/* Left Column - Image Panel */}
          <div className="space-y-4">
            <ImagePanel
              imageData={originalImageData}
              imageFormat={originalImageFormat}
              onImageUpload={handleImageUpload}
              onClear={handleClearImage}
            />

            {/* Encoded Image Display (only in encode mode) */}
            {mode === "encode" && encodedImageData && (
              <div className="rounded-lg border border-terminal-border bg-terminal-bg p-4">
                <h2 className="mb-3 text-base font-semibold text-neon-green">
                  Encoded Image
                </h2>
                <div className="space-y-3">
                  <div className="relative rounded border border-border bg-background-secondary p-2">
                    <Image
                      src={`data:image/${encodedImageFormat};base64,${encodedImageData}`}
                      alt="Encoded result"
                      width={800}
                      height={600}
                      className="mx-auto max-h-64 rounded object-contain w-full"
                      unoptimized
                    />
                  </div>
                  <button
                    onClick={handleDownloadEncodedImage}
                    className="w-full rounded bg-neon-green px-4 py-2 text-sm font-semibold text-background transition-all hover:opacity-90"
                  >
                    Download Encoded Image
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Operation Panel */}
          <div>
            {originalImageData ? (
              <div className="rounded-lg border border-terminal-border bg-terminal-bg p-4">
                <h2 className="mb-3 text-base font-semibold text-neon-green">
                  {mode === "encode" ? "Encode Message" : "Decode Message"}
                </h2>
                {mode === "encode" ? (
                  <EncodePanel
                    imageData={originalImageData}
                    imageFormat={originalImageFormat}
                    onEncodedImage={handleEncodedImage}
                  />
                ) : (
                  <DecodePanel imageData={originalImageData} />
                )}
              </div>
            ) : (
              <div className="flex h-full items-center justify-center rounded-lg border border-terminal-border bg-terminal-bg p-8">
                <div className="text-center">
                  <svg
                    className="mx-auto mb-3 h-12 w-12 text-text-muted"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  <p className="text-sm text-text-muted">
                    Upload an image to get started
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
