from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
import pillow_heif

def generate_unique_filename(base_filename):
    """
    Generates a unique filename by appending a counter to the base filename if it already exists.
    """
    filename, extension = os.path.splitext(base_filename)
    counter = 1
    unique_filename = base_filename
    
    while os.path.exists(unique_filename):
        unique_filename = f"{filename}-{counter}{extension}"
        counter += 1

    return unique_filename

def create_pdf_from_images(image_folder, output_pdf):
    # Get a unique filename for the output PDF
    output_pdf = generate_unique_filename(output_pdf)

    # Set page dimensions in points (8.5"x11" = 612x792 points)
    page_width, page_height = letter

    # Create the PDF canvas
    c = canvas.Canvas(output_pdf, pagesize=letter)

    # Iterate over all files in the folder
    for filename in os.listdir(image_folder):
        print(filename)
        if filename.lower().endswith(('.jpg', '.jpeg', '.heic')):
            img_path = os.path.join(image_folder, filename)
            temp_jpg_path = None

            try:
                # Handle HEIC files by converting to JPG first
                if filename.lower().endswith('.heic'):
                    heif_file = pillow_heif.read_heif(img_path)
                    image = Image.frombytes(
                        heif_file.mode, 
                        heif_file.size, 
                        heif_file.data,
                        "raw",
                    )
                    temp_jpg_path = img_path + "_temp.jpg"
                    image.save(temp_jpg_path, "JPEG")
                    img_path = temp_jpg_path

                # Rest of your existing image processing code
                with Image.open(img_path) as img:
                    img_width, img_height = img.size
                    aspect_ratio = img_width / img_height

                    if img_width > img_height:
                        new_width = page_width
                        new_height = new_width / aspect_ratio
                    else:
                        new_height = page_height
                        new_width = new_height * aspect_ratio

                    x = (page_width - new_width) / 2
                    y = (page_height - new_height) / 2

                    img_resized = img.resize((int(new_width), int(new_height)), Image.LANCZOS)
                    img_resized_path = img_path + "_resized.jpg"
                    img_resized.save(img_resized_path)

                    c.drawImage(img_resized_path, x, y, width=new_width, height=new_height)
                    os.remove(img_resized_path)

                # Clean up temporary HEIC conversion if it exists
                if temp_jpg_path and os.path.exists(temp_jpg_path):
                    os.remove(temp_jpg_path)

                c.showPage()

            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                # Clean up any temporary files if there was an error
                if temp_jpg_path and os.path.exists(temp_jpg_path):
                    os.remove(temp_jpg_path)
                continue

    # Save the PDF
    c.save()
    print(f"PDF created: {output_pdf}")

# Replace the hardcoded usage section at the bottom with:
if __name__ == "__main__":
    image_folder = input("Enter the path to your images folder: ").strip()
    
    # Convert to absolute path and expand user directory (~)
    image_folder = os.path.expanduser(image_folder)
    image_folder = os.path.abspath(image_folder)
    
    # Verify the folder exists
    if not os.path.exists(image_folder):
        print(f"Error: The folder '{image_folder}' does not exist.")
        print("Please make sure you enter the full path, for example:")
        print("  /Users/username/Desktop/my_images")
        print("  ~/Desktop/my_images")
    else:
        print(f"Using folder: {image_folder}")
        output_pdf = "output.pdf"
        create_pdf_from_images(image_folder, output_pdf)
