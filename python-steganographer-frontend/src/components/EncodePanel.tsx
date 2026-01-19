"use client";

import { useState, useEffect } from "react";

import AlgorithmSelector from "@/components/AlgorithmSelector";
import { encodeImage, getImageCapacity } from "@/lib/api";
import { AlgorithmType } from "@/lib/types";

interface EncodePanelProps {
  imageData: string;
  imageFormat: string;
  onEncodedImage: (base64: string, format: string) => void;
}

export default function EncodePanel({
  imageData,
  imageFormat,
  onEncodedImage,
}: EncodePanelProps) {
  const [algorithm, setAlgorithm] = useState<AlgorithmType>(AlgorithmType.LSB);
  const [message, setMessage] = useState("");
  const [capacity, setCapacity] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadingCapacity, setLoadingCapacity] = useState(false);

  // Fetch capacity when algorithm or image changes
  useEffect(() => {
    const fetchCapacity = async () => {
      setLoadingCapacity(true);
      setError(null);
      try {
        const response = await getImageCapacity({
          imageData,
          algorithm,
        });
        setCapacity(response.capacityCharacters);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to get capacity");
        setCapacity(null);
      } finally {
        setLoadingCapacity(false);
      }
    };

    fetchCapacity();
  }, [imageData, algorithm]);

  const handleEncode = async () => {
    if (!message.trim()) {
      setError("Please enter a message to encode");
      return;
    }

    if (capacity !== null && message.length > capacity) {
      setError(`Message is too long! Maximum ${capacity} characters allowed.`);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await encodeImage({
        imageData,
        outputFormat: imageFormat,
        message,
        algorithm,
      });

      onEncodedImage(response.imageData, imageFormat);
      setMessage("");
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to encode image");
    } finally {
      setLoading(false);
    }
  };

  const characterCount = message.length;
  const isOverCapacity = capacity !== null && characterCount > capacity;

  return (
    <div className="space-y-4">
      <AlgorithmSelector selected={algorithm} onChange={setAlgorithm} />

      {/* Capacity Display */}
      <div className="rounded border border-terminal-border bg-terminal-bg p-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-text-secondary">Image Capacity:</span>
          {loadingCapacity ? (
            <span className="text-sm text-text-muted">Calculating...</span>
          ) : capacity !== null ? (
            <span className="font-mono text-sm font-semibold text-neon-blue">
              {capacity} characters
            </span>
          ) : (
            <span className="text-sm text-neon-red">Unknown</span>
          )}
        </div>
      </div>

      {/* Message Input */}
      <div className="space-y-2">
        <label className="text-sm font-medium text-text-secondary">
          Secret Message
        </label>
        <textarea
          value={message}
          onChange={e => setMessage(e.target.value)}
          placeholder="Enter your secret message here..."
          className={`h-32 w-full rounded border bg-terminal-bg p-3 font-mono text-sm text-text-secondary focus:outline-none focus:ring-2 ${
            isOverCapacity
              ? "border-neon-red focus:ring-neon-red"
              : "border-terminal-border focus:ring-neon-green"
          }`}
        />
        <div className="flex items-center justify-between text-xs">
          <span
            className={`font-mono ${
              isOverCapacity ? "text-neon-red" : "text-text-muted"
            }`}
          >
            {characterCount} / {capacity ?? "?"} characters
          </span>
          {isOverCapacity && (
            <span className="text-neon-red">Message exceeds capacity!</span>
          )}
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="rounded border border-neon-red bg-neon-red/10 p-3 text-sm text-neon-red">
          {error}
        </div>
      )}

      {/* Encode Button */}
      <button
        onClick={handleEncode}
        disabled={loading || !message.trim() || isOverCapacity}
        className="w-full rounded bg-neon-green px-6 py-3 font-semibold text-background transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Encoding..." : "Encode Message"}
      </button>
    </div>
  );
}
