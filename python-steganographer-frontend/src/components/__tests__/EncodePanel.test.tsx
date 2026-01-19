import { render, screen, fireEvent, waitFor } from "@testing-library/react";

import EncodePanel from "@/components/EncodePanel";
import { encodeImage, getImageCapacity } from "@/lib/api";
import { AlgorithmType } from "@/lib/types";

jest.mock("../../lib/api", () => ({
  encodeImage: jest.fn(),
  getImageCapacity: jest.fn(),
}));

const mockEncodeImage = encodeImage as jest.MockedFunction<typeof encodeImage>;
const mockGetImageCapacity = getImageCapacity as jest.MockedFunction<
  typeof getImageCapacity
>;

describe("EncodePanel", () => {
  const mockOnEncodedImage = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockGetImageCapacity.mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2026-01-01T12:00:00Z",
      capacityCharacters: 100,
    });
  });

  it("renders the component with algorithm selector", () => {
    render(
      <EncodePanel
        imageData="base64data"
        imageFormat="png"
        onEncodedImage={mockOnEncodedImage}
      />
    );

    expect(screen.getByText("Steganography Algorithm")).toBeInTheDocument();
    expect(screen.getByText("LSB")).toBeInTheDocument();
    expect(screen.getByText("DCT")).toBeInTheDocument();
  });

  it("fetches and displays image capacity", async () => {
    render(
      <EncodePanel
        imageData="base64data"
        imageFormat="png"
        onEncodedImage={mockOnEncodedImage}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("100 characters")).toBeInTheDocument();
    });

    expect(mockGetImageCapacity).toHaveBeenCalledWith({
      imageData: "base64data",
      algorithm: AlgorithmType.LSB,
    });
  });

  it("shows loading state while fetching capacity", async () => {
    mockGetImageCapacity.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <EncodePanel
        imageData="base64data"
        imageFormat="png"
        onEncodedImage={mockOnEncodedImage}
      />
    );

    expect(screen.getByText("Calculating...")).toBeInTheDocument();
  });

  it("displays message textarea", () => {
    render(
      <EncodePanel
        imageData="base64data"
        imageFormat="png"
        onEncodedImage={mockOnEncodedImage}
      />
    );

    const textarea = screen.getByPlaceholderText(
      "Enter your secret message here..."
    );
    expect(textarea).toBeInTheDocument();
  });

  it("updates character count as user types", async () => {
    render(
      <EncodePanel
        imageData="base64data"
        imageFormat="png"
        onEncodedImage={mockOnEncodedImage}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("100 characters")).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(
      "Enter your secret message here..."
    );
    fireEvent.change(textarea, { target: { value: "Hello" } });

    expect(screen.getByText("5 / 100 characters")).toBeInTheDocument();
  });

  it("shows error when message exceeds capacity", async () => {
    render(
      <EncodePanel
        imageData="base64data"
        imageFormat="png"
        onEncodedImage={mockOnEncodedImage}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("100 characters")).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(
      "Enter your secret message here..."
    );
    const longMessage = "a".repeat(101);
    fireEvent.change(textarea, { target: { value: longMessage } });

    expect(screen.getByText("Message exceeds capacity!")).toBeInTheDocument();
  });

  it("successfully encodes message", async () => {
    mockEncodeImage.mockResolvedValue({
      code: 200,
      message: "Success",
      timestamp: "2026-01-01T12:00:00Z",
      imageData: "encodedbase64",
    });

    render(
      <EncodePanel
        imageData="base64data"
        imageFormat="png"
        onEncodedImage={mockOnEncodedImage}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("100 characters")).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(
      "Enter your secret message here..."
    );
    fireEvent.change(textarea, { target: { value: "Secret message" } });

    const encodeButton = screen.getByText("Encode Message");
    fireEvent.click(encodeButton);

    await waitFor(() => {
      expect(mockEncodeImage).toHaveBeenCalledWith({
        imageData: "base64data",
        outputFormat: "png",
        message: "Secret message",
        algorithm: AlgorithmType.LSB,
      });
    });

    expect(mockOnEncodedImage).toHaveBeenCalledWith("encodedbase64", "png");
  });

  it("shows error when encoding fails", async () => {
    mockEncodeImage.mockRejectedValue(new Error("Encoding failed"));

    render(
      <EncodePanel
        imageData="base64data"
        imageFormat="png"
        onEncodedImage={mockOnEncodedImage}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("100 characters")).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(
      "Enter your secret message here..."
    );
    fireEvent.change(textarea, { target: { value: "Test" } });

    const encodeButton = screen.getByText("Encode Message");
    fireEvent.click(encodeButton);

    await waitFor(() => {
      expect(screen.getByText("Encoding failed")).toBeInTheDocument();
    });
  });

  it("prevents encoding empty message", async () => {
    render(
      <EncodePanel
        imageData="base64data"
        imageFormat="png"
        onEncodedImage={mockOnEncodedImage}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("100 characters")).toBeInTheDocument();
    });

    const encodeButton = screen.getByText("Encode Message");

    // Button should be disabled for empty message
    expect(encodeButton).toBeDisabled();
    expect(mockEncodeImage).not.toHaveBeenCalled();
  });

  it("disables encode button when loading", async () => {
    mockEncodeImage.mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <EncodePanel
        imageData="base64data"
        imageFormat="png"
        onEncodedImage={mockOnEncodedImage}
      />
    );

    await waitFor(() => {
      expect(screen.getByText("100 characters")).toBeInTheDocument();
    });

    const textarea = screen.getByPlaceholderText(
      "Enter your secret message here..."
    );
    fireEvent.change(textarea, { target: { value: "Test" } });

    const encodeButton = screen.getByText("Encode Message");
    fireEvent.click(encodeButton);

    await waitFor(() => {
      expect(screen.getByText("Encoding...")).toBeInTheDocument();
    });

    const disabledButton = screen.getByText("Encoding...");
    expect(disabledButton).toBeDisabled();
  });

  it("refetches capacity when algorithm changes", async () => {
    render(
      <EncodePanel
        imageData="base64data"
        imageFormat="png"
        onEncodedImage={mockOnEncodedImage}
      />
    );

    await waitFor(() => {
      expect(mockGetImageCapacity).toHaveBeenCalledWith({
        imageData: "base64data",
        algorithm: AlgorithmType.LSB,
      });
    });

    const dctButton = screen.getByText("DCT").closest("button");
    if (dctButton) {
      fireEvent.click(dctButton);
    }

    await waitFor(() => {
      expect(mockGetImageCapacity).toHaveBeenCalledWith({
        imageData: "base64data",
        algorithm: AlgorithmType.DCT,
      });
    });
  });
});
