"""LangGraph医疗诊断后端服务"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
import os
from dotenv import load_dotenv

# 在应用启动时加载环境变量
load_dotenv()

# 创建FastAPI应用
app = FastAPI(
    title="医疗诊断LangGraph服务",
    description="基于LangGraph的智能医疗诊断系统",
    version="1.0.0"
)

# 添加CORS中间件 - 使用简单配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "医疗诊断LangGraph服务运行中"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "medical-diagnosis"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
