# BlackHat SEO (Django + DRF)

این مخزن یک پروژه Django + Django REST Framework برای ایجاد درخواست‌های موازی (scraping / load-like requests) به یک URL مشخص است. پروژه از Celery برای اجرای تسک‌ها در پس‌زمینه استفاده می‌کند و داده‌هایی مانند پراکسی‌ها، user-agentها و لاگ درخواست‌ها را در دیتابیس SQLite ذخیره می‌کند.

توجه: این پروژه نمونه‌ای برای تحقیق و توسعه (R&D) به نظر می‌رسد و با هدف آموزشی ساخته شده است. استفاده از هر ابزار یا اسکریپتی برای ارسال ترافیک به وب‌سایت‌ها بدون اجازه می‌تواند غیرقانونی یا غیراخلاقی باشد. از این نرم‌افزار مسئولانه استفاده کنید.

## محتوای اصلی

- `config/` : تنظیمات Django، Celery و آدرس‌دهی پروژه.
- `blockHat/` : اپ اصلی که شامل مدل‌ها، ویوها، serializerها، تسک‌های Celery و مسیرها است.
  - `models.py` : مدل‌های `Proxy`, `TaskStatus`, `UserAgentDesktop`, `UserAgentMobile`, `RequestLog`.
  - `utils/tasks.py` : تسک Celery `request_data_task` که چند رشته‌ای (ThreadPoolExecutor) برای ارسال درخواست‌ها استفاده می‌کند.
  - `views/` : ویوهای API برای اجرای تسک، آپلود پراکسی و user-agent و مشاهده وضعیت تسک.
  - `urls.py` : مسیرهای API اپ.
- `auth/` : شامل `AuthJwt.py` (در حال حاضر خالی).
- `db.sqlite3` : دیتابیس SQLite (نمونه/محلی).
- `requrtments.txt` : وابستگی‌های پروژه.

## نیازمندی‌ها

- Python 3.11+ (پروژه با Django 5.2 نوشته شده است)
- RabbitMQ در حالت محلی برای Celery (تنظیم پیش‌فرض: `amqp://guest:guest@localhost:5672`)

وابستگی‌ها (مشاهده‌شده در `requrtments.txt`):

- Django==5.2.6
- djangorestframework==3.16.1
- celery==5.5.3
- drf-spectacular
- drf-spectacular-sidecar
- requests
- user-agents
- redis (در فایل requirements آمده اما کانفیگ استفاده نشده)

برای نصب وابستگی‌ها:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requrtments.txt
```

(در ویندوز از PowerShell بالا استفاده کنید)

## تنظیمات اولیه

1. RabbitMQ را نصب و اجرا کنید (برای توسعه محلی می‌توانید از نسخه پیش‌فرض guest/guest استفاده کنید).
2. فایل تنظیمات (`config/settings.py`) شامل SECRET_KEY و DEBUG است. در محیط تولید مقدار `DEBUG = False` و `SECRET_KEY` امن قرار دهید.
3. دیتابیس به‌صورت پیش‌فرض SQLite است. اگر می‌خواهید از Postgres یا MySQL استفاده کنید، `DATABASES` را ویرایش کنید.

## مهاجرت‌ها و اجرای سرور

```powershell
# در محیط مجازی فعال‌شده
python manage.py migrate
python manage.py runserver
```

## راه‌اندازی Celery (تسک‌ها)

پیکربندی Celery در `config/celery.py` تنظیم شده و در `config/settings.py` مقدار `CELERY_BROKER_URL` برابر `amqp://guest:guest@localhost:5672` است.

راه‌اندازی worker (در پوشه پروژه):

```powershell
# از درون virtualenv
celery -A config worker -l info
```

همچنین از `flower` یا ابزارهای مشابه برای مانیتورینگ می‌توانید استفاده کنید.

## API Endpoints

مسیرهای اپ در `blockHat/urls.py` تعریف شده‌اند. مسیر پایه (در `config/urls.py`) را بررسی کنید و در صورت لازم prefix را اضافه کنید. مسیرهای شناخته‌شده:

- GET /run-request/?url=`<URL>`&range=`<N>`&user_agent=<all|mobile|desktop>&referrer=`<REF>`

  - شروع یک تسک Celery برای ارسال N درخواست به URL مشخص.
  - پاسخ: `{"message":..., "task_id": "..."}`
  - پارامترها:
    - `url` (الزامی)
    - `range` (الزامی، تعداد درخواست‌ها)
    - `user_agent` (اختیاری: `all`, `mobile`, `desktop`)، پیش‌فرض `all`
    - `referrer` (اختیاری) پیش‌فرض `https://www.facebook.com/`
- POST /upload-proxies/ (multipart/form-data)

  - آپلود فایل `.txt` یا `.csv` حاوی لیست پراکسی‌ها. حداکثر سایز 1MB.
  - پاسخ شامل تعداد کل، اضافه‌شده‌ها و ردشده‌هاست.
- POST /upload-user-agents/ (multipart/form-data)

  - آپلود فایل `.txt` که هر خط یک user-agent است. با استفاده از کتابخانه `user-agents` نوع موبایل/دسکتاپ تشخیص داده شده و در مدل مربوطه ذخیره می‌شود.
- GET /task-status/<task_id>/

  - مشاهده وضعیت تسک (RUNNING/COMPLETED)، تعداد درخواست‌های تکمیل‌شده و مدت زمان اجرای تسک.

## مدل‌ها (خلاصه)

- Proxy: proxy_test (متن)، created_at
- TaskStatus: task_id, url, referer, total_requests, completed_requests, status, duration, created_at, updated_at
- UserAgentDesktop: user_agent, created_at
- UserAgentMobile: user_agent, created_at
- RequestLog: task(FK to TaskStatus), status_code, url, proxy, referer, user_agent, language, error, created_at

## توضیح عملکرد تسک اصلی

تسک `request_data_task` در `blockHat/utils/tasks.py`:

- یک رکورد `TaskStatus` ایجاد یا بازیابی می‌کند.
- لیست پراکسی‌ها و user-agentها را از دیتابیس می‌خواند.
- با استفاده از `ThreadPoolExecutor` تا N درخواست همزمان ارسال می‌کند (حداکثر 20 worker یا N).
- برای هر درخواست یک ردیف `RequestLog` ذخیره می‌کند و تعداد `completed_requests` را آپدیت می‌کند.
- مدت زمان اجرای تسک را محاسبه و وضعیت تسک را به `COMPLETED` تغییر می‌دهد.

نکته عملکردی: تسک از کتابخانه `requests` استفاده می‌کند؛ بنابراین توابع blocking هستند ولی با ThreadPoolExecutor موازی‌سازی انجام می‌شود.

## موارد امنیتی و حقوقی

- فایل `config/settings.py` شامل یک SECRET_KEY خام است. در مخزن عمومی نباید SECRET_KEY قرار گیرد.
- ارسال ترافیک به سرویس‌های دیگر بدون اجازه ممکن است قوانین را نقض کند؛ حتماً از این کد در محیط‌های آزمایشی و با اجازه هدف استفاده کنید.

## اجرا و آزمایش محلی سریع

1. فعال کردن virtualenv و نصب وابستگی‌ها (دستور بالا)
2. اجرای مهاجرت‌ها: `python manage.py migrate`
3. اجرای سرور: `python manage.py runserver`
4. اجرای RabbitMQ محلی و سپس راه‌اندازی Celery worker:

```powershell
# در یک ترمینال
rabbitmq-server  # یا راه‌اندازی سرویس RabbitMQ به روشی که روی ویندوز شما نصب شده

# در ترمینال دوم
celery -A config worker -l info
```

5. ارسال درخواست برای تست: باز کردن مرورگر یا curl به:

```
http://127.0.0.1:8000/run-request/?url=https://example.com&range=10
```

## سوالات و پشتیبانی

اگر می‌خواهید README را به نسخه انگلیسی یا مستندات API بیشتر (مثلاً نمونه پاسخ‌ها، schema drf-spectacular) تبدیل کنم، بگو تا اضافه کنم.

---

README به زبان فارسی نوشته شد و شامل راه‌اندازی، مستندات endpointها و توضیحات معماری است. اگر ترجیحات دیگری برای قالب‌بندی یا جزئیات می‌خواهی (مثلاً افزودن مثال‌های JSON، نمودار ER، یا فایل Postman) بگو تا اضافه کنم.
