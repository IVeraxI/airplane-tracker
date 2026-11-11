import json
import os
from abc import ABC, abstractmethod
from src.aeroplane import Aeroplane


class BaseSaver(ABC):
    """Абстрактный класс, обязывающий реализовать методы работы с хранилищем."""

    @abstractmethod
    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Метод для добавления информации о самолете в файл."""
        pass

    @abstractmethod
    def get_aeroplanes(self) -> list[Aeroplane]:
        """Метод для получения данных из файла."""
        pass

    @abstractmethod
    def delete_aeroplane(self, callsign: str) -> None:
        """Метод для удаления информации о самолете."""
        pass


class JSONSaver(BaseSaver):
    """Класс для сохранения информации о самолетах в JSON-файл."""

    def __init__(self, filename: str = "data/aeroplanes.json"):
        self.filename = filename
        # Автоматически создаем папку data, если её вдруг нет
        os.makedirs(os.path.dirname(self.filename), exist_ok=True)

        # Если файла еще нет, создаем пустой JSON-список
        if not os.path.exists(self.filename):
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump([], f)

    def _read_file(self) -> list[dict]:
        """Внутренний метод для чтения сырых словарей из файла."""
        with open(self.filename, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_file(self, data: list[dict]) -> None:
        """Внутренний метод для записи словарей в файл."""
        with open(self.filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def add_aeroplane(self, aeroplane: Aeroplane) -> None:
        """Добавляет один самолет в конец JSON-файла."""
        data = self._read_file()
        data.append({
            "callsign": aeroplane.callsign,
            "country": aeroplane.country,
            "velocity": aeroplane.velocity,
            "altitude": aeroplane.altitude
        })
        self._write_file(data)

    def get_aeroplanes(self) -> list[Aeroplane]:
        """Достает данные из файла и превращает их обратно в объекты Aeroplane."""
        data = self._read_file()
        return [Aeroplane(**item) for item in data]

    def delete_aeroplane(self, callsign: str) -> None:
        """Удаляет самолет из файла по позывному (заглушка)."""
        data = self._read_file()
        # Оставляем только те самолеты, чей позывной не совпадает с удаляемым
        filtered_data = [plane for plane in data if plane.get("callsign") != callsign]
        self._write_file(filtered_data)

    def save_all(self, aeroplanes: list[Aeroplane]) -> None:
        """Кастомный метод для удобства: разом сохраняет весь список радара."""
        data = [
            {
                "callsign": p.callsign,
                "country": p.country,
                "velocity": p.velocity,
                "altitude": p.altitude
            } for p in aeroplanes
        ]
        self._write_file(data)
        print(f"Успешно сохранено {len(data)} самолетов в файл {self.filename}")
