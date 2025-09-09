

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, EmailStr, Field, ValidationError
from typing import Optional, List
from bson import ObjectId

app = FastAPI()

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=80)
    email: EmailStr
    age: int = Field(..., ge=0)
    is_active: bool = True

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=80)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class UserOut(UserBase):
    id: str = Field(alias="_id")

@app.on_event("startup")
async def startup_db():
    global client, db, users_collection
    client = AsyncIOMotorClient("mongodb://root:root@mongodb:27017")
    db = client["atividade_extra"]
    users_collection = db["users"]
    # Índice único para email
    await users_collection.create_index("email", unique=True)

def user_helper(user) -> dict:
    user["_id"] = str(user["_id"])
    return user

# POST /users
@app.post("/users", response_model=UserOut, status_code=201)
async def create_user(user: UserCreate):
    try:
        result = await users_collection.insert_one(user.dict())
        new_user = await users_collection.find_one({"_id": result.inserted_id})
        return user_helper(new_user)
    except Exception as e:
        if "duplicate key error" in str(e):
            raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
        raise HTTPException(status_code=400, detail="Erro ao criar usuário.")

# GET /users
@app.get("/users", response_model=List[UserOut])
async def list_users(
    q: Optional[str] = Query(None, description="Busca por nome"),
    min_age: Optional[int] = Query(None, ge=0),
    max_age: Optional[int] = Query(None, ge=0),
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100)
):
    query = {}
    if q:
        query["name"] = {"$regex": q, "$options": "i"}
    if min_age is not None or max_age is not None:
        query["age"] = {}
        if min_age is not None:
            query["age"]["$gte"] = min_age
        if max_age is not None:
            query["age"]["$lte"] = max_age
    if is_active is not None:
        query["is_active"] = is_active
    skip = (page - 1) * limit
    users = await users_collection.find(query).sort("name", 1).skip(skip).limit(limit).to_list(length=limit)
    return [user_helper(u) for u in users]

# GET /users/{id}
@app.get("/users/{id}", response_model=UserOut)
async def get_user(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido.")
    user = await users_collection.find_one({"_id": ObjectId(id)})
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return user_helper(user)

# PUT /users/{id}
@app.put("/users/{id}", response_model=UserOut)
async def update_user(id: str, user: UserUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido.")
    user_data = {k: v for k, v in user.dict().items() if v is not None}
    if not user_data:
        raise HTTPException(status_code=400, detail="Nenhum dado para atualizar.")
    try:
        result = await users_collection.update_one({"_id": ObjectId(id)}, {"$set": user_data})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        updated = await users_collection.find_one({"_id": ObjectId(id)})
        return user_helper(updated)
    except Exception as e:
        if "duplicate key error" in str(e):
            raise HTTPException(status_code=409, detail="E-mail já cadastrado.")
        raise HTTPException(status_code=400, detail="Erro ao atualizar usuário.")

# DELETE /users/{id}
@app.delete("/users/{id}", status_code=204)
async def delete_user(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="ID inválido.")
    result = await users_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    return JSONResponse(status_code=204, content=None)
