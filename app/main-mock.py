import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

api = FastAPI()
api.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@api.get("/hello")
async def hello():
    return 'hello world!'


@api.get("/chat")
async def chat(demand: str = ''):
    import time
    time.sleep(2)
    return {
        "features": [
            {"label": "品牌", "value": "联想"},
            {"label": "型号", "value": "00001"},
            {"label": "内存", "value": "16G"},
            {"label": "重量", "value": "1.5 Kg"},
            {"label": "尺寸", "value": "300 * 150 * 32 mm"},
            {"label": "log", "value": demand},
        ],
        "reason": "推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因推荐原因\n"
    }


if __name__ == '__main__':
    uvicorn.run("main:api", reload=True)
