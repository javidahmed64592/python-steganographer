import { render, screen, fireEvent } from "@testing-library/react";

import AlgorithmSelector from "@/components/AlgorithmSelector";
import { AlgorithmType } from "@/lib/types";

describe("AlgorithmSelector", () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("renders the component with label", () => {
    render(
      <AlgorithmSelector selected={AlgorithmType.LSB} onChange={mockOnChange} />
    );

    expect(screen.getByText("Steganography Algorithm")).toBeInTheDocument();
  });

  it("renders both LSB and DCT buttons", () => {
    render(
      <AlgorithmSelector selected={AlgorithmType.LSB} onChange={mockOnChange} />
    );

    expect(screen.getByText("LSB")).toBeInTheDocument();
    expect(screen.getByText("Least Significant Bit")).toBeInTheDocument();
    expect(screen.getByText("DCT")).toBeInTheDocument();
    expect(screen.getByText("Discrete Cosine Transform")).toBeInTheDocument();
  });

  it("applies active styling to selected LSB algorithm", () => {
    render(
      <AlgorithmSelector selected={AlgorithmType.LSB} onChange={mockOnChange} />
    );

    const lsbButton = screen.getByText("LSB").closest("button");
    expect(lsbButton).toHaveClass(
      "bg-neon-green",
      "text-background",
      "shadow-neon"
    );

    const dctButton = screen.getByText("DCT").closest("button");
    expect(dctButton).toHaveClass("bg-background-tertiary", "text-text-muted");
  });

  it("applies active styling to selected DCT algorithm", () => {
    render(
      <AlgorithmSelector selected={AlgorithmType.DCT} onChange={mockOnChange} />
    );

    const dctButton = screen.getByText("DCT").closest("button");
    expect(dctButton).toHaveClass(
      "bg-neon-green",
      "text-background",
      "shadow-neon"
    );

    const lsbButton = screen.getByText("LSB").closest("button");
    expect(lsbButton).toHaveClass("bg-background-tertiary", "text-text-muted");
  });

  it("calls onChange with LSB when LSB button is clicked", () => {
    render(
      <AlgorithmSelector selected={AlgorithmType.DCT} onChange={mockOnChange} />
    );

    const lsbButton = screen.getByText("LSB").closest("button");
    if (lsbButton) {
      fireEvent.click(lsbButton);
    }

    expect(mockOnChange).toHaveBeenCalledTimes(1);
    expect(mockOnChange).toHaveBeenCalledWith(AlgorithmType.LSB);
  });

  it("calls onChange with DCT when DCT button is clicked", () => {
    render(
      <AlgorithmSelector selected={AlgorithmType.LSB} onChange={mockOnChange} />
    );

    const dctButton = screen.getByText("DCT").closest("button");
    if (dctButton) {
      fireEvent.click(dctButton);
    }

    expect(mockOnChange).toHaveBeenCalledTimes(1);
    expect(mockOnChange).toHaveBeenCalledWith(AlgorithmType.DCT);
  });

  it("has proper responsive layout", () => {
    render(
      <AlgorithmSelector selected={AlgorithmType.LSB} onChange={mockOnChange} />
    );

    const buttonContainer = screen
      .getByText("LSB")
      .closest("button")?.parentElement;
    expect(buttonContainer).toHaveClass("flex", "gap-3");
  });

  it("buttons have transition classes for smooth animations", () => {
    render(
      <AlgorithmSelector selected={AlgorithmType.LSB} onChange={mockOnChange} />
    );

    const lsbButton = screen.getByText("LSB").closest("button");
    expect(lsbButton).toHaveClass("transition-all");

    const dctButton = screen.getByText("DCT").closest("button");
    expect(dctButton).toHaveClass("transition-all");
  });
});
