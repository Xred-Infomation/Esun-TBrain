
from sentence_transformers import SentenceTransformer

# 定義模型名稱和保存路徑
# model_name = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
# local_path = './local_models/paraphrase_multilingual_MiniLM_L12_v2'

model_name = 'intfloat/multilingual-e5-small'
local_path = '../local_models/intfloat_multilingual_e5_small'


def download_and_save_model(model_name, local_path):
    """
    下載指定的句子嵌入模型並保存至本地。

    該函數使用 `sentence-transformers` 庫來下載指定的句子嵌入模型，以便進行多語言文本表示。下載後的模型將保存到本地
    指定的路徑，方便離線使用。用戶可根據需求切換不同模型。

    參數:
        model_name (str): Hugging Face 上的模型名稱，例如 'intfloat/multilingual-e5-small'。
        local_path (str): 本地保存模型的路徑，例如 './local_models/intfloat_multilingual_e5_small'。
    """
    # 下載並保存模型
    model = SentenceTransformer(model_name)
    model.save(local_path)

# 執行下載與保存模型
download_and_save_model(model_name, local_path)
