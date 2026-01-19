import { render, screen, fireEvent, waitFor } from "@testing-library/react";

import DecodePanel from "@/components/DecodePanel";
import { decodeImage } from "@/lib/api";
import { AlgorithmType } from "@/lib/types";

jest.mock("../../lib/api", () => ({
  decodeImage: jest.fn(),
}));

const mockDecodeImage = decodeImage as jest.MockedFunction<typeof decodeImage>;

describe("DecodePanel", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    Object.assign(navigator, {
      clipboard: {
        writeText: jest.fn(),
      },
    });
  });

  it("renders the component with algorithm selector", () => {
    render(<DecodePanel imageData="base64data" />);

    expect(screen.getByText("Steganography Algorithm")).toBeInTheDocument();
    expect(screen.getByText("LSB")).toBeInTheDocument();
    expect(screen.getByText("DCT")).toBeInTheDocument();
  });

  it("displays decode button", () => {
    render(<DecodePanel imageData="base64data" />);

    expect(screen.getByText("Decode Message")).toBeInTheDocument();
  });

  it("successfully decodes message", async () => {
    mockDecodeImage.mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2026-01-01T12:00:00Z",
      decodedMessage: "Hidden secret message",
    });

    render(<DecodePanel imageData="base64data" />);

    const decodeButton = screen.getByText("Decode Message");
    fireEvent.click(decodeButton);

    await waitFor(() => {
      expect(mockDecodeImage).toHaveBeenCalledWith({
        imageData: "base64data",
        algorithm: AlgorithmType.LSB,
      });
    });

    expect(screen.getByText("Hidden secret message")).toBeInTheDocument();
    expect(screen.getByText("Decoded Message")).toBeInTheDocument();
  });

  it("shows loading state while decoding", async () => {
    mockDecodeImage.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(<DecodePanel imageData="base64data" />);

    const decodeButton = screen.getByText("Decode Message");
    fireEvent.click(decodeButton);

    await waitFor(() => {
      expect(screen.getByText("Decoding...")).toBeInTheDocument();
    });

    const disabledButton = screen.getByText("Decoding...");
    expect(disabledButton).toBeDisabled();
  });

  it("displays error when decoding fails", async () => {
    mockDecodeImage.mockRejectedValue(new Error("Decoding failed"));

    render(<DecodePanel imageData="base64data" />);

    const decodeButton = screen.getByText("Decode Message");
    fireEvent.click(decodeButton);

    await waitFor(() => {
      expect(screen.getByText("Decoding failed")).toBeInTheDocument();
    });
  });

  it("displays message when no message found", async () => {
    mockDecodeImage.mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2026-01-01T12:00:00Z",
      decodedMessage: "",
    });

    render(<DecodePanel imageData="base64data" />);

    const decodeButton = screen.getByText("Decode Message");
    fireEvent.click(decodeButton);

    await waitFor(() => {
      expect(screen.getByText("No message found in image")).toBeInTheDocument();
    });
  });

  it("copies message to clipboard when copy button is clicked", async () => {
    mockDecodeImage.mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2026-01-01T12:00:00Z",
      decodedMessage: "Hidden secret message",
    });

    render(<DecodePanel imageData="base64data" />);

    const decodeButton = screen.getByText("Decode Message");
    fireEvent.click(decodeButton);

    await waitFor(() => {
      expect(screen.getByText("Hidden secret message")).toBeInTheDocument();
    });

    const copyButton = screen.getByText("Copy to Clipboard");
    fireEvent.click(copyButton);

    expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
      "Hidden secret message"
    );
  });

  it("shows copy button only after successful decode", async () => {
    render(<DecodePanel imageData="base64data" />);

    expect(screen.queryByText("Copy to Clipboard")).not.toBeInTheDocument();

    mockDecodeImage.mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2026-01-01T12:00:00Z",
      decodedMessage: "Test message",
    });

    const decodeButton = screen.getByText("Decode Message");
    fireEvent.click(decodeButton);

    await waitFor(() => {
      expect(screen.getByText("Copy to Clipboard")).toBeInTheDocument();
    });
  });

  it("uses selected algorithm for decoding", async () => {
    mockDecodeImage.mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2026-01-01T12:00:00Z",
      decodedMessage: "Test",
    });

    render(<DecodePanel imageData="base64data" />);

    const dctButton = screen.getByText("DCT").closest("button");
    if (dctButton) {
      fireEvent.click(dctButton);
    }

    const decodeButton = screen.getByText("Decode Message");
    fireEvent.click(decodeButton);

    await waitFor(() => {
      expect(mockDecodeImage).toHaveBeenCalledWith({
        imageData: "base64data",
        algorithm: AlgorithmType.DCT,
      });
    });
  });

  it("has proper styling for error messages", async () => {
    mockDecodeImage.mockRejectedValue(new Error("Test error"));

    render(<DecodePanel imageData="base64data" />);

    const decodeButton = screen.getByText("Decode Message");
    fireEvent.click(decodeButton);

    await waitFor(() => {
      const errorDiv = screen.getByText("Test error").closest("div");
      expect(errorDiv).toHaveClass(
        "border-neon-red",
        "bg-neon-red/10",
        "text-neon-red"
      );
    });
  });

  it("has proper styling for decoded message", async () => {
    mockDecodeImage.mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2026-01-01T12:00:00Z",
      decodedMessage: "Secret",
    });

    render(<DecodePanel imageData="base64data" />);

    const decodeButton = screen.getByText("Decode Message");
    fireEvent.click(decodeButton);

    await waitFor(() => {
      const message = screen.getByText("Secret");
      expect(message).toHaveClass("text-neon-green", "font-mono");
    });
  });

  it("clears previous message when decoding again", async () => {
    mockDecodeImage.mockResolvedValueOnce({
      code: 200,
      message: "Success",
      timestamp: "2026-01-01T12:00:00Z",
      decodedMessage: "First message",
    });

    render(<DecodePanel imageData="base64data" />);

    const decodeButton = screen.getByText("Decode Message");
    fireEvent.click(decodeButton);

    await waitFor(() => {
      expect(screen.getByText("First message")).toBeInTheDocument();
    });

    mockDecodeImage.mockResolvedValueOnce({
      code: 200,
      message: "Success",
      timestamp: "2026-01-01T12:00:00Z",
      decodedMessage: "Second message",
    });
    fireEvent.click(decodeButton);

    await waitFor(() => {
      expect(screen.getByText("Second message")).toBeInTheDocument();
      expect(screen.queryByText("First message")).not.toBeInTheDocument();
    });
  });
});
