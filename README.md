# BlackHat Seo For R&D

این پروژه یک API مبتنی بر Django + Django REST Framework است که برای تست و شبیه‌سازی درخواست‌های وب طراحی شده — به‌صورت دسته‌ای یا موازی — و برای ثبت، زمان‌بندی و مدیریت اجراها از Celery استفاده می‌کند.

مهم: این مستند خواندن کد منبع است و با فرض محیط توسعه محلی نوشته شده. از این ابزار برای حمله یا ایجاد ترافیک مخرب به وب‌سایت‌هایی که مالک آن نیستید استفاده نکنید. استفاده نادرست ممکن است غیرقانونی باشد.

## قابلیت‌ها

- زمان‌بندی و اجرای وظایف درخواست HTTP با Celery (پشتیبانی از ETA و تاخیر)
- اجرای سریال (تک‌درخواست در حلقه) و اجرای هم‌زمان (ThreadPoolExecutor)
- لیست و مشاهده وضعیت تسک‌ها، توقف و از سرگیری تسک‌ها
- آپلود پروکسی‌ها و User-Agent ها (فایل‌های .txt / .csv)
- ذخیره لاگ درخواست‌ها با جزئیات (کد وضعیت، UA، پروکسی، خطا)
- احراز هویت JWT برای دسترسی به endpointهای محافظت‌شده
- چند دیتابیس: SQLite پیش‌فرض و یک اتصال MySQL جدا برای کاربران (دسترسی read از طریق router)
- مستندات API با drf-spectacular (Swagger/Redoc)

## ساختار پروژه (انتخابی)

- `config/` : تنظیمات Django، Celery و urls
- `accounts/` : مدل کاربر سفارشی، serializer و view برای لیست کاربران (استفاده از دیتابیس `user_cid`)
- `blockHat/` : مدل‌ها، serializerها و endpointهای اصلی برای مدیریت تسک، پروکسی و UA
- `blockHat/utils/tasks.py` : وظایف Celery که درخواست‌ها را ارسال و لاگ‌ها را ذخیره می‌کنند
- `db.sqlite3` : دیتابیس توسعه محلی پیش‌فرض

## پیش‌نیازها

- Python 3.11+ (پروژه با Django 5.2 و پکیج‌های جدید سازگار است)
- RabbitMQ (به‌عنوان broker پیش‌فرض Celery در `config/settings.py`: `amqp://guest:guest@localhost:5672`)
- (اختیاری) MySQL برای اتصال `user_cid` اگر می‌خواهید از دیتابیس کاربران خارجی استفاده کنید

فایل وابستگی‌ها: `requrtments.txt` (نسخه‌های قفل‌شده)

## تنظیم محیط توسعه محلی

1. ایجاد و فعال‌سازی virtualenv:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. نصب وابستگی‌ها:

```powershell
pip install -r requrtments.txt
```

3. فایل محیطی (اختیاری):
   اگر از MySQL برای `user_cid` استفاده می‌کنید، مقادیر زیر باید در محیط قرار گیرند (مثلاً با `set` در PowerShell یا از طریق فایل `.env` و `python-decouple`):

- DB_NAME_USER
- DB_USER_USR
- DB_PASSWORD_USER
- DB_HOST_USER
- DB_PORT_USER

4. مایگریت‌ها و ساخت سوپر یوزر:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

## اجرا (سرور + Celery)

1. اجرای RabbitMQ (نمونه محلی): نصب و اجرای RabbitMQ روی پورت 5672
2. اجرا کردن Celery worker در پوشه پروژه:

```powershell
# از روت پروژه اجرا کنید
celery -A config worker --loglevel=info
```

3. (اختیاری) اگر می‌خواهید تسک‌ها را برنامه‌ریزی کنید یا از ویژگی‌های result backend استفاده کنید، اطمینان حاصل کنید که broker و backend پیکربندی شده‌اند. تنظیمات پیش‌فرض:

- BROKER: `amqp://guest:guest@localhost:5672`
- RESULT_BACKEND: `rpc://`

4. اجرای سرور توسعه Django:

```powershell
python manage.py runserver
```

## احراز هویت

- پروژه از JWT (djangorestframework-simplejwt) استفاده می‌کند.
- گرفتن توکن:
  - POST به `/api/token/` با `username` و `password` → برمی‌گرداند `access` و `refresh` token
  - POST به `/api/token/refresh/` برای گرفتن توکن جدید
- بسیاری از endpointهای مهم (مثل `run-request/`) محافظت شده و نیاز به هدر `Authorization: Bearer <ACCESS_TOKEN>` دارند.

## مهم‌ترین endpointها

- ثبت و زمان‌بندی درخواست‌ها (GET): `/run-request/`

  - پارامترها (query params):
    - `url` (required)
    - `range` (required) — تعداد درخواست‌ها (محدوده: 1 تا 1000)
    - `user_agent` (optional) — `all`|`mobile`|`desktop` (پیش‌فرض: `all`)
    - `referrer` (optional) — مقدار هدر Referer
    - `delay` (optional) — تأخیر بر حسب ثانیه (countdown)
    - `eta` (optional) — زمان شروع بصورت ISO datetime (اگر استفاده شود، `delay` نادیده گرفته می‌شود)
  - پاسخ شامل `task_id` و `eta` و پیام است
- اجرای با ThreadPool (GET): `/run-request-thread/` (پارامترها مثل بالا)
- آپلود پروکسی (POST فایل .txt یا .csv): `/upload-proxies/` (فایل با key=`file`)
- آپلود User-Agents (POST فایل .txt): `/upload-user-agents/` (فایل با key=`file`)
- مشاهده وضعیت تسک (GET): `/task-status-info/<task_id>/`
- لیست تاریخچه تسک‌ها (GET): `/list-history-task-status/` — خروجی صفحه‌بندی شده
- متوقف کردن تسک (POST): `/stop-task/<task_id>/`
- از سرگیری تسک متوقف‌شده (POST): `/run-stoped-task/<task_id>/`
- لیست کاربران (خواندن از دیتابیس `user_cid`): `/all/users/`

## مدل‌های مهم

- `blockHat.models.TaskStatus` — ذخیره وضعیت هر تسک
- `blockHat.models.RequestLog` — لاگ هر درخواست
- `blockHat.models.Proxy` — لیست پروکسی‌ها
- `accounts.models.User` — مدل کاربر سفارشی

## نحوه کار داخلی (خلاصه)

- وقتی endpoint `/run-request/` فراخوانی می‌شود، یک تسک Celery (`request_data_task_simple` یا `request_data_thread`) ایجاد می‌شود.
- تسک‌ها پروکسی‌ها و user-agentها را از دیتابیس می‌گیرند و با `requests.get` به URL هدف درخواست می‌زنند.
- لاگ هر درخواست در `RequestLog` ذخیره می‌شود و `TaskStatus` با پیشرفت به‌روز می‌شود.
- امکان توقف تسک با تغییر فیلد `stop_requested` و سپس خواندن آن داخل حلقه تسک فراهم شده است.

## هشدار امنیتی و اخلاقی

- این پروژه ابزارهایی دارد که می‌توانند حجم بالایی از ترافیک ساختگی بسازند. این ابزارها می‌توانند به‌راحتی مورد سوءاستفاده قرار گیرند.
- فقط روی سرویس‌هایی آزمایش کنید که مالک آن هستید یا صراحتا اجازه تست دارید.

## توسعه و دیباگ

- لاگ‌های Celery در زمان اجرا اطلاعات خوبی درباره وضعیت تسک‌ها چاپ می‌کنند.
- برای توسعه محلی، از `DEBUG=True` در `config/settings.py` استفاده شده است — در محیط تولید آن را خاموش کنید.

## موارد پیشنهادی برای بهبود (آتی)

- اضافه کردن تست‌های واحد برای viewها و tasks
- اضافه کردن rate-limiting و محدودیت‌های بیشتر برای هر تسک
- اعتبارسنجی و پاک‌سازی بهتر ورودی‌ها (مثلاً فرمت URL و referrer)
- پشتیبانی از پروکسی‌های با auth و استفاده از pool مدیریت شده برای requests
- مانیتورینگ و dashboard برای تسک‌های در حال اجرا
