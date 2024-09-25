import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import shutil
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
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
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.annotations = []
        self.rectangles = []
        self.class_stats = {}

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

        # Next Image button
        self.next_button = tk.Button(self.root, text="Next Image", command=self.next_image, state=tk.DISABLED)
        self.next_button.pack(pady=10)

        # Clear annotations button
        self.clear_button = tk.Button(self.root, text="Clear Annotations", command=self.clear_annotations, state=tk.DISABLED)
        self.clear_button.pack(pady=10)

        # Create a frame for the statistics
        self.stats_frame = tk.Frame(self.root)
        self.stats_frame.pack(side=tk.RIGHT, padx=20)

        # Create an initial plot for class distribution
        self.create_statistics_plot()

    def browse_folder(self):
        self.folder_path = filedialog.askdirectory(title="Select Input Folder")
        if self.folder_path:
            self.output_folder = filedialog.askdirectory(title="Select Output Folder")
            if not self.output_folder:
                messagebox.showerror("Error", "No output folder selected!")
                return

            self.image_list = []
            self.image_index = 0
                
            for root_dir, dirs, files in os.walk(self.folder_path):
                for file in files:
                    if file.lower().endswith('bmp'):
                        self.image_list.append(os.path.join(root_dir, file))
            
            if not self.image_list:
                messagebox.showerror("Error", "No images found in the selected folder and its subfolders!")
                return
            
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
        self.annotations.clear() 


    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red')

    def on_mouse_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        if self.rect and self.start_x and self.start_y:
            self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def clear_annotations(self):
        for rect in self.rectangles:
            self.canvas.delete(rect)
        self.rectangles.clear()
        self.annotations.clear()

        self.update_statistics_plot()

    def on_button_release(self, event):
        end_x, end_y = (event.x, event.y)
        label = simpledialog.askstring("Input", "Enter class label:")
        if label:
            self.annotations.append({
                'x1': self.start_x,
                'y1': self.start_y,
                'x2': end_x,
                'y2': end_y,
                'label': label
            })
            print(f"Annotation: {self.annotations[-1]}")
            self.rectangles.append(self.rect)

            if label in self.class_stats:
                self.class_stats[label] += 1
            else:
                self.class_stats[label] = 1

        else:
            if self.rect:
                self.canvas.delete(self.rect)

    def next_image(self):
        if self.annotations:
            self.save_annotations()
        self.save_progress()
        self.image_index += 1
        if self.image_index >= len(self.image_list):
            messagebox.showinfo("Info", "No more images in the folder and subfolders!")
            self.next_button.config(state=tk.DISABLED)
        else:
            self.display_image()

    def save_annotations(self):
        image_path = self.image_list[self.image_index]

        image_uuid = str(uuid.uuid4())
        image_extension = os.path.splitext(image_path)[1]
        new_image_name = f"{image_uuid}{image_extension}"
        image_output_path = os.path.join(self.output_folder, new_image_name)
        shutil.copy(image_path, image_output_path)

        self.annotations_table.insert({
            'image_file': new_image_name,
            'annotations': self.annotations
        })

        self.update_statistics_plot()
        print(f"Annotations saved for {new_image_name}")

    def load_progress(self):
        progress = self.progress_table.get(Query().folder == self.folder_path)
        if progress and type(progress) == dict:
            self.image_index = progress.get('image_index', 0)
        else:
            self.image_index = 0

    def save_progress(self):
        self.progress_table.upsert({
            'folder': self.folder_path,
            'image_index': self.image_index
        }, Query().folder == self.folder_path)

        print(f"Progress saved for folder: {self.folder_path}, image index: {self.image_index}")

    def create_statistics_plot(self):
        self.fig, self.ax = plt.subplots(figsize=(4, 3))
        self.ax.bar([], [])
        self.stats_canvas = FigureCanvasTkAgg(self.fig, master=self.stats_frame)
        self.stats_canvas.get_tk_widget().pack()

    def update_statistics_plot(self):
        self.ax.clear()
        all_annotations = self.annotations_table.all()
        self.class_stats = {}
        for entry in all_annotations:
            for annotation in entry['annotations']:
                label = annotation['label']
                if label in self.class_stats:
                    self.class_stats[label] += 1
                else:
                    self.class_stats[label] = 1

        classes = list(self.class_stats.keys())
        counts = list(self.class_stats.values())

        self.ax.bar(classes, counts, color='skyblue')
        self.ax.set_xlabel("Classes")
        self.ax.set_ylabel("Number of Annotations")
        self.ax.set_title("Class Distribution")
        self.ax.tick_params(axis='x', rotation=45)
        self.stats_canvas.draw()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageLabelingTool(root)
    root.mainloop()