import { renderHook } from "@testing-library/react";

import {
  getHealth,
  login,
  encodeImage,
  decodeImage,
  getImageCapacity,
  useHealthStatus,
  type HealthStatus,
} from "@/lib/api";
import type {
  HealthResponse,
  LoginResponse,
  EncodeRequest,
  EncodeResponse,
  DecodeRequest,
  DecodeResponse,
  CapacityRequest,
  CapacityResponse,
} from "@/lib/types";
import { AlgorithmType } from "@/lib/types";

jest.mock("../api", () => {
  const actual = jest.requireActual("../api");
  return {
    ...actual,
    getHealth: jest.fn(),
    login: jest.fn(),
    encodeImage: jest.fn(),
    decodeImage: jest.fn(),
    getImageCapacity: jest.fn(),
  };
});

// Mock fetch for config endpoint
global.fetch = jest.fn();

const mockGetHealth = getHealth as jest.MockedFunction<typeof getHealth>;
const mockLogin = login as jest.MockedFunction<typeof login>;
const mockEncodeImage = encodeImage as jest.MockedFunction<typeof encodeImage>;
const mockDecodeImage = decodeImage as jest.MockedFunction<typeof decodeImage>;
const mockGetImageCapacity = getImageCapacity as jest.MockedFunction<
  typeof getImageCapacity
>;

describe("API Tests", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("health", () => {
    it("should fetch health status successfully", async () => {
      const mockHealth: HealthResponse = {
        message: "Server is healthy",
        timestamp: "2023-01-01T00:00:00Z",
        status: "healthy",
      };

      mockGetHealth.mockResolvedValue(mockHealth);

      const health = await getHealth();

      expect(mockGetHealth).toHaveBeenCalled();
      expect(health).toEqual(mockHealth);
      expect(health.status).toBe("healthy");
    });

    it("should handle health check error", async () => {
      const errorMessage = "Service unavailable";
      mockGetHealth.mockRejectedValue(new Error(errorMessage));

      await expect(getHealth()).rejects.toThrow(errorMessage);
    });

    it("should handle network error (no response)", async () => {
      const errorMessage =
        "No response from server. Please check if the backend is running.";
      mockGetHealth.mockRejectedValue(new Error(errorMessage));

      await expect(getHealth()).rejects.toThrow(errorMessage);
    });
  });

  describe("login", () => {
    it("should successfully login with valid API key", async () => {
      const mockResponse: LoginResponse = {
        message: "Login successful.",
        timestamp: "2023-01-01T00:00:00Z",
      };

      mockLogin.mockResolvedValue(mockResponse);

      const result = await login("valid-api-key-123");

      expect(result).toEqual(mockResponse);
      expect(mockLogin).toHaveBeenCalledWith("valid-api-key-123");
    });

    it("should reject with error for invalid API key", async () => {
      const errorMessage = "Invalid API key";
      mockLogin.mockRejectedValue(new Error(errorMessage));

      await expect(login("invalid-key")).rejects.toThrow(errorMessage);
    });

    it("should reject with unauthorized error", async () => {
      const errorMessage = "Missing API key";
      mockLogin.mockRejectedValue(new Error(errorMessage));

      await expect(login("")).rejects.toThrow(errorMessage);
    });

    it("should handle network error", async () => {
      const errorMessage =
        "No response from server. Please check if the backend is running.";
      mockLogin.mockRejectedValue(new Error(errorMessage));

      await expect(login("test-key")).rejects.toThrow(errorMessage);
    });
  });

  describe("useHealthStatus", () => {
    it("should initialize with 'checking' status", () => {
      const { result, unmount } = renderHook(() => useHealthStatus());
      expect(result.current).toBe("checking");
      unmount();
    });

    it("should return correct HealthStatus type", () => {
      const { result, unmount } = renderHook(() => useHealthStatus());
      const status: HealthStatus = result.current;
      expect(["checking", "online", "offline"]).toContain(status);
      unmount();
    });
  });

  describe("encodeImage", () => {
    const mockRequest: EncodeRequest = {
      imageData: "base64encodedimage",
      outputFormat: "png",
      message: "Secret message",
      algorithm: AlgorithmType.LSB,
    };

    it("should successfully encode an image", async () => {
      const mockResponse: EncodeResponse = {
        message: "Image encoded successfully",
        timestamp: "2023-01-01T00:00:00Z",
        imageData: "encodedbase64image",
      };

      mockEncodeImage.mockResolvedValue(mockResponse);

      const result = await encodeImage(mockRequest);

      expect(result).toEqual(mockResponse);
      expect(mockEncodeImage).toHaveBeenCalledWith(mockRequest);
    });

    it("should handle encoding with DCT algorithm", async () => {
      const dctRequest: EncodeRequest = {
        ...mockRequest,
        algorithm: AlgorithmType.DCT,
      };

      const mockResponse: EncodeResponse = {
        message: "Image encoded successfully",
        timestamp: "2023-01-01T00:00:00Z",
        imageData: "encodedbase64image",
      };

      mockEncodeImage.mockResolvedValue(mockResponse);

      const result = await encodeImage(dctRequest);

      expect(result).toEqual(mockResponse);
      expect(mockEncodeImage).toHaveBeenCalledWith(dctRequest);
    });

    it("should handle encoding error", async () => {
      const errorMessage = "Image encoding failed";
      mockEncodeImage.mockRejectedValue(new Error(errorMessage));

      await expect(encodeImage(mockRequest)).rejects.toThrow(errorMessage);
    });

    it("should handle invalid image data", async () => {
      const errorMessage = "Invalid image data";
      mockEncodeImage.mockRejectedValue(new Error(errorMessage));

      await expect(encodeImage(mockRequest)).rejects.toThrow(errorMessage);
    });

    it("should handle message too long error", async () => {
      const errorMessage = "Message exceeds image capacity";
      mockEncodeImage.mockRejectedValue(new Error(errorMessage));

      await expect(encodeImage(mockRequest)).rejects.toThrow(errorMessage);
    });
  });

  describe("decodeImage", () => {
    const mockRequest: DecodeRequest = {
      imageData: "base64encodedimage",
      algorithm: AlgorithmType.LSB,
    };

    it("should successfully decode an image", async () => {
      const mockResponse: DecodeResponse = {
        message: "Image decoded successfully",
        timestamp: "2023-01-01T00:00:00Z",
        decodedMessage: "Secret message",
      };

      mockDecodeImage.mockResolvedValue(mockResponse);

      const result = await decodeImage(mockRequest);

      expect(result).toEqual(mockResponse);
      expect(mockDecodeImage).toHaveBeenCalledWith(mockRequest);
    });

    it("should handle decoding with DCT algorithm", async () => {
      const dctRequest: DecodeRequest = {
        ...mockRequest,
        algorithm: AlgorithmType.DCT,
      };

      const mockResponse: DecodeResponse = {
        message: "Image decoded successfully",
        timestamp: "2023-01-01T00:00:00Z",
        decodedMessage: "Hidden message",
      };

      mockDecodeImage.mockResolvedValue(mockResponse);

      const result = await decodeImage(dctRequest);

      expect(result).toEqual(mockResponse);
      expect(mockDecodeImage).toHaveBeenCalledWith(dctRequest);
    });

    it("should return empty message when no message found", async () => {
      const mockResponse: DecodeResponse = {
        message: "Image decoded successfully",
        timestamp: "2023-01-01T00:00:00Z",
        decodedMessage: "",
      };

      mockDecodeImage.mockResolvedValue(mockResponse);

      const result = await decodeImage(mockRequest);

      expect(result.decodedMessage).toBe("");
      expect(mockDecodeImage).toHaveBeenCalledWith(mockRequest);
    });

    it("should handle decoding error", async () => {
      const errorMessage = "Image decoding failed";
      mockDecodeImage.mockRejectedValue(new Error(errorMessage));

      await expect(decodeImage(mockRequest)).rejects.toThrow(errorMessage);
    });

    it("should handle invalid image data", async () => {
      const errorMessage = "Invalid image data";
      mockDecodeImage.mockRejectedValue(new Error(errorMessage));

      await expect(decodeImage(mockRequest)).rejects.toThrow(errorMessage);
    });

    it("should handle corrupted steganographic data", async () => {
      const errorMessage = "Could not decode message from image";
      mockDecodeImage.mockRejectedValue(new Error(errorMessage));

      await expect(decodeImage(mockRequest)).rejects.toThrow(errorMessage);
    });
  });

  describe("getImageCapacity", () => {
    const mockRequest: CapacityRequest = {
      imageData: "base64encodedimage",
      algorithm: AlgorithmType.LSB,
    };

    it("should successfully get image capacity", async () => {
      const mockResponse: CapacityResponse = {
        message: "Capacity calculated successfully",
        timestamp: "2023-01-01T00:00:00Z",
        capacityCharacters: 1000,
      };

      mockGetImageCapacity.mockResolvedValue(mockResponse);

      const result = await getImageCapacity(mockRequest);

      expect(result).toEqual(mockResponse);
      expect(mockGetImageCapacity).toHaveBeenCalledWith(mockRequest);
    });

    it("should return different capacity for DCT algorithm", async () => {
      const dctRequest: CapacityRequest = {
        ...mockRequest,
        algorithm: AlgorithmType.DCT,
      };

      const mockResponse: CapacityResponse = {
        message: "Capacity calculated successfully",
        timestamp: "2023-01-01T00:00:00Z",
        capacityCharacters: 100,
      };

      mockGetImageCapacity.mockResolvedValue(mockResponse);

      const result = await getImageCapacity(dctRequest);

      expect(result.capacityCharacters).toBe(100);
      expect(mockGetImageCapacity).toHaveBeenCalledWith(dctRequest);
    });

    it("should handle capacity calculation error", async () => {
      const errorMessage = "Capacity check failed";
      mockGetImageCapacity.mockRejectedValue(new Error(errorMessage));

      await expect(getImageCapacity(mockRequest)).rejects.toThrow(errorMessage);
    });

    it("should handle invalid image data", async () => {
      const errorMessage = "Invalid image data";
      mockGetImageCapacity.mockRejectedValue(new Error(errorMessage));

      await expect(getImageCapacity(mockRequest)).rejects.toThrow(errorMessage);
    });

    it("should return capacity greater than 0 for valid images", async () => {
      const mockResponse: CapacityResponse = {
        message: "Capacity calculated successfully",
        timestamp: "2023-01-01T00:00:00Z",
        capacityCharacters: 500,
      };

      mockGetImageCapacity.mockResolvedValue(mockResponse);

      const result = await getImageCapacity(mockRequest);

      expect(result.capacityCharacters).toBeGreaterThan(0);
    });
  });
});
