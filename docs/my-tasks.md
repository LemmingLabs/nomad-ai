🤖 Task: Реализация AI Logic & Trip Continuation
Зона ответственности: Промпт-инжиниринг, интеграция с LLM (Groq), история чата и динамическое обновление маршрута.

📂 Структура файлов и задачи

Таск 1 — Реализовать TripMessage model
Файл: app/models/trip_message.py
Поля: id, trip_id, role (user/assistant/system), content (text), created_at.
Требования:
Настроить relationship с моделью Trip.
Настроить каскадное удаление: при удалении поездки её сообщения удаляются автоматически (cascade="all, delete-orphan").

Таск 2 — Реализовать message schemas
Файл: app/schemas/trip_message.py
Схемы: TripMessageCreateRequest, TripMessageResponse, TripContinuationResponse.
Особенность: TripContinuationResponse должен содержать два поля: message (ответ ассистента) и updated_itinerary (опционально обновленный JSON маршрута).

Таск 3 — Реализовать trip message repository
Файл: app/repositories/trip_message_repository.py
Функции: create_message, get_trip_messages (с сортировкой по created_at ASC).
Требования: Только работа с БД, без вызовов AI-сервисов.

Таск 4 — Реализовать Prompt Builder
Файл: app/utils/prompt_builder.py
Что сделать: Создать шаблоны (f-strings или Jinja2) для:
Системного промпта (роль тревел-эксперта).
Первичной генерации на основе предпочтений.
Продолжения диалога (учет контекста + запрос на обновление JSON).

Таск 5 — Реализовать Groq Client
Файл: app/integrations/groq_client.py
Что сделать: Обертка над библиотекой groq.
Функционал: Метод для отправки списка сообщений и получения structured output (JSON mode). Если ключей нет — возвращать Mock-данные.

Таск 6 — Реализовать AI Service
Файл: app/services/ai_service.py
Логика: Главный оркестратор AI.
Собирает промпты через PromptBuilder.
Вызывает GroqClient.
Парсит ответ, разделяя текстовое сообщение и сырой JSON маршрута.

Таск 7 — Реализовать Trip Message Service
Файл: app/services/trip_message_service.py
Workflow:
Сохранить сообщение пользователя в БД.
Вытащить историю сообщений для контекста.
Вызвать AIService для получения ответа.
Сохранить ответ ассистента в БД.
Обновить поле itinerary_json в модели Trip.

Таск 8 — Реализовать continuation endpoint
Файл: app/api/v1/messages.py
Эндпоинт: POST /trips/{trip_id}/messages
Требования:
Проверка прав доступа (trip.user_id == current_user.id).
Вызов TripMessageService.
Возврат нового сообщения и обновленного плана поездки.
✅ Definition of Done (Критерии готовности)

Таблица trip_messages создана и связана с trips.

Эндпоинт продолжения диалога принимает текст и возвращает ответ ассистента.

AI-логика (промпты и клиенты) изолирована в папках utils, integrations и services.

Реализован Mock-режим: если Groq недоступен, система возвращает заглушки, не ломая флоу.

При добавлении уточняющего сообщения (например, "добавь еще один музей") itinerary_json в базе данных обновляется.
Out of scope: Стриминг ответа (Server-Sent Events), поддержка вложений (фото), сложная модерация контента.