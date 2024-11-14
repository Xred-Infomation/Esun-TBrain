# AI Cup 玉山杯

組別: **TEAM_6776**

## 一、環境建置 
### Python 套件安裝 [Python：3.10.11]
先安裝套件
```cmd
pip install -r requirements.txt
```


### 安裝OCR以及設定環境變數

需先安裝[OCR 下載路徑](https://github.com/tesseract-ocr/tesseract/releases/tag/5.5.0)檔案，然後將OCR目錄設定為系統環境變數



環境變數設定 → 本機 → 內容 → 進階系統設定 → 環境變數 → 系統變數 → path → 添加路徑(以安裝位置為主) C:\Program Files\Tesseract-OCR
![image](https://hackmd.io/_uploads/H16q_ymMyl.png)


### 安裝CUDA
需先安裝[CUDA 下載路徑](https://developer.nvidia.com/cuda-toolkit-archive)檔案，然後將目錄設定為系統環境變數
![image](https://hackmd.io/_uploads/BJ73BlQzkl.png)
使用版本： `CUDA Toolkit 12.4.0 `
檢查安裝是否成功：`nvcc -V`
![image](https://hackmd.io/_uploads/rk1JLgQGye.png)

### 設定環境檔

打開`config.ini`，設定openAI api token

```python
[OpenAI]
API_KEY = 請放入你的OpenAI_API_Token
```

## 二、 預處理
### 下載embedding模型到本地
```cmd
python ./Prepocess/0.saveEmdedding.py
```

### OCR解析資料
> 若Preporcess/pre_data/finance_gpt有文檔，可略過執行這段

用OCR掃描文檔，文檔內容會存在`./Preprocess/output`
```cmd
python ./Preprocess/ocy.py
```

再手動把文檔丟入chatgpt幫忙潤稿，存到`./Preprocess/pre_data/finance_gpt`

## 三、 程式執行

### 執行預測程式
分別跑這三個程式，會產生預測結果在`./dataset/preliminary`
``` cmd
python ./Model/run_faq.py

python ./Model/run_finance.py

python ./Model/run_insurance.py
```

### 合併程式碼
再利用這支程式碼，將三個結果合併在`./dataset/question/pred_trieve.json`
```cmd
python ./Postprocess/run_merge_anwser.py
```

# 解題說明

### 一、資料集處理
1. 將PDF Loader 無法解析之文件，進行OCR辨識。如有辨識效果不佳之檔案進行手動放置Chat GPT 進行辨識並人工進行判斷建立文件內容。

### 二、預處理

1. 先將embedding模型載入本地
2. 分類questions 題型，分成三種題型，方便後續執行


### 三、程式執行

將運作程式根據題型分為三種，根據題目類型演算法方式也有調整
* faq
* finance
* insurance

### faq
> 在測試集只用embedding就有很高的成效，所以我們就不讓AI做最後判斷。
1. 同樣讀取題目，進行Embedding
Embedding模型：`intfloat_multilingual_e5_small`
2. 將Embedding最相似的結果，作為最終回傳值。
3. 產生`pred_retrieve_faq.json`檔

---

### finance
> 我們發現finance圖表分析較多，所以需要的reference內容就越長，題目大多都是需要邏輯分析比較過，才能得知，使用openAI-4o，chunk約500時，成效最好。再大再小都會影響最後效果。
> 也有用openAI-4o-mini測試，但是效果會差一點。

1. 同樣讀取題目，進行Embedding
Embedding模型：`openAI`
2. 將參考文件內容切Chunk做相近似查詢
3. 將相似結果詢問AI模型抓與題目最相似的結果；如AI無法判斷，則以Embedding最相似的結果，作為最終回傳值。
4. 產生`pred_retrieve_finance.json`檔

#### Chunk參數
| chunk_size   |      chunk_overlap | top_k |
| --- | --- | --- |
| 500 |  50 | 8 |



#### AI模型
| model | temparautre|
| --- | --- |
| ChatGpt-4o | 0.3 |

---


### insurance
> insurance題型就較為簡單，題目都是問保單的內容有無提供，並不用太多邏輯思考。
> 所以就簡單用openAI-4o-mini，chunk約120時，成效最好。
1. 同樣讀取題目，進行Embedding
Embedding模型：`intfloat_multilingual_e5_small`
2. 將參考文件內容切Chunk做相近似查詢
3. 將相似結果詢問AI模型抓與題目最相似的結果；如AI無法判斷，則以Embedding最相似的結果，作為最終回傳值。
4. 產生`pred_retrieve_insurance.json`檔

#### Chunk 參數
|  chunk_size| chunk_overlap|top_k |
|  ----  | ----| -- |
| 120    | 50 | 3 |

#### AI模型
| model | temparautre|
| --- | --- |
| ChatGpt-4o-mini | 0.3 |

----

### 四、後處理

最後將三個程式運行的json結果，合併成最終答案`pred_retrieve.json`檔



