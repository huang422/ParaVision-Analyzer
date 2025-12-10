"""
Main analyzer module for parathyroid tumor analysis
"""

import os
import cv2
import json
import numpy as np
import pandas as pd
from glob import glob

from paravision_analyzer.core.features import FeatureExtractor
from paravision_analyzer.core.utils import draw_visualization


class ParathyroidTumorAnalyzer:
    """Main analyzer class for parathyroid tumor analysis"""

    def __init__(self, image_dir, json_dir, output_dir, px_per_mm=19, progress_callback=None):
        """
        Initialize analyzer

        Args:
            image_dir (str): Directory containing original images
            json_dir (str): Directory containing labelme annotation JSON files
            output_dir (str): Directory for output results
            px_per_mm (float): Pixel to millimeter conversion ratio (default: 1mm=19px)
            progress_callback (callable, optional): Callback function for progress updates
        """
        self.image_dir = image_dir
        self.json_dir = json_dir
        self.output_dir = output_dir
        self.px_per_mm = px_per_mm
        self.progress_callback = progress_callback
        self.px_to_mm = 1.0 / px_per_mm

        # Create output directories if they don't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        if not os.path.exists(os.path.join(output_dir, "visualizations")):
            os.makedirs(os.path.join(output_dir, "visualizations"))

        # Initialize feature extractor
        self.feature_extractor = FeatureExtractor(px_per_mm=px_per_mm)

        # Storage for results
        self.results = []
        self.processed_images = []

    def analyze_all_images(self):
        """Analyze all annotated images"""
        # Get all JSON files
        json_files = glob(os.path.join(self.json_dir, "*.json"))
        total_files = len(json_files)

        # Pre-load all JSON files to avoid repeated reads
        json_cache = {}
        for json_file in json_files:
            base_name = os.path.basename(json_file).replace(".json", "")
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_cache[base_name] = json.load(f)
            except Exception as e:
                print(f"Error loading JSON file {json_file}: {str(e)}")
                if self.progress_callback:
                    self.progress_callback(0, total_files, f"Error loading JSON: {base_name}")

        for idx, json_file in enumerate(json_files):
            # Get corresponding image filename from JSON filename
            base_name = os.path.basename(json_file).replace(".json", "")

            # Open supported image format files
            supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
            image_file = None
            for ext in supported_extensions:
                temp_image_file = os.path.join(self.image_dir, f"{base_name}{ext}")
                if os.path.exists(temp_image_file):
                    image_file = temp_image_file
                    break

            if os.path.exists(image_file) and base_name in json_cache:
                if self.progress_callback:
                    self.progress_callback(idx, total_files, f"Processing image: {base_name}")
                self.analyze_image(image_file, json_cache[base_name], base_name)
                self.processed_images.append(
                    os.path.join(self.output_dir, "visualizations", f"{base_name}_analysis.png")
                )
            else:
                if self.progress_callback:
                    self.progress_callback(idx, total_files, f"Image file not found: {base_name}")

        # Save CSV results only here to avoid duplicates
        self.save_results_to_csv()

    def analyze_image(self, image_path, annotation_data, base_name):
        """
        Analyze a single image and its annotation

        Args:
            image_path (str): Path to image file
            annotation_data (dict): Parsed annotation data
            base_name (str): Base filename (without extension)
        """
        # Read image file as numpy array to avoid Chinese path errors
        image_data = np.fromfile(image_path, dtype=np.uint8)
        image = cv2.imdecode(image_data, cv2.IMREAD_COLOR)

        if image is None:
            print(f"Cannot read image: {image_path}")
            return

        # Convert BGR to RGB for display
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert color image to grayscale
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Create visualization results
        visualization = image_rgb.copy()

        # Reserve space for text information in top right corner
        info_texts = []

        # Process each annotated region
        for idx, shape in enumerate(annotation_data['shapes']):
            if shape['shape_type'] == 'polygon':
                # Get polygon points
                points = np.array(shape['points'], dtype=np.int32)

                # Create mask
                mask = np.zeros(gray_image.shape, dtype=np.uint8)
                cv2.fillPoly(mask, [points], 255)

                # Calculate region area (pixel count)
                area_pixels = cv2.countNonZero(mask)

                # Calculate grayscale region statistics
                roi_gray = cv2.bitwise_and(gray_image, mask)

                # Consider only pixels within mask
                roi_pixels = roi_gray[mask > 0]

                if len(roi_pixels) > 0:
                    # Binary processing (using Otsu's method for automatic threshold)
                    _, binary = cv2.threshold(roi_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                    # Calculate statistics in binary region
                    binary_roi = binary[mask > 0]

                    # Convert polygon points to format for contour analysis
                    contour_points = points.reshape(-1, 1, 2)

                    # Calculate features using FeatureExtractor
                    intensity_features = self.feature_extractor.calculate_intensity_features(
                        roi_pixels, binary_roi
                    )
                    shape_features = self.feature_extractor.calculate_shape_features(
                        mask, contour_points
                    )
                    ellipse_features = self.feature_extractor.calculate_ellipse_features(
                        contour_points
                    )
                    glcm_features = self.feature_extractor.calculate_glcm_features(
                        gray_image, mask
                    )

                    # Calculate polygon perimeter and area
                    perimeter = cv2.arcLength(contour_points, True)
                    area_pixels = cv2.countNonZero(mask)

                    # Convert to millimeter units
                    perimeter_mm = perimeter * self.px_to_mm
                    area_mm = area_pixels * (self.px_to_mm ** 2)

                    # Store results
                    tumor_id = f"{base_name}_tumor_{idx+1}"
                    result_dict = {
                        'Image': base_name,
                        'Tumor_ID': tumor_id,
                        'Area_Pixels': area_pixels,
                        'Area_mm2': area_mm,
                        'Perimeter_Pixels': perimeter,
                        'Perimeter_mm': perimeter_mm,
                    }

                    # Merge all features
                    result_dict.update(intensity_features)
                    result_dict.update(shape_features)
                    result_dict.update(ellipse_features)
                    result_dict.update(glcm_features)

                    self.results.append(result_dict)

                    # Draw region contour on visualization image
                    cv2.polylines(visualization, [contour_points], True, (255, 0, 0), 2)

                    # Display ID at tumor center
                    centroid = np.mean(points, axis=0, dtype=np.int32)
                    cv2.putText(
                        visualization, f"{idx+1}",
                        (centroid[0], centroid[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2
                    )

                    # Collect this tumor's information for later display in top right corner
                    angle_info = "N/A"
                    major_axis_mm = "N/A"
                    if not np.isnan(ellipse_features['Ellipse_MajorAxis']):
                        major_angle = ellipse_features['Ellipse_MajorAxis_Angle']
                        angle_info = f"Angle: {major_angle:.1f} deg"
                        major_axis_mm = f"MajorAxis: {ellipse_features['Ellipse_MajorAxis_mm']:.2f} mm"

                    # Collect complete information
                    info_text = {
                        'id': idx+1,
                        'text': [
                            f"ID: {idx+1}",
                            f"Area: {area_mm:.2f} mm2",
                            f"Perimeter: {perimeter_mm:.2f} mm",
                            major_axis_mm,
                            angle_info
                        ]
                    }
                    info_texts.append(info_text)

                    # Fit and draw ellipse
                    if not np.isnan(ellipse_features['Ellipse_MajorAxis']):
                        draw_visualization(visualization, contour_points, ellipse_features)

        # Display all tumor information in top right corner
        font = cv2.FONT_HERSHEY_SIMPLEX
        y_offset = 30
        padding = 10

        for info in info_texts:
            # Calculate height of this information block
            block_height = len(info['text']) * 30

            # Display each line of information in top right corner
            for i, line in enumerate(info['text']):
                if line:  # Only display non-empty lines
                    cv2.putText(
                        visualization, line,
                        (visualization.shape[1] - 300, y_offset + i * 30),
                        font, 0.7, (255, 255, 255), 2
                    )

            # Update y starting position for next information block
            y_offset += block_height + padding

        # Save visualization results
        vis_path = os.path.join(self.output_dir, "visualizations", f"{base_name}_analysis.png")

        # Convert RGB back to BGR for cv2.imwrite
        visualization_bgr = cv2.cvtColor(visualization, cv2.COLOR_RGB2BGR)
        cv2.imwrite(vis_path, visualization_bgr)

    def save_results_to_csv(self):
        """Save all analysis results to CSV file"""
        if self.results:
            csv_path = os.path.join(self.output_dir, "parathyroid_analysis_results.csv")
            df = pd.DataFrame(self.results)
            df.to_csv(csv_path, index=False)
            print(f"Analysis results saved to: {csv_path}")
            return csv_path
        else:
            print("No analyzable images found")
            return None
