# ParaVision Analyzer
## 副甲狀腺影像辨識電腦視覺系統

[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green?logo=opencv)](https://opencv.org/)

ParaVision Analyzer是全方位醫學影像分析工具，用於自動化副甲狀腺腫瘤檢測、特徵提取和量化分析。此工具處理標註的醫學影像，提取形態學、紋理和強度特徵，為醫療專業人員和研究人員提供客觀的測量數據。

## 示範展示

![分析示範](docs/img/img1.png)

*範例輸出展示自動化腫瘤檢測，包含擬合橢圓、長短軸及量化測量數據*

## 目錄

- [概述](#概述)
- [功能特色](#功能特色)
- [安裝](#安裝)
- [快速開始](#快速開始)
- [資料目錄結構](#資料目錄結構)
- [使用方法](#使用方法)
- [特徵提取](#特徵提取)
- [專案結構](#專案結構)
- [系統需求](#系統需求)
- [文檔](#文檔)
- [授權條款](#授權條款)

## 概述

ParaVision Analyzer 是一個基於 Python 的醫學影像分析工具，專為副甲狀腺腫瘤特徵提取和量化分析而設計。系統處理帶有多邊形標註（使用 LabelMe 創建）的醫學影像，自動提取 **40+ 項特徵**，包括：

- **形態學特徵**：面積、周長、圓形度、長寬比
- **形狀描述符**：橢圓擬合、Feret 直徑、凸度、實心度
- **強度統計**：平均值、中位數、標準差、偏度、峰度
- **紋理特徵**：基於 GLCM 的特徵（對比度、同質性、能量、相關性、熵）

本工具提供使用者友善的 GUI 應用程式和命令列功能，適用於臨床工作流程和醫學研究。

## 功能特色

### 核心能力

- **自動化特徵提取**：每個標註區域提取 40+ 項量化特徵
- **批次處理**：同時處理多個影像和標註
- **視覺化分析**：生成標註影像，顯示檢測區域、擬合橢圓特徵和測量值
- **彈性單位**：可配置像素到物理單位的轉換
- **完整輸出**：結構化 CSV 結果，包含所有測量值
- **互動式 GUI**：使用者友善介面，具有即時預覽和導航功能
- **命令列介面**：可腳本化的批次處理，用於自動化
- **模組化架構**：清晰、易於維護的程式碼結構

## 安裝

### 前置需求

- **Python**：3.7 或更高版本
- **作業系統**：Windows、macOS 或 Linux

### 方法 1：使用 pip（推薦）

```bash
# 複製儲存庫
git clone https://github.com/huang422/ParaVision-Analyzer.git
cd ParaVision-Analyzer

# 安裝相依套件
pip install -r requirements.txt

# 以開發模式安裝套件
pip install -e .
```

### 方法 2：手動安裝

```bash
# 個別安裝相依套件
pip install numpy pandas opencv-python matplotlib scipy scikit-image Pillow
```

### 驗證安裝

```bash
python -c "import paravision_analyzer; print(paravision_analyzer.__version__)"
```

## 快速開始

### 使用 GUI 應用程式

```bash
# 執行 GUI
python scripts/run_gui.py
```

1. 設定您的目錄路徑：
   - **影像目錄**：`data/images`
   - **標註目錄**：`data/annotations`
   - **輸出目錄**：`data/results`
2. 配置轉換比例（預設：19 像素 = 1mm）
3. 點擊「開始分析」
4. 在預覽面板中查看結果

### 使用命令列x

```bash
python scripts/run_cli.py \
    --image-dir data/images \
    --annotation-dir data/annotations \
    --output-dir data/results \
    --px-per-mm 19
```

### 作為 Python 套件使用

```python
from paravision_analyzer import ParathyroidTumorAnalyzer

# 初始化分析器
analyzer = ParathyroidTumorAnalyzer(
    image_dir="data/images",
    json_dir="data/annotations",
    output_dir="data/results",
    px_per_mm=19
)

# 執行分析
analyzer.analyze_all_images()
```

## 資料目錄結構

### 重要提醒：資料檔案不會上傳到 Git

`data/` 目錄及其內容（醫學影像、標註和結果）基於隱私和安全考量，**已排除在 Git 之外**。詳見 [.gitignore](.gitignore)。

### 必要的目錄結構

```
data/
├── README.md            # 資料目錄文檔（包含在 Git 中）
├── images/              # 醫學影像（不在 Git 中）
│   ├── .gitkeep        # 保留目錄結構
│   ├── image_1.jpg
│   ├── image_2.png
│   └── ...
├── annotations/         # LabelMe JSON 標註（不在 Git 中）
│   ├── .gitkeep
│   ├── image_1.json     # 必須與 image_1.jpg 匹配
│   ├── image_2.json     # 必須與 image_2.png 匹配
│   └── ...
└── results/            # 分析輸出（不在 Git 中）
    ├── .gitkeep
    ├── parathyroid_analysis_results.csv
    └── visualizations/
        ├── image_1_analysis.png
        ├── image_2_analysis.png
        └── ...
```

### 設定您的資料

1. **準備影像**：
   - 將醫學影像放在 `data/images/`
   - 支援格式：JPG、JPEG、PNG、BMP
   - 確保影像已去識別化（無患者身份資訊）

2. **創建標註**：
   - 使用 [LabelMe](https://github.com/wkentaro/labelme) 標註影像
   - 將 JSON 檔案儲存在 `data/annotations/`
   - **重要**：標註檔案必須與影像具有**相同的檔名**（除了副檔名）
   - 每個多邊形至少需要 5 個點才能進行橢圓特徵提取

3. **執行分析**：
   - 結果自動生成在 `data/results/`
   - CSV 檔案包含所有提取的特徵
   - 視覺化資料夾包含標註影像

**詳細的資料設定說明，請參閱 [data/README.md](data/README.md)**

## 使用方法

### GUI 應用程式功能

GUI 提供：
- 影像、標註和輸出的路徑配置
- 即時進度追蹤
- 具有縮放和平移的影像預覽
- 瀏覽已分析的影像
- 快速存取結果（CSV 和視覺化）

### 命令列選項

```bash
python scripts/run_cli.py --help
```

**參數：**
- `--image-dir`：包含醫學影像的目錄（必填）
- `--annotation-dir`：包含 JSON 標註的目錄（必填）
- `--output-dir`：輸出結果的目錄（必填）
- `--px-per-mm`：像素到毫米的轉換比例（預設：19）

### 使用 LabelMe 創建標註

1. **安裝 LabelMe**：從 [GitHub Releases](https://github.com/wkentaro/labelme/releases) 下載
2. **開啟影像**：載入您的醫學影像
3. **創建多邊形**：
   - 點擊「創建多邊形」
   - 用至少 5 個點標記腫瘤邊界
   - 右鍵點擊關閉多邊形
4. **儲存**：標註儲存為 `[影像名稱].json`

**詳細標註說明，請參閱 [data/README.md](data/README.md)**

## 特徵提取

### 提取的特徵（40+ 項）

#### 1. 基本測量
- 面積（像素和 mm²）
- 周長（像素和 mm）
- 影像和腫瘤識別

#### 2. 強度特徵
- 平均值、中位數、最小值、最大值強度
- 標準差
- 二值化平均強度（Otsu 閾值）
- 偏度和峰度

#### 3. 形狀特徵
- 圓形度
- 長寬比
- 不規則指數
- 凸度
- 實心度
- Feret 直徑
- 面積分數

#### 4. 橢圓特徵
- 橢圓面積和周長
- 長軸和短軸長度（像素和 mm）
- 長軸和短軸角度

#### 5. 紋理特徵（GLCM）
- 對比度
- 同質性
- 能量
- 相關性
- 差異性
- ASM（角二階矩）
- 熵

### 視覺化輸出

![分析視覺化](docs/img/img1.png)

每個分析的影像顯示：
- **紅色輪廓**：標註的腫瘤邊界
- **綠色橢圓**：擬合橢圓
- **藍線**：長軸
- **黃線**：短軸
- **紫色虛線**：水平參考線
- **文字覆蓋**：ID、面積、周長、長軸、角度

**詳細特徵描述，請參閱 [docs/Instruction.md](docs/Instruction.md)**

## 專案結構

```
ParaVision-Analyzer/
├── paravision_analyzer/       # 主套件
│   ├── __init__.py           # 套件初始化
│   ├── core/                 # 核心分析模組
│   │   ├── __init__.py
│   │   ├── analyzer.py       # 主分析類別
│   │   ├── features.py       # 特徵提取
│   │   └── utils.py          # 工具函數
│   └── gui/                  # GUI 應用程式
│       ├── __init__.py
│       └── application.py    # GUI 實作
├── scripts/                   # 執行腳本
│   ├── run_gui.py            # 啟動 GUI
│   └── run_cli.py            # 命令列介面
├── data/                      # 資料目錄（不在 Git 中）
│   ├── README.md             # 資料設定說明
│   ├── images/               # 醫學影像
│   ├── annotations/          # LabelMe 標註
│   └── results/              # 分析輸出
├── docs/                      # 文檔
│   ├── Instruction.md        # 特徵描述
│   └── img/                  # 文檔影像
├── quick_start.py             # 主要入口點
├── requirements.txt           # Python 相依套件
├── .gitignore                 # Git 忽略規則
└── README.md                  # 英文文檔
```

## 系統需求

### 軟體需求

- **Python**：3.7 或更高版本
- **作業系統**：Windows、macOS 或 Linux

### Python 相依套件

- `opencv-python` (cv2)：影像處理和電腦視覺
- `numpy`：數值計算
- `pandas`：資料處理和 CSV 輸出
- `matplotlib`：視覺化和繪圖
- `scipy`：統計分析
- `scikit-image`：紋理特徵提取（GLCM）
- `Pillow` (PIL)：GUI 的影像處理
- `tkinter`：GUI 框架（通常隨 Python 內建）

### 硬體需求

- **記憶體**：最低 4GB，建議 8GB
- **儲存空間**：足夠的空間用於影像和結果
- **顯示器**：GUI 最低解析度 1280x720

## 文檔

- **[README.md](README.md)** - 英文文檔
- **[README_zh-TW.md](README_zh-TW.md)** - 本文件（繁體中文）
- **[docs/Instruction.md](docs/Instruction.md)** - 詳細特徵描述和計算
- **[data/README.md](data/README.md)** - 資料目錄設定和指南

## 貢獻

這是一個為醫學研究開發的專有專案。貢獻僅限於授權人員。

## 授權條款

© 2025 Tom Huang. All rights reserved.

This software is released under the MIT License.

### 第三方工具

- [LabelMe](https://github.com/wkentaro/labelme)：影像標註工具
- [OpenCV](https://opencv.org/)：電腦視覺函式庫
- [scikit-image](https://scikit-image.org/)：Python 影像處理

## 聯絡方式

如有問題、議題或合作諮詢：
- **Developer**：Tom Huang
- **Email**：huang1473690@gmail.com

## 疑難排解

### 常見問題

**問題**：「找不到影像檔案」
- **解決方案**：確保影像和標註檔名匹配（除了副檔名）

**問題**：「橢圓特徵為 NaN」
- **解決方案**：標註必須至少有 5 個點

**問題**：「無法讀取影像」
- **解決方案**：檢查影像格式是否支援（JPG、PNG、BMP）

**問題**：「找不到可分析的影像」
- **解決方案**：
  - 驗證 `data/images/` 和 `data/annotations/` 包含匹配的檔案
  - 檢查檔名是否完全匹配（除了副檔名）
  - 確保 JSON 檔案為有效的 LabelMe 格式

**更多疑難排解，請參閱 [data/README.md](data/README.md)**

---

**版本**：1.0.0
**最後更新**：April 2025
**狀態**：Production Ready

**語言**：[English](README.md) | [繁體中文](README_zh-TW.md)
