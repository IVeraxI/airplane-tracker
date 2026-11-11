import requests

print("Отправляем запрос к OpenSky Network...")
# URL для получения данных обо всех самолетах в мире
url = "https://opensky-network.org/api/states/all"

try:
    # Отправляем GET-запрос
    response = requests.get(url)
    print(f"Статус-код: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        planes = data.get("states", [])
        print(f"Связь идеальная! Радары засекли {len(planes)} самолетов прямо сейчас.")
    else:
        print("Сервер API вернул ошибку.")
except Exception as e:
    print(f"Ошибка соединения: {e}")
