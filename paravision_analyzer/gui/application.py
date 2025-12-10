"""
GUI application for ParaVision Analyzer
"""

import os
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import threading

from paravision_analyzer.core.analyzer import ParathyroidTumorAnalyzer


class ParathyroidAnalyzerGUI:
    """GUI application class for parathyroid analyzer"""

    def __init__(self, master):
        self.master = master
        self.master.title("ParaVision Analyzer")
        self.master.geometry("900x700")

        # Drag-related variables
        self.drag_data = {"x": 0, "y": 0, "dragging": False}
        self.image_item = None  # Save Canvas image item ID
        self.can_drag = False  # Mark whether dragging is allowed (only when zoomed in)

        # Set default directories and conversion ratio
        self.image_dir = tk.StringVar(value=os.path.join(os.getcwd(), "data", "images"))
        self.json_dir = tk.StringVar(value=os.path.join(os.getcwd(), "data", "annotations"))
        self.output_dir = tk.StringVar(value=os.path.join(os.getcwd(), "data", "results"))
        self.px_to_mm_ratio = tk.StringVar(value="19")  # Default 1mm=19px

        self.create_widgets()
        self.center_window()

        # Analysis results
        self.results_csv = None
        self.current_image_index = 0
        self.processed_images = []
        self.current_zoom = 1.0
        self.original_image = None

    def center_window(self):
        """Center the window on screen"""
        self.master.update_idletasks()
        width = self.master.winfo_width()
        height = self.master.winfo_height()
        x = (self.master.winfo_screenwidth() // 2) - (width // 2)
        y = (self.master.winfo_screenheight() // 2) - (height // 2)
        self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def create_widgets(self):
        """Create GUI widgets"""
        # Create main frame
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Settings and controls
        left_frame = ttk.Frame(main_frame, padding="5", borderwidth=2, relief="groove")
        left_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False, padx=(0, 10))

        # Right panel - Display area
        right_frame = ttk.Frame(main_frame, padding="5")
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ========== Left panel content ==========
        # Title
        title_label = ttk.Label(left_frame, text="ParaVision Analyzer", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 15))

        # Path settings area
        path_frame = ttk.LabelFrame(left_frame, text="Path Settings", padding=10)
        path_frame.pack(fill=tk.X, padx=5, pady=5)

        # Image directory
        ttk.Label(path_frame, text="Image Directory:").pack(anchor=tk.W)
        image_path_frame = ttk.Frame(path_frame)
        image_path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Entry(image_path_frame, textvariable=self.image_dir).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(image_path_frame, text="Browse", command=self.browse_image_dir).pack(side=tk.RIGHT, padx=(5, 0))

        # Annotation directory
        ttk.Label(path_frame, text="Annotation Directory:").pack(anchor=tk.W)
        json_path_frame = ttk.Frame(path_frame)
        json_path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Entry(json_path_frame, textvariable=self.json_dir).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(json_path_frame, text="Browse", command=self.browse_json_dir).pack(side=tk.RIGHT, padx=(5, 0))

        # Output directory
        ttk.Label(path_frame, text="Output Directory:").pack(anchor=tk.W)
        output_path_frame = ttk.Frame(path_frame)
        output_path_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Entry(output_path_frame, textvariable=self.output_dir).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_path_frame, text="Browse", command=self.browse_output_dir).pack(side=tk.RIGHT, padx=(5, 0))

        # Pixel to millimeter conversion ratio
        ttk.Label(path_frame, text="Conversion Ratio (1mm = ? px):").pack(anchor=tk.W)
        ratio_frame = ttk.Frame(path_frame)
        ratio_frame.pack(fill=tk.X)
        ttk.Entry(ratio_frame, textvariable=self.px_to_mm_ratio, width=8).pack(side=tk.LEFT)
        ttk.Label(ratio_frame, text="(Default: 19px)").pack(side=tk.LEFT, padx=5)

        # Analysis button and progress bar
        control_frame = ttk.LabelFrame(left_frame, text="Analysis Control", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=10)

        self.analyze_button = ttk.Button(control_frame, text="Start Analysis", command=self.start_analysis)
        self.analyze_button.pack(fill=tk.X, pady=(0, 10))

        self.progress_var = tk.DoubleVar()
        self.progress = ttk.Progressbar(control_frame, variable=self.progress_var, maximum=100)
        self.progress.pack(fill=tk.X, pady=(0, 5))

        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(control_frame, textvariable=self.status_var, wraplength=200)
        self.status_label.pack(fill=tk.X)

        # Results operation area
        results_frame = ttk.LabelFrame(left_frame, text="Results", padding=10)
        results_frame.pack(fill=tk.X, padx=5, pady=5)

        self.open_csv_button = ttk.Button(results_frame, text="Open CSV Results", command=self.open_csv, state=tk.DISABLED)
        self.open_csv_button.pack(fill=tk.X, pady=(0, 5))

        self.open_folder_button = ttk.Button(results_frame, text="Open Result Folder", command=self.open_result_folder, state=tk.DISABLED)
        self.open_folder_button.pack(fill=tk.X)

        # Copyright information
        copyright_label = ttk.Label(
            left_frame,
            text="© 2025 Tom Huang \nAll rights reserved",
            font=("Arial", 8)
        )
        copyright_label.pack(side=tk.BOTTOM, pady=10)

        # ========== Right panel content ==========
        # Image browsing area
        self.image_frame = ttk.LabelFrame(right_frame, text="Analysis Result Preview", padding=10)
        self.image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create canvas container to support zooming and panning
        self.canvas = tk.Canvas(self.image_frame, bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Add zoom and pan events to canvas
        self.canvas.bind("<MouseWheel>", self.zoom)  # Windows scroll event
        self.canvas.bind("<Button-4>", self.zoom)    # Linux scroll up
        self.canvas.bind("<Button-5>", self.zoom)    # Linux scroll down

        # Add drag functionality
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)

        # Image browsing controls
        nav_frame = ttk.Frame(self.image_frame)
        nav_frame.pack(fill=tk.X, pady=(10, 0))

        # Navigation buttons and counter
        nav_buttons_frame = ttk.Frame(nav_frame)
        nav_buttons_frame.pack(fill=tk.X)

        # Left buttons
        left_button_frame = ttk.Frame(nav_buttons_frame)
        left_button_frame.pack(side=tk.LEFT, expand=True)
        self.prev_button = ttk.Button(left_button_frame, text="Previous", command=self.show_prev_image, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT)

        # Center counter
        center_frame = ttk.Frame(nav_buttons_frame)
        center_frame.pack(side=tk.LEFT, expand=True)
        self.image_counter = ttk.Label(center_frame, text="0/0")
        self.image_counter.pack(side=tk.TOP)

        # Right buttons
        right_button_frame = ttk.Frame(nav_buttons_frame)
        right_button_frame.pack(side=tk.RIGHT, expand=True)
        self.next_button = ttk.Button(right_button_frame, text="Next", command=self.show_next_image, state=tk.DISABLED)
        self.next_button.pack(side=tk.RIGHT)

        # Zoom control buttons - centered layout
        zoom_frame = ttk.Frame(nav_frame)
        zoom_frame.pack(fill=tk.X, pady=(5, 0))

        # Center buttons
        zoom_buttons_container = ttk.Frame(zoom_frame)
        zoom_buttons_container.pack(side=tk.TOP, fill=tk.X)

        # Left padding space
        ttk.Frame(zoom_buttons_container).pack(side=tk.LEFT, expand=True)

        # Zoom buttons in center
        zoom_buttons = ttk.Frame(zoom_buttons_container)
        zoom_buttons.pack(side=tk.LEFT)

        self.zoom_out_button = ttk.Button(zoom_buttons, text="Zoom Out (-)", command=self.zoom_out, state=tk.DISABLED)
        self.zoom_out_button.pack(side=tk.LEFT, padx=5)

        self.zoom_reset_button = ttk.Button(zoom_buttons, text="Reset Zoom (100%)", command=self.zoom_reset, state=tk.DISABLED)
        self.zoom_reset_button.pack(side=tk.LEFT, padx=5)

        self.zoom_in_button = ttk.Button(zoom_buttons, text="Zoom In (+)", command=self.zoom_in, state=tk.DISABLED)
        self.zoom_in_button.pack(side=tk.LEFT, padx=5)

        # Right padding space
        ttk.Frame(zoom_buttons_container).pack(side=tk.LEFT, expand=True)

    def browse_image_dir(self):
        """Browse for image directory"""
        dirname = filedialog.askdirectory(initialdir=self.image_dir.get())
        if dirname:
            self.image_dir.set(dirname)

    def browse_json_dir(self):
        """Browse for annotation directory"""
        dirname = filedialog.askdirectory(initialdir=self.json_dir.get())
        if dirname:
            self.json_dir.set(dirname)

    def browse_output_dir(self):
        """Browse for output directory"""
        dirname = filedialog.askdirectory(initialdir=self.output_dir.get())
        if dirname:
            self.output_dir.set(dirname)

    def update_progress(self, current, total, message=""):
        """Update progress bar and status"""
        progress = int((current + 1) / total * 100)
        self.progress_var.set(progress)
        self.status_var.set(message)
        self.master.update_idletasks()

    def start_analysis(self):
        """Start analysis process"""
        # Check if paths are valid
        if not os.path.exists(self.image_dir.get()):
            messagebox.showerror("Error", "Image directory does not exist!")
            return

        if not os.path.exists(self.json_dir.get()):
            messagebox.showerror("Error", "Annotation directory does not exist!")
            return

        # Disable button
        self.analyze_button.configure(state=tk.DISABLED)

        # Reset progress
        self.progress_var.set(0)
        self.status_var.set("Starting analysis...")

        # Run analysis in new thread
        self.analysis_thread = threading.Thread(target=self.run_analysis)
        self.analysis_thread.daemon = True
        self.analysis_thread.start()

    def run_analysis(self):
        """Run analysis in background thread"""
        try:
            # Get conversion ratio
            try:
                px_per_mm = float(self.px_to_mm_ratio.get())
                if px_per_mm <= 0:
                    raise ValueError("Conversion ratio must be positive")
            except ValueError:
                messagebox.showwarning("Warning", "Invalid conversion ratio. Using default (1mm = 19px).")
                px_per_mm = 19
                self.px_to_mm_ratio.set("19")

            # Create analyzer and execute analysis
            analyzer = ParathyroidTumorAnalyzer(
                self.image_dir.get(),
                self.json_dir.get(),
                self.output_dir.get(),
                px_per_mm,
                self.update_progress
            )
            analyzer.analyze_all_images()
            self.results_csv = os.path.join(analyzer.output_dir, "parathyroid_analysis_results.csv")
            self.processed_images = analyzer.processed_images

            # Enable buttons after completion
            self.master.after(0, self.analysis_complete)
        except Exception as e:
            messagebox.showerror("Error", f"Error during analysis: {str(e)}")

    def analysis_complete(self):
        """Handle analysis completion"""
        self.status_var.set("Analysis completed")
        self.analyze_button.configure(state=tk.NORMAL)
        self.open_csv_button.configure(state=tk.NORMAL)
        self.open_folder_button.configure(state=tk.NORMAL)

        # If there are result images, display first one
        if self.processed_images:
            self.current_image_index = 0
            self.show_image(self.processed_images[0])

            # Enable navigation buttons
            self.prev_button.configure(state=tk.NORMAL)
            self.next_button.configure(state=tk.NORMAL)
            self.zoom_in_button.configure(state=tk.NORMAL)
            self.zoom_out_button.configure(state=tk.NORMAL)
            self.zoom_reset_button.configure(state=tk.NORMAL)

            # Update counter
            self.image_counter.configure(text=f"1/{len(self.processed_images)}")

        messagebox.showinfo("Complete", "Image analysis completed!")

    def open_csv(self):
        """Open CSV results file"""
        if self.results_csv and os.path.exists(self.results_csv):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(self.results_csv)
                elif os.name == 'posix':  # macOS, Linux
                    os.system(f"open '{self.results_csv}'")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open CSV file: {str(e)}")

    def open_result_folder(self):
        """Open result folder"""
        if os.path.exists(self.output_dir.get()):
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(self.output_dir.get())
                elif os.name == 'posix':  # macOS, Linux
                    os.system(f"open '{self.output_dir.get()}'")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot open result directory: {str(e)}")

    def show_image(self, image_path):
        """Display image on canvas"""
        try:
            if os.path.exists(image_path):
                self.canvas.delete("all")
                self.original_image = Image.open(image_path)
                self.current_zoom = 1.0
                self.drag_data = {"x": 0, "y": 0, "dragging": False}
                self.can_drag = False
                self.update_image()
                self.image_counter.configure(text=f"{self.current_image_index + 1}/{len(self.processed_images)}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot display image: {str(e)}")

    def update_image(self):
        """Update displayed image with current zoom"""
        if self.original_image:
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()

            if canvas_width <= 1:
                canvas_width = 600
                canvas_height = 400

            img_width, img_height = self.original_image.size
            self.canvas.delete("all")
            self.image_item = None

            if self.current_zoom == 1.0:
                scale = min(canvas_width / img_width, canvas_height / img_height)
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                resized_img = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.can_drag = False
            else:
                new_width = int(img_width * self.current_zoom)
                new_height = int(img_height * self.current_zoom)
                resized_img = self.original_image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                self.can_drag = True

            self.tk_img = ImageTk.PhotoImage(resized_img)
            x_position = (canvas_width - new_width) // 2
            y_position = (canvas_height - new_height) // 2
            self.image_item = self.canvas.create_image(x_position, y_position, anchor="nw", image=self.tk_img)

    def start_drag(self, event):
        """Start dragging"""
        if self.can_drag:
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y
            self.drag_data["dragging"] = True

    def drag(self, event):
        """Handle dragging"""
        if self.drag_data["dragging"] and self.image_item is not None and self.can_drag:
            dx = event.x - self.drag_data["x"]
            dy = event.y - self.drag_data["y"]
            self.canvas.move(self.image_item, dx, dy)
            self.drag_data["x"] = event.x
            self.drag_data["y"] = event.y

    def stop_drag(self, event=None):
        """Stop dragging"""
        self.drag_data["dragging"] = False

    def zoom(self, event):
        """Handle zoom with mouse wheel"""
        if not self.original_image:
            return

        if event.num == 4 or event.delta > 0:
            self.current_zoom *= 1.1
        elif event.num == 5 or event.delta < 0:
            self.current_zoom *= 0.9

        self.current_zoom = max(0.1, min(self.current_zoom, 5.0))
        self.update_image()

    def zoom_in(self):
        """Zoom in"""
        if self.original_image:
            self.current_zoom *= 1.2
            self.current_zoom = min(self.current_zoom, 5.0)
            self.update_image()

    def zoom_out(self):
        """Zoom out"""
        if self.original_image:
            self.current_zoom *= 0.8
            self.current_zoom = max(self.current_zoom, 0.1)
            self.update_image()

    def zoom_reset(self):
        """Reset zoom"""
        if self.original_image:
            self.current_zoom = 1.0
            self.drag_data = {"x": 0, "y": 0, "dragging": False}
            self.update_image()

    def show_prev_image(self):
        """Show previous image"""
        if self.processed_images:
            self.current_image_index = (self.current_image_index - 1) % len(self.processed_images)
            self.show_image(self.processed_images[self.current_image_index])

    def show_next_image(self):
        """Show next image"""
        if self.processed_images:
            self.current_image_index = (self.current_image_index + 1) % len(self.processed_images)
            self.show_image(self.processed_images[self.current_image_index])
