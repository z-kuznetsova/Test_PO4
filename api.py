from fastapi import FastAPI, Header, HTTPException, Form, UploadFile, File, Query
from pydantic import BaseModel
from datetime import datetime
import uuid

app = FastAPI()

# Пример хранилища пользователей
users_db = {
    "user@example.com": "password123"  # email: password
}

# Пример API ключа для пользователя
api_keys = {
    "user@example.com": "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae729"
}

class ApiKeyResponse(BaseModel):
    key: str

# Пример хранилища питомцев
pets_db = []

class PetResponse(BaseModel):
    id: str
    name: str
    animal_type: str
    age: int
    created_at: float
    user_id: str

@app.get("/api/key", response_model=ApiKeyResponse)
async def get_api_key(
    email: str = Header(...),
    password: str = Header(...)
):
    # Проверяем, существует ли пользователь и совпадает ли пароль
    if email in users_db and users_db[email] == password:
        # Возвращаем API ключ
        return ApiKeyResponse(key=api_keys[email])
    else:
        # Возвращаем ошибку 403, если комбинация email и пароля неверная
        raise HTTPException(status_code=403, detail="Invalid email or password")

@app.post("/api/pets", response_model=PetResponse)
async def add_pet(
        auth_key: str = Header(...),
        name: str = Form(...),
        animal_type: str = Form(...),
        age: int = Form(...)
):
    # Проверка корректности API ключа
    user_id = None
    for email, key in api_keys.items():
        if key == auth_key:
            user_id = email
            break

    if user_id is None:
        raise HTTPException(status_code=403, detail="Invalid auth_key")

    # Создание нового питомца
    pet_id = str(uuid.uuid4())  # Генерация уникального ID для питомца
    new_pet = {
        "id": pet_id,
        "name": name,
        "animal_type": animal_type,
        "age": age,
        "created_at": datetime.timestamp(datetime.now()),
        "user_id": user_id
    }

    pets_db.append(new_pet)  # Добавление питомца в базу данных

    return PetResponse(**new_pet)

@app.get("/api/pets", response_model=list[PetResponse])
async def get_pets(
        auth_key: str = Header(...),
        filter: str = Query(None)
):
    # Проверка корректности API ключа
    user_id = None
    for email, key in api_keys.items():
        if key == auth_key:
            user_id = email
            break

    if user_id is None:
        raise HTTPException(status_code=403, detail="Invalid auth_key")

    # Фильтрация питомцев
    if filter == "my_pets":
        user_pets = [pet for pet in pets_db if pet["user_id"] == user_id]
        return user_pets

    # Если фильтр не задан или задан некорректно, возвращаем всех питомцев
    return pets_db

@app.put("/api/pets/{pet_id}", response_model=PetResponse)
async def update_pet(
        pet_id: str,
        auth_key: str = Header(...),
        name: str = Form(None),
        animal_type: str = Form(None),
        age: int = Form(None)
):
    # Проверка корректности API ключа
    user_id = None
    for email, key in api_keys.items():
        if key == auth_key:
            user_id = email
            break

    if user_id is None:
        raise HTTPException(status_code=403, detail="Invalid auth_key")

    # Поиск питомца по ID
    pet = next((pet for pet in pets_db if pet["id"] == pet_id and pet["user_id"] == user_id), None)

    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found or you do not have permission to update this pet")

    # Обновление информации о питомце
    if name is not None:
        pet["name"] = name
    if animal_type is not None:
        pet["animal_type"] = animal_type
    if age is not None:
        pet["age"] = age

    return PetResponse(**pet)

@app.delete("/api/pets/{pet_id}")
async def delete_pet(
        pet_id: str,
        auth_key: str = Header(...)
):
    # Проверка корректности API ключа
    user_id = None
    for email, key in api_keys.items():
        if key == auth_key:
            user_id = email
            break

    if user_id is None:
        raise HTTPException(status_code=403, detail="Invalid auth_key")

    # Поиск питомца по ID
    pet = next((pet for pet in pets_db if pet["id"] == pet_id and pet["user_id"] == user_id), None)

    if pet is None:
        raise HTTPException(status_code=404, detail="Pet not found or you do not have permission to delete this pet")

    # Удаление питомца из базы данных
    pets_db.remove(pet)

    return {"detail": "Pet deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
