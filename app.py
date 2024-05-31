import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
import zipfile
import os
from io import BytesIO

@st.cache_resource
def load_model():
    model = YOLO("yolov8m.pt")
    return model

# Load the YOLO model
model = load_model()

# Streamlit app
st.title("Object Detection and Image Merging")

# Bulk upload images
uploaded_files = st.file_uploader("Choose images...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    # Read the first image to determine allowed ranges for border and space between
    sample_img_bytes = np.asarray(bytearray(uploaded_files[0].read()), dtype=np.uint8)
    sample_img = cv2.imdecode(sample_img_bytes, 1)
    img_height, img_width = sample_img.shape[:2]

    # Reset the file pointer to the beginning for re-reading
    uploaded_files[0].seek(0)

    # Display global sliders for max border and space between
    max_allowed_border = min(img_height, img_width) // 2
    st.write(f"Select the maximum border and space between for all images")
    border = st.slider("Select border size", 0, max_allowed_border, 0)
    space_between = st.slider("Select space between size", 0, max_allowed_border, 0)

    processed_images = []

    for uploaded_file in uploaded_files:
        # Read each uploaded image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        
        st.image(img, channels="BGR", caption=f"Uploaded Image: {uploaded_file.name}")

        # Perform object detection
        result = model.predict(img)
        result = result[0]
        all_boxes = [box.xyxy[0].tolist() for box in result.boxes]

        # Compute the minimum bounding rectangle that encloses all the bounding boxes
        x_min = round(min(box[0] for box in all_boxes))
        y_min = round(min(box[1] for box in all_boxes))
        x_max = round(max(box[2] for box in all_boxes))
        y_max = round(max(box[3] for box in all_boxes))
        combined_box = [x_min, y_min, x_max, y_max]

        # Calculate borders and space between
        y_min_border = max(y_min - border, 0)
        y_max_border = y_max + border if y_max + border < img.shape[0] else img.shape[0]
        x_min_border = max(x_min - border, 0)
        x_max_border = x_max + border if x_max + border < img.shape[1] else img.shape[1]
        x_min_bw = max(x_min - space_between, 0)
        x_max_bw = x_max + space_between if x_max + space_between < img.shape[1] else img.shape[1]

        # Concatenate images side by side
        combined_img = cv2.hconcat([
            img[y_min_border:y_max_border, x_min_border:x_max_bw], 
            img[y_min_border:y_max_border, x_min_bw:x_max_border]
        ])

        # Display the combined image
        st.image(combined_img, channels="BGR", caption=f"Combined Image for: {uploaded_file.name}")

        # Save processed image to list
        processed_images.append((uploaded_file.name, combined_img))

    # Create a zip file with all processed images
    if processed_images:
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for img_name, img in processed_images:
                img_bytes = cv2.imencode('.jpg', img)[1].tobytes()
                zip_file.writestr(img_name, img_bytes)

        # Provide download link for the zip file
        st.download_button(
            label="Download all processed images as zip",
           
