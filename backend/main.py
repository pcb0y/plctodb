from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
import shutil
import uuid

from database import engine, Base
from config import settings
from models import User
from routers import auth, machines, products, parameters, templates, logs

app = FastAPI(title="挤出机工艺参数管理系统", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)

frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/frontend", StaticFiles(directory=str(frontend_path)), name="frontend")

uploads_path = frontend_path / "uploads"
if uploads_path.exists():
    app.mount("/uploads", StaticFiles(directory=str(uploads_path)), name="uploads")

app.include_router(auth.router)
app.include_router(machines.router)
app.include_router(products.router)
app.include_router(parameters.router)
app.include_router(templates.router)
app.include_router(logs.router)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    uploads_dir = Path(__file__).parent.parent / "frontend" / "uploads"
    uploads_dir.mkdir(parents=True, exist_ok=True)
    
    ext = Path(file.filename).suffix
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = uploads_dir / filename
    
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return {"url": f"/uploads/{filename}", "filename": filename}

@app.get("/")
async def root():
    return RedirectResponse(url="/frontend/index.html")

@app.on_event("startup")
async def startup():
    try:
        import pymysql
        conn = pymysql.connect(
            host=settings.DB_HOST,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            port=settings.DB_PORT
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;")
        cursor.close()
        conn.close()
        print(f"✅ 数据库 {settings.DB_NAME} 创建成功")
    except Exception as e:
        print(f"⚠️  数据库创建失败: {e}")
    
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表结构创建成功")
    
    from sqlalchemy.orm import Session
    from passlib.context import CryptContext
    
    db = Session(bind=engine)
    if not db.query(User).first():
        try:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash("admin")
            admin_user = User(username="admin", hashed_password=hashed_password, role="admin")
            db.add(admin_user)
            db.commit()
            print("✅ 默认管理员用户创建成功")
        except Exception as e:
            print(f"⚠️  创建默认管理员失败: {e}")
    db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9527)
