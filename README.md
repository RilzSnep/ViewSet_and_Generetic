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



# ViewSet_and_Generetic

## Описание
Проект для курса DRF, реализующий систему управления обучением (LMS) с использованием Django REST Framework.

## Настройка удаленного сервера

1. **Создайте сервер** (например, на Yandex Cloud):
   - Установите Ubuntu 22.04.
   - Назначьте публичный IP (например, `158.160.184.103`).

2. **Установите зависимости**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-venv postgresql nginx gunicorn
   ```

3. **Настройте PostgreSQL**:
   ```bash
   sudo -u postgres psql
   CREATE DATABASE viewset_and_generic_db;
   CREATE USER myuser WITH PASSWORD 'mypassword' CREATEDB;
   ALTER DATABASE viewset_and_generic_db OWNER TO myuser;
   GRANT ALL PRIVILEGES ON SCHEMA public TO myuser;
   GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO myuser;
   ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO myuser;
   \q
   ```

4. **Клонируйте репозиторий**:
   ```bash
   git clone https://github.com/RilzSnep/ViewSet_and_Generetic.git
   cd ViewSet_and_Generetic
   ```

5. **Настройте виртуальное окружение**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

6. **Создайте файл `.env`** (на основе `.env.example`):
   - Скопируйте `.env.example` в `.env` и настройте переменные:
     ```bash
     cp .env.example .env
     nano .env
     ```
   - Пример `.env`:
     ```plaintext
     DATABASE_URL=postgresql://myuser:mypassword@localhost:5432/viewset_and_generic_db
     SECRET_KEY=your-secret-key
     DEBUG=True
     ```

7. **Примените миграции**:
   ```bash
   python manage.py migrate
   ```

8. **Настройте Gunicorn и Nginx**:
   - Создайте файл `/etc/systemd/system/gunicorn.service`:
     ```ini
     [Unit]
     Description=gunicorn daemon
     After=network.target

     [Service]
     User=rilzsnep
     WorkingDirectory=/var/www/ViewSet_and_Generetic
     ExecStart=/var/www/ViewSet_and_Generetic/venv/bin/gunicorn --workers 3 --bind unix:/var/www/ViewSet_and_Generetic/gunicorn.sock config.wsgi:application
     Restart=always

     [Install]
     WantedBy=multi-user.target
     ```
   - Запустите Gunicorn:
     ```bash
     sudo systemctl start gunicorn
     sudo systemctl enable gunicorn
     ```
   - Настройте Nginx (`/etc/nginx/sites-available/viewset`):
     ```nginx
     server {
         listen 80;
         server_name 158.160.184.103;

         location = /favicon.ico { access_log off; log_not_found off; }
         location /static/ {
             root /var/www/ViewSet_and_Generetic;
         }

         location / {
             proxy_pass http://unix:/var/www/ViewSet_and_Generetic/gunicorn.sock;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         }
     }
     ```
   - Активируйте конфигурацию:
     ```bash
     sudo ln -s /etc/nginx/sites-available/viewset /etc/nginx/sites-enabled/
     sudo nginx -t
     sudo systemctl restart nginx
     ```

9. **Настройте безопасность**:
   - Используйте SSH-ключи для доступа (добавьте публичный ключ в `~/.ssh/authorized_keys`).
   - Ограничьте порты:
     ```bash
     sudo ufw allow 22
     sudo ufw allow 80
     sudo ufw deny 5432
     sudo ufw enable
     ```

## Настройка деплоя через GitHub Actions

1. **Добавьте секреты** в GitHub:
   - Перейдите в `Settings > Secrets and variables > Actions`.
   - Добавьте `SSH_PRIVATE_KEY` (приватный ключ для доступа к серверу `158.160.184.103`).

2. **Workflow**:
   - Файл `.github/workflows/main.yml` настроен для:
     - Запуска тестов при push в ветку `dev`.
     - Деплоя на сервер после успешных тестов.

3. **Запуск**:
   - Выполните `git push origin dev`, чтобы автоматически запустить workflow.
   - После успешных тестов проект деплоится на сервер.

## Доступ к приложению
После деплоя приложение доступно по адресу: `http://158.160.184.103/api/lessons/1/`.

## Требования
- Python 3.12
- PostgreSQL
- Git
- SSH-доступ к серверу
