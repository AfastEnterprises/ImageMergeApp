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
        # Determine the number of columns
        num_columns = 2  # Change this value if you want more columns

        # Calculate the number of rows
        num_rows = (len(images) + num_columns - 1) // num_columns

        # Create a list of lists to hold images in each row
        rows = [[] for _ in range(num_rows)]

        for i, img in enumerate(images):
            row_idx = i // num_columns
            rows[row_idx].append(img)

        # Stack images in each row horizontally
        horizontal_stacked_images = [stack_images(row, 'Horizontal') for row in rows]

        # Stack all rows vertically
        new_image = stack_images(horizontal_stacked_images, 'Vertical')

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
