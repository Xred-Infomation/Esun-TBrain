import pytesseract
import os
from pdf2image import convert_from_path
from PIL import Image
import glob

def pdf_to_text(input_path, output_txt_path, dpi=450):

    """
    使用OCR將PDF檔案轉換為文字並儲存至.txt文件。

    參數:
    input_path (str): PDF檔案的路徑。
    output_txt_path (str): 輸出文字檔案的路徑。
    dpi (int): 轉換PDF頁面為圖片時的解析度（預設為450）。

    此函數的執行流程：
    1. 將PDF每頁轉換為圖片。
    2. 對每張圖片使用OCR提取文字。
    3. 將提取的文字儲存至指定的.txt文件。
    4. 清理處理過程中產生的暫存圖片。

    """

    # 設定 Tesseract 執行檔路徑
    # pytesseract.pytesseract.tesseract_cmd = r"/opt/homebrew/Cellar/tesseract/5.4.1_2/bin/tesseract"

    # 1. PDF 轉為圖片
    pages = convert_from_path(input_path, dpi, thread_count=8)

    # 建立暫存圖片資料夾
    temp_image_dir = "../Preprocess/temp_images"
    if not os.path.exists(temp_image_dir):
        os.makedirs(temp_image_dir)

    # 2. 逐頁進行 OCR 並儲存文字
    all_text = []
    for i, page in enumerate(pages):
        image_path = f"{temp_image_dir}/page_{i + 1}.png"

        # 儲存圖片
        page.save(image_path, "PNG")

        # 使用 Tesseract 進行 OCR
        text = pytesseract.image_to_string(Image.open(image_path), lang="chi_tra")
        all_text.append(text)

        # 刪除暫存的圖片
        os.remove(image_path)

    # 3. 將 OCR 文字存成 txt 檔
    with open(output_txt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(all_text))

    # 4.刪除暫存資料夾
    os.rmdir(temp_image_dir)
    print(f"OCR 完成，文字已儲存到：{output_txt_path}")


def process_all_pdfs_in_folder(folder_path, output_folder):
    """
    處理資料夾中的所有 PDF 檔案，並將 OCR 結果儲存到對應的 .txt 文件中。

    Args:
        folder_path (str): 包含 PDF 檔案的資料夾路徑。
        output_folder (str): 輸出文字檔案的資料夾路徑。

    流程:
        1. 檢查輸出資料夾是否存在，若無則建立。
        2. 找出資料夾中的所有 PDF 檔案。
        3. 對每個 PDF 檔案執行 OCR 並儲存文字。
    """

    # 建立 output 資料夾（如果不存在）
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 找到資料夾中的所有 PDF 檔案
    pdf_files = glob.glob(os.path.join(folder_path, "*.pdf"))

    # 確保資料夾內有 PDF 檔案
    if not pdf_files:
        print("沒有找到 PDF 檔案")
        return

    # 逐一處理每個 PDF 檔案
    for pdf_file in pdf_files:
        # 提取檔名（不含副檔名）
        base_name = os.path.splitext(os.path.basename(pdf_file))[0]
        output_txt_path = os.path.join(output_folder, f"{base_name}.txt")

        print(f"處理檔案：{pdf_file}")
        pdf_to_text(pdf_file, output_txt_path)

if __name__ == "__main__":
    input_folder_path ="../Preprocess/image"
    output_folder_path = "./output"  # OCR 文字輸出資料夾

    # 執行批次處理資料夾中的 PDF 檔案
    process_all_pdfs_in_folder(input_folder_path, output_folder_path)
