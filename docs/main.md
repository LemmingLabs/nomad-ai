NomadAI — Smart Travel Planner for Kyrgyzstan


1. Общее описание проекта
NomadAI — AI-платформа для планирования путешествий по Кыргызстану. Пользователь вводит бюджет, количество дней и интересы — система возвращает полный план поездки: маршрут по дням, разбивку бюджета, варианты транспорта и проживания, AI-советы.
Цель продукта
Помочь туристам эффективно планировать поездки, оптимизируя расходы
Направлять денежные потоки в локальную туристическую инфраструктуру
Снизить порог входа для самостоятельных путешествий по Кыргызстану
Основные сценарии использования
Турист вводит бюджет 200$, 5 дней, интересы: природа, горы → получает готовый маршрут
Сравнивает 3 сценария (Бюджет / Быстро / Комфорт) и выбирает подходящий
Скачивает PDF с полным планом поездки перед отъездом


2. Основной функционал (по модулям)
2.1 Генерация маршрута (AI)
Параметр
Описание
Что делает
AI генерирует маршрут по дням: локации, активности, логику поездки
Вход
budget, days, interests[]
Выход
Список DayPlan объектов с локациями и активностями
Реализация
Вызов OpenAI API с prompt, парсинг ответа в структуру

2.2 Budget Breakdown
Параметр
Описание
Что делает
Рассчитывает разбивку бюджета по категориям
Вход
budget, days, accommodation_type
Выход
Budget объект: housing, transport, food, activities
Реализация
Формульный расчёт на backend, данные захардкожены

2.3 Оценка транспорта
Параметр
Описание
Что делает
Считает стоимость, время и расстояние между точками маршрута
Вход
origin, destination (названия или координаты)
Выход
distance_km, duration_min, price_range
Реализация
2GIS/Google Maps API для дистанции + формульный расчёт стоимости

2.4 Проживание
Параметр
Описание
Что делает
Предлагает варианты жилья под бюджет пользователя
Вход
budget_per_night, city, accommodation_type
Выход
Список Accommodation объектов
Реализация
Локальная захардкоженная база вариантов

2.5 Маршрут по дням
Параметр
Описание
Что делает
Отображает полный план по дням: место, активности, транспорт
Вход
Список мест от AI + транспортные расчёты
Выход
Список DayPlan с обогащёнными данными
Реализация
AI даёт список мест, backend добавляет расстояния и стоимость

2.6 AI советы (Smart Tips)
Параметр
Описание
Что делает
Генерирует практические советы по поездке
Вход
Контекст маршрута (сезон, локации, бюджет)
Выход
Список советов (tips[])
Реализация
Вызов AI с отдельным prompt для tips

2.7 Альтернативные варианты
Сценарий
Жильё
Транспорт
Приоритет
Budget (Дешёвый)
Хостел 10–15$/ночь
Маршрутки, шеринг
Минимум расходов
Fast (Быстрый)
Средний отель
Такси, короткий маршрут
Экономия времени
Comfort (Комфортный)
Отель 3*+
Трансфер, частный транспорт
Удобство

2.8 Экспорт в PDF
Параметр
Описание
Что делает
Генерирует PDF с полным планом поездки
Содержимое
Маршрут по дням, бюджет, советы, изображения локаций
Изображения
Unsplash API по ключевым словам (горы, пляж, город)
Реализация
Backend генерирует HTML → конвертирует в PDF (weasyprint/puppeteer)



3. Архитектура системы
3.1 Frontend — React
Страницы (pages)
/  — HomePage: форма ввода параметров
/result  — ResultPage: отображение сгенерированного маршрута
/pdf-preview  — PDFPreview (опционально)
Компоненты
TripForm — форма с полями: бюджет, дни, интересы
DayCard — карточка одного дня маршрута
BudgetChart — визуализация разбивки бюджета
TransportInfo — информация о транспорте между точками
AlternativeTabs — табы Budget / Fast / Comfort
TipsBlock — блок AI советов
ExportButton — кнопка скачать PDF
MapEmbed — встроенная карта (2GIS или Google)
3.2 Backend — FastAPI
Структура проекта
app/
  main.py              — entry point, CORS, routers
  routers/
    trip.py            — /generate-trip
    transport.py       — /estimate-transport
    pdf.py             — /export-pdf
  services/
    ai_service.py      — вызов OpenAI API
    budget_service.py  — расчёт бюджета
    transport_service.py — расчёт транспорта
    pdf_service.py     — генерация PDF
  schemas/
    trip_schema.py     — Pydantic модели запросов и ответов
  data/
    accommodations.py  — захардкоженные варианты жилья
    locations.py       — список локаций Кыргызстана
  config.py            — API ключи, константы
3.3 AI слой
Используется OpenAI API (gpt-4o или gpt-4o-mini). Вызов через ai_service.py.
Пример prompt для генерации маршрута
system: "You are a travel expert for Kyrgyzstan. Always respond in valid JSON."
user: "Plan a {days}-day trip to Kyrgyzstan with budget ${budget}.
  Interests: {interests}.
  Return JSON: { days: [{ day: 1, location: '', activities: [], tips: '' }] }"
3.4 Интеграции
Сервис
Назначение
Статус MVP
2GIS API / Google Maps
Расстояние и время между точками
Подключается
Unsplash API
Изображения локаций для PDF
Подключается
OpenAI API
Генерация маршрута и советов
Основная зависимость
WeasyPrint / Puppeteer
Конвертация HTML → PDF
Подключается



4. API Endpoints
POST /generate-trip
Генерирует полный план поездки на основе параметров пользователя.
Request
{
  "budget": 300,
  "days": 5,
  "interests": ["nature", "mountains", "food"],
  "accommodation_type": "budget"  // budget | standard | comfort
}
Response
{
  "trip_id": "uuid",
  "days": [
    {
      "day": 1,
      "location": "Bishkek",
      "activities": ["Visit Ala-Too Square", "Osh Bazaar"],
      "transport": { "from": "Airport", "to": "Bishkek", "price_range": "300-400 KGS", "duration_min": 40 },
      "accommodation": { "name": "Sakura Hostel", "price_per_night": 12, "type": "hostel" }
    }
  ],
  "budget_breakdown": {
    "housing": 60, "transport": 40, "food": 75, "activities": 50, "reserve": 75
  },
  "alternatives": { "budget": {...}, "fast": {...}, "comfort": {...} },
  "tips": ["Best to travel in June-August", "Bring cash — ATMs are rare outside Bishkek"]
}
POST /estimate-transport
Рассчитывает стоимость и время маршрута между двумя точками.
Request
{
  "origin": "Bishkek",
  "destination": "Issyk-Kul",
  "transport_type": "taxi"  // taxi | marshrutka | transfer
}
Response
{
  "distance_km": 250,
  "duration_min": 180,
  "price_range": { "min": 3200, "max": 4500, "currency": "KGS" },
  "recommended": "marshrutka"
}
POST /export-pdf
Генерирует PDF файл с планом поездки.
Request
{
  "trip_id": "uuid"  // или полный trip объект
}
Response
Binary PDF file (Content-Type: application/pdf)


GET /accommodations
Возвращает варианты проживания по фильтрам.
Request (query params)
?city=Bishkek&type=hostel&max_price=20
Response
{
  "accommodations": [
    { "name": "Sakura Hostel", "city": "Bishkek", "type": "hostel",
      "price_per_night": 12, "rating": 4.2, "contacts": "..." }
  ]
}


5. Логика расчётов
5.1 Расчёт бюджета
Все расчёты в budget_service.py. Используются фиксированные коэффициенты:
Категория
Формула
Пример (5 дней, budget)
Жильё
days × price_per_night
5 × 12$ = 60$
Питание
days × food_per_day
5 × 15$ = 75$
Активности
days × activity_budget
5 × 10$ = 50$
Транспорт
Сумма всех маршрутов
~40$
Резерв
10% от суммы
~23$

Диапазоны по типу жилья (захардкожено)
hostel: 10–15$ / ночь
standard hotel: 30–50$ / ночь
comfort hotel: 60–100$ / ночь
5.2 Расчёт транспорта
Формула расчёта стоимости (transport_service.py):
price = base_fare + (distance_km × rate_per_km) + (duration_min × rate_per_min)
Тарифы (захардкожено, в сомах)
Тип
base_fare
rate_per_km
rate_per_min
Такси
80
12
2
Маршрутка
30
3
0.5
Трансфер
500
20
3

Расстояние и время запрашиваются через 2GIS API или Google Maps Distance Matrix API. В MVP — можно использовать захардкоженную таблицу расстояний между ключевыми локациями.


6. Структура данных (модели)
Trip
{
  "trip_id": "uuid",
  "budget": 300,
  "days": 5,
  "interests": ["nature", "mountains"],
  "accommodation_type": "budget",
  "day_plans": [DayPlan],
  "budget_breakdown": Budget,
  "alternatives": { "budget": Alt, "fast": Alt, "comfort": Alt },
  "tips": ["string"]
}
DayPlan
{
  "day": 1,
  "location": "Bishkek",
  "activities": ["string"],
  "accommodation": Accommodation,
  "transport": Transport,
  "image_url": "https://..."
}
Transport
{
  "from": "Bishkek",
  "to": "Ala-Archa",
  "distance_km": 40,
  "duration_min": 60,
  "price_range": { "min": 600, "max": 800, "currency": "KGS" },
  "type": "taxi"
}
Budget
{
  "total": 300,
  "housing": 60,
  "transport": 40,
  "food": 75,
  "activities": 50,
  "reserve": 75,
  "currency": "USD"
}
Accommodation
{
  "name": "Sakura Hostel",
  "city": "Bishkek",
  "type": "hostel",
  "price_per_night": 12,
  "rating": 4.2,
  "address": "...",
  "contacts": "..."
}


7. UI структура
Главная страница (/)
Заголовок + краткое описание
Форма TripForm:
Поле: Бюджет (число, USD)
Поле: Количество дней (1–14)
Теги интересов: природа, горы, культура, еда, активный отдых
Тип жилья: Budget / Standard / Comfort
Кнопка «Сгенерировать маршрут»
Состояния: idle → loading → success / error
Страница результата (/result)
Блок «Маршрут по дням» — DayCard × N
Заголовок дня (Day 1: Bishkek)
Список активностей
Транспорт: откуда, куда, цена, время
Жильё на ночь
Изображение локации
Блок «Бюджет» — BudgetChart
Pie chart или bar chart с разбивкой
Таблица сумм по категориям
Блок «Альтернативы» — AlternativeTabs
3 таба: Budget / Fast / Comfort
Блок «AI Советы» — TipsBlock
Карта — MapEmbed (2GIS iframe)
Кнопка «Скачать PDF» — ExportButton


8. Поток работы пользователя (User Flow)
Шаг
Действие пользователя
Действие системы
1
Открывает сайт
Загружается форма TripForm
2
Вводит: бюджет 300$, 5 дней, природа+горы, бюджетный тип жилья
Валидация полей
3
Нажимает «Сгенерировать маршрут»
Показывается лоадер, POST /generate-trip
4
Ожидает ~3–8 секунд
Backend вызывает AI, считает бюджет и транспорт
5
Видит результат
React рендерит ResultPage с данными
6
Просматривает маршрут, меняет вкладку альтернатив
Переключение tabs без нового запроса
7
Нажимает «Скачать PDF»
POST /export-pdf, получает файл



9. План разработки (7 дней)
День
Frontend
Backend
AI / Интеграции
День 1
TripForm компонент, layout, роутинг
Инициализация FastAPI, структура папок
Настройка OpenAI API ключа, тест запроса
День 2
Подключение к API, состояния загрузки
Роутер /generate-trip, ai_service.py
Написание и тест промпта генерации маршрута
День 3
DayCard компонент, ResultPage layout
Парсинг ответа AI, структура DayPlan
Доработка промпта, обработка ошибок AI
День 4
BudgetChart, отображение разбивки
budget_service.py, расчёт формулами
—
День 5
TransportInfo, карточки транспорта
transport_service.py, /estimate-transport
Подключение 2GIS API (или заглушка)
День 6
AlternativeTabs, TipsBlock, MapEmbed, ExportButton
pdf_service.py, /export-pdf, accommodations data
Промпт для tips, Unsplash API для изображений
День 7
Финальный UI polish, mobile responsive
Тесты endpoints, CORS, error handling
End-to-end тест, подготовка демо



10. Распределение ролей (команда 3–4 чел.)
Роль
Задачи
Кто отвечает
Backend Dev
FastAPI, routers, services, расчёты бюджета и транспорта, PDF генерация
—
Frontend Dev
React компоненты, страницы, интеграция с API, стили
—
AI / Integrations
OpenAI промпты, 2GIS/Google Maps, Unsplash API, оптимизация ответов AI
—
UX / Презентация
Финальный дизайн, polish UI, подготовка демо, слайды
—



11. Упрощения в MVP
Захардкоженные данные (заглушки)
База отелей и хостелов — статический Python файл, не реальный API бронирования
Тарифы транспорта — фиксированные коэффициенты, не реальные тарифы такси
Расстояния между точками — можно использовать таблицу вместо API (если 2GIS не подключён)
Цены на активности — средние оценки, не реальные прайсы
Упрощения функционала
Нет авторизации и сохранения маршрутов
Нет реального бронирования (отели, транспорт)
Нет платёжной системы
Карта — статичный embed без интерактивного маршрута
PDF без интерактивных элементов
Что может не работать в демо
2GIS API — при отсутствии ключа использовать захардкоженные расстояния
Unsplash API — при отсутствии ключа использовать placeholder изображения


12. Будущие улучшения (post-MVP)
Интеграция реального API бронирования отелей (Booking.com, local partners)
Реальные тарифы Яндекс.Такси / inDriver для Кыргызстана
B2B API для туроператоров
Мобильное приложение
Мультиязычность (KG, RU, EN)
Интеграция с реальными ценами (парсинг / партнёрские соглашения)
