# 檔案說明

```plaintext
Preprocess/
├── image/                         # PDF Loader 無法解析之文件
├── output/                        # OCR 處理後的文字輸出資料夾
├── local_models/                  # 預先載入embedding模型
├── pre_data/
    ├──finance_gpt/                # GPT辨識及人工處理之文件
├── temp_images/                   # OCR暫存圖片之路徑
├── 0.saveEmbedding.py             # 載入Embedding 模型至本地
├── ocr.py                         # OCR 主執行檔

```

### 各檔案說明
* image/：PDF Loader 無法解析之文件。

* output/：OCR 處理後的文字輸出資料夾。
* local_models/: embedding模型
* pre_data/finance_gpt/：PT辨識及人工處理之文件。

* temp_images/：OCR暫存圖片之路徑。

* 0.saveEmbedding.py：載入Embedding 模型至本地。

* ocr.py：OCR 主執行檔。