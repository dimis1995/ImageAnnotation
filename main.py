import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk # type: ignore

class ImageLabelingTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Labeling Tool")

        # Variables
        self.image_index = 0
        self.image_list = []
        self.folder_path = ""

        # Set up UI elements
        self.setup_ui()

    def setup_ui(self):
        # Browse button
        self.browse_button = tk.Button(self.root, text="Browse Folder", command=self.browse_folder)
        self.browse_button.pack(pady=10)

        # Canvas to display images
        self.canvas = tk.Canvas(self.root, width=600, height=400)
        self.canvas.pack()

        # Next button
        self.next_button = tk.Button(self.root, text="Next Image", command=self.next_image, state=tk.DISABLED)
        self.next_button.pack(pady=10)

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

    def display_image(self):
        image_path = os.path.join(self.folder_path, self.image_list[self.image_index])
        image = Image.open(image_path)
        image = image.resize((600, 400))
        self.photo = ImageTk.PhotoImage(image)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.root.title(f"Image Labeling Tool - {self.image_list[self.image_index]}")

    def next_image(self):
        self.image_index += 1
        if self.image_index >= len(self.image_list):
            messagebox.showinfo("Info", "No more images in the folder!")
            self.next_button.config(state=tk.DISABLED)
        else:
            self.display_image()

# Main application loop
if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLabelingTool(root)
    root.mainloop()