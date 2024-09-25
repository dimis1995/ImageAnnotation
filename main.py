import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import shutil
import json
from tinydb import TinyDB, Query
import uuid

class ImageLabelingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Labeling Tool")

        # DB setup
        self.db = TinyDB('annotations_db.json')
        self.annotations_table = self.db.table('annotations')
        self.progress_table = self.db.table('progress')

        # Variables
        self.image_index = 0
        self.image_list = []
        self.folder_path = ""
        self.image = None
        self.photo = None
        self.rect = None  # For bounding box
        self.start_x = None
        self.start_y = None
        self.annotations = []  # To store bounding boxes and labels
        self.rectangles = []  # To store the created rectangles


        # Class statistics
        self.class_stats = {}  # Dictionary to store the count of annotations for each class
        # Set up UI elements
        self.setup_ui()

    def setup_ui(self):
        # Browse button
        self.browse_button = tk.Button(self.root, text="Browse Folder", command=self.browse_folder)
        self.browse_button.pack(pady=10)

        # Canvas to display images
        self.canvas = tk.Canvas(self.root, width=600, height=400)
        self.canvas.pack()

        # Bind mouse events for drawing
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        # Next button
        self.next_button = tk.Button(self.root, text="Next Image", command=self.next_image, state=tk.DISABLED)
        self.next_button.pack(pady=10)

        # Clear button
        self.clear_button = tk.Button(self.root, text="Clear Annotations", command=self.clear_annotations, state=tk.DISABLED)
        self.clear_button.pack(pady=10)

        # Show Statistics Button
        self.stats_button = tk.Button(self.root, text="Show Statistics", command=self.show_statistics)
        self.stats_button.pack(pady=10)

    def browse_folder(self):
        self.folder_path = filedialog.askdirectory(title="Select Input Folder")
        if self.folder_path:
            # Prompt for output directory only once
            self.output_folder = filedialog.askdirectory(title="Select Output Folder")
            if not self.output_folder:
                messagebox.showerror("Error", "No output folder selected!")
                return

            # Clear previous image list and index
            self.image_list = []
            self.image_index = 0
                
            # Traverse the folder and subfolders to collect image files
            for root_dir, dirs, files in os.walk(self.folder_path):
                for file in files:
                    if file.lower().endswith('bmp'):
                        self.image_list.append(os.path.join(root_dir, file))
            
            if not self.image_list:
                messagebox.showerror("Error", "No images found in the selected folder and its subfolders!")
                return
            
            # Load the saved progress for the folder
            self.load_progress()

            self.display_image()
            self.next_button.config(state=tk.NORMAL)
            self.clear_button.config(state=tk.NORMAL)

    def display_image(self):
        self.clear_annotations()
        image_path = self.image_list[self.image_index]
        self.image = Image.open(image_path)
        self.image = self.image.resize((600, 400), Image.Resampling.LANCZOS)
        self.photo = ImageTk.PhotoImage(self.image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.root.title(f"Image Labeling Tool - {os.path.basename(image_path)}")
        self.annotations.clear()  # Clear previous annotations


    def on_button_press(self, event):
        # Save the starting coordinates of the bounding box
        self.start_x = event.x
        self.start_y = event.y
        # Create a rectangle, but don't display it yet
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        # Update the rectangle as the mouse is dragged
        cur_x, cur_y = (event.x, event.y)
        if self.rect and self.start_x and self.start_y:
            self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def clear_annotations(self):
        # Clear all the rectangles from the canvas
        if len(self.rectangles) > 0:
            for rect in self.rectangles:
                self.canvas.delete(rect)
            self.rectangles.clear()
            self.annotations.clear()  # Clear all stored annotations

    def on_button_release(self, event):
        # Finalize the bounding box and ask for the class label
        end_x, end_y = (event.x, event.y)
        # Ask user for class label
        label = simpledialog.askstring("Input", "Enter class label:")
        if label:
            # Save annotation (bounding box coordinates and label)
            self.annotations.append({
                'x1': self.start_x,
                'y1': self.start_y,
                'x2': end_x,
                'y2': end_y,
                'label': label
            })
            print(f"Annotation: {self.annotations[-1]}")  # For now, just print it
            # Add the rectangle to the list of rectangles
            self.rectangles.append(self.rect)


            # Update the class statistics
            if label in self.class_stats:
                self.class_stats[label] += 1
            else:
                self.class_stats[label] = 1

        else:
            if self.rect:
                self.canvas.delete(self.rect)

    def next_image(self):
        # Save annotations for the current image before moving to the next one
        if self.annotations:
            self.save_annotations()

        # Save progress before moving to the next image
        self.save_progress()

        # Move to the next image
        self.image_index += 1
        if self.image_index >= len(self.image_list):
            messagebox.showinfo("Info", "No more images in the folder and subfolders!")
            self.next_button.config(state=tk.DISABLED)
        else:
            self.display_image()

    def save_annotations(self):
        image_path = self.image_list[self.image_index]
        if not self.output_folder:
            self.output_folder = filedialog.askdirectory(title="Select Output Folder")  # Ensure this is done once outside this method

        image_uuid = str(uuid.uuid4())
        image_extension = os.path.splitext(image_path)[1]
        new_image_name = f"{image_uuid}{image_extension}"

        # Define the output paths for the image and the annotation file
        image_output_path = os.path.join(self.output_folder, new_image_name)

        # Copy the image to the output folder
        shutil.copy(image_path, image_output_path)

        # Save annotations as a JSON file
        self.annotations_table.insert({'image_file': new_image_name, 'annotations': self.annotations})

        print(f"Annotations saved for {self.image_list[self.image_index]} to {new_image_name}")

    def load_progress(self):
        # Load progress from a progress file (if it exists)
        progress = self.progress_table.get(Query().folder == self.folder_path)
        if progress and type(progress) == dict:
            self.image_index = progress.get('image_index', 0)
        else:
            self.image_index = 0

    def save_progress(self):
        # Upsert (insert or update) the progress for the current folder
        self.progress_table.upsert({
            'folder': self.folder_path,
            'image_index': self.image_index
        }, Query().folder == self.folder_path)

        print(f"Progress saved for folder: {self.folder_path}, image index: {self.image_index}")



    def show_statistics(self):
        import matplotlib.pyplot as plt

        # Query TinyDB for all annotations
        all_annotations = self.annotations_table.all()

        # Reset class_stats and populate from database
        self.class_stats = {}
        for entry in all_annotations:
            for annotation in entry['annotations']:
                label = annotation['label']
                if label in self.class_stats:
                    self.class_stats[label] += 1
                else:
                    self.class_stats[label] = 1

        if not self.class_stats:
            messagebox.showinfo("Info", "No annotations available to display statistics.")
            return

        classes = list(self.class_stats.keys())
        counts = list(self.class_stats.values())

        plt.figure(figsize=(8, 6))
        plt.bar(classes, counts, color='skyblue')
        plt.xlabel("Classes")
        plt.ylabel("Number of Annotations")
        plt.title("Class Distribution")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

# Main application loop
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLabelingTool(root)
    root.mainloop()