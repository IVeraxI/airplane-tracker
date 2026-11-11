import sys
import os

# Добавляем папку src в пути поиска, чтобы импорты работали корректно
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.api import AeroplanesAPI
from src.aeroplane import Aeroplane
from src.storage import JSONSaver


def user_interaction():
    print("=== РАДАР OPEN SKY (Сервер: Нидерланды) ===")
    api = AeroplanesAPI()
    saver = JSONSaver()

    # 1. Ввод страны для сканирования
    country = input("\nВведите название страны для сканирования (например, Швейцария, Италия, Канада): ").strip()
    if not country:
        print("Страна не введена. Завершение работы.")
        return

    # Запрашиваем сырые данные
    raw_planes = api.get_data(country)

    if not raw_planes:
        print("Самолеты не найдены или произошла ошибка радара. Попробуйте другую страну.")
        return

    # 2. Преобразуем в объекты и сохраняем в JSON
    aeroplanes = Aeroplane.cast_to_object_list(raw_planes)
    saver.save_all(aeroplanes)
    print(f"[{len(aeroplanes)} бортов успешно занесены в базу данных]\n")

    current_list = aeroplanes

    # 3. Фильтрация по стране регистрации
    filter_words = input(
        "Введите страны регистрации для фильтрации через пробел (или Enter, чтобы показать все): ").split()
    if filter_words:
        # Приводим к нижнему регистру для надежного поиска
        filter_words_lower = [w.lower() for w in filter_words]
        current_list = [p for p in current_list if p.country.lower() in filter_words_lower]
        print(f"После фильтрации осталось самолетов: {len(current_list)}")

    if not current_list:
        print("Нет самолетов, удовлетворяющих условиям фильтрации.")
        return

    # 4. Топ-N по высоте
    try:
        top_n = int(input("\nВведите количество самолетов для вывода в ТОП по высоте: "))
    except ValueError:
        print("Некорректное число, выводим топ-5.")
        top_n = 5

    # Сортируем список. По умолчанию метод __lt__ сортирует по возрастанию, нам нужно по убыванию (reverse=True)
    current_list.sort(reverse=True)
    top_aeroplanes = current_list[:top_n]

    # 5. Вывод результатов
    print(f"\n--- ТОП {len(top_aeroplanes)} САМОЛЕТОВ ---")
    for p in top_aeroplanes:
        print(p)


if __name__ == "__main__":
    try:
        user_interaction()
    except KeyboardInterrupt:
        print("\nПрограмма принудительно завершена.")
