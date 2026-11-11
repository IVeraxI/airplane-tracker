class Aeroplane:
    """Класс для представления информации о самолете."""

    def __init__(self, callsign: str | None, country: str | None, velocity: float | None, altitude: float | None):
        """
        Инициализация с валидацией данных.
        Если радар не передал значение (None), заменяем его на безопасное.
        """
        # Убираем лишние пробелы из позывного или ставим заглушку
        self.callsign = callsign.strip() if callsign and callsign.strip() else "UNKNOWN"

        self.country = str(country) if country else "Unknown"

        # Если скорость или высота None, ставим 0.0. Иначе конвертируем в float
        self.velocity = float(velocity) if velocity is not None else 0.0
        self.altitude = float(altitude) if altitude is not None else 0.0

    def __str__(self):
        return f"Рейс {self.callsign:8} | Страна: {self.country:15} | Высота: {self.altitude:7.1f} м | Скорость: {self.velocity:5.1f} м/с"

    def __repr__(self):
        return f"Aeroplane('{self.callsign}', '{self.country}', {self.velocity}, {self.altitude})"

    # --- Магические методы для сравнения по высоте (нужно для вывода Топ-N) ---
    def __lt__(self, other: "Aeroplane") -> bool:
        """Сравнение 'меньше' по высоте полета."""
        if not isinstance(other, Aeroplane):
            raise TypeError("Сравнивать можно только с объектом Aeroplane")
        return self.altitude < other.altitude

    def __eq__(self, other: "Aeroplane") -> bool:
        """Сравнение 'равно' по высоте полета."""
        if not isinstance(other, Aeroplane):
            return False
        return self.altitude == other.altitude

    # --- Отдельные методы для сравнения по скорости ---
    def is_faster_than(self, other: "Aeroplane") -> bool:
        """Пользовательский метод: возвращает True, если этот самолет быстрее."""
        if not isinstance(other, Aeroplane):
            raise TypeError("Сравнивать можно только с объектом Aeroplane")
        return self.velocity > other.velocity

    @classmethod
    def cast_to_object_list(cls, data_list: list[list]) -> list["Aeroplane"]:
        """Преобразует список списков (сырые данные API) в список объектов Aeroplane."""
        aeroplanes = []
        for data in data_list:
            try:
                # По документации OpenSky: [1]=callsign, [2]=country, [7]=altitude, [9]=velocity
                aeroplane = cls(
                    callsign=data[1],
                    country=data[2],
                    velocity=data[9],
                    altitude=data[7]
                )
                aeroplanes.append(aeroplane)
            except (IndexError, ValueError, TypeError) as e:
                # Если радар вернул совсем битую строку — пропускаем ее
                continue
        return aeroplanes
