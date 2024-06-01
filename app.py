import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import tempfile

def stack_images(image, mode, border_size):
    if border_size > 0:
        image = cv2.copyMakeBorder(image, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT)
    
    if mode == 'Horizontal':
        stacked_image = np.hstack([image, image])
    elif mode == 'Vertical':
        stacked_image = np.vstack([image, image])
    elif mode == 'Both':
        stacked_image = np.hstack([image, image])
        stacked_image = np.vstack([stacked_image, stacked_image])
    else:
        stacked_image = image
        
    return stacked_image

st.title("Bulk Image Processor")

uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
mode = st.selectbox("Choose how to stack images", ["None", "Horizontal", "Vertical", "Both"])
border_size = st.slider("Select border size", 0, 50, 0)

if uploaded_files:
    output_dir = tempfile.mkdtemp()
    for uploaded_file in uploaded_files:
        image = np.array(Image.open(uploaded_file))
        processed_image = stack_images(image, mode, border_size)
        output_path = os.path.join(output_dir, uploaded_file.name)
        cv2.imwrite(output_path, cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR))
        st.image(processed_image, caption=uploaded_file.name, use_column_width=True)
    
    st.success("Processing complete. Download your files below:")
    
    for file_name in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "rb") as file:
            btn = st.download_button(
                label=f"Download {file_name}",
                data=file,
                file_name=file_name,
                mime="image/png"
            )
