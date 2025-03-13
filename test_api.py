import pytest
from fastapi.testclient import TestClient
from api import app  # Импортируем ваше FastAPI приложение

client = TestClient(app)

# Тест 1: Получение API ключа с правильными учетными данными
def test_get_api_key_success():
    response = client.get("/api/key", headers={"email": "user@example.com", "password": "password123"})
    assert response.status_code == 200
    assert "key" in response.json()

# Тест 2: Получение API ключа с неправильными учетными данными
def test_get_api_key_failure():
    response = client.get("/api/key", headers={"email": "user@example.com", "password": "wrongpassword"})
    assert response.status_code == 403

# Тест 3: Добавление питомца с правильным API ключом
def test_add_pet_success():
    response = client.post(
        "/api/pets",
        headers={"auth-key": "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae729"},
        data={
            "name": "Buddy",
            "animal_type": "Dog",
            "age": 3
        }
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Buddy"

# Тест 4: Добавление питомца с неправильным API ключом
def test_add_pet_failure():
    response = client.post(
        "/api/pets",
        headers={"auth-key": "wrongkey"},
        data={"name": "Buddy",
              "animal_type": "Dog",
              "age": 3
        }
    )
    assert response.status_code == 403

# Тест 5: Получение списка питомцев без фильтра
def test_get_pets_no_filter():
    response = client.get(
        "/api/pets",
        headers={"auth-key": "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae729"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Тест 6: Получение списка питомцев с фильтром "my_pets"
def test_get_pets_my_pets_filter():
    response = client.get(
        "/api/pets",
        headers={"auth-key": "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae729"},
        params={"filter": "my_pets"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Тест 7: Обновление информации о питомце
def test_update_pet():
    auth_key = "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae729"
    # Сначала добавим питомца
    add_response = client.post(
        "/api/pets",
        headers={"auth-key": auth_key},
        data={"name": "Buddy", "animal_type": "Dog", "age": 3})
    pet_id = add_response.json()["id"]
    # Обновим информацию
    update_response = client.put(
        f"/api/pets/{pet_id}",
        headers={"auth-key": auth_key},
        data={"name": "Buddy Updated"})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Buddy Updated"

# Тест 8: Удаление питомца
def test_delete_pet():
    auth_key = "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae729"
    # Сначала добавим питомца
    add_response = client.post(
        "/api/pets",
        headers={"auth-key": auth_key},
        data={"name": "Buddy", "animal_type": "Dog", "age": 3})
    pet_id = add_response.json()["id"]
    # Удалим питомца
    delete_response = client.delete(
        f"/api/pets/{pet_id}",
        headers={"auth-key": auth_key})
    assert delete_response.status_code == 200
    assert delete_response.json()["detail"] == "Pet deleted successfully"

# Тест 9: Попытка обновления несуществующего питомца
def test_update_nonexistent_pet():
    auth_key = "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae729"
    response = client.put(
        "/api/pets/nonexistentid",
        headers={"auth-key": auth_key},
        data={"name": "Ghost"})
    assert response.status_code == 404

# Тест 10: Попытка удаления несуществующего питомца
def test_delete_nonexistent_pet():
    auth_key = "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae729"
    response = client.delete(
        "/api/pets/nonexistentid",
        headers={"auth-key": auth_key})
    assert response.status_code == 404

# Тест 11: Получение списка питомцев с неправильным API ключом
def test_get_pets_invalid_auth_key():
    response = client.get(
        "/api/pets",
        headers={"auth-key": "wrongkey"})
    assert response.status_code == 403

# Тест 12: Добавление питомца без обязательных полей
def test_add_pet_missing_fields():
    auth_key = "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae729"
    response = client.post(
        "/api/pets",
        headers={"auth-key": auth_key},
        data={"name": "Buddy"})
    assert response.status_code == 422  # Unprocessable Entity

# Тест 13: Обновление питомца без изменений
def test_update_pet_no_changes():
    auth_key = "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae729"
    add_response = client.post(
        "/api/pets",
        headers={"auth-key": auth_key},
        data={"name": "Buddy", "animal_type": "Dog", "age": 3})
    pet_id = add_response.json()["id"]
    update_response = client.put(
        f"/api/pets/{pet_id}",
        headers={"auth-key": auth_key})
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Buddy"

# Тест 14: Получение API ключа без заголовков
def test_get_api_key_no_headers():
    response = client.get("/api/key")
    assert response.status_code == 422  # Unprocessable Entity

# Тест 15: Добавление питомца без API ключа
def test_add_pet_no_auth_key():
    response = client.post(
        "/api/pets",
        data={"name": "Buddy", "animal_type": "Dog", "age": 3})
    assert response.status_code == 422  # Unprocessable Entity



