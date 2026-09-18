# TestSupply

Два независимых проекта в одном репозитории:

- **`landing/`** — лендинг-резюме (React + Vite, статика).
- **`catalog/`** — каталог поставщиков продуктов питания для ресторанов
  (B2B): поиск по базе, семантический поиск, поиск новых поставщиков в
  интернете через AI, сравнение. Backend — FastAPI + PostgreSQL + Redis +
  Qdrant, frontend — React + Vite.

## Быстрый локальный запуск (всё сразу, через Docker)

Нужен только Docker и Docker Compose.

1. Скопируй пример конфига и впиши свой ключ OpenAI:

   ```bash
   cp catalog/backend/.env.example catalog/backend/.env
   # открой catalog/backend/.env и вставь OPENAI_API_KEY
   ```

2. Подними всё:

   ```bash
   docker compose up -d --build
   ```

3. Открой в браузере (порты слушают только `127.0.0.1` — рассчитано на то,
   что снаружи их публикует nginx на сервере; локально заходи так же, через
   localhost):
   - **http://localhost:8081** — лендинг
   - **http://localhost:8080/catalog/** — каталог поставщиков
   - **http://localhost:8080/api/docs** — Swagger-документация API

Первый запрос к поиску может занять ~30 секунд — грузится модель
эмбеддингов (дальше кэшируется в volume и работает быстро).

Остановить всё: `docker compose down` (данные останутся в volume, `-v`
удалит и их).

## Разработка отдельных частей без Docker

### Лендинг

```bash
cd landing
npm install
npm run dev
```

### Каталог — backend

Нужны Python 3.13, PostgreSQL, Redis (можно поднять их через
`docker compose up -d postgres redis qdrant` из корня, а backend
запускать локально).

```bash
cd catalog/backend
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # впиши OPENAI_API_KEY, поправь *_URL на localhost
uvicorn app.main:app --reload
```

### Каталог — frontend

```bash
cd catalog/frontend
npm install
npm run dev
```

При локальном `npm run dev` фронт по умолчанию обращается к
`http://localhost:8000` (см. `.env.development`). В собранном виде
(Docker/`npm run build`) он ходит на относительный `/api` — это
проксирует nginx самого контейнера фронта, поэтому в проде отдельно
настраивать адрес бэкенда не нужно.

## Переменные окружения (`catalog/backend/.env`)

Секретов в репозитории нет — есть только `catalog/backend/.env.example`
как образец. Свой `.env` **не коммитить** (уже в `.gitignore`). Ключевые
переменные:

| Переменная | Назначение |
|---|---|
| `LLM_PROVIDER` | `openai` или `local` (Ollama/LM Studio и т.п.) |
| `OPENAI_API_KEY`, `OPENAI_MODEL` | нужны при `LLM_PROVIDER=openai` |
| `LLM_BASE_URL`, `LLM_MODEL` | нужны при `LLM_PROVIDER=local` |
| `DATABASE_URL`, `REDIS_URL`, `QDRANT_URL` | адреса инфраструктуры |
| `CORS_ORIGINS` | через запятую, какие фронты пускать |

## Структура деплоя

- `docker-compose.yml` (в корне) — полный стек: Postgres, Redis, Qdrant,
  backend, frontend каталога (127.0.0.1:8080, собран с базовым путём
  `/catalog/`), лендинг (127.0.0.1:8081). Наружу ничего не публикуется
  напрямую — на сервере перед этим стоит системный nginx (вне Docker,
  конфиг в репозитории не хранится), который отдаёт домен по 80/443 и
  проксирует `/catalog/` и `/api/` на 8080, а всё остальное — на 8081.
- `catalog/docker-compose.yml` — тот же каталог отдельно, без лендинга
  (публикует порты бэкенда/фронта напрямую) — удобно для разработки
  только каталога.

Подробности по самому каталогу — в `catalog/backend` и
`catalog/frontend` (структура слоями: api → services → repositories →
db на бэкенде).
