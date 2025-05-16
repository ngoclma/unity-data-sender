from PIL import Image
import os

def convert_images_to_pdf(input_dir, output_dir):
    """
    Convert images in JPG, PNG, and EPS formats to PDF.

    Args:
        input_dir (str): Directory containing input images.
        output_dir (str): Directory to save the converted PDFs.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Supported image formats
    supported_formats = (".jpg", ".jpeg", ".png", ".eps")

    # Iterate through files in the input directory
    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_formats):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, f"{os.path.splitext(filename)[0]}.pdf")

            try:
                with Image.open(input_path) as img:
                    # Convert EPS to RGB if necessary
                    if img.format == "EPS":
                        try:
                            from PIL import EpsImagePlugin
                            EpsImagePlugin.gs_windows_binary = r"C:\\Program Files\\gs\\gs10.04.0\\bin\\gswin64c.exe"  # Update with your Ghostscript path
                            img = img.convert("RGB")
                        except ImportError as ie:
                            print("Ghostscript is required to process EPS files.")
                            raise ie

                    # Save the image as a PDF with high resolution
                    img.save(output_path, "PDF", resolution=1000.0)
                    print(f"Converted {filename} to PDF.")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Example usage
input_directory = "/Users/AnhNgoc/Desktop/fyp_charts"
output_directory = "/Users/AnhNgoc/Desktop/fyp_fig_pdf"
convert_images_to_pdf(input_directory, output_directory)