import streamlit as st
from PIL import Image, ImageOps
import io
import zipfile
import os

def process_images(images, stack_option, resize_option, border_size):
    processed_images = []

    for image in images:
        img = Image.open(image)

        # Resize Image
        if resize_option:
            img = img.resize(resize_option)

        # Add Border
        if border_size > 0:
            img = ImageOps.expand(img, border=border_size, fill='black')

        processed_images.append(img)

    # Stack Images
    if stack_option == "Horizontal":
        combined_image = Image.new('RGB', (sum(img.width for img in processed_images), max(img.height for img in processed_images)))
        x_offset = 0
        for img in processed_images:
            combined_image.paste(img, (x_offset,0))
            x_offset += img.width

    elif stack_option == "Vertical":
        combined_image = Image.new('RGB', (max(img.width for img in processed_images), sum(img.height for img in processed_images)))
        y_offset = 0
        for img in processed_images:
            combined_image.paste(img, (0,y_offset))
            y_offset += img.height

    elif stack_option == "Both":
        combined_image = Image.new('RGB', (2 * max(img.width for img in processed_images), 2 * max(img.height for img in processed_images)))
        x_offset = 0
        y_offset = 0
        for idx, img in enumerate(processed_images):
            combined_image.paste(img, (x_offset,y_offset))
            x_offset += img.width
            if (idx + 1) % 2 == 0:
                x_offset = 0
                y_offset += img.height

    return combined_image

st.title("Bulk Image Processor")

uploaded_files = st.file_uploader("Upload Images", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

stack_option = st.selectbox("Stack Images", ["Horizontal", "Vertical", "Both"])
resize_option = st.slider("Resize to (width, height)", 100, 800, (400, 400))
border_size = st.slider("Border Size", 0, 50, 0)

if st.button("Process and Download"):
    if uploaded_files:
        images = [Image.open(image) for image in uploaded_files]
        processed_image = process_images(images, stack_option, resize_option, border_size)

        # Save the processed images to a zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            img_buffer = io.BytesIO()
            processed_image.save(img_buffer, format="PNG")
            zip_file.writestr("processed_image.png", img_buffer.getvalue())

        zip_buffer.seek(0)

        st.download_button("Download ZIP", zip_buffer, "processed_images.zip", "application/zip")

    else:
        st.warning("Please upload at least one image.")
