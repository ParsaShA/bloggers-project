# تیم تولید محتوای وبلاگ با CrewAI + FastAPI

یک Crew شامل سه Agent (پژوهشگر، نویسنده، ویراستار) که با `Process.sequential` اجرا می‌شود و از طریق یک API با FastAPI در دسترس است.

## ساختار

```
blog-crew/
├── app/
│   ├── __init__.py
│   ├── crew.py      # Agent، Task، Crew و Process
│   └── main.py      # endpointهای FastAPI
├── requirements.txt
└── .env.example
```

## نصب و اجرا

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # کلیدها را داخل .env قرار دهید
uvicorn app.main:app --reload
```

مستندات تعاملی: http://127.0.0.1:8000/docs

## Endpointها

| مسیر | توضیح |
|---|---|
| `GET /health` | بررسی سلامت سرویس |
| `POST /generate` | تولید پست برای یک موضوع (`use_editor` اختیاری) |
| `POST /compare` | اجرا برای چند موضوع (حداقل ۲) و مقایسه‌ی تعداد کلمات و متن‌ها |
| `POST /compare-editor` | خروجی با ویراستار در برابر بدون ویراستار برای یک موضوع |

نمونه:

```bash
curl -X POST http://127.0.0.1:8000/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "هوش مصنوعی در بورس تهران"}'

curl -X POST http://127.0.0.1:8000/compare \
  -H "Content-Type: application/json" \
  -d '{"topics": ["هوش مصنوعی در بورس تهران", "هوش مصنوعی در آموزش"]}'
```

## تطبیق با الزامات تمرین

- دو Agent اصلی (Researcher و Writer) + Editor اختیاری (امتیاز اضافه)
- `Process.sequential` و `verbose=True` (مراحل استدلال در لاگ ترمینال دیده می‌شود)
- Writer بدون ابزار است و فقط از `context=[research_task]` استفاده می‌کند
- اجرا با دو موضوع متفاوت از طریق `/compare`
- ابزار جستجو: `SerperDevTool` (با `SERPER_API_KEY`) و در غیر این صورت `WebsiteSearchTool`

## سوال فکری پایانی (پاسخ پیشنهادی؛ پس از اجرای `/compare-editor` با مشاهده‌ی خودتان تطبیق دهید)

با حذف ویراستار، متن نهایی معمولاً از نظر محتوا شبیه است، اما در جزئیات کیفیت افت می‌کند: ناهماهنگی لحن، خطاهای نگارشی و املایی، جمله‌های طولانی یا تکراری، و گاهی خروج از بازه‌ی ۳۰۰ تا ۴۰۰ کلمه. دلیلش این است که نویسنده هم‌زمان باید محتوا را بسازد و کیفیت زبانی را کنترل کند، در حالی که ویراستار با نقش و هدف جداگانه، فقط روی بازبینی تمرکز می‌کند و یک «دور دوم» مستقل روی متن می‌اندازد؛ تقسیم وظیفه و بازبینی چندمرحله‌ای همان اصل اصلی کار تیمی در CrewAI است.
