# Prompt Engineering Guide — AI Image & Video Generation

> Шпаргалка для агентства. Принципы написания промптов для генерации изображений и видео.

---

## 1. Универсальная структура промпта

```
[Стиль/Медиум] + [Субъект] + [Действие/Поза] + [Окружение/Фон] + [Освещение] + [Настроение/Атмосфера] + [Технические параметры]
```

**Пример:**
```
Cinematic photograph of a young entrepreneur working on a laptop in a modern co-working space,
golden hour light streaming through floor-to-ceiling windows, shallow depth of field,
shot on Arri Alexa, 35mm lens, warm color grading, professional corporate photography
```

---

## 2. Ключевые принципы

### Будь конкретным
- Плохо: `красивый пейзаж`
- Хорошо: `Misty mountain valley at dawn, pine forests in foreground, snow-capped peaks, volumetric fog, aerial drone perspective`

### Указывай стиль и медиум
Камера/плёнка: `shot on Canon EOS R5`, `Kodak Portra 400`, `35mm film grain`
Арт-стиль: `watercolor illustration`, `vector flat design`, `isometric 3D render`
Референсы: `in the style of Studio Ghibli`, `Wes Anderson color palette`

### Управляй освещением
| Термин | Эффект |
|--------|--------|
| `golden hour` | Тёплый мягкий свет |
| `blue hour` | Холодный сумеречный тон |
| `Rembrandt lighting` | Драматичный портретный свет |
| `neon-lit` | Киберпанк/городская атмосфера |
| `studio lighting, softbox` | Чистый продуктовый свет |
| `backlit, rim light` | Силуэт с контурным светом |
| `overcast, diffused` | Ровный мягкий свет без теней |

### Указывай композицию
`rule of thirds`, `centered composition`, `symmetrical`, `wide establishing shot`,
`close-up`, `macro`, `bird's eye view`, `low angle`, `Dutch angle`, `over-the-shoulder`

---

## 3. Промпты для изображений по моделям

### FLUX 1.1 Pro (Higgsfield)
- Хорошо понимает естественный язык, длинные описательные промпты
- Отлично работает с фотореализмом и типографикой
- Поддерживает текст на изображениях (указывай в кавычках: `with text "Hello World"`)

```
Professional SaaS dashboard UI mockup displayed on a MacBook Pro screen,
clean minimal design, data visualization charts, dark mode interface,
shallow depth of field, studio product photography, neutral gray background
```

### Midjourney (через API/Discord)
- Использует параметры: `--ar 16:9`, `--v 6.1`, `--style raw`, `--q 2`
- Краткие, ёмкие промпты работают лучше длинных
- `--no` для негативных промптов: `--no text, watermark, blurry`

```
modern tech startup office interior, glass walls, warm lighting,
minimalist furniture, plants --ar 16:9 --v 6.1 --style raw
```

### Stable Diffusion (SDXL / SD3)
- Использует систему весов: `(important detail:1.3)`, `[less important:0.7]`
- Негативный промпт критически важен
- CFG Scale 7-9 для баланса качества/креативности

```
Positive: professional headshot portrait of a confident business woman,
(sharp focus:1.2), studio lighting, neutral background, corporate style,
(high quality:1.3), 8k uhd

Negative: blurry, distorted, ugly, deformed hands, watermark, text,
low quality, oversaturated
```

---

## 4. Промпты для видео по моделям

### Kling 2.0 / 3.0
- Описывай движение камеры явно: `camera slowly pans left`, `tracking shot following subject`
- Указывай темп: `slow motion`, `time-lapse`, `real-time`
- Первый кадр описывай детально — модель строит от него

```
Smooth tracking shot of a sleek mobile app interface being demonstrated on a smartphone,
fingers scrolling through modern UI, shallow depth of field,
soft studio lighting on white desk, camera slowly orbits around the phone, 5 seconds
```

### Veo 3.1 (Google)
- Понимает сложные сценарии и физику
- Хорошо работает с описанием «от начала к концу»
- Поддерживает длинные промпты с нарративом

```
A cinematic product reveal: camera starts on a dark surface, a beam of light
slowly illuminates a futuristic gadget from above, the device powers on
with a subtle glow, camera circles around it revealing sleek design details,
dramatic orchestral music mood, 4K commercial quality
```

### Wan 2.5
- Сильный в стилизации и аниме-контенте
- Указывай frame rate если важно: `24fps cinematic`, `60fps smooth`

### Sora 2 (OpenAI)
- Хорошо понимает физику и пространственные отношения
- Описывай сцену как режиссёр: начало → развитие → конец
- Работает с «кинематографическим» языком

```
Opening shot: a wide aerial view of a futuristic city at sunset.
The camera slowly descends toward a glass skyscraper.
Through the windows, we see a team collaborating around a holographic display.
The camera pushes through the glass into the room. Warm interior lighting,
lens flare from the sunset. Cinematic, Blade Runner 2049 mood.
```

### MiniMax
- Быстрая генерация, хорош для итераций
- Короткие чёткие промпты работают лучше

---

## 5. Промпты для направлений агентства

### SaaS / Продуктовые скриншоты
```
Шаблон: [Device] displaying [App type] with [Key UI elements],
[Environment], [Lighting], [Photography style]
```
Ключевые слова: `clean UI`, `modern dashboard`, `data visualization`,
`dark mode / light mode`, `glassmorphism`, `neumorphism`

### Landing Pages / Веб-дизайн
```
Шаблон: [Style] hero section for [Business type],
[Visual elements], [Color scheme], [Mood]
```
Ключевые слова: `above the fold`, `hero image`, `gradient background`,
`floating elements`, `3D illustration`, `isometric icons`

### AI Video / Продакшн
```
Шаблон: [Shot type] of [Subject] [Action],
[Camera movement], [Lighting], [Duration], [Mood/Reference]
```
Ключевые слова: `cinematic`, `commercial quality`, `smooth transition`,
`product reveal`, `logo animation`, `brand intro`

### Боты / Техническое
```
Шаблон: [Device/Interface] showing [Chat/Bot interface],
[Conversation example], [Context], [Style]
```
Ключевые слова: `chat interface`, `message bubbles`, `typing indicator`,
`bot avatar`, `conversation flow`, `mobile app screenshot`

---

## 6. Усилители качества

### Фотореализм
`photorealistic`, `hyperrealistic`, `8K UHD`, `RAW photo`,
`shot on [camera model]`, `[lens] mm lens`, `DSLR quality`

### Иллюстрация
`detailed illustration`, `vector art`, `concept art`,
`digital painting`, `matte painting`, `trending on ArtStation`

### 3D
`3D render`, `Octane render`, `Unreal Engine 5`, `ray tracing`,
`global illumination`, `physically based rendering`, `C4D`

### Кинематограф (для видео)
`cinematic`, `anamorphic lens`, `film grain`, `color graded`,
`35mm`, `shallow DOF`, `bokeh`, `letterbox`

---

## 7. Чего избегать

| Проблема | Решение |
|----------|---------|
| Слишком абстрактно | Добавь конкретные детали и числа |
| Конфликтующие стили | Выбери один стиль и придерживайся |
| Слишком много объектов | Фокус на 1-2 главных элементах |
| Нет указания на качество | Добавь `high quality`, `detailed`, разрешение |
| Руки/пальцы (изображения) | Используй `(detailed hands:1.2)` или скрой руки композицией |
| Текст на изображениях | Указывай текст в кавычках, не все модели умеют |
| Нет движения (видео) | Явно описывай камеру и действие субъекта |

---

## 8. Workflow: от идеи к результату

1. **Бриф** → определи цель, аудиторию, платформу размещения
2. **Референсы** → собери визуальные примеры желаемого результата
3. **Черновик промпта** → используй шаблон из секции 5
4. **Dry run** → `python generate_images.py --dry-run --prompt "saas_dashboard"`
5. **Первая генерация** → оцени результат, запиши что исправить
6. **Итерация** → уточни промпт, измени параметры
7. **Финал** → лучший результат → постобработка если нужно
8. **Сохрани промпт** → добавь удачный промпт в `prompts.json`

---

## 9. Переменные в prompts.json

Промпты в `prompts.json` поддерживают переменные `{variable}`:

```bash
# Подставить переменные при генерации
python generate_images.py --prompt saas_dashboard --vars '{"app_name": "TaskFlow", "color_scheme": "dark blue"}'

# Dry run для проверки
python generate_images.py --prompt saas_dashboard --vars '{"app_name": "TaskFlow"}' --dry-run
```

---

*Последнее обновление: апрель 2026*
