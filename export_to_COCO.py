import os
import cv2
from tinydb import TinyDB

# Load TinyDB database
db = TinyDB('annotations_db.json')
annotations_table = db.table('annotations')

# Output folder for converted annotations
output_folder = 'yolo_annotations'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Class-to-ID mapping
class_mapping = {}
class_id_counter = 0

# Create the classes.txt file
classes_file = open("classes.txt", "w")

# Loop through annotations in TinyDB
for record in annotations_table.all():
    image_file = record['image_file']
    annotations = record['annotations']
    original_width = record['original_width']
    original_height = record['original_height']

    # Load the resized image (assuming it's 600x400)
    resized_width, resized_height = 600, 400

    # Create a .txt file for each image in YOLO format
    annotation_filename = os.path.splitext(image_file)[0] + ".txt"
    annotation_file_path = os.path.join(output_folder, annotation_filename)
    
    with open(annotation_file_path, "w") as f:
        for annotation in annotations:
            x1, y1, x2, y2 = annotation['x1'], annotation['y1'], annotation['x2'], annotation['y2']
            label = annotation['label']

            # Dynamically assign class ID if not already assigned
            if label not in class_mapping:
                class_mapping[label] = class_id_counter
                classes_file.write(f"{label}\n")  # Write class to classes.txt
                class_id_counter += 1

            class_id = class_mapping[label]

            # Convert coordinates from resized 600x400 to original size
            x1 = int(x1 * original_width / resized_width)
            y1 = int(y1 * original_height / resized_height)
            x2 = int(x2 * original_width / resized_width)
            y2 = int(y2 * original_height / resized_height)

            # Convert to YOLO format (normalize values)
            x_center = ((x1 + x2) / 2) / original_width
            y_center = ((y1 + y2) / 2) / original_height
            bbox_width = (x2 - x1) / original_width
            bbox_height = (y2 - y1) / original_height

            # Write the YOLO annotation
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {bbox_width:.6f} {bbox_height:.6f}\n")

# Close the classes.txt file
classes_file.close()

print("Annotations and class mapping converted to YOLO format.")