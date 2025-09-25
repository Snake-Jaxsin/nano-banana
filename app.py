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

# Configure AI Models
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
image_gen_model = genai.GenerativeModel('imagen-4.0-generate-001')  # Main model for generation
analysis_model = genai.GenerativeModel('gemini-2.5-flash')  # For image analysis only

# Custom CSS for super appealing artistic photographic theme
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0c2461 0%, #1e3799 50%, #4a69bd 100%);
    }
    
    /* Headers */
    .main-header {
        font-size: 4rem;
        background: linear-gradient(45deg, #ffd700, #ff6b6b, #48dbfb, #1dd1a1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-family: 'Playfair Display', serif;
        font-weight: 900;
        margin-bottom: 1rem;
        text-shadow: 0 4px 8px rgba(0,0,0,0.3);
        letter-spacing: 1px;
    }
    
    .sub-header {
        font-size: 2rem;
        color: #ffd700;
        font-family: 'Montserrat', sans-serif;
        font-weight: 700;
        margin-bottom: 1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        border-bottom: 3px solid #ff6b6b;
        padding-bottom: 0.5rem;
    }
    
    /* Sidebar */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e3799 0%, #0c2461 100%);
        border-right: 4px solid #ffd700;
    }
    
    /* Radio buttons in sidebar */
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        border: 2px solid rgba(255, 215, 0, 0.3);
    }
    
    /* Selected radio button */
    div[data-testid="stVerticalBlock"] div[data-testid="stVerticalBlock"]:has(input:checked) {
        background: rgba(255, 215, 0, 0.2);
        border: 2px solid #ffd700;
        transform: scale(1.02);
        transition: all 0.3s ease;
    }
    
    /* Radio button labels */
    label {
        color: white !important;
        font-family: 'Montserrat', sans-serif;
        font-weight: 600;
        font-size: 1.1rem;
    }
    
    /* Text area - FIXED VISIBILITY */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.95) !important;
        color: #0c2461 !important;
        font-family: 'Montserrat', sans-serif;
        font-size: 1.1rem;
        border: 3px solid #ffd700;
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(255, 215, 0, 0.3);
        caret-color: #0c2461 !important;
        cursor: text !important;
    }
    
    .stTextArea textarea:focus {
        border-color: #ff6b6b;
        box-shadow: 0 4px 20px rgba(255, 107, 107, 0.4);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(45deg, #ff6b6b, #ffd700, #48dbfb);
        background-size: 300% 300%;
        color: #0c2461;
        border: none;
        border-radius: 25px;
        padding: 1rem 2rem;
        font-size: 1.2rem;
        font-weight: 700;
        font-family: 'Montserrat', sans-serif;
        transition: all 0.5s ease;
        animation: gradientShift 3s ease infinite;
        box-shadow: 0 6px 20px rgba(255, 107, 107, 0.4);
    }
    
    .stButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.6);
        animation: gradientShift 1.5s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50% }
        50% { background-position: 100% 50% }
        100% { background-position: 0% 50% }
    }
    
    /* File uploader */
    .stFileUploader > div {
        background: rgba(255, 255, 255, 0.95);
        border: 3px dashed #48dbfb;
        border-radius: 15px;
        padding: 2rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #ff6b6b;
        background: rgba(255, 255, 255, 1);
        transform: scale(1.02);
    }
    
    /* Images */
    .uploaded-image {
        border-radius: 15px;
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
        border: 3px solid #ffd700;
        transition: all 0.3s ease;
    }
    
    .uploaded-image:hover {
        transform: scale(1.03);
        box-shadow: 0 12px 35px rgba(255, 215, 0, 0.4);
    }
    
    /* Columns background */
    .block-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Success message */
    .success-message {
        background: linear-gradient(45deg, #1dd1a1, #48dbfb);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        font-weight: 700;
        font-size: 1.3rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
        box-shadow: 0 6px 20px rgba(29, 209, 161, 0.4);
    }
    
    /* Operation cards */
    .operation-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0.05));
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 15px;
        border: 2px solid rgba(255, 215, 0, 0.3);
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    
    .operation-card:hover {
        border-color: #ff6b6b;
        transform: translateY(-5px);
    }
    
    /* Text elements */
    .stMarkdown {
        color: white;
    }
    
    .caption {
        color: #48dbfb !important;
        font-style: italic;
        font-weight: 500;
    }
    
    /* Info boxes */
    .stInfo {
        background: rgba(72, 219, 251, 0.2) !important;
        border: 2px solid #48dbfb;
        border-radius: 15px;
        color: white;
    }
    
    /* Warning boxes */
    .stWarning {
        background: rgba(255, 107, 107, 0.2) !important;
        border: 2px solid #ff6b6b;
        border-radius: 15px;
        color: white;
    }
    
    /* Spinner */
    .stSpinner > div {
        border: 3px solid #48dbfb;
        border-radius: 50%;
        border-top: 3px solid #ffd700;
        width: 40px;
        height: 40px;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

def save_image_from_response(response, filename=None):
    """Helper function to save the image from the API response."""
    try:
        # Check for direct image in response
        if hasattr(response, '_result') and hasattr(response._result, 'candidates'):
            for candidate in response._result.candidates:
                if hasattr(candidate, 'content'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data'):
                            image_data = BytesIO(part.inline_data.data)
                            img = Image.open(image_data)
                            return img
        
        # Check standard format
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content:
                    for part in candidate.content.parts:
                        if hasattr(part, 'inline_data') and part.inline_data:
                            try:
                                # Handle base64 encoded data
                                if hasattr(part.inline_data, 'data'):
                                    image_data = part.inline_data.data
                                    st.write(f"Debug: Data type: {type(image_data)}, Length: {len(image_data) if hasattr(image_data, '__len__') else 'N/A'}")
                                    
                                    if isinstance(image_data, str):
                                        # Base64 string
                                        image_data = base64.b64decode(image_data)
                                        st.write(f"Debug: Decoded data length: {len(image_data)}")
                                    
                                    if len(image_data) < 100:
                                        st.error(f"Debug: Data too small, content: {image_data[:50]}")
                                        continue
                                    
                                    # Check if data starts with valid image headers
                                    if not (image_data.startswith(b'\xff\xd8') or  # JPEG
                                           image_data.startswith(b'\x89PNG') or   # PNG
                                           image_data.startswith(b'GIF')):        # GIF
                                        st.error(f"Debug: Invalid image format. First 20 bytes: {image_data[:20]}")
                                        continue
                                        
                                    img = Image.open(BytesIO(image_data))
                                    return img
                            except Exception as e:
                                st.error(f"Error decoding image data: {str(e)}")
                                continue
                        elif hasattr(part, 'file_data') and part.file_data:
                            # Handle file data format
                            pass
        
        # Check if request was blocked/filtered
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'finish_reason') and candidate.finish_reason == 1:
                st.error("🚫 Image generation was blocked. Try a different, more appropriate prompt.")
                return None
        
        # No image found - check for text response
        try:
            if hasattr(response, 'text') and response.text:
                st.info(f"Model response: {response.text}")
        except:
            st.warning("⚠️ No image was generated. The request may have been filtered or the model returned no content.")
        
        return None
    except Exception as e:
        if "finish_reason is 1" in str(e):
            st.error("🚫 Image generation was blocked. Try a different, more appropriate prompt.")
        else:
            st.error(f"Error processing response: {str(e)}")
        return None

def process_image_edit(image, prompt, operation_type):
    """Process image based on operation type"""
    try:
        # Generate content based on operation type
        if operation_type == "edit":
            response = analysis_model.generate_content([prompt, image])
        elif operation_type == "fusion" and len(st.session_state.get('fusion_images', [])) > 1:
            img2 = st.session_state.fusion_images[1]
            response = analysis_model.generate_content([prompt, image, img2])
        elif operation_type == "restoration":
            response = analysis_model.generate_content([prompt, image])
        elif operation_type == "generation":
            response = image_gen_model.generate_content(prompt)
        else:
            return None
        
        return save_image_from_response(response)
        
    except Exception as e:
        st.error(f"Error processing image: {str(e)}")
        st.error(f"Operation: {operation_type}, Prompt: {prompt[:50]}...")
        return None

# Streamlit App
def main():
    # Add custom fonts
    st.markdown(
        '<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@900&family=Montserrat:wght@400;600;700&display=swap" rel="stylesheet">',
        unsafe_allow_html=True
    )
    
    st.markdown('<h1 class="main-header">✨ VISION AI STUDIO</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div style="text-align: center; color: #48dbfb; font-family: Montserrat; font-size: 1.3rem; margin-bottom: 2rem; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">'
        'Transform Your Creativity Into Stunning Visual Masterpieces'
        '</div>', 
        unsafe_allow_html=True
    )
    
    # Initialize session state
    if 'uploaded_image' not in st.session_state:
        st.session_state.uploaded_image = None
    if 'fusion_images' not in st.session_state:
        st.session_state.fusion_images = []
    if 'result_image' not in st.session_state:
        st.session_state.result_image = None
    
    # Sidebar for operation selection
    st.sidebar.markdown('<h2 class="sub-header">🎨 CREATIVE TOOLS</h2>', unsafe_allow_html=True)
    
    # Operation descriptions
    operations = {
        "Image Edit": {"icon": "🎭", "desc": "Transform your image with AI-powered edits", "color": "#ff6b6b"},
        "Image Fusion": {"icon": "🔄", "desc": "Blend two images into something extraordinary", "color": "#48dbfb"},
        "Image Restoration": {"icon": "✨", "desc": "Restore and enhance old photographs", "color": "#1dd1a1"},
        "Text to Image": {"icon": "📝", "desc": "Generate images from your imagination", "color": "#ffd700"}
    }
    
    operation = st.sidebar.radio(
        "Choose your creative tool:",
        list(operations.keys()),
        format_func=lambda x: f"{operations[x]['icon']} {x}"
    )
    
    # Display operation description
    st.sidebar.markdown(
        f'<div class="operation-card">'
        f'<div style="color: {operations[operation]["color"]}; font-size: 2rem; text-align: center;">{operations[operation]["icon"]}</div>'
        f'<div style="text-align: center; color: white; font-family: Montserrat; font-weight: 700; font-size: 1.2rem;">{operation}</div>'
        f'<div style="text-align: center; color: #48dbfb; font-family: Montserrat; margin-top: 0.5rem;">{operations[operation]["desc"]}</div>'
        f'</div>', 
        unsafe_allow_html=True
    )
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">📸 UPLOAD IMAGE</h2>', unsafe_allow_html=True)
        
        if operation in ["Image Edit", "Image Restoration"]:
            uploaded_file = st.file_uploader(
                "🎯 Drag & drop your image here", 
                type=['png', 'jpg', 'jpeg'],
                help="Upload a high-quality image for best results"
            )
            if uploaded_file is not None:
                image = Image.open(uploaded_file)
                
                # Rotation controls
                col_rot1, col_rot2, col_rot3 = st.columns([1, 2, 1])
                with col_rot2:
                    rotation = st.select_slider(
                        "🔄 Rotate Image",
                        options=[0, 90, 180, 270],
                        value=0,
                        format_func=lambda x: f"{x}°"
                    )
                
                if rotation != 0:
                    image = image.rotate(-rotation, expand=True)
                
                st.session_state.uploaded_image = image
                st.image(image, caption="📷 Your Original Masterpiece", use_container_width=True, output_format="PNG")
        
        elif operation == "Image Fusion":
            uploaded_files = st.file_uploader(
                "🖼️ Select two images to blend", 
                type=['png', 'jpg', 'jpeg'], 
                accept_multiple_files=True,
                help="Choose two images that you want to merge creatively"
            )
            if uploaded_files and len(uploaded_files) >= 2:
                images = [Image.open(uploaded_files[0]), Image.open(uploaded_files[1])]
                
                # Rotation controls for both images
                col1_1, col1_2 = st.columns(2)
                with col1_1:
                    rot1 = st.select_slider(
                        "🔄 Rotate First Image",
                        options=[0, 90, 180, 270],
                        value=0,
                        format_func=lambda x: f"{x}°",
                        key="rot1"
                    )
                    if rot1 != 0:
                        images[0] = images[0].rotate(-rot1, expand=True)
                    st.image(images[0], caption="🖼️ First Image", use_container_width=True)
                
                with col1_2:
                    rot2 = st.select_slider(
                        "🔄 Rotate Second Image",
                        options=[0, 90, 180, 270],
                        value=0,
                        format_func=lambda x: f"{x}°",
                        key="rot2"
                    )
                    if rot2 != 0:
                        images[1] = images[1].rotate(-rot2, expand=True)
                    st.image(images[1], caption="🖼️ Second Image", use_container_width=True)
                
                st.session_state.fusion_images = images
        
        elif operation == "Text to Image":
            st.info("🌟 Describe your vision in detail below. The more descriptive, the better!")
    
    with col2:
        st.markdown('<h2 class="sub-header">💫 CREATIVE PROMPT</h2>', unsafe_allow_html=True)
        
        prompt_examples = {
            "Image Edit": "Try: 'Convert to cinematic style with dramatic shadows' or 'Enhance colors to make them pop vibrantly'",
            "Image Fusion": "Try: 'Merge the subject from first image into the background of the second seamlessly'",
            "Image Restoration": "Try: 'Fix all scratches and color fading while preserving the authentic vintage feel'",
            "Text to Image": "Try: 'A majestic eagle soaring over snow-capped mountains during sunrise, professional wildlife photography'"
        }
        
        # Text area with empty default value
        prompt = st.text_area(
            "Describe your creative vision:",
            value="",  # Empty instead of example text
            height=150,
            help="Be as descriptive as possible for the best results!",
            placeholder="Describe what you want to create..."
        )
        
        # Show example below the text area
        st.markdown(f'<div class="caption">💡 {prompt_examples[operation]}</div>', unsafe_allow_html=True)
        
        if st.button("🚀 GENERATE MASTERPIECE", use_container_width=True):
            if (operation in ["Image Edit", "Image Restoration"] and st.session_state.uploaded_image is None) or \
               (operation == "Image Fusion" and len(st.session_state.fusion_images) < 2) or \
               (operation == "Text to Image" and not prompt.strip()):
                st.warning("⚠️ Please provide all required inputs first!")
            else:
                with st.spinner("🎨 Creating your masterpiece... This may take a few moments."):
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
        
        # Display result
        if st.session_state.result_image:
            st.markdown('<div class="success-message">🎉 YOUR MASTERPIECE IS READY!</div>', unsafe_allow_html=True)
            
            # Add rotation control for generated image
            result_rotation = st.select_slider(
                "🔄 Rotate Generated Image",
                options=[0, 90, 180, 270],
                value=0,
                format_func=lambda x: f"{x}°",
                key="result_rotation"
            )
            
            display_image = st.session_state.result_image
            if result_rotation != 0:
                display_image = st.session_state.result_image.rotate(-result_rotation, expand=True)
            
            st.image(display_image, use_container_width=True, output_format="PNG", caption="✨ AI-Generated Masterpiece")
            
            # Download button
            buf = BytesIO()
            display_image.save(buf, format="PNG")
            st.download_button(
                label="📥 DOWNLOAD HIGH-QUALITY IMAGE",
                data=buf.getvalue(),
                file_name=f"vision_ai_{operation.lower().replace(' ', '_')}.png",
                mime="image/png",
                use_container_width=True
            )
            
            # Reset button
            if st.button("🔄 CREATE ANOTHER MASTERPIECE", use_container_width=True):
                st.session_state.result_image = None
                st.rerun()

    # Footer
    st.markdown("---")
    st.markdown(
        '<div style="text-align: center; color: #ffd700; font-family: Montserrat; font-size: 1rem; margin-top: 2rem;">'
        '✨ Powered by Gemini AI • 🎨 Professional Grade Image Processing • 💫 Unlimited Creativity<br>'
        '<span style="color: #48dbfb;">Developer: Jesse Hernandez</span>'
        '</div>', 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()