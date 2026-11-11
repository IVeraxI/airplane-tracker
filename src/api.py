import requests
from abc import ABC, abstractmethod


class BaseAPI(ABC):
    """Абстрактный базовый класс для интеграции с внешними API."""

    @abstractmethod
    def get_data(self, *args, **kwargs):
        """Обязательный метод для получения данных."""
        pass


class AeroplanesAPI(BaseAPI):
    """Класс для получения самолетов над конкретной страной через Nominatim и OpenSky."""

    def __init__(self):
        self.nominatim_url = "https://nominatim.openstreetmap.org/search"
        self.opensky_url = "https://opensky-network.org/api/states/all"
        self.headers = {"User-Agent": "AirplaneTracker/1.0 (HomePC)"}

    def _get_bounding_box(self, country: str) -> list[float] | None:
        """Вспомогательный метод: запрашивает квадрат координат (границы) страны."""
        params = {
            "q": country,
            "format": "json",
            "limit": 1
        }

        try:
            response = requests.get(self.nominatim_url, params=params, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if data:
                    # Забираем границы и конвертируем их в float: [юг, север, запад, восток]
                    bbox = data[0].get("boundingbox")
                    print(f"Границы для '{country}' найдены.")
                    return [float(coord) for coord in bbox]
            print(f"Ошибка получения координат. Статус: {response.status_code}")
        except Exception as e:
            print(f"Ошибка связи с Nominatim: {e}")

        return None

    def get_data(self, country: str) -> list[list]:
        """Главный метод: сначала получает координаты, затем запрашивает самолеты."""
        print(f"Ищем координаты для страны: {country}...")
        bbox = self._get_bounding_box(country)

        if not bbox:
            print("Не можем продолжить поиск самолетов без координат.")
            return []

        print(f"Сканируем воздушное пространство: {country}...")

        # В OpenSky параметры: lamin (юг), lamax (север), lomin (запад), lomax (восток)
        params = {
            "lamin": bbox[0],
            "lamax": bbox[1],
            "lomin": bbox[2],
            "lomax": bbox[3]
        }

        try:
            response = requests.get(self.opensky_url, params=params)
            if response.status_code == 200:
                data = response.json()
                planes = data.get("states")
                if planes:
                    print(f"Радар засек {len(planes)} самолетов над '{country}'!")
                    return planes
                else:
                    print(f"Над '{country}' сейчас нет самолетов с включенными транспондерами.")
                    return []
            else:
                print(f"Ошибка радара OpenSky. Статус: {response.status_code}")
        except Exception as e:
            print(f"Ошибка связи с радаром: {e}")

        return []
