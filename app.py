import streamlit as st
import cv2
import numpy as np
import io
import zipfile

def process_images(images, stack_option, border_size):
    processed_images = []

    for image in images:
        # Read image with OpenCV
        image_bytes = np.asarray(bytearray(image.read()), dtype=np.uint8)
        img = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)

        # Add Border
        if border_size > 0:
            img = cv2.copyMakeBorder(img, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=[0, 0, 0])

        processed_images.append(img)

    # Stack Images
    if stack_option == "Horizontal":
        combined_image = cv2.hconcat(processed_images)
    elif stack_option == "Vertical":
        combined_image = cv2.vconcat(processed_images)
    elif stack_option == "Both":
        row1 = cv2.hconcat(processed_images[:2])
        row2 = cv2.hconcat(processed_images[2:])
        combined_image = cv2.vconcat([row1, row2])

    return combined_image

st.title("Bulk Image Processor")

uploaded_files = st.file_uploader("Upload Images", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])

stack_option = st.selectbox("Stack Images", ["Horizontal", "Vertical", "Both"])
border_size = st.slider("Border Size", 0, 50, 0)

if st.button("Process and Download"):
    if uploaded_files:
        # Processing images
        processed_image = process_images(uploaded_files, stack_option, border_size)

        # Save the processed image to a zip file
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for uploaded_file in uploaded_files:
                image_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
                img = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
                if border_size > 0:
                    img = cv2.copyMakeBorder(img, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=[0, 0, 0])

                # Encode image as PNG
                is_success, buffer = cv2.imencode(".png", img)
                img_bytes = io.BytesIO(buffer)

                # Write to zip with the original file name
                zip_file.writestr(uploaded_file.name, img_bytes.getvalue())

        zip_buffer.seek(0)

        st.download_button("Download ZIP", zip_buffer, "processed_images.zip", "application/zip")

    else:
        st.warning("Please upload at least one image.")
