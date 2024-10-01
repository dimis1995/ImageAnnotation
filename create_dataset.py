import os
import shutil
import random

# Paths to the existing dataset
images_dir = 'output'  # Path to your folder containing the images
labels_dir = 'yolo_annotations'  # Path to your folder containing .txt files
output_dir = 'dataset'

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Create train and val folders
train_images_dir = os.path.join(output_dir, 'images', 'train')
val_images_dir = os.path.join(output_dir, 'images', 'val')
train_labels_dir = os.path.join(output_dir, 'labels', 'train')
val_labels_dir = os.path.join(output_dir, 'labels', 'val')

os.makedirs(train_images_dir, exist_ok=True)
os.makedirs(val_images_dir, exist_ok=True)
os.makedirs(train_labels_dir, exist_ok=True)
os.makedirs(val_labels_dir, exist_ok=True)

# Get all image files
images = [f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp'))]
random.shuffle(images)

# Split the dataset (80% train, 20% val)
train_split = int(0.8 * len(images))

train_images = images[:train_split]
val_images = images[train_split:]

# Copy the images and labels into train and val directories
def move_files(image_list, images_source, labels_source, images_dest, labels_dest):
    for image_file in image_list:
        # Copy the image
        shutil.copy(os.path.join(images_source, image_file), os.path.join(images_dest, image_file))
        
        # Get corresponding label file
        label_file = os.path.splitext(image_file)[0] + '.txt'
        if os.path.exists(os.path.join(labels_source, label_file)):
            shutil.copy(os.path.join(labels_source, label_file), os.path.join(labels_dest, label_file))

move_files(train_images, images_dir, labels_dir, train_images_dir, train_labels_dir)
move_files(val_images, images_dir, labels_dir, val_images_dir, val_labels_dir)

# Create dataset.yaml file
classes_txt_path = 'classes.txt'  # Path to your classes.txt file
with open(classes_txt_path, 'r') as f:
    class_names = f.read().splitlines()

dataset_yaml = f"""
train: {os.path.abspath(train_images_dir)}
val: {os.path.abspath(val_images_dir)}

nc: {len(class_names)}
names: {class_names}
"""

with open(os.path.join(output_dir, 'dataset.yaml'), 'w') as f:
    f.write(dataset_yaml)

print("Dataset preparation complete!")