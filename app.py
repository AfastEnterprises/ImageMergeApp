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
def stack_images(images, direction, border_size):
    images_with_border = [add_border(img, border_size) for img in images]

    if direction == 'Horizontal':
        total_width = sum(img.width for img in images_with_border)
        max_height = max(img.height for img in images_with_border)
        new_image = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for img in images_with_border:
            new_image.paste(img, (x_offset, 0))
            x_offset += img.width

    elif direction == 'Vertical':
        total_height = sum(img.height for img in images_with_border)
        max_width = max(img.width for img in images_with_border)
        new_image = Image.new('RGB', (max_width, total_height))

        y_offset = 0
        for img in images_with_border:
            new_image.paste(img, (0, y_offset))
            y_offset += img.height

    elif direction == 'Both':
        # Stack horizontally first
        total_width = sum(img.width for img in images_with_border)
        max_height = max(img.height for img in images_with_border)
        horizontal_image = Image.new('RGB', (total_width, max_height))

        x_offset = 0
        for img in images_with_border:
            horizontal_image.paste(img, (x_offset, 0))
            x_offset += img.width

        # Then stack the resulting image vertically
        total_height = 2 * horizontal_image.height
        final_image = Image.new('RGB', (horizontal_image.width, total_height))
        final_image.paste(horizontal_image, (0, 0))
        final_image.paste(horizontal_image, (0, horizontal_image.height))

        return final_image

    return new_image

# Streamlit app
st.title("Bulk Image Processor")

uploaded_files = st.file_uploader("Upload Images", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

if uploaded_files:
    border_size = st.slider("Select border size", min_value=0, max_value=50, value=0)
    direction = st.selectbox("Select stacking direction", ["Horizontal", "Vertical", "Both"])

    if st.button("Process Images"):
        processed_images = []
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            processed_image = stack_images([image], direction, border_size)
            processed_images.append((processed_image, uploaded_file.name))

        # Save processed images to a zip file
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for processed_image, filename in processed_images:
                img_buffer = BytesIO()
                processed_image.save(img_buffer, format="PNG")
                zip_file.writestr(filename, img_buffer.getvalue())

        zip_buffer.seek(0)
        st.download_button("Download Processed Images", zip_buffer, "processed_images.zip", "application/zip")
