<style>
.column_style {
  color: #8B4513;
  background-color: #F0F0F0;
  border: 1px solid #ddd;
  border-radius: 5px;
}
</style>

# 副甲狀腺影像辨識
## 簡介
副甲狀腺影像辨識分析工具，從標註的腫瘤區域中提取特徵，包括大小、形狀、紋理和強度測量。此分析工具提供客觀的測量與自動化，能快速進行大量的樣本辨識與分析，協助醫療專業人員和研究人員辨識副甲狀腺特徵，可用於診斷研究和比較。

# 分析特徵欄位概述
## **基本測量**
<!--  -->

### **影像與腫瘤編號**
- **輸出欄位 :**
**<span class="column_style">Image</span>**, 
**<span class="column_style">Tumor_ID</span>**
- **說明分析 :** 原始影像檔名稱與影像中標註的腫瘤數量。

### **面積**
- **輸出欄位 :**
**<span class="column_style">Area_Pixels</span>**,
**<span class="column_style">Area_mm2</span>**
- **說明分析 :** 標註的腫瘤區域總面積，單位為像素與毫米平方，用於判斷腫瘤大小。
- **計算方式 :** Area_mm2 = Area_Pixels × (n)$^2$，n為設定的像素轉物理單位比例。

### **周長**
- **輸出欄位 :**
**<span class="column_style">Perimeter_Pixels</span>**,
**<span class="column_style">Perimeter_mm</span>**
- **說明分析 :** 標註的腫瘤區域周長，單位為像素與毫米平方，用於判斷腫瘤大小。
- **計算方式 :** 腫瘤邊界上連續點之間的歐氏距離總和，Perimeter_mm = Perimeter_Pixels × n，n為設定的像素轉物理單位比例。

## **灰階值強度特徵**
強度特徵描述腫瘤區域內灰階值的分布和統計數值。
<!--  -->

### **平均強度**
- **輸出欄位 :**
**<span class="column_style">Mean_Intensity</span>**
- **說明分析 :** 腫瘤區域內的平均像素強度，表示腫瘤的整體亮度，可能與組織密度有關。
- **計算方式 :** $\mu = \frac{1}{N} \sum_{i=1}^{N} I_i$ 其中 $I_i$ 是像素 $i$ 的強度，$N$ 是腫瘤區域中的總像素數。

### **中位數強度**
- **輸出欄位 :** **<span class="column_style">Median_Intensity</span>**
- **說明分析 :** 腫瘤區域內所有像素強度的中間值，腫瘤內亮度的中位數。
- **計算方式 :** $\text{Median Intensity} = 
  \begin{cases} 
  I_{[(n+1)/2]} & \text{若 } n \text{ 為奇數} \\
  \frac{I_{[n/2]} + I_{[(n/2)+1]}}{2} & \text{若 } n \text{ 為偶數}
  \end{cases}$

### **最小和最大強度**
- **輸出欄位 :** **<span class="column_style">Min_Intensity</span>**,
**<span class="column_style">Max_Intensity</span>**
- **說明分析 :** 腫瘤區域內所有像素強度的最小值與最大值，腫瘤內最暗和最亮的點。
- **計算方式 :** 腫瘤區域中所有像素 $i$ 的 $\min({I_i})$ 和 $\max({I_i})$

### **標準差強度**
- **輸出欄位 :** **<span class="column_style">Std_Intensity</span>**
- **說明分析 :** 測量像素強度的變異或分散程度，較高的值表示腫瘤內部的異質性較大。
- **計算方式 :**  $\sigma = \sqrt{\frac{1}{N} \sum_{i=1}^{N} (I_i - \mu)^2}$ 其中 $\mu$ 是平均強度。

### **二進制平均強度**
- **輸出欄位 :** **<span class="column_style">Binary_Mean_Intensity</span>**
- **說明分析 :** 找到最佳閾值自動區分腫瘤組織，亮度分布可反映其異質性。
- **計算方式 :** 使用Otsu's演算法對腫瘤區域二值化後的平均像素值。

### **偏度**
- **輸出欄位 :** **<span class="column_style">Skewness</span>**
- **說明分析 :** 測量強度分布的不對稱性，與組織特性的不對稱性相關。
- **計算方式 :** $\text{Skewness} = \frac{1}{N\sigma^3} \sum_{i=1}^{N} (I_i - \mu)^3$

### **峰度**
- **輸出欄位 :** **<span class="column_style">Kurtosis</span>**
- **說明分析 :** 測量強度分布的尾部重度，較高的值表示更重的尾部，更容易出現離群值的分布。
- **計算方式 :** $\text{Kurtosis} = \frac{1}{N\sigma^4} \sum_{i=1}^{N} (I_i - \mu)^4 - 3$

## **形狀特徵**
描述腫瘤區域的幾何特徵
<!--  -->

### **圓弧度**
- **輸出欄位 :** **<span class="column_style">Circularity</span>**
- **說明分析 :** 測量腫瘤形狀的圓弧程度。數值範圍0到1，值為1表示越接近圓的形狀，而較低的值表示形狀越細長或不規則。
- **計算方式 :** $\text{Circularity} = \frac{4\pi \times \text{Area}}{\text{Perimeter}^2}$

### **長寬比**
- **輸出欄位 :** **<span class="column_style">Aspect_Ratio</span>**
- **說明分析 :** 腫瘤邊界矩形的寬度與高度的比率，數值範圍大於0通常為1到10，接近1的值表示更方形的形狀，而值越大表示形狀越細長。
- **計算方式 :** $\text{Aspect Ratio} = \frac{\text{Width}}{\text{Height}}$。

### **不規則性指數**
- **輸出欄位 :** **<span class="column_style">Irregularity_Index</span>**
- **說明分析 :** 實際周長與凸包周長的比率，數值範圍大於等於1，較高的值表示腫瘤區域有凹陷突起或不規則的邊界形狀。
- **計算方式 :** $\text{Irregularity} = \frac{\text{Perimeter}}{\text{Convex Hull Perimeter}}$

### **凸性**
- **輸出欄位 :** **<span class="column_style">Convexity</span>**
- **說明分析 :** 凸包周長與實際周長的比率，數值範圍0到1，較低的值表示更凹或更不規則的形狀，是不規則指數的倒數。
- **計算方式 :** $\text{Convexity} = \frac{\text{Convex Hull Perimeter}}{\text{Perimeter}}$

### **實度(凹陷指數)**
- **輸出欄位 :** **<span class="column_style">Solidity</span>**
- **說明分析 :** 腫瘤面積與其凸包面積的比率，數值範圍0到1，較低的值表示有潛在凹痕或更凹的形狀。
- **計算方式 :** $\text{Solidity} = \frac{\text{Area}}{\text{Convex Hull Area}}$

### **Feret直徑**
- **輸出欄位 :** **<span class="column_style">Ferets_Diameter</span>**
- **說明分析 :** 表示腫瘤的最長尺寸(像素)，無論其方向如何。
- **計算方式 :** 腫瘤輪廓上任意一對點之間的最大歐氏距離。

### **Area Fraction (面積分數)**
- **輸出欄位 :** **<span class="column_style">Area_Fraction</span>**
- **說明分析 :** 腫瘤面積與其邊界矩形面積的比率，數值範圍0到1，較低的值表示邊界矩形內有空更不規則形狀。
- **計算方式 :** $\text{Area Fraction} = \frac{\text{Area}}{\text{Bounding Rectangle Area}}$

## **橢圓相關特徵**
使用直接最小二乘擬合橢圓演算法，找到最適合包含腫瘤區域輸入點的橢圓
<!--  -->

### **橢圓面積**
- **輸出欄位 :** **<span class="column_style">Ellipse_Area</span>**
- **說明分析 :** 計算擬合橢圓的橢圓面積。
- **計算方式 :** $\text{Ellipse Area} = \pi \times a \times b$ 其中 $a$ 和 $b$ 是半長軸和半短軸。

### **橢圓周長**
- **輸出欄位 :** **<span class="column_style">Ellipse_Perimeter</span>**
- **說明分析 :** 計算擬合橢圓的周長。
- **計算方式 :** $\text{Ellipse Perimeter} \approx \pi(a+b)(1 + \frac{3h}{10 + \sqrt{4-3h}})$ 其中 $h = \frac{(a-b)^2}{(a+b)^2}$

### **橢圓長短軸**
- **輸出欄位 :** **<span class="column_style">Ellipse_MajorAxis</span>**
**<span class="column_style">Ellipse_MajorAxis_mm</span>**,
**<span class="column_style">Ellipse_MinorAxis</span>**
- **說明分析 :** 擬合橢圓的長軸和短軸的長度。
- **計算方式 :** 由輪廓點的協方差矩陣的特徵值確定長短軸。

### **橢圓長短軸角度**
- **輸出欄位 :** **<span class="column_style">Ellipse_MajorAxis_Angle</span>**
**<span class="column_style">Ellipse_MinorAxis_Angle</span>**
- **說明分析 :** 擬合橢圓的長/短軸的分別與水平線在第四象限的夾角角度。
- **計算方式 :** 長/短軸分別與水平軸之間的角度，標準化到0-180°範圍。

## **紋理特徵**
紋理特徵GLCM分析像素之間的空間關係，提供了關於圖像紋理結構的資訊，描述了特定距離和方向上，兩個像素之間灰度值的聯合機率分布。
<!--  -->

### **GLCM對比度**
- **輸出欄位 :** **<span class="column_style">GLCM_Contrast</span>**
- **說明分析 :** 測量局部變化的強度，反映圖像的清晰度和紋理的深淺程度
- **計算方式 :** $\text{Contrast} = \sum_{i,j} |i-j|^2 \times p(i,j)$ 其中 $p(i,j)$是像素值 $i$ 和 $j$ 共現的機率。

### **GLCM同質性**
- **輸出欄位 :** **<span class="column_style">GLCM_Homogeneity</span>**
- **說明分析 :** 衡量灰度分布的均勻性，值越大代表紋理越平滑。
- **計算方式 :** $\text{Homogeneity} = \sum_{i,j} \frac{p(i,j)}{1+|i-j|}$

### **GLCM能量**
- **輸出欄位 :** **<span class="column_style">GLCM_Energy</span>**
- **說明分析 :** 衡量灰度分布的有序程度和均勻性，值越大代表紋理越有序。
- **計算方式 :** $\text{Energy} = \sqrt{\sum_{i,j} p(i,j)^2}$

### **GLCM相關性**
- **輸出欄位 :** **<span class="column_style">GLCM_Correlation</span>**
- **說明分析 :** 測量灰度水平與相鄰像素灰度水平的線性依賴關係，較高的值表示內部有更線性結構的紋理。
- **計算方式 :**  $\text{Correlation} = \sum_{i,j} \frac{(i-\mu_i)(j-\mu_j)p(i,j)}{\sigma_i \sigma_j}$ 其中 $\mu_i$、$\mu_j$、$\sigma_i$ 和 $\sigma_j$ 是平均值和標準差。

### **GLCM差異性**
- **輸出欄位 :** **<span class="column_style">GLCM_Dissimilarity</span>**
- **說明分析 :** 與對比度類似，但使用絕對差異而非平方差異，高差異性表示紋理差異大。
- **計算方式 :** $\text{Dissimilarity} = \sum_{i,j} |i-j| \times p(i,j)$

### **GLCM角二階矩**
- **輸出欄位 :** **<span class="column_style">GLCM_ASM</span>**
- **說明分析 :** 測量紋理的均勻性，較高的值表示更同質的紋理。
- **計算方式 :** $\text{ASM} = \sum_{i,j} p(i,j)^2$

### **GLCM熵**
- **輸出欄位 :** **<span class="column_style">GLCM_Entropy</span>**
- **說明分析 :** 測量紋理的隨機性或複雜性，較高的值表示腫瘤內部有更隨機或複雜的紋理
- **計算方式 :** $\text{Entropy} = -\sum_{i,j} p(i,j) \log_2(p(i,j))$ 其中 $p(i,j) > 0$

<div style="page-break-after: always;"></div>

<!--  -->
# 視覺化辨識結果
![辨識結果](./img/img1.png)
### **圖像區域**
- **紅色框線**:標註點的區域框線
- **綠色框線**:標註點擬合的橢圓框線
- **藍色實線**:橢圓長軸
- **黃色實現**:橢圓短軸
- **紫色虛線**:水平軸

### **文字區域**
- **ID**:影像中樣本數量編號
- **Areo**:辨識區域面積
- **Perimeter**:辨識區域周長
- **MajorAxis**:長軸長度
- **Angle**:長軸與水平線在第四象限夾角角度

<div style="page-break-after: always;"></div>

# 附錄A: 介面操作說明
<!-- # pyinstaller --onefile PatternRecognition.py -->
執行檔與使用者操作畫面，是本案影像辨識工項外提供的額外服務，讓使用者操作更方便。

### **操作步驟**
1. 選擇影像檔案資料夾路徑 **<span class="column_style">Image Directory</span>**，每次會讀取資料夾中所有影像檔進行辨識。
2. 選擇標註檔案路徑 **<span class="column_style">Annotation Directory</span>**，每次會讀取資料夾中所有標註檔與影像檔檔名匹配的資料進行辨識。
3. 注意影像檔與標註檔檔名需相同，否則無法進行辨識
4. 選擇輸出路徑 **<span class="column_style">Output Directory</span>**
5. 輸出結果會在輸出路徑中產生結構化CSV檔案與辨識圖片視覺化結果，parathyroid_analysis_results.csv為辨識結果的結構化資料，visualizations資料夾為視覺化圖片。
6. 輸入像素轉物理單位比例 **<span class="column_style">Conversion Ratio</span>**，使用者可自行依照需求調整轉換比例。
7. 執行分析按鈕進行辨識 **<span class="column_style">Start Analysis</span>**
8. 開啟輸出目錄 **<span class="column_style">Open Result Folder</span>**
9.  開啟CSV結果檔 **<span class="column_style">Open CSV Results</span>**
10. 查看辨識分析結果 **<span class="column_style">Previous</span>**, **<span class="column_style">Next</span>**，選擇上一張與下一張影像。
11. 調整查看影像大小，可使用滑鼠滾輪與拖曳 **<span class="column_style">Zoom In</span>**, **<span class="column_style">Zoom Out</span>**，**<span class="column_style">Reset Zoom</span>**

<div style="page-break-after: always;"></div>

# 附錄B: 資料準備與標註
1. 下載labelme開源影像標註工具 https://github.com/wkentaro/labelme/releases 選擇作業系統版本安裝。
2. 開啟labelme輸入影像檔，點選Create Polygons按鈕，進行閉合多邊形標註。
3. 標註座標點需要至少5個點，否則橢圓相關特徵辨識後會呈現空值，因橢圓特徵計算演算法與橢圓數學參數需要至少5個點。
4. 標註完成儲存後json格式的標註檔就是所有標註點的座標，根據座標就能分辨多邊形(腫瘤)區域
5. 將影像檔與標註檔儲存成兩兩相對的相同檔名 (預設應該就是相同檔名了ex: img1.jpg & img1.json)
6. 建議資料夾目錄存放方式，分別為影像檔資料夾與標註檔資料夾。


<script type="text/javascript" src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML"></script>
<script type="text/x-mathjax-config"> MathJax.Hub.Config({ tex2jax: {inlineMath: [['$', '$']]}, messageStyle: "none" });</script>
