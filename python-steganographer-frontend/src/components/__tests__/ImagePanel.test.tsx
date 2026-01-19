import { render, screen, fireEvent } from "@testing-library/react";

import ImagePanel from "@/components/ImagePanel";

// Mock Next.js Image component
jest.mock("next/image", () => ({
  __esModule: true,
  default: (props: React.ImgHTMLAttributes<HTMLImageElement>) => {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const { unoptimized, ...restProps } =
      props as React.ImgHTMLAttributes<HTMLImageElement> & {
        unoptimized?: boolean;
      };
    // eslint-disable-next-line @next/next/no-img-element, jsx-a11y/alt-text
    return <img {...restProps} />;
  },
}));

describe("ImagePanel", () => {
  const mockOnImageUpload = jest.fn();
  const mockOnClear = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    global.alert = jest.fn();
  });

  it("renders the component with heading", () => {
    render(
      <ImagePanel
        imageData={null}
        imageFormat="png"
        onImageUpload={mockOnImageUpload}
        onClear={mockOnClear}
      />
    );

    expect(screen.getByText("Image Upload")).toBeInTheDocument();
  });

  it("displays upload area when no image is present", () => {
    render(
      <ImagePanel
        imageData={null}
        imageFormat="png"
        onImageUpload={mockOnImageUpload}
        onClear={mockOnClear}
      />
    );

    expect(screen.getByText("Click to upload")).toBeInTheDocument();
    expect(screen.getByText(/or drag and drop/)).toBeInTheDocument();
    expect(screen.getByText("PNG, JPG, JPEG, or GIF")).toBeInTheDocument();
  });

  it("displays image preview when image data is present", () => {
    render(
      <ImagePanel
        imageData="base64data"
        imageFormat="png"
        onImageUpload={mockOnImageUpload}
        onClear={mockOnClear}
      />
    );

    const image = screen.getByAltText("Uploaded preview");
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute("src", "data:image/png;base64,base64data");
  });

  it("displays Change Image and Clear buttons when image is present", () => {
    render(
      <ImagePanel
        imageData="base64data"
        imageFormat="png"
        onImageUpload={mockOnImageUpload}
        onClear={mockOnClear}
      />
    );

    expect(screen.getByText("Change Image")).toBeInTheDocument();
    expect(screen.getByText("Clear")).toBeInTheDocument();
  });

  it("calls onClear when Clear button is clicked", () => {
    render(
      <ImagePanel
        imageData="base64data"
        imageFormat="png"
        onImageUpload={mockOnImageUpload}
        onClear={mockOnClear}
      />
    );

    const clearButton = screen.getByText("Clear");
    fireEvent.click(clearButton);

    expect(mockOnClear).toHaveBeenCalledTimes(1);
  });

  it("has hidden file input", () => {
    const { container } = render(
      <ImagePanel
        imageData={null}
        imageFormat="png"
        onImageUpload={mockOnImageUpload}
        onClear={mockOnClear}
      />
    );

    const fileInput = container.querySelector('input[type="file"]');
    expect(fileInput).toBeInTheDocument();
    expect(fileInput).toHaveClass("hidden");
    expect(fileInput).toHaveAttribute("accept", "image/*");
  });

  it("processes valid image file upload", () => {
    const { container } = render(
      <ImagePanel
        imageData={null}
        imageFormat="png"
        onImageUpload={mockOnImageUpload}
        onClear={mockOnClear}
      />
    );

    const fileInput = container.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;
    const file = new File(["dummy"], "test.png", { type: "image/png" });

    // Mock FileReader
    const mockFileReader = {
      readAsDataURL: jest.fn(),
      onload: null as ((this: FileReader, ev: ProgressEvent) => void) | null,
      result: "data:image/png;base64,dGVzdGRhdGE=",
    };

    global.FileReader = jest.fn(() => mockFileReader) as never;

    fireEvent.change(fileInput, { target: { files: [file] } });

    // Trigger the onload callback with proper event structure
    if (mockFileReader.onload) {
      mockFileReader.onload.call(
        mockFileReader as unknown as FileReader,
        {
          target: mockFileReader,
        } as unknown as ProgressEvent
      );
    }

    expect(mockOnImageUpload).toHaveBeenCalledWith(
      "dGVzdGRhdGE=",
      "png",
      "test"
    );
  });

  it("normalizes jpeg format to jpg", () => {
    const { container } = render(
      <ImagePanel
        imageData={null}
        imageFormat="png"
        onImageUpload={mockOnImageUpload}
        onClear={mockOnClear}
      />
    );

    const fileInput = container.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;
    const file = new File(["dummy"], "test.jpeg", { type: "image/jpeg" });

    const mockFileReader = {
      readAsDataURL: jest.fn(),
      onload: null as ((this: FileReader, ev: ProgressEvent) => void) | null,
      result: "data:image/jpeg;base64,dGVzdGRhdGE=",
    };

    global.FileReader = jest.fn(() => mockFileReader) as never;

    fireEvent.change(fileInput, { target: { files: [file] } });

    if (mockFileReader.onload) {
      mockFileReader.onload.call(
        mockFileReader as unknown as FileReader,
        {
          target: mockFileReader,
        } as unknown as ProgressEvent
      );
    }

    expect(mockOnImageUpload).toHaveBeenCalledWith(
      "dGVzdGRhdGE=",
      "jpg",
      "test"
    );
  });

  it("shows alert for non-image files", () => {
    const { container } = render(
      <ImagePanel
        imageData={null}
        imageFormat="png"
        onImageUpload={mockOnImageUpload}
        onClear={mockOnClear}
      />
    );

    const fileInput = container.querySelector(
      'input[type="file"]'
    ) as HTMLInputElement;
    const file = new File(["dummy"], "test.pdf", { type: "application/pdf" });

    fireEvent.change(fileInput, { target: { files: [file] } });

    expect(global.alert).toHaveBeenCalledWith("Please upload an image file");
    expect(mockOnImageUpload).not.toHaveBeenCalled();
  });

  it("has proper styling classes", () => {
    render(
      <ImagePanel
        imageData={null}
        imageFormat="png"
        onImageUpload={mockOnImageUpload}
        onClear={mockOnClear}
      />
    );

    const heading = screen.getByText("Image Upload");
    expect(heading).toHaveClass("text-neon-green");

    const uploadArea = screen.getByText("Click to upload").closest("div");
    expect(uploadArea).toHaveClass(
      "border-dashed",
      "cursor-pointer",
      "hover:bg-background-tertiary"
    );
  });
});
