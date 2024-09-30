import cv2
import os

# Paths to the images and annotations
image_folder = 'output'  # Folder containing the images
annotation_folder = 'yolo_annotations'  # Folder containing the YOLO annotations
classes_file = 'classes.txt'  # File containing class names

# Load class names from the classes.txt file
with open(classes_file, "r") as f:
    classes = f.read().splitlines()

# Function to visualize bounding boxes
def visualize_annotations(image_path, annotation_path):
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not load image {image_path}")
        return

    height, width, _ = img.shape

    # Read the annotation file
    with open(annotation_path, "r") as f:
        lines = f.readlines()

        for line in lines:
            class_id, x_center, y_center, bbox_width, bbox_height = map(float, line.split())

            # Convert normalized YOLO format back to image coordinates
            x_center *= width
            y_center *= height
            bbox_width *= width
            bbox_height *= height

            x1 = int(x_center - bbox_width / 2)
            y1 = int(y_center - bbox_height / 2)
            x2 = int(x_center + bbox_width / 2)
            y2 = int(y_center + bbox_height / 2)

            # Get the class name
            class_name = classes[int(class_id)]

            # Draw the bounding box
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(img, class_name, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    # Display the image with bounding boxes
    cv2.imshow("Image with Annotations", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Loop through the images and corresponding annotation files
for image_file in os.listdir(image_folder):
    image_path = os.path.join(image_folder, image_file)

    # Find the corresponding annotation file
    annotation_file = os.path.splitext(image_file)[0] + ".txt"
    annotation_path = os.path.join(annotation_folder, annotation_file)

    if os.path.exists(annotation_path):
        visualize_annotations(image_path, annotation_path)
    else:
        print(f"No annotation found for {image_file}")