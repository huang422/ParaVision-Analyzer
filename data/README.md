# Data Directory Structure

**IMPORTANT: This directory and its contents are NOT uploaded to Git**

This directory contains medical images, annotations, and analysis results. Due to privacy concerns and file size limitations, these files are excluded from version control (see [.gitignore](../.gitignore)).

## Directory Structure

```
data/
├── images/              # Medical images (NOT in Git)
│   ├── image_1.jpg
│   ├── image_2.png
│   └── ...
├── annotations/         # LabelMe JSON annotations (NOT in Git)
│   ├── image_1.json
│   ├── image_2.json
│   └── ...
└── results/            # Analysis output (NOT in Git)
    ├── parathyroid_analysis_results.csv
    └── visualizations/
        ├── image_1_analysis.png
        ├── image_2_analysis.png
        └── ...
```

## Setting Up Your Data

### 1. Images Directory (`images/`)

Place your medical images in this directory. Supported formats:
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)
- BMP (`.bmp`)

**Requirements:**
- Images should be properly labeled for medical analysis
- Ensure patient privacy is maintained
- Image filenames should be descriptive but not contain sensitive information

**Example:**
```
images/
├── patient_001_scan.jpg
├── patient_002_scan.png
└── sample_03.jpg
```

### 2. Annotations Directory (`annotations/`)

Place your LabelMe annotation JSON files in this directory.

**Requirements:**
- Each annotation file must have the **same filename** as its corresponding image (except extension)
- Created using [LabelMe annotation tool](https://github.com/wkentaro/labelme)
- Must contain polygon annotations with at least 5 points for ellipse feature extraction

**Example:**
```
annotations/
├── patient_001_scan.json      # Matches patient_001_scan.jpg
├── patient_002_scan.json      # Matches patient_002_scan.png
└── sample_03.json             # Matches sample_03.jpg
```

**Annotation Format:**
```json
{
  "version": "5.0.1",
  "flags": {},
  "shapes": [
    {
      "label": "tumor",
      "points": [
        [x1, y1],
        [x2, y2],
        [x3, y3],
        ...
      ],
      "group_id": null,
      "shape_type": "polygon",
      "flags": {}
    }
  ],
  "imagePath": "image.jpg",
  "imageData": null,
  "imageHeight": 1024,
  "imageWidth": 1024
}
```

### 3. Results Directory (`results/`)

This directory is automatically created when you run the analysis. It contains:

**CSV File:**
- `parathyroid_analysis_results.csv` - Structured data with all extracted features

**Visualizations:**
- `visualizations/` - Annotated images showing detected regions, fitted ellipses, and measurements

**Example Structure After Analysis:**
```
results/
├── parathyroid_analysis_results.csv
└── visualizations/
    ├── patient_001_scan_analysis.png
    ├── patient_002_scan_analysis.png
    └── sample_03_analysis.png
```

## Creating Annotations with LabelMe

### Installation

1. Download LabelMe from [GitHub Releases](https://github.com/wkentaro/labelme/releases)
2. Choose the version for your operating system (Windows, macOS, Linux)

### Usage

1. Open LabelMe application
2. Load your medical image: `File` → `Open`
3. Create polygon annotation:
   - Click `Create Polygons` button
   - Click on the image to place points around the tumor boundary
   - Right-click to close the polygon
   - **Minimum 5 points required** for ellipse calculations
4. Label the annotation (e.g., "tumor")
5. Save the annotation: `File` → `Save`
   - Saves as `[image_name].json` by default

### Best Practices

- Use at least 5-10 points per polygon for accurate ellipse fitting
- Mark the exact tumor boundary carefully
- Save annotations with matching filenames
- Keep original images and annotations backed up separately

## Data Privacy and Security

**CRITICAL REMINDERS:**

1. **Never commit medical data to Git repositories**
   - Patient privacy must be protected
   - HIPAA/GDPR compliance required for medical data
   - Use `.gitignore` to exclude data directories

2. **Secure Storage**
   - Store data on encrypted drives
   - Use secure backup solutions
   - Limit access to authorized personnel only

3. **Data Anonymization**
   - Remove patient identifiable information from filenames
   - Use anonymized IDs or codes
   - Maintain separate secure mapping of IDs to patient records

4. **Sharing Data**
   - Transfer data through secure channels only
   - Obtain proper consent and approvals
   - Follow institutional review board (IRB) guidelines

## Sample Data

For testing and demonstration purposes, you can create a sample dataset:

### Option 1: Use Test Images

Place sample non-sensitive images in `images/` and create test annotations:

```bash
# Example structure
data/images/sample_1.jpg
data/annotations/sample_1.json
```

### Option 2: Download Sample Dataset

If available, download the sample dataset from the project maintainers and extract to this directory.

## Troubleshooting

### Common Issues

**Issue:** "Image file not found" error
- **Solution:** Ensure image and annotation files have matching filenames

**Issue:** "Ellipse features are NaN"
- **Solution:** Annotations must have at least 5 points

**Issue:** "Cannot read image" error
- **Solution:** Check if the image format is supported (JPG, PNG, BMP)

**Issue:** "No analyzable images found"
- **Solution:**
  - Verify both `images/` and `annotations/` directories contain files
  - Check that filenames match exactly (except extensions)
  - Ensure JSON files are valid LabelMe format

## Getting Help

For more information:
- See the main [README.md](../README.md) for usage instructions
- Check [Instruction.md](../docs/Instruction.md) for feature descriptions
- Contact the development team for support

---

**Note:** This directory structure is maintained by `.gitkeep` files to preserve the folder hierarchy in the Git repository while excluding actual data files.
