import os
import streamlit as st
import google.generativeai as genai
from PIL import Image
from io import BytesIO
import tempfile
import base64

# Configuration
from dotenv import load_dotenv
load_dotenv()

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-2.5-flash-image-preview')

# Custom CSS for cotton candy theme
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #ff6bff;
        text-align: center;
        text-shadow: 2px 2px 4px #ffb3ff;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #6b8cff;
        text-shadow: 1px 1px 2px #b3c6ff;
    }
    .stButton>button {
        background: linear-gradient(45deg, #ff6bff, #6b8cff);
        color: white;
        border: none;
        border-radius: 20px;
        padding: 0.5rem 2rem;
        font-size: 1rem;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(45deg, #ff8bff, #8babff);
        transform: scale(1.05);
    }
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #ffe6ff, #e6f0ff);
    }
    .uploaded-image {
        border-radius: 15px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def save_image_from_response(response, filename=None):
    """Helper function to save the image from the API response."""
    if response.candidates and response.candidates[0].content.parts:
        for part in response.candidates[0].content.parts:
            if part.inline_data:
                image_data = BytesIO(part.inline_data.data)
                img = Image.open(image_data)
                if filename:
                    img.save(filename)
                return img
    return None

def image_to_base64(image):
    """Convert PIL Image to base64 for display"""
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

def process_image_edit(image, prompt, operation_type):
    """Process image based on operation type"""
    try:
        if operation_type == "edit":
            response = model.generate_content([prompt, image])
        elif operation_type == "fusion" and len(st.session_state.get('fusion_images', [])) > 1:
            img2 = st.session_state.fusion_images[1]
            response = model.generate_content([prompt, image, img2])
        elif operation_type == "restoration":
            response = model.generate_content([prompt, image])
        elif operation_type == "generation":
            response = model.generate_content(prompt)
        else:
            return None
            
        return save_image_from_response(response)
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        return None

# Streamlit App
def main():
    st.markdown('<h1 class="main-header">✨ Picture Perfect AI Studio ✨</h1>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    if 'fusion_images' not in st.session_state:
        st.session_state.fusion_images = []
    if 'result_image' not in st.session_state:
        st.session_state.result_image = None
    
    # Sidebar for operation selection
    st.sidebar.markdown('<h2 class="sub-header">🎨 Choose Your Magic</h2>', unsafe_allow_html=True)
    operation = st.sidebar.radio(
        "Select Operation:",
        ["Image Edit", "Image Fusion", "Image Restoration", "Text to Image"]
    )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">📤 Upload Image</h2>', unsafe_allow_html=True)
        
        if operation in ["Image Edit", "Image Restoration"]:
            uploaded_file = st.file_uploader("Choose an image...", type=['png', 'jpg', 'jpeg'])
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                st.session_state.uploaded_image = image
                st.image(image, caption="Uploaded Image", use_column_width=True, output_format="PNG")
        
        elif operation == "Image Fusion":
            st.info("Upload two images for fusion")
            uploaded_files = st.file_uploader("Choose two images...", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
            if uploaded_files and len(uploaded_files) >= 2:
                st.session_state.fusion_images = [Image.open(uploaded_files[0]), Image.open(uploaded_files[1])]
                col1_1, col1_2 = st.columns(2)
                with col1_1:
                    st.image(st.session_state.fusion_images[0], caption="Image 1", use_column_width=True)
                with col1_2:
                    st.image(st.session_state.fusion_images[1], caption="Image 2", use_column_width=True)
        
        elif operation == "Text to Image":
            st.info("Enter a prompt to generate an image from text")
    
    with col2:
        st.markdown('<h2 class="sub-header">🔮 Magic Prompt</h2>', unsafe_allow_html=True)
        
        # Default prompts based on operation
        default_prompts = {
            "Image Edit": "Make the subject wear a small wizard hat and spectacles.",
            "Image Fusion": "Combine the elements from both images realistically.",
            "Image Restoration": "Restore this image. Sharpen details, remove damage, and enhance colors.",
            "Text to Image": "A beautiful landscape with mountains and a lake"
        }
        
        prompt = st.text_area(
            "Enter your magic prompt:",
            value=default_prompts[operation],
            height=100
        )
        
        if st.button("✨ Cast Spell", use_container_width=True):
            with st.spinner("Working magic..."):
                if operation == "Image Edit" and st.session_state.uploaded_image:
                    result = process_image_edit(st.session_state.uploaded_image, prompt, "edit")
                    st.session_state.result_image = result
                
                elif operation == "Image Fusion" and len(st.session_state.fusion_images) >= 2:
                    result = process_image_edit(st.session_state.fusion_images[0], prompt, "fusion")
                    st.session_state.result_image = result
                
                elif operation == "Image Restoration" and st.session_state.uploaded_image:
                    result = process_image_edit(st.session_state.uploaded_image, prompt, "restoration")
                    st.session_state.result_image = result
                
                elif operation == "Text to Image":
                    result = process_image_edit(None, prompt, "generation")
                    st.session_state.result_image = result
                
                else:
                    st.warning("Please upload the required images first!")
        
        # Display result
        if st.session_state.result_image:
            st.markdown('<h2 class="sub-header">🎉 Your Creation</h2>', unsafe_allow_html=True)
            st.image(st.session_state.result_image, use_column_width=True, output_format="PNG")
            
            # Download button
            buf = BytesIO()
            st.session_state.result_image.save(buf, format="PNG")
            st.download_button(
                label="📥 Download Image",
                data=buf.getvalue(),
                file_name="magic_result.png",
                mime="image/png",
                use_container_width=True
            )

if __name__ == "__main__":
    main()