import uvicorn
import pandas as pd
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from sentence_transformers import SentenceTransformer, util
from transformers import AutoModel, AutoTokenizer
import torch
import json

api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print('load chatglm:')
tokenizer = AutoTokenizer.from_pretrained("THUDM/chatglm-6b", trust_remote_code=True)
model = AutoModel.from_pretrained("THUDM/chatglm-6b-int4", trust_remote_code=True).half().cuda()
model = model.eval()

print('load data:')
df = pd.read_csv('./data/info_comb.csv')
data = pd.read_csv('data/data.csv')
info = pd.read_csv('data/info.csv')
with open('./data/features.json', 'r') as f:
    features = json.load(f)

print('load embedding encoder:')
embedder = SentenceTransformer('./data/simcse-model', device='cuda')
info_embeddings = embedder.encode(df['describe'], convert_to_tensor=True)

promp_pre = "这里有一篇笔记本电脑的产品描述：\n"
promp_mid = "\n\n客户诉求是："
promp_after = "\n你是一个导购机器人，请根据客户诉求向他推荐这款产品"
print('start complete:')

@api.get("/hello")
async def hello():
    return 'hello world!'


@api.get("/chat")
async def chat(demand: str = ''):
    query_embedding = embedder.encode(demand, convert_to_tensor=True)
    cos_scores = util.cos_sim(query_embedding, info_embeddings)[0]
    match_idx = int(torch.argmax(cos_scores))
    print(f"query: {demand}\n, match: {df.at[match_idx, 'describe']}")
    
    text = data.at[df.at[match_idx, 'idx'], 'text']
    prompt = promp_pre + text + promp_mid + demand + promp_after
    suggestion, _ = model.chat(tokenizer, prompt, max_length=4096)
    return {
        "features": [
            {"label": "品牌", "value": info.at[df.at[match_idx, 'idx'], '品牌']}, 
            {"label": "型号", "value": info.at[df.at[match_idx, 'idx'], '型号']}] + [
            {"label": k, "value": v} for k, v in features[df.at[match_idx, 'idx']].items()],
        "reason": suggestion
    }


if __name__ == '__main__':
    uvicorn.run("main:api", host='0.0.0.0')
