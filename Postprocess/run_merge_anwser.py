import json

def merge_json_files(file1, file2, file3, output_file):
    """
    合併三個 JSON 文件中的 'answers' 列表，根據 'qid' 排序後，儲存到新的 JSON 文件中。

    此函數會讀取三個包含 'answers' 鍵的 JSON 文件，將此鍵下的列表合併後依 'qid' 欄位排序，
    並將結果寫入指定的輸出 JSON 文件中。

    參數:
        file1 (str): 第一個 JSON 文件的路徑。
        file2 (str): 第二個 JSON 文件的路徑。
        file3 (str): 第三個 JSON 文件的路徑。
        output_file (str): 合併並排序後的 JSON 數據儲存路徑。

    """
    # 讀取三個 JSON 檔案的內容
    with open(file1, 'r') as f1, open(file2, 'r') as f2, open(file3, 'r') as f3:
        data1 = json.load(f1)
        data2 = json.load(f2)
        data3 = json.load(f3)
    
    # 合併三個 JSON 檔案的 'answers' 列表
    merged_data = data1['answers'] + data2['answers'] + data3['answers']
    
    sorted_data = sorted(merged_data, key=lambda x: x["qid"])

    # 將合併後的數據寫入到一個新的 JSON 檔案
    with open(output_file, 'w') as f_out:
        json.dump({'answers': sorted_data}, f_out, indent=4)

#  使用範例
insurance_path = "dataset/preliminary/pred_retrieve_insurance.json"
finance_path = "dataset/preliminary/pred_retrieve_finance.json"
faq_path = "dataset/preliminary/pred_retrieve_faq.json"
answer_path ="dataset/preliminary/pred_retrieve.json"

merge_json_files(insurance_path,finance_path ,faq_path ,answer_path)
