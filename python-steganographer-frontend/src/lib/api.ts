import axios from "axios";
import { useEffect, useState } from "react";

import { getApiKey } from "@/lib/auth";
import type {
  CapacityRequest,
  CapacityResponse,
  DecodeRequest,
  DecodeResponse,
  EncodeRequest,
  EncodeResponse,
  HealthResponse,
  LoginResponse,
} from "@/lib/types";

// Determine the base URL based on environment
const getBaseURL = () => {
  if (typeof window === "undefined") return "";

  // In production static build, API is served from same origin
  if (process.env.NODE_ENV === "production") {
    return window.location.origin;
  }

  // In development, proxy to backend (handled by Next.js rewrites)
  return "";
};

// API client configuration
const api = axios.create({
  baseURL: getBaseURL() + "/api", // This will be proxied in dev, direct in production
  timeout: 60000, // 60 seconds timeout for LLM responses
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include API key
api.interceptors.request.use(
  config => {
    const apiKey = getApiKey();
    if (apiKey) {
      config.headers["X-API-KEY"] = apiKey;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Health status type
export type HealthStatus = "online" | "offline" | "checking";

const extractErrorMessage = (error: unknown): string => {
  if (axios.isAxiosError(error)) {
    if (error.response) {
      const errorData = error.response.data;

      // Check for BaseResponse format with message field
      if (errorData?.message) {
        return errorData.message;
      }

      // Check for detail field (common in FastAPI errors)
      if (errorData?.detail) {
        return typeof errorData.detail === "string"
          ? errorData.detail
          : JSON.stringify(errorData.detail);
      }

      // Fallback to generic server error
      return `Server error: ${error.response.status} ${error.response.statusText}`;
    } else if (error.request) {
      return "No response from server. Please check if the backend is running.";
    } else {
      return `Request failed: ${error.message}`;
    }
  }
  return "An unexpected error occurred";
};

const isSuccessResponse = (data: { code?: number }): boolean => {
  return data.code !== undefined && data.code >= 200 && data.code < 300;
};

// API functions
export const getHealth = async (): Promise<HealthResponse> => {
  try {
    const response = await api.get<HealthResponse>("/health");
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const login = async (apiKey: string): Promise<LoginResponse> => {
  try {
    const response = await api.get<LoginResponse>("/login", {
      headers: {
        "X-API-KEY": apiKey,
      },
    });
    const data = response.data;

    if (!isSuccessResponse(data)) {
      throw new Error(data.message || "Login failed");
    }

    return data;
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const encodeImage = async (
  request: EncodeRequest
): Promise<EncodeResponse> => {
  try {
    // Convert camelCase to snake_case for backend
    const payload = {
      image_data: request.imageData,
      output_format: request.outputFormat,
      message: request.message,
      algorithm: request.algorithm,
    };

    const response = await api.post<{
      code: number;
      message: string;
      timestamp: string;
      image_data: string;
    }>("/image/encode", payload);

    const data = response.data;

    if (!isSuccessResponse(data)) {
      throw new Error(data.message || "Image encoding failed");
    }

    // Convert snake_case response to camelCase
    return {
      code: data.code,
      message: data.message,
      timestamp: data.timestamp,
      imageData: data.image_data,
    };
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const decodeImage = async (
  request: DecodeRequest
): Promise<DecodeResponse> => {
  try {
    // Convert camelCase to snake_case for backend
    const payload = {
      image_data: request.imageData,
      algorithm: request.algorithm,
    };

    const response = await api.post<{
      code: number;
      message: string;
      timestamp: string;
      decoded_message: string;
    }>("/image/decode", payload);

    const data = response.data;

    if (!isSuccessResponse(data)) {
      throw new Error(data.message || "Image decoding failed");
    }

    // Convert snake_case response to camelCase
    return {
      code: data.code,
      message: data.message,
      timestamp: data.timestamp,
      decodedMessage: data.decoded_message,
    };
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

export const getImageCapacity = async (
  request: CapacityRequest
): Promise<CapacityResponse> => {
  try {
    // Convert camelCase to snake_case for backend
    const payload = {
      image_data: request.imageData,
      algorithm: request.algorithm,
    };

    const response = await api.post<{
      code: number;
      message: string;
      timestamp: string;
      capacity_characters: number;
    }>("/image/capacity", payload);

    const data = response.data;

    if (!isSuccessResponse(data)) {
      throw new Error(data.message || "Capacity check failed");
    }

    // Convert snake_case response to camelCase
    return {
      code: data.code,
      message: data.message,
      timestamp: data.timestamp,
      capacityCharacters: data.capacity_characters,
    };
  } catch (error) {
    throw new Error(extractErrorMessage(error));
  }
};

// Health status hook
export function useHealthStatus(): HealthStatus {
  const [status, setStatus] = useState<HealthStatus>("checking");

  useEffect(() => {
    let isMounted = true;

    const checkHealth = async () => {
      try {
        const data = await getHealth();
        if (isMounted) {
          if (data.status === "healthy") {
            setStatus("online");
          } else {
            setStatus("offline");
          }
        }
      } catch {
        if (isMounted) {
          setStatus("offline");
        }
      }
    };

    checkHealth();
    const interval = setInterval(checkHealth, 30000); // every 30s
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return status;
}

export default api;
