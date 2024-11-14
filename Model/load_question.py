import json


def read_questions_from_json(file_path):
  """
    從 JSON 檔案中讀取問題資料。

    Args:
        file_path (str): JSON 檔案的路徑。

    Returns:
        list: 包含問題的列表，如果 JSON 檔案中沒有 "questions" 欄位則返回空列表。
  """
  with open(file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)
  return data.get("questions", [])


def process_questions(questions):
  """
    處理問題列表，並轉換為以問題 ID 為鍵的字典格式。

    Args:
        questions (list): 包含問題的列表，每個問題都是一個字典。

    Returns:
        dict: 以問題 ID（qid）為鍵的字典，值為包含 "source"、"query" 和 "category" 的字典。
  """
  questions_dict = {}
  for question in questions:
    qid = question.get("qid")
    questions_dict[qid] = {
        "source": question.get("source"),
        "query": question.get("query"),
        "category": question.get("category")
    }
  return questions_dict


def getQuestion(questions_file_path) -> dict:
  """
    從指定的 JSON 檔案中讀取並處理問題資料，返回以問題 ID 為鍵的字典。

    Args:
        questions_file_path (str): JSON 檔案的路徑。

    Returns:
        dict: 以問題 ID（qid）為鍵的字典，值為包含 "source"、"query" 和 "category" 的字典。
  """
  # 使用示例
  # questions_file_path = "questions_insurance.json"
  questions = read_questions_from_json(questions_file_path)
  return process_questions(questions)
