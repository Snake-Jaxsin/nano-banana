import os
import google.generativeai as genai
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

# Configuration
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

# Prompt, Image, and Response Setup
input_image_path = "input_dog.png"
prommpt = "Make the dog wear a small wizard hat and spectacles."
output_filename = "edited_image_result.png"

# saving image helper function from text prompt response
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
    print(f"Editing image '{input_image_path}' with prompt: '{prommpt}'...")
    try:
        img_to_edit = Image.open(input_image_path)
        response = model.generate_content([prommpt, img_to_edit])
        save_image_from_response(response, output_filename)
    except FileNotFoundError:
        print(f"Error: The file '{input_image_path}' was not found.")

if __name__ == "__main__":
    main()
