import streamlit as st
from PIL import Image, ImageOps
import numpy as np
import os
import tempfile
import zipfile
import concurrent.futures

# Function to load the password from Streamlit secrets
def load_password():
    return st.secrets["password"]

def stack_images(image, mode):
    if mode == 'Horizontal':
        stacked_image = Image.fromarray(np.hstack([image, image]))
    elif mode == 'Vertical':
        stacked_image = Image.fromarray(np.vstack([image, image]))
    elif mode == 'Both':
        stacked_image = Image.fromarray(np.hstack([image, image]))
        stacked_image = Image.fromarray(np.vstack([np.array(stacked_image), np.array(stacked_image)]))
    else:
        stacked_image = image
        
    return stacked_image

def process_image(uploaded_file, mode, padding, output_dir):
    image = Image.open(uploaded_file)
    image = np.array(image)
    processed_image = stack_images(image, mode)
    if padding > 0:
        processed_image = ImageOps.expand(processed_image, border=padding, fill='white')
    output_path = os.path.join(output_dir, uploaded_file.name)
    processed_image.save(output_path)
    return uploaded_file.name, output_path

def main():
    # Check if the user is authenticated
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        # Show the login form
        st.title("Login")
        password = st.text_input("Enter password", type="password")
        if st.button("Login"):
            if password == load_password():
                st.session_state.authenticated = True
                st.experimental_rerun()
            else:
                st.error("Invalid password")
        return

    # Main app content goes here
    st.title("Bulk Image Processor")

    uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
    mode = st.selectbox("Choose how to stack images", ["None", "Horizontal", "Vertical", "Both"])
    padding = st.slider("Select padding size", 0, 50, 0)

    if uploaded_files:
        output_dir = tempfile.mkdtemp()
        processed_files = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for uploaded_file in uploaded_files:
                futures.append(executor.submit(process_image, uploaded_file, mode, padding, output_dir))
            for future in concurrent.futures.as_completed(futures):
                processed_files.append(future.result())

        st.success("Processing complete. Download your files below:")

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            with zipfile.ZipFile(tmp, 'w') as z:
                for filename, filepath in processed_files:
                    z.write(filepath, filename)

        with open(tmp.name, 'rb') as f:
            btn = st.download_button(
                label='Download processed images as ZIP',
                data=f,
                file_name='processed_images.zip',
                mime='application/zip'
            )

if __name__ == "__main__":
    main()
