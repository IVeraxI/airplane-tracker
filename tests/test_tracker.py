import pytest
from unittest.mock import patch, MagicMock
from src.aeroplane import Aeroplane
from src.storage import JSONSaver
from src.api import AeroplanesAPI
from src.main import user_interaction


# --- ТЕСТЫ КЛАССА AEROPLANE ---
def test_aeroplane_init_valid():
    """Проверка корректной инициализации самолета."""
    plane = Aeroplane("SU123", "Russia", 250.0, 10000.0)
    assert plane.callsign == "SU123"
    assert plane.country == "Russia"
    assert plane.velocity == 250.0
    assert plane.altitude == 10000.0


def test_aeroplane_init_none_values():
    """Проверка валидации битых данных (замена None на дефолтные значения)."""
    plane = Aeroplane(None, None, None, None)
    assert plane.callsign == "UNKNOWN"
    assert plane.country == "Unknown"
    assert plane.velocity == 0.0
    assert plane.altitude == 0.0


def test_aeroplane_comparison():
    """Проверка сравнения самолетов по высоте и скорости."""
    plane1 = Aeroplane("P1", "C1", 200.0, 5000.0)
    plane2 = Aeroplane("P2", "C2", 250.0, 10000.0)
    assert plane1 < plane2
    assert plane2.is_faster_than(plane1)


def test_cast_to_object_list():
    """Проверка конвертации сырых данных в объекты."""
    raw_data = [
        ['8014b9', 'VTAGL   ', 'India', 1, 2, 3, 4, 10000.0, False, 250.0],
        ['error_data']
    ]
    planes = Aeroplane.cast_to_object_list(raw_data)
    assert len(planes) == 1
    assert planes[0].callsign == "VTAGL"


# --- ТЕСТЫ ХРАНИЛИЩА ---
def test_json_saver(tmp_path):
    """Проверка сохранения и чтения из JSON-файла (используем временную папку)."""
    test_file = tmp_path / "test_aeroplanes.json"
    saver = JSONSaver(filename=str(test_file))
    plane = Aeroplane("TEST1", "TestCountry", 100.0, 1000.0)

    saver.add_aeroplane(plane)
    assert len(saver.get_aeroplanes()) == 1

    saver.delete_aeroplane("TEST1")
    assert len(saver.get_aeroplanes()) == 0

    saver.save_all([plane])
    assert len(saver.get_aeroplanes()) == 1


# --- ТЕСТЫ API И MAIN (MOCK) ---
@patch('src.api.requests.get')
def test_api_get_data(mock_get):
    """Проверяем API без реальных запросов в интернет."""
    mock_nom = MagicMock()
    mock_nom.status_code = 200
    mock_nom.json.return_value = [{"boundingbox": ["10", "20", "30", "40"]}]

    mock_open = MagicMock()
    mock_open.status_code = 200
    mock_open.json.return_value = {"states": [["123", "TEST", "Russia", 1, 2, 3, 4, 10000.0, False, 250.0]]}

    mock_get.side_effect = [mock_nom, mock_open]

    api = AeroplanesAPI()
    result = api.get_data("TestCountry")
    assert len(result) == 1
    assert result[0][1] == "TEST"


@patch('builtins.input', side_effect=['Италия', '', '5'])
@patch('src.main.AeroplanesAPI.get_data')
def test_main_user_interaction(mock_get_data, mock_input):
    """Проверяем консольное меню, подменяя input() на список заготовленных ответов."""
    mock_get_data.return_value = [
        ['123', 'TEST', 'Italy', 1, 2, 3, 4, 10000.0, False, 250.0]
    ]
    user_interaction()

# --- ДОПОЛНИТЕЛЬНЫЕ ТЕСТЫ ДЛЯ 90%+ ПОКРЫТИЯ ---

def test_aeroplane_extra_methods():
    """Добиваем 100% в aeroplane.py: проверяем repr, равенство и ошибки типов."""
    p1 = Aeroplane("SU1", "Russia", 200.0, 8000.0)
    p2 = Aeroplane("SU2", "Russia", 220.0, 8000.0)

    assert "Aeroplane" in repr(p1)
    assert p1 == p2
    assert (p1 == "не самолет") is False

    with pytest.raises(TypeError):
        _ = p1 < "не самолет"

    with pytest.raises(TypeError):
        p1.is_faster_than("не самолет")


@patch('src.api.requests.get')
def test_api_errors_and_empty(mock_get):
    """Проверяем поведение API при сбоях сети и пустом небе."""
    api = AeroplanesAPI()

    # Сценарий 1: Сервер координат вернул ошибку 404
    mock_fail = MagicMock(status_code=404)
    mock_get.return_value = mock_fail
    assert api.get_data("UnknownCountry") == []

    # Сценарий 2: Координаты нашлись, но небо пустое (states = None)
    mock_nom = MagicMock(status_code=200)
    mock_nom.json.return_value = [{"boundingbox": ["10", "20", "30", "40"]}]
    mock_open_empty = MagicMock(status_code=200)
    mock_open_empty.json.return_value = {"states": None}

    mock_get.side_effect = [mock_nom, mock_open_empty]
    assert api.get_data("EmptySkyCountry") == []


@patch('builtins.input', side_effect=[''])
def test_main_empty_country(mock_input):
    """Тест меню: пользователь сразу нажал Enter вместо страны."""
    user_interaction()


@patch('builtins.input', side_effect=['Италия', 'Italy', 'не_число'])
@patch('src.main.AeroplanesAPI.get_data')
def test_main_filter_and_invalid_top(mock_get_data, mock_input):
    """Тест меню: фильтрация по стране и ввод букв вместо цифр в Топ-N."""
    mock_get_data.return_value = [
        ['123', 'TEST', 'Italy', 1, 2, 3, 4, 10000.0, False, 250.0]
    ]
    user_interaction()
