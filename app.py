import streamlit as st
import cv2
import numpy as np
from ultralytics import YOLO
from io import BytesIO
import zipfile
from PIL import Image

@st.cache_resource
def load_model():
    model = YOLO("yolov8m.pt")
    return model

# Load the YOLO model
model = load_model()

# Streamlit app
st.title("Object Detection and Image Merging")

# Allow user to choose option for max border and half max space between
use_max_border_space = st.checkbox("Apply max border and half max space between for all images", value=False)

# Global option to merge images normally without detection
merge_without_detection = st.checkbox("Merge images without detection", value=False)

# Upload multiple images
uploaded_files = st.file_uploader("Choose image files...", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    images = []
    filenames = []
    
    for uploaded_file in uploaded_files:
        # Read the uploaded image
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, 1)
        images.append(img)
        filenames.append(uploaded_file.name)
    
    # Prepare a BytesIO buffer for the zip file
    zip_buffer = BytesIO()
    
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        # Process each image
        for img, filename in zip(images, filenames):
            st.image(img, channels="BGR", caption=f"Uploaded Image: {filename}")

            if merge_without_detection:
                # Concatenate images side by side without detection
                combined_img = cv2.hconcat([img, img])
            else:
                # Perform object detection
                result = model.predict(img)
                result = result[0]

                if len(result.boxes) > 0:
                    all_boxes = [box.xyxy[0].tolist() for box in result.boxes]

                    for box in result.boxes:
                        cords = box.xyxy[0].tolist()
                        cords = [round(x) for x in cords]
                        x1, y1, x2, y2 = cords
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw green rectangles

                    # Compute the minimum bounding rectangle that encloses all the bounding boxes
                    x_min = round(min(box[0] for box in all_boxes))
                    y_min = round(min(box[1] for box in all_boxes))
                    x_max = round(max(box[2] for box in all_boxes))
                    y_max = round(max(box[3] for box in all_boxes))
                    combined_box = [x_min, y_min, x_max, y_max]

                    # Calculate max border and max space between
                    max_border = min(y_min, img.shape[0] - y_max)
                    max_space_between = min(x_min, img.shape[1] - x_max)
                    border = max_border if use_max_border_space else st.slider(f"Select border size for {filename}", 0, max_border, 0)
                    space_between = max_space_between // 2 if use_max_border_space else st.slider(f"Select space between size for {filename}", 0, max_space_between, 0)

                    # Calculate borders and space between
                    y_min_border = max(y_min - border, 0)
                    y_max_border = y_max + border if y_max + border < img.shape[0] else img.shape[0]
                    x_min_border = max(x_min - border, 0)
                    x_max_border = x_max + border if x_max + border < img.shape[1] else img.shape[1]
                    x_min_bw = max(x_min - space_between, 0)
                    x_max_bw = x_max + space_between if x_max + space_between < img.shape[1] else img.shape[1]

                    # Concatenate images side by side with detected bounding boxes
                    combined_img = cv2.hconcat([
                        img[y_min_border:y_max_border, x_min_border:x_max_bw], 
                        img[y_min_border:y_max_border, x_min_bw:x_max_border]
                    ])
                else:
                    # Concatenate images side by side without bounding boxes if no objects are detected
                    combined_img = cv2.hconcat([img, img])

            # Convert combined image to RGB (OpenCV uses BGR by default)
            combined_img_rgb = cv2.cvtColor(combined_img, cv2.COLOR_BGR2RGB)

            # Display the processed image with bounding boxes
            st.image(combined_img_rgb, caption=f"Processed Image: {filename}", use_column_width=True)

            # Save the image to a buffer
            img_pil = Image.fromarray(combined_img_rgb)
            img_buffer = BytesIO()
            img_pil.save(img_buffer, format="JPEG")
            img_buffer.seek(0)

            # Write the buffer to the zip file
            zip_file.writestr(filename, img_buffer.read())

    # Provide a download link for the zip file
    st.download_button(
        label="Download all images as zip",
        data=zip_buffer.getvalue(),
        file_name="processed_images.zip",
        mime="application/zip"
    )
