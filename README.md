### Документация API проекта "Event_app"

## запуск через докер - docker-compose up --build -d
просмтр логов - docker-compose logs -f
остановить контейнер - docker-compose down


## API-ендпоинты

# /admin - панель админа в джанго

# POST api/users/login - логин, 
принимает {
    'email':useremail,
    'password':userpassword
}
ответ {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
        "id": 1,
        "name": "Иван Иванов",
        "email": "ivan@example.com",
        "is_superuser": false
    }
}


# POST api/user/register - регистрация пользователя,
 принимает {
    'name':name,
    'email':useremail,
    'password':userpassword
}
Ответ: {
    "id": 1,
    "name": "Иван Иванов",
    "email": "ivan@example.com",
    "is_superuser": false
}

# GET api/events 
Права доступа - все пользователи

Query Parameters:
search - поиск по названию
ordering - сортировка (id, name)
page - номер страницы (пагинация)

ответ 
{
    "count": 2,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Крокус Сити Холл",
            "latitude": 55.8259,
            "longitude": 37.3931,
            "weather": "cloudy"
        },
        {
            "id": 2,
            "name": "Третьяковская галерея",
            "latitude": 55.7415,
            "longitude": 37.6208,
            "weather": "sunny"
        }
    ]
}


# POST api/venue создать новое место
Права доступа: только администратор

принимает: {
    "name": "Новый стадион",
    "latitude": 55.7048,
    "longitude": 37.3579,
    "weather": "clear"
}

# GET api/venues/{id} получить детали места 

# PUT api/venues/{id} обновить место

# DELETE api/venues/{id} удалить место

# GET  api/events/ посомтреть события 

Права доступа:
Обычные пользователи: видят только PUBLISHED события
Администраторы: видят все события

Query Parameters для фильтрации:

Параметр |	Тип |	Описание |	Пример
search	| string	| Поиск по названию события или месту проведения	| ?search=концерт
ordering	string	| Сортировка (start_datetime, end_datetime, title, -start_datetime) |	?ordering=-start_datetime
start_datetime_after |	datetime	| События, начавшиеся после	| ?start_datetime_after=2024-12-01T00:00:00
start_datetime_before	| datetime	| События, начавшиеся до	| ?start_datetime_before=2024-12-31T23:59:59
end_datetime_after |	datetime |	События, закончившиеся после |	?end_datetime_after=2024-12-01T00:00:00
end_datetime_before |	datetime |	События, закончившиеся до |	?end_datetime_before=2024-12-31T23:59:59
publish_datetime_after	| datetime	| События, опубликованные после |	?publish_datetime_after=2024-12-01T00:00:00
publish_datetime_before |	datetime |	События, опубликованные до |	?publish_datetime_before=2024-12-31T23:59:59
venue__id	| integer |	Фильтр по месту проведения |	?venue__id=1
rating_min	| integer |	Минимальный рейтинг | (0-25) |	?rating_min=10
rating_max	| integer |	Максимальный рейтинг | (0-25) |	?rating_max=20
status	| string |	Фильтр по статусу | (DRAFT, PUBLISHED, CANCELLED) |	?status=PUBLISHED

пример запроса : GET /api/events/?start_datetime_after=2024-12-01T00:00:00&start_datetime_before=2024-12-31T23:59:59&venue__id=1&rating_min=10&rating_max=25&ordering=-start_datetime

ответ: {
    "count": 3,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "title": "Концерт рок-группы",
            "desk": "Выступление известной рок-группы",
            "publish_datetime": "2024-12-01T10:00:00Z",
            "start_datetime": "2024-12-15T19:00:00Z",
            "end_datetime": "2024-12-15T22:00:00Z",
            "author": {
                "id": 1,
                "name": "Админ Админов",
                "email": "admin@example.com"
            },
            "venue": {
                "id": 1,
                "name": "Крокус Сити Холл",
                "latitude": 55.8259,
                "longitude": 37.3931,
                "weather": "cloudy"
            },
            "rating": 20,
            "status": "PUBLISHED",
            "images": [
                {
                    "id": 1,
                    "image": "http://example.com/media/event_images/concert.jpg",
                    "preview": "http://example.com/media/event_previews/concert_preview.jpg"
                }
            ]
        }
    ]
}

# POST api/events/ создать событие
права доступа: только администратор

пример запроса {
    "title": "Новый год 2025",
    "desk": "Празднование нового года",
    "publish_datetime": "2024-12-20T10:00:00Z",
    "start_datetime": "2024-12-31T22:00:00Z",
    "end_datetime": "2025-01-01T04:00:00Z",
    "venue": 1,
    "rating": 15,
    "status": "DRAFT"
}

автор автоматически текущий пользователь

#  GET /api/events/{id}/ получить детали события 

# PUT /api/events/{id}/ обновить событие

# DELETE /api/events/{id}/ удалить событие

# POST /api/events/import/ добавить событие из XLSX

права доступа: тольок администратор

формат эксель документа можно найти ниже 

ответ: {
    "created": 5,
    "errors": []
}

либо если запрос 207: {
    "created": 3,
    "errors": [
        {
            "row": 5,
            "error": "Неверный формат даты: time data 'invalid' does not match format"
        },
        {
            "row": 7,
            "error": "Неверный формат координат: 55.1234"
        }
    ]
}

# GET /api/events/export/ экспорт события из XLSX документа

права доступа: все аторизованные пользователи 

Query Parameters: Те же, что и для фильтрации событий

пример запроса: GET /api/events/export/?start_datetime_after=2024-12-01&start_datetime_before=2024-12-31&venue__id=1&rating_min=10&rating_max=25

ответ: 
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

Content-Disposition: attachment; filename=events_export.xlsx

Тело: Excel файл с данными

# POST /api/events/{event_id}/images/ - загрузка изображения
Права доступа: авторизованный пользователь
Загружает одно или несколько изображений для события. Изображения автоматически создают превью-версию размером 200x200px при загрузке. Превью будет связано с первым изображением, а остальные изображения будут добавлены в список изображений события

пример : POST /api/events/1/images/

Тело запроса (Content-Type: multipart/form-data):

{
    "images": ["image1.jpg", "image2.jpg"]
}

Ответ:

{
    "images": [
        {
            "id": 1,
            "image": "http://example.com/media/event_images/image1.jpg",
            "preview": "http://example.com/media/event_previews/image1_preview.jpg"
        },
        {
            "id": 2,
            "image": "http://example.com/media/event_images/image2.jpg",
            "preview": "http://example.com/media/event_previews/image2_preview.jpg"
        }
    ]
}

# GET /api/events/{event_id}/images/ получить изображения 

Права доступа: Все пользователи

Описание: Получает все изображения, связанные с событием, включая превью.

Ответ:

{
    "images": [
        {
            "id": 1,
            "image": "http://example.com/media/event_images/image1.jpg",
            "preview": "http://example.com/media/event_previews/image1_preview.jpg"
        },
        {
            "id": 2,
            "image": "http://example.com/media/event_images/image2.jpg",
            "preview": "http://example.com/media/event_previews/image2_preview.jpg"
        }
    ]
}




##  Статусы событий
Статус |	Описание |	Кто видит
DRAFT	| Черновик |	Только администраторы
PUBLISHED |	Опубликовано	| Все пользователи
CANCELLED |	Отменено |	Все пользователи

## Коды ошибок 

Код	| Описание
400	| Неверный запрос (валидация данных)
401	| Не авторизован
403	| Доступ запрещен (нет прав)
404	| Ресурс не найден
207	| Частичный успех (при импорте с ошибками)



## 2. Таблица Events содержит в себе:
• Название
• Каждое событие может иметь несколько изображений. Изображения автоматически создают превью-версию при загрузке.
• Описание
• Дата и время публикации
• Дата и время начала проведения
• Дата и время завершения проведения
• Автор
• Место проведения (Таблица venue связанная Foreign_key)
    - Название
    - Гео-координаты места (точка) latitude, longitude
    - Погода в месте проведения
• Рейтинг (от 0 до 25)
• Статус

## 3 Импорт и экспорт xlsx файлов

# пример валидного xlsx файла


title |	desk |	publish_datetime |	start_datetime |end_datetime |	venue_name |	venue_coordinates |	rating | weather
Концерт рок-группы |Выступление известной | рок-группы в главном зале|2024-12-01 10:00|2024-12-15 19:00|2024-12-15 22:00|Стадион Лужник|55.8259,37.3931	20| Облачно


## Требования к файлу:
# 1. Формат файла:
    Только .xlsx (Excel 2007+)

    Первая строка - заголовки (обязательно)

    Кодировка: UTF-8

# 2. Колонки (обязательные в порядке следования):
    title (строка) - Название события
    Не может быть пустым
    Максимум 200 символов

    desk (строка) - Описание события
    Может быть пустым
    Текстовое поле

    publish_datetime (дата/время) - Дата публикации
    Формат: YYYY-MM-DD HH:MM
    Пример: 2024-12-01 10:00

    start_datetime (дата/время) - Начало события
    Формат: YYYY-MM-DD HH:MM
    Должно быть позже publish_datetime(не добавли проверку**)

    end_datetime (дата/время) - Окончание события
    Формат: YYYY-MM-DD HH:MM
    Должно быть позже start_datetime

    venue_name (строка) - Название места проведения
    Не может быть пустым
    Если место существует - оно будет использовано, иначе создано

    venue_coordinates (строка) - Координаты места
    Формат: широта,долгота
    Пример: 55.7558,37.6173
    Десятичные разделители через точку
    Разделитель значений - запятая

    rating (целое число) - Рейтинг события
    Диапазон: 0-25
    Если пусто или не число = 0
    Если > 25 = 25
    Если < 0 = 0

    weather (строка) - Погодные условия
    Произвольная строка
    Примеры: sunny, cloudy, rainy, snowy, windy, clear


## 4 Celety Task - постоянные задачи

# Задача: update_weather_for_venues()
Назначение: Автоматически обновляет погодные данные для всех мест проведения событий.

Расписание: Выполняется периодически (каждые 1800 секнд(пол часа))

Логика работы:
- Получает все существующие места проведения (Venue)
- Для каждого места генерирует случайные погодные данные
- Сохраняет данные в поле weather модели Venue
# Задача: published_sheduled_events()
Назначение: Автоматически изменяет статус событий с DRAFT на PUBLISHED когда наступает время публикации.

Расписание: Выполняется периодически (рекомендуется каждые 5 минут)
Логика работы:
- Находит все события со статусом DRAFT
- Проверяет, наступило ли время публикации (publish_datetime)
- Если время наступило - меняет статус на PUBLISHED

# Задача: send_event_email(subject, message, recipient_list)
На текущий момент стоит залушка вместо реальной почты

Параметры:

- subject (string) - Тема письма
- message (string) - Текст письма
- recipient_list (list) - Список email адресов получателей


