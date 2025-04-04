# ViewSet_and_Generetic

Проект для онлайн-обучения, реализованный с использованием Django, DRF, PostgreSQL, Redis и Celery.

## Запуск проекта через Docker Compose

### Требования
- Docker
- Docker Compose

### Шаги для запуска
1. Склонируйте репозиторий:
   ```bash
   git clone <ссылка_на_репозиторий>
   
2. Перейдите в директорию проекта:
    ```bash
    cd ViewSet_and_Generetic
    ```

3. Создайте файл .env на основе шаблона .env.example и заполните его своими данными:    
    ```bash
    cp .env.example .env
    ```
    
4. Запустите проект:
    ```bash
    docker-compose up --build
    ```
   * Флаг --build пересобирает образы при необходимости.

Проверка работоспособности

1. Бэкенд: Откройте браузер и перейдите по адресу http://localhost:8000. Вы должны увидеть Django-сервер.
2. База данных: Подключитесь к PostgreSQL:

    ```bash
    docker-compose exec db psql -U postgres -d viewset_and_generic_db
    ```
3. Redis: Проверьте доступность:
    
    ```bash
    docker-compose exec redis redis-cli ping
    ```
   Ожидаемый ответ: PONG.
    
4. Celery: Проверьте логи воркера:
    ```bash
    docker-compose logs celery
    ```
    
5. Celery Beat: Проверьте логи планировщика:
    ```bash
    docker-compose logs celery-beat
    ```
    
### Остановка проекта
- Для остановки выполните:
    ```bash 
    docker-compose down
    ```
- Для удаления томов (если нужно очистить данные):
    
    ```bash
    docker-compose down -v
    ```
    

### Дополнительные рекомендации:
1. **`.gitignore`**:
   Убедитесь, что у вас есть файл `.gitignore` с такими строками:
   - .env
   - .idea/
    - venv/
   - pycache/
    - *.pyc
   - db.sqlite3
   - media/

2. **Git и GitHub**:
- Создайте ветку для домашней работы (например, `feature/docker-compose`).
- Загрузите изменения (`docker-compose.yaml`, `.env.example`, обновлённый `README.md`) в репозиторий.
- Создайте pull request в ветку `develop`.

3. **Проверка перед отправкой**:
- Убедитесь, что все сервисы запускаются командой `docker-compose up --build`.
- Проверьте, что зависимости между сервисами работают (например, бэкенд не стартует, пока `db` и `redis` не готовы).

Если у вас есть ещё вопросы или что-то нужно доработать, дайте знать!