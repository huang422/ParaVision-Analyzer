"""
Utility functions for visualization and helper operations
"""

import cv2
import numpy as np
from math import pi, cos, sin, radians


def draw_visualization(visualization, contour_points, ellipse_features):
    """
    Draw ellipse visualization on image

    Args:
        visualization (numpy.ndarray): Image to draw on
        contour_points (numpy.ndarray): Contour points
        ellipse_features (dict): Dictionary containing ellipse features
    """
    try:
        ellipse = cv2.fitEllipse(contour_points)
        center, axes, angle = ellipse

        # Draw ellipse contour
        cv2.ellipse(visualization, ellipse, (0, 255, 0), 2)

        # Determine major and minor axes
        width, height = axes
        if width > height:
            # Width greater than height, width is major axis
            major_axis_length = width / 2
            minor_axis_length = height / 2
            major_angle_rad = radians(angle)
            display_angle = angle
        else:
            # Height greater than width, height is major axis
            major_axis_length = height / 2
            minor_axis_length = width / 2
            major_angle_rad = radians(angle + 90)
            display_angle = angle + 90
            # Keep angle in 0-180 range
            if display_angle >= 180:
                display_angle -= 180

        # Calculate major axis endpoints
        x1 = int(center[0] - major_axis_length * cos(major_angle_rad))
        y1 = int(center[1] - major_axis_length * sin(major_angle_rad))
        x2 = int(center[0] + major_axis_length * cos(major_angle_rad))
        y2 = int(center[1] + major_axis_length * sin(major_angle_rad))

        # Draw major axis
        cv2.line(visualization, (x1, y1), (x2, y2), (0, 0, 255), 2)

        # Minor axis angle is always major axis angle + 90 degrees
        minor_angle_rad = major_angle_rad + pi/2

        # Calculate minor axis endpoints
        x3 = int(center[0] - minor_axis_length * cos(minor_angle_rad))
        y3 = int(center[1] - minor_axis_length * sin(minor_angle_rad))
        x4 = int(center[0] + minor_axis_length * cos(minor_angle_rad))
        y4 = int(center[1] + minor_axis_length * sin(minor_angle_rad))

        # Draw minor axis
        cv2.line(visualization, (x3, y3), (x4, y4), (255, 255, 0), 2)

        # Draw horizontal reference line to show angle (using dashed line effect)
        line_length = max(major_axis_length, 100)
        # Simulate dashed line effect with multiple short lines
        dash_length = 10
        gap_length = 5
        start_x = int(center[0] - line_length)
        end_x = int(center[0] + line_length)
        y = int(center[1])

        for x in range(start_x, end_x, dash_length + gap_length):
            line_end = min(x + dash_length, end_x)
            cv2.line(visualization, (x, y), (line_end, y), (255, 0, 255), 1)

    except Exception as e:
        print(f"Error drawing ellipse: {e}")


def validate_annotation(annotation_data):
    """
    Validate annotation data format

    Args:
        annotation_data (dict): Annotation data to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if 'shapes' not in annotation_data:
        return False

    for shape in annotation_data['shapes']:
        if 'shape_type' not in shape or 'points' not in shape:
            return False
        if shape['shape_type'] == 'polygon' and len(shape['points']) < 3:
            return False

    return True
