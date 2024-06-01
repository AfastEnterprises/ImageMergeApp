import streamlit as st
from PIL import Image, ImageOps
import os
import zipfile
from io import BytesIO

# Function to add border to an image
def add_border(image, border_size):
    if border_size > 0:
        return ImageOps.expand(image, border=border_size, fill='black')
    return image

# Function to stack images
def stack_images(images, direction):
    if direction == 'Horizontal':
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)
        new_image = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for img in images:
            new_image.paste(img, (x_offset, 0))
            x_offset += img.width

    elif direction == 'Vertical':
        total_height = sum(img.height for img in images)
        max_width = max(img.width for img in images)
        new_image = Image.new('RGB', (max_width, total_height))

        y_offset = 0
        for img in images:
            new_image.paste(img, (0, y_offset))
            y_offset += img.height

    elif direction == 'Both':
        # First stack images horizontally
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)
        horizontal_image = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for img in images:
            horizontal_image.paste(img, (x_offset, 0))
            x_offset += img.width

        # Then stack the resulting horizontal image vertically
        new_image = Image.new('RGB', (horizontal_image.width, 2 * horizontal_image.height))
        new_image.paste(horizontal_image, (0, 0))
        new_image.paste(horizontal_image, (0, horizontal_image.height))

    return new_image

# Streamlit app
st.title("Bulk Image Processor")

uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    border_size = st.slider("Select border size", min_value=0, max_value=50, value=0)
    direction = st.selectbox("Select stacking direction", ["Horizontal", "Vertical", "Both"])

    if st.button("Process Images"):
        images = [Image.open(file) for file in uploaded_files]
        stacked_image = stack_images(images, direction)
        final_image = add_border(stacked_image, border_size)
        
        # Save final image to a zip file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            img_buffer = BytesIO()
            final_image.save(img_buffer, format="PNG")
            zip_file.writestr("processed_image.png", img_buffer.getvalue())

        zip_buffer.seek(0)
        st.download_button("Download Processed Image", zip_buffer, "processed_image.zip", "application/zip")
