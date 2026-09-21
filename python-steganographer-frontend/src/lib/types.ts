// TypeScript types matching FastAPI Pydantic models

// Base response types
export interface BaseResponse {
  message: string;
  timestamp: string;
}

// Steganography types
export enum AlgorithmType {
  LSB = "lsb",
  DCT = "dct",
}

// Response types
export interface HealthResponse extends BaseResponse {}

export interface GetAuthEnabledResponse extends BaseResponse {
  auth_enabled: boolean;
}

export interface EncodeResponse extends BaseResponse {
  imageData: string; // Base64 encoded image
}

export interface DecodeResponse extends BaseResponse {
  decodedMessage: string;
}

export interface CapacityResponse extends BaseResponse {
  capacityCharacters: number; // Maximum number of characters that can be encoded
}

// Request types
export interface EncodeRequest {
  imageData: string; // Base64 encoded image
  outputFormat: string; // e.g., "png", "jpeg"
  message: string;
  algorithm: AlgorithmType;
}

export interface DecodeRequest {
  imageData: string; // Base64 encoded image
  algorithm: AlgorithmType;
}

export interface CapacityRequest {
  imageData: string; // Base64 encoded image
  algorithm: AlgorithmType;
}
