import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Configuration
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

# Prompt, Images, and Response Setup
image1_path = "dog_image.png"
image2_path = "cap_image.png"
prompt = "Make the dog from the first image wear the cap from the second image. The cap should fit realistically on the dog's head."
output_filename = "dog_with_cap_result.png"

def save_image_from_response(response, filename):
    """Helper function to save the image from the API response."""
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_data = BytesIO(part.inline_data.data)
                img = Image.open(image_data)
                img.save(filename)
                print(f"Image successfully saved as {filename}")
                return filename
    print("No image data found in the response.")
    return None

def main():
    print(f"Fusing images '{image1_path}' and '{image2_path}'...")
    try:
        img1 = Image.open(image1_path)
        img2 = Image.open(image2_path)
        response = model.generate_content([prompt, img1, img2])
        save_image_from_response(response, output_filename)
    except FileNotFoundError:
        print("Error: One or both image files were not found.")

if __name__ == "__main__":
    main()
