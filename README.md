# Agency Template Repository

Шаблон-репозиторий для проектов AI-агентства. Содержит готовые CI/CD пайплайны, шаблоны задач и систему уведомлений.

## Быстрый старт

### 1. Создай репозиторий из этого шаблона

На GitHub нажми **"Use this template"** → **"Create a new repository"**.

### 2. Выбери нужный workflow

В папке `.github/workflows/` лежат пайплайны для разных типов проектов:

| Файл | Для чего |
|------|----------|
| `nextjs-vercel.yml` | Next.js + Vercel (SaaS, веб-приложения) |
| `react-vite.yml` | React + Vite + Vercel (SPA, лендинги) |
| `python-bot.yml` | Python боты (Telegram, Discord) |
| `notify-failure.yml` | Алерты при падении (оставь всегда) |

**Удали workflow-файлы, которые не нужны для конкретного проекта.** Оставь только подходящий + `notify-failure.yml`.

### 3. Настрой Secrets

GitHub → Settings → Secrets and variables → Actions → New repository secret.

### 4. Telegram-бот для мониторинга

```bash
cd telegram-bot
cp .env.example .env
pip install -r requirements.txt
python bot.py
```

Бот умеет: мониторить uptime сайтов (каждые 5 мин), присылать алерты при даунтайме, показывать статус по команде `/status`.
