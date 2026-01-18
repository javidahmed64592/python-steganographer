"use client";

import { useState } from "react";

import AlgorithmSelector from "@/components/AlgorithmSelector";
import { decodeImage } from "@/lib/api";
import { AlgorithmType } from "@/lib/types";

interface DecodePanelProps {
  imageData: string;
}

export default function DecodePanel({ imageData }: DecodePanelProps) {
  const [algorithm, setAlgorithm] = useState<AlgorithmType>(AlgorithmType.LSB);
  const [decodedMessage, setDecodedMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleDecode = async () => {
    setLoading(true);
    setError(null);
    setDecodedMessage(null);

    try {
      const response = await decodeImage({
        imageData,
        algorithm,
      });

      setDecodedMessage(response.decodedMessage);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to decode image");
      setDecodedMessage(null);
    } finally {
      setLoading(false);
    }
  };

  const handleCopyMessage = () => {
    if (decodedMessage) {
      navigator.clipboard.writeText(decodedMessage);
    }
  };

  return (
    <div className="space-y-4">
      <AlgorithmSelector selected={algorithm} onChange={setAlgorithm} />

      {/* Decode Button */}
      <button
        onClick={handleDecode}
        disabled={loading}
        className="w-full rounded bg-neon-green px-6 py-3 font-semibold text-background transition-all hover:opacity-90 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Decoding..." : "Decode Message"}
      </button>

      {/* Error Message */}
      {error && (
        <div className="rounded border border-neon-red bg-neon-red/10 p-3 text-sm text-neon-red">
          {error}
        </div>
      )}

      {/* Decoded Message Display */}
      {decodedMessage !== null && (
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <label className="text-sm font-medium text-text-secondary">
              Decoded Message
            </label>
            <button
              onClick={handleCopyMessage}
              className="text-xs text-neon-blue transition-colors hover:text-neon-green"
            >
              Copy to Clipboard
            </button>
          </div>
          <div className="relative rounded border border-terminal-border bg-terminal-bg p-4">
            {decodedMessage ? (
              <p className="whitespace-pre-wrap font-mono text-sm text-neon-green">
                {decodedMessage}
              </p>
            ) : (
              <p className="font-mono text-sm italic text-text-muted">
                No message found in image
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
