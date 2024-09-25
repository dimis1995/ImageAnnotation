import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import shutil
import json

class ImageLabelingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Labeling Tool")

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

    def browse_folder(self):
        self.folder_path = filedialog.askdirectory()
        if self.folder_path:
            # Clear previous image list and index
            self.image_list = []
            self.image_index = 0
            
            # Traverse the folder and subfolders to collect image files
            for root_dir, dirs, files in os.walk(self.folder_path):
                for file in files:
                    if file.lower().endswith(('bmp')):
                        self.image_list.append(os.path.join(root_dir, file))
            
            if not self.image_list:
                messagebox.showerror("Error", "No images found in the selected folder and its subfolders!")
                return
            
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

        else:
            if self.rect:
                self.canvas.delete(self.rect)

    def next_image(self):
        # Save annotations for the current image before moving to the next one
        if self.annotations:
            self.save_annotations()

        # Move to the next image
        self.image_index += 1
        if self.image_index >= len(self.image_list):
            messagebox.showinfo("Info", "No more images in the folder and subfolders!")
            self.next_button.config(state=tk.DISABLED)
        else:
            self.display_image()

    def save_annotations(self):
        image_path = self.image_list[self.image_index]
        output_folder = filedialog.askdirectory(title="Select Output Folder")  # Ensure this is done once outside this method

        # Ensure the output folder exists
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Define the output paths for the image and the annotation file
        base_name = os.path.basename(image_path)
        image_output_path = os.path.join(output_folder, base_name)
        annotation_output_path = os.path.join(output_folder, f"{os.path.splitext(base_name)[0]}.json")

        # Copy the image to the output folder
        shutil.copy(image_path, image_output_path)

        # Save annotations as a JSON file
        with open(annotation_output_path, 'w') as f:
            json.dump(self.annotations, f, indent=4)

        print(f"Annotations saved for {base_name}")

# Main application loop
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLabelingTool(root)
    root.mainloop()