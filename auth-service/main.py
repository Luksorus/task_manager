from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="Auth Service", version="1.0.0")

# Модель данных
class User(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Имитация базы данных
fake_users_db = [
    {"username": "admin", "password": "admin123", "email": "admin@example.com"},
    {"username": "user", "password": "user123", "email": "user@example.com"}
]

@app.get("/")
def read_root():
    return {"message": "Auth Service is running", "status": "active"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "auth-service",
        "version": "1.0.0",
        "timestamp": "2024-01-15T10:00:00Z"
    }

@app.post("/register")
def register_user(user: User):
    # Проверка существования пользователя
    for existing_user in fake_users_db:
        if existing_user["username"] == user.username:
            raise HTTPException(status_code=400, detail="User already exists")
    
    # Добавление нового пользователя
    new_user = {
        "username": user.username,
        "password": user.password,
        "email": user.email
    }
    fake_users_db.append(new_user)
    
    return {
        "message": "User registered successfully",
        "username": user.username,
        "status": "success"
    }

@app.post("/login")
def login(login_data: LoginRequest):
    for user in fake_users_db:
        if user["username"] == login_data.username and user["password"] == login_data.password:
            return {
                "message": "Login successful",
                "username": login_data.username,
                "token": "fake-jwt-token-123456",
                "status": "success"
            }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/users")
def get_users():
    return {
        "users": [
            {"username": user["username"], "email": user["email"]}
            for user in fake_users_db
        ],
        "count": len(fake_users_db)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)