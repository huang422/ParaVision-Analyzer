"""
Feature extraction module for parathyroid tumor analysis

This module contains all feature extraction functions including:
- Shape features
- Intensity features
- Texture features (GLCM)
- Ellipse fitting features
"""

import cv2
import numpy as np
from scipy import stats
from skimage.feature import graycomatrix, graycoprops
from math import pi, sqrt


class FeatureExtractor:
    """Feature extraction class for tumor analysis"""

    def __init__(self, px_per_mm=19):
        """
        Initialize feature extractor

        Args:
            px_per_mm (float): Pixel to millimeter conversion ratio (default: 19)
        """
        self.px_per_mm = px_per_mm
        self.px_to_mm = 1.0 / px_per_mm

    def calculate_glcm_features(self, roi_gray, mask):
        """
        Calculate Gray Level Co-occurrence Matrix (GLCM) texture features

        Args:
            roi_gray (numpy.ndarray): Grayscale region of interest
            mask (numpy.ndarray): Binary mask for the tumor region

        Returns:
            dict: Dictionary containing GLCM features
        """
        try:
            # Ensure ROI is large enough for GLCM calculation
            if np.count_nonzero(mask) > 25:  # At least 5x5 region needed
                # Extract minimum rectangle containing the tumor
                y_indices, x_indices = np.where(mask > 0)
                top, bottom = np.min(y_indices), np.max(y_indices)
                left, right = np.min(x_indices), np.max(x_indices)

                # Ensure extracted region is at least 2x2
                if right - left < 1 or bottom - top < 1:
                    raise ValueError("ROI too small for GLCM calculation")

                # Extract ROI
                roi_small = roi_gray[top:bottom+1, left:right+1]
                mask_small = mask[top:bottom+1, left:right+1]

                # Create image containing only tumor region
                roi_tumor_only = np.zeros_like(roi_small)
                roi_tumor_only[mask_small > 0] = roi_small[mask_small > 0]

                # Scale grayscale range to fewer levels to avoid sparse GLCM
                levels = 8
                roi_rescaled = (roi_tumor_only // (256 // levels)).astype(np.uint8)

                # Remove all zero pixels (not part of tumor region)
                non_zero_mask = roi_rescaled > 0

                # If non-zero portion is too small, can't calculate GLCM
                if np.count_nonzero(non_zero_mask) < 4:
                    raise ValueError("Effective ROI too small for GLCM calculation")

                # Calculate GLCM (distance=1, angles=[0, 45, 90, 135] degrees)
                glcm = graycomatrix(
                    roi_rescaled, [1],
                    [0, np.pi/4, np.pi/2, 3*np.pi/4],
                    levels=levels,
                    symmetric=True,
                    normed=True
                )

                # Calculate GLCM properties
                contrast = np.mean(graycoprops(glcm, 'contrast')[0])
                homogeneity = np.mean(graycoprops(glcm, 'homogeneity')[0])
                energy = np.mean(graycoprops(glcm, 'energy')[0])
                correlation = np.mean(graycoprops(glcm, 'correlation')[0])
                dissimilarity = np.mean(graycoprops(glcm, 'dissimilarity')[0])
                ASM = np.mean(graycoprops(glcm, 'ASM')[0])

                # Calculate entropy
                glcm_flat = glcm.flatten()
                glcm_flat = glcm_flat[glcm_flat > 0]
                entropy = -np.sum(glcm_flat * np.log2(glcm_flat)) if len(glcm_flat) > 0 else np.nan
            else:
                raise ValueError("ROI too small for GLCM calculation")
        except Exception as e:
            print(f"Error in GLCM calculation: {e}")
            contrast = homogeneity = energy = correlation = dissimilarity = ASM = entropy = np.nan

        return {
            'GLCM_Contrast': contrast,
            'GLCM_Homogeneity': homogeneity,
            'GLCM_Energy': energy,
            'GLCM_Correlation': correlation,
            'GLCM_Dissimilarity': dissimilarity,
            'GLCM_ASM': ASM,
            'GLCM_Entropy': entropy
        }

    def calculate_ellipse_features(self, points):
        """
        Calculate ellipse fitting features

        Args:
            points (numpy.ndarray): Contour points

        Returns:
            dict: Dictionary containing ellipse features
        """
        if len(points) < 5:  # At least 5 points needed to fit ellipse
            return {
                'Ellipse_Area': np.nan,
                'Ellipse_Perimeter': np.nan,
                'Ellipse_MajorAxis': np.nan,
                'Ellipse_MajorAxis_mm': np.nan,
                'Ellipse_MinorAxis': np.nan,
                'Ellipse_MajorAxis_Angle': np.nan,
                'Ellipse_MinorAxis_Angle': np.nan
            }

        try:
            # Use OpenCV's ellipse fitting function
            ellipse = cv2.fitEllipse(points)
            center, axes, angle = ellipse

            # Get major and minor axes
            a, b = axes[0] / 2, axes[1] / 2  # Convert to semi-major and semi-minor
            major_axis = max(a, b) * 2
            minor_axis = min(a, b) * 2

            # Calculate ellipse area
            ellipse_area = pi * a * b

            # Use Ramanujan's formula to approximate ellipse perimeter
            h = ((a - b) ** 2) / ((a + b) ** 2)
            ellipse_perimeter = pi * (a + b) * (1 + 3*h / (10 + sqrt(4 - 3*h)))

            # Determine major axis angle
            if a >= b:  # If horizontal axis is major axis
                major_angle = angle
            else:  # If vertical axis is major axis
                major_angle = angle + 90

            # Normalize angle to 0-180 degrees
            major_angle = major_angle % 180

            # Minor axis angle is always perpendicular to major axis
            minor_angle = (major_angle + 90) % 180

            major_axis_mm = major_axis * self.px_to_mm

            return {
                'Ellipse_Area': ellipse_area,
                'Ellipse_Perimeter': ellipse_perimeter,
                'Ellipse_MajorAxis': major_axis,
                'Ellipse_MajorAxis_mm': major_axis_mm,
                'Ellipse_MinorAxis': minor_axis,
                'Ellipse_MajorAxis_Angle': major_angle,
                'Ellipse_MinorAxis_Angle': minor_angle
            }
        except Exception as exc:
            print(f"Error calculating ellipse features: {str(exc)}")
            return {
                'Ellipse_Area': np.nan,
                'Ellipse_Perimeter': np.nan,
                'Ellipse_MajorAxis': np.nan,
                'Ellipse_MajorAxis_mm': np.nan,
                'Ellipse_MinorAxis': np.nan,
                'Ellipse_MajorAxis_Angle': np.nan,
                'Ellipse_MinorAxis_Angle': np.nan
            }

    def calculate_shape_features(self, mask, points):
        """
        Calculate shape features

        Args:
            mask (numpy.ndarray): Binary mask
            points (numpy.ndarray): Contour points

        Returns:
            dict: Dictionary containing shape features
        """
        area = cv2.countNonZero(mask)
        perimeter = cv2.arcLength(points, True)

        # Calculate circularity (4π * Area / Perimeter²)
        circularity = 4 * pi * area / (perimeter ** 2) if perimeter > 0 else np.nan
        circularity = 1.0 if circularity > 1 else circularity

        # Calculate convex hull
        hull = cv2.convexHull(points)
        hull_area = cv2.contourArea(hull)
        hull_perimeter = cv2.arcLength(hull, True)

        # Calculate convexity = convex hull perimeter / actual perimeter
        convexity = hull_perimeter / perimeter if perimeter > 0 else np.nan
        convexity = 1.0 if convexity > 1 else convexity

        # Calculate solidity = region area / convex hull area
        solidity = area / hull_area if hull_area > 0 else np.nan
        solidity = 1.0 if solidity > 1 else solidity

        # Calculate irregularity index = actual perimeter / convex hull perimeter
        irregularity = perimeter / hull_perimeter if hull_perimeter > 0 else np.nan

        # Calculate aspect ratio (using bounding rectangle)
        x, y, w, h = cv2.boundingRect(points)
        if w >= h:
            aspect_ratio = w / h
        elif w < h:
            aspect_ratio = h / w
        else:
            aspect_ratio = np.nan

        # Calculate Feret's Diameter - maximum distance between any two points
        max_distance = 0
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                dist = np.sqrt((points[i][0][0] - points[j][0][0])**2 +
                             (points[i][0][1] - points[j][0][1])**2)
                if dist > max_distance:
                    max_distance = dist

        # Calculate area fraction = region area / bounding rectangle area
        area_fraction = area / (w * h) if (w * h) > 0 else np.nan

        return {
            'Circularity': circularity,
            'Aspect_Ratio': aspect_ratio,
            'Irregularity_Index': irregularity,
            'Convexity': convexity,
            'Solidity': solidity,
            'Ferets_Diameter': max_distance,
            'Area_Fraction': area_fraction
        }

    def calculate_intensity_features(self, roi_pixels, binary_roi):
        """
        Calculate intensity-based features

        Args:
            roi_pixels (numpy.ndarray): Pixel intensities in ROI
            binary_roi (numpy.ndarray): Binary ROI pixels

        Returns:
            dict: Dictionary containing intensity features
        """
        if len(roi_pixels) == 0:
            return {
                'Mean_Intensity': np.nan,
                'Median_Intensity': np.nan,
                'Min_Intensity': np.nan,
                'Max_Intensity': np.nan,
                'Std_Intensity': np.nan,
                'Binary_Mean_Intensity': np.nan,
                'Skewness': np.nan,
                'Kurtosis': np.nan
            }

        mean_intensity = np.mean(roi_pixels)
        median_intensity = np.median(roi_pixels)
        max_intensity = np.max(roi_pixels)
        min_intensity = np.min(roi_pixels)
        std_intensity = np.std(roi_pixels)
        binary_mean = np.mean(binary_roi)

        # Calculate higher-order statistics
        skewness = stats.skew(roi_pixels) if len(roi_pixels) > 2 else np.nan
        kurtosis = stats.kurtosis(roi_pixels) if len(roi_pixels) > 3 else np.nan

        return {
            'Mean_Intensity': mean_intensity,
            'Median_Intensity': median_intensity,
            'Min_Intensity': min_intensity,
            'Max_Intensity': max_intensity,
            'Std_Intensity': std_intensity,
            'Binary_Mean_Intensity': binary_mean,
            'Skewness': skewness,
            'Kurtosis': kurtosis
        }
