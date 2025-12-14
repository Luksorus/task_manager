from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from enum import Enum

app = FastAPI(title="Task Service", version="1.0.0")

# Модели данных
class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.TODO
    created_at: datetime
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None

class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None

# Имитация базы данных
fake_tasks_db = []
task_id_counter = 1

@app.get("/")
def read_root():
    return {"message": "Task Service is running", "status": "active"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "task-service",
        "version": "1.0.0",
        "task_count": len(fake_tasks_db),
        "timestamp": "2024-01-15T10:00:00Z"
    }

@app.get("/tasks")
def get_tasks(status: Optional[TaskStatus] = None):
    if status:
        filtered_tasks = [task for task in fake_tasks_db if task["status"] == status]
        return {"tasks": filtered_tasks, "count": len(filtered_tasks)}
    return {"tasks": fake_tasks_db, "count": len(fake_tasks_db)}

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in fake_tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks")
def create_task(task_request: CreateTaskRequest):
    global task_id_counter
    
    new_task = {
        "id": task_id_counter,
        "title": task_request.title,
        "description": task_request.description,
        "priority": task_request.priority,
        "status": TaskStatus.TODO,
        "created_at": datetime.now(),
        "due_date": task_request.due_date,
        "assigned_to": None
    }
    
    fake_tasks_db.append(new_task)
    task_id_counter += 1
    
    return {
        "message": "Task created successfully",
        "task_id": new_task["id"],
        "task": new_task
    }

@app.put("/tasks/{task_id}")
def update_task(task_id: int, status: Optional[TaskStatus] = None, assigned_to: Optional[str] = None):
    for task in fake_tasks_db:
        if task["id"] == task_id:
            if status:
                task["status"] = status
            if assigned_to:
                task["assigned_to"] = assigned_to
            
            return {
                "message": "Task updated successfully",
                "task_id": task_id,
                "updated_fields": {
                    "status": status,
                    "assigned_to": assigned_to
                }
            }
    
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global fake_tasks_db
    initial_length = len(fake_tasks_db)
    
    fake_tasks_db = [task for task in fake_tasks_db if task["id"] != task_id]
    
    if len(fake_tasks_db) < initial_length:
        return {
            "message": "Task deleted successfully",
            "task_id": task_id,
            "remaining_tasks": len(fake_tasks_db)
        }
    else:
        raise HTTPException(status_code=404, detail="Task not found")

@app.get("/stats")
def get_stats():
    stats = {
        "total_tasks": len(fake_tasks_db),
        "by_status": {
            "todo": len([t for t in fake_tasks_db if t["status"] == TaskStatus.TODO]),
            "in_progress": len([t for t in fake_tasks_db if t["status"] == TaskStatus.IN_PROGRESS]),
            "done": len([t for t in fake_tasks_db if t["status"] == TaskStatus.DONE])
        },
        "by_priority": {
            "low": len([t for t in fake_tasks_db if t["priority"] == TaskPriority.LOW]),
            "medium": len([t for t in fake_tasks_db if t["priority"] == TaskPriority.MEDIUM]),
            "high": len([t for t in fake_tasks_db if t["priority"] == TaskPriority.HIGH])
        }
    }
    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)