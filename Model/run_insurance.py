from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import Docx2txtLoader, PyPDFLoader
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
import load_question
from collections import Counter
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain_core.prompts import PromptTemplate
import re
# import jieba  # 用於中文文本分詞
import threading
from configparser import ConfigParser

show_query_result_length = 3 # retrieve數量

# 設定檔解析器
config = ConfigParser()
config.read("../config.ini")

local_path = '../Preprocess/local_models/intfloat_multilingual_e5_small'
embeddings = HuggingFaceEmbeddings(model_name=local_path,  model_kwargs={'device':'cuda:0'})

# 預處理文件目錄
d_directory = '../Preprocess/pre_data/finance_gpt/'

# 文本分段器設定
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=120,
    chunk_overlap=50,
    length_function=len,
    is_separator_regex=False,
)

# 設定檔解析器
config = ConfigParser()
config.read("config.ini")

llm = ChatOpenAI(
    temperature=0.3,
    model_name="gpt-4o-mini",
    openai_api_key=config["OpenAI"]["API_KEY"])


def runDocument(qid, details ):
    """
    執行檔案處理與檢索匹配，將檢索結果保存至答案字典。

    對每個題目所對應的文件進行處理，生成片段，並加入到 FAISS 向量數據庫中以進行相似性檢索。

    參數:
        qid (int): 問題的編號。
        details (dict): 包含問題來源、問題內容及分類資訊的字典。
    """

    documents = []
    db = None
    # 把題目source list  全部加進來
    for i in details['source']:
        # doc = 一份 pdf 檔案
        doc = getPDfDocuemnt(
            f"../reference/{details['category']}/{i}.pdf", details['category'], i)
        if doc.page_content == "":
            # PDF Loader 無法讀取時，採用OCR預處理資料
            preprocess_text = processText(f"{i}.txt" )
        else:
            preprocess_text = doc.page_content
       
        #資料清洗
        preprocess_text = preprocess_text.replace(" ", "")       
        preprocess_text = preprocess_text.lower()
        doc_split = text_splitter.split_text(preprocess_text)
        doc_chunk = [Document(page_content=text, metadata={
                              "source": i})for text in doc_split if isinstance(text, str)]
        documents = documents + doc_chunk
    db = FAISS.from_documents(documents, embedding=embeddings)
    result = getDB_search(qid, details['query'], db)

    answer_dict['answers'].append(
        {"qid": qid, "retrieve": result})



def getDB_search(qid, question, faissdb) -> list:
    """
    根據問題在 FAISS 數據庫中進行相似性檢索，並返回檢索結果。

    參數:
        qid (int): 問題編號。
        question (str): 問題的文本內容。
        faissdb (FAISS): 用於進行相似性檢索的 FAISS 數據庫。
    """
  
    query_result = faissdb.similarity_search_with_score(
        question, k=show_query_result_length)
    
    result_str = ''
    result_list=[]  #有需要再傳回給對方API
    arr = []
    index = 0

    # 將題目source轉成Document格式
    for doc,score in query_result:
        index += 1
        arr.append(f"{doc.metadata.get('source')}({float(score):.4f})")
    
        result_str = result_str +  ( f"Document {index}:\npage_content: {doc.page_content}\nMetadata: {doc.metadata.get('source')}") + "\n\n"
        result_list.append({
                "page_content": doc.page_content,
                "metadata": doc.metadata,
                "score": float(score)  # 轉換為 float
            })
  

    # 定義輸出的 JSON 結構
    response_schemas = [
        ResponseSchema(
            name="Metadata", 
            description="Please give metadata source number. But don't add any comment in json.")
    ]

    # 創建 StructuredOutputParser
    output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
    # 將輸出格式的指示與模板結合
    format_instructions = output_parser.get_format_instructions()
    

    prompt_template = PromptTemplate(
        template=(
        "{param_retrive}"
        "問題：{param_ques}\n\n"
        "### 注意：\n"
        "- 如果問題中提到的年份是公曆（如2022年），文件中可能會使用民國年份表示（如民國111年，需減去1911）。\n"
        "- 如果問題中提到第一季，代表為1月1日至3月31日\n"
        "- 如果問題中提到第二季，代表為4月1日至6月30日\n"
        "- 如果問題中提到第三季，代表為7月1日至9月30日\n"
        "- 如果問題中提到第四季，代表為10月1日至12月31日\n"
        "- 如果問題中提到仟元，等同千元"
        "- 如果答案裡面沒有提及年分，但是題目關係度很高，也請列入考慮\n\n"
        "- 如果問題有提到表單，回答內容表單也須一樣\n\n"
        "請問我的問題在上述Document中哪一個最符合？metadata source是多少？\n"
        "{param_format}"
    ),
        input_variables=['param_ques'],
        partial_variables={'param_format': format_instructions}
    )

    # 詢問LLM題目與資料及最符合的結果
    prompt = prompt_template.format(param_ques=question,param_retrive=result_str)
    ai_msg = llm.invoke(prompt)

     # 解析LLM回傳結果
    try:
        response_json = output_parser.parse(ai_msg.content)
    except Exception as err:
        print("錯誤:", err)
        print("處理題目: ", qid, question)
        print(ai_msg.content)
        
    try:
        #AI 判斷後的答案
        return int(response_json.get("Metadata"))
    except Exception as err:
        #無法解析AI 的答案時，利用相近演算法最相近的結果為回傳值
        print("錯誤:", err)
        print(ai_msg)
        return int(query_result[0][0].metadata['source'])  


def getPDfDocuemnt(file_path, category, no) :
    """
    將 PDF 文件加載並轉換為 Document 對象。

    參數:
        file_path (str): PDF 文件的路徑。
        category (str): 文件分類。
        no (int): 文件的編號。

    回傳:
        Document: 包含文件內容和元數據的 Document 對象。
    """
    loader = PyPDFLoader(file_path)
    datas = loader.load()
    data = []
    for i in datas:
        data.append(i.page_content)
    return Document(page_content="".join(data),
                    metadata={"source": no, "category": category},)

def processText(fileName):
    """
    從指定文本文件中讀取內容並返回。

    參數:
        fileName (str): 文件名稱。

    回傳:
        str: 文件內容。
    """
    with open(d_directory + fileName, "r", encoding="utf-8") as file:
        # Read the contents of the file
        content = file.read()
    return content

def save_results_to_json(results, file_path):
    """
    將檢索結果保存到 JSON 文件。

    參數:
        results (dict): 檢索結果字典。
        file_path (str): 保存 JSON 文件的路徑。
    """
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)

# 讀取題目
dicts = load_question.getQuestion("../dataset/preliminary/question/questions_insurance.json")

results = []
answer_dict = {"answers": []}  # 初始化字典

threads = []
count = 0

# 多線程處理，加速處理速度
for qid, details in dicts.items():
    count = count + 1
  
    thread = threading.Thread(target=runDocument, args=(qid, details))
    thread.start()
    threads.append(thread)  # 將每個啟動的線程加入列表

    # 控制每8個線程後進行批次等待，避免一次啟動過多線程
    if count % 8 == 0:
        for t in threads:
            t.join()
        threads.clear()  # 清空已完成的線程列表

# 最後等待所有剩下的線程
for t in threads:
    t.join()

# 儲存最終答案結果
save_results_to_json(
    answer_dict, "../dataset/preliminary/pred_retrieve_insurance.json")
