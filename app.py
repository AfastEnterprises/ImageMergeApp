import streamlit as st
import cv2
import numpy as np
from PIL import Image
import os
import tempfile
import zipfile

def stack_images(images, mode):
    stacked_image = np.concatenate(images, axis=0 if mode == "Vertical" else 1)
    return stacked_image

def add_border(image, border_size):
    if border_size > 0:
        image = cv2.copyMakeBorder(image, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT)
    return image

st.title("Bulk Image Processor")

uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
mode = st.selectbox("Choose how to stack images", ["Horizontal", "Vertical"])
border_size = st.slider("Select border size", 0, 50, 0)

if uploaded_files:
    images = []
    for uploaded_file in uploaded_files:
        image = np.array(Image.open(uploaded_file))
        images.append(image)
    
    stacked_image = stack_images(images, mode)
    processed_image = add_border(stacked_image, border_size)
    
    output_dir = tempfile.mkdtemp()
    output_path = os.path.join(output_dir, "processed_image.png")
    cv2.imwrite(output_path, cv2.cvtColor(processed_image, cv2.COLOR_RGB2BGR))
    
    st.image(processed_image, caption="Processed Image", use_column_width=True)
    
    st.success("Processing complete. Download your file below:")
    
    with open(output_path, 'rb') as f:
        btn = st.download_button(
            label='Download processed image',
            data=f,
            file_name='processed_image.png',
            mime='image/png'
        )
