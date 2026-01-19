"use client";

import { AlgorithmType } from "@/lib/types";

interface AlgorithmSelectorProps {
  selected: AlgorithmType;
  onChange: (algorithm: AlgorithmType) => void;
}

export default function AlgorithmSelector({
  selected,
  onChange,
}: AlgorithmSelectorProps) {
  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-text-secondary">
        Steganography Algorithm
      </label>
      <div className="flex gap-3">
        <button
          onClick={() => onChange(AlgorithmType.LSB)}
          className={`flex-1 rounded px-4 py-3 text-sm font-medium transition-all ${
            selected === AlgorithmType.LSB
              ? "bg-neon-green text-background shadow-neon"
              : "bg-background-tertiary text-text-muted"
          }`}
        >
          <div className="font-bold">LSB</div>
          <div className="text-xs opacity-80">Least Significant Bit</div>
        </button>
        <button
          onClick={() => onChange(AlgorithmType.DCT)}
          className={`flex-1 rounded px-4 py-3 text-sm font-medium transition-all ${
            selected === AlgorithmType.DCT
              ? "bg-neon-green text-background shadow-neon"
              : "bg-background-tertiary text-text-muted"
          }`}
        >
          <div className="font-bold">DCT</div>
          <div className="text-xs opacity-80">Discrete Cosine Transform</div>
        </button>
      </div>
    </div>
  );
}
