import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import tempfile
import zipfile

def stack_images(image, mode, padding):
    if mode == 'Horizontal':
        stacked_image = np.hstack([image, image])
    elif mode == 'Vertical':
        stacked_image = np.vstack([image, image])
    elif mode == 'Both':
        stacked_image = np.hstack([image, image])
        stacked_image = np.vstack([stacked_image, stacked_image])
    else:
        stacked_image = image
    
    stacked_image_with_padding = cv2.copyMakeBorder(stacked_image, padding, padding, padding, padding, cv2.BORDER_CONSTANT, value=(255, 255, 255))
        
    return stacked_image_with_padding

st.title("Bulk Image Processor")

uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
mode = st.selectbox("Choose how to stack images", ["None", "Horizontal", "Vertical", "Both"])
padding = st.slider("Select padding size", 0, 50, 0)

if uploaded_files:
    output_dir = tempfile.mkdtemp()
    processed_files = []
    for uploaded_file in uploaded_files:
        image = np.array(Image.open(uploaded_file))
        processed_image = stack_images(image, mode, padding)
        output_path = os.path.join(output_dir, uploaded_file.name)
        cv2.imwrite(output_path, cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR))
        processed_files.append((uploaded_file.name, output_path))
    
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
