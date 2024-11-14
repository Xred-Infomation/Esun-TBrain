import json
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
import re


answer_dict = {"answers": []}  # 初始化字典

# 載入embedding 模型
local_path = '../local_models/intfloat_multilingual_e5_small'
embeddings = HuggingFaceEmbeddings(model_name=local_path,  model_kwargs={'device':'cuda:0'})

# 讀取題目
with open('../dataset/preliminary/question/questions_faq.json', 'r', encoding='utf-8') as file_1:
    data_1 = json.load(file_1)

questions = data_1['questions']

# 讀取答案資料集
with open('../reference/faq/pid_map_content.json', 'r', encoding='utf-8') as file_2:
    ANS = json.load(file_2)


def getAllSource(question_no_arr):
    """
    根據問題編號列表獲取對應的資料源文件。

    此函數迭代每個問題編號，調用 get_question_doc 來組成一個 Document 列表。

    參數:
        question_no_arr (list): 問題編號列表。

    回傳:
        list: 包含多個 Document 的列表，每個 Document 表示一個問題的相關資料。
    """
    docs = []
    for question_no in question_no_arr:
        docs.append(get_question_doc(question_no))
    return docs


def get_question_doc(question_no):
    """
    生成特定問題編號的 Document。

    該函數將每個問題及其答案拼接成一個文本，並去除非字母字元後建立 Document 對象。

    參數:
        question_no (int): 問題編號。

    回傳:
        Document: 包含問題及答案的文本內容和該問題編號的 Document 對象。
    """
    one_question_ref = []
    for query in ANS[str(question_no)]:
        q = query['question']
        a = ",".join(query['answers'])
        one_question_ref.append(q+a)
    text = "".join(one_question_ref)
    text =  re.sub(r'[^\w\s]', '', text)  # 会匹配所有非字母
    doc = Document(page_content=text, metadata={"source": question_no})
    return doc


def save_results_to_json(results, file_path):
    """
    將檢索結果保存到 JSON 文件。

    此函數將指定的結果字典保存為 JSON 文件，確保字符編碼為 UTF-8。

    參數:
        results (dict): 包含檢索結果的字典。
        file_path (str): 保存 JSON 文件的路徑。
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)


"""
1.根據每個題目所提供的source
2.做 embedding 再根據題目source建立索引
3.以相似性搜尋，返回分數最相近的第一筆
"""
for case_1 in questions:
    documents = getAllSource(case_1['source'])
    query = case_1['query']
    faissdb = FAISS.from_documents(documents, embedding=embeddings)
    query_result = faissdb.similarity_search_with_score(
        query, 1)
    # print(query_result[0][0].metadata.get("source"))
    # print(query, query_result)
    print(query_result[0][0])
    answer_dict['answers'].append(
        {"qid": case_1['qid'], "retrieve": query_result[0][0].metadata.get("source")})

# 將檔案存成json
save_results_to_json(
    answer_dict, "../dataset/preliminary/pred_retrieve_faq.json")


