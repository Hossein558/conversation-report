# رفع اشکال

## مکالمه پیدا نمی‌شود

پیام `فایل مکالمه یافت نشد` یعنی در مسیر پیش‌فرض، پوشه‌ای با آن `ConversationID` و فایل `transcript.jsonl` وجود ندارد.

اول فهرست موجود را بگیرید:

```powershell
python src/conversation_report.py --list
```

اگر فهرست خالی بود یا مکالمه‌ها جای دیگری هستند، مسیر را صریح بدهید:

```powershell
python src/conversation_report.py <ConversationID> --brain-dir "D:\path\to\brain"
```

دلایل رایج:

| علت | توضیح |
| --- | --- |
| اشتباه در شناسه | شناسه با خط تیره و ۳۶ کاراکتر است، مثل `cf795541-f47d-4888-9a43-4bc011e7d1ea` |
| مسیر پیش‌فرض متفاوت | اگر Antigravity روی پروفایل کاربر دیگری نصب است، مسیر عوض می‌شود |
| مکالمه فقط در حافظه است | مکالمه‌های در حال اجرا ممکن است هنوز فایل کامل نداشته باشند |
| کاربر اشتباه | روی ویندوز مسیر از `C:\Users\<Username>` شروع می‌شود، نه از پوشه خانه شل |

## خروجی متن‌ها وسط جمله بریده است

در `transcript.jsonl` محتوای حجیم با `<truncated N bytes>` جایگزین می‌شود. برای متن کامل:

```powershell
python src/conversation_report.py <ConversationID> --full-log --full
```

اگر باز هم بریده بود، فایل اصلی همان مرحله را مستقیم بخوانید:

```powershell
Get-Content "$env:USERPROFILE\.gemini\antigravity\brain\<ConversationID>\.system_generated\steps\<شماره>\output.txt"
```

## گزارش می‌گوید مکالمه کار اجرایی نداشته

این تقریباً همیشه یعنی فقط فیلد `content` خوانده شده. در لاگ واقعی، رکوردهای `MODEL` یا `content` دارند یا `tool_calls`:

| حالت | تعداد در یک مکالمه واقعی |
| --- | --- |
| فقط `tool_calls` | ۷۹۹ |
| فقط `content` | ۹۵۶ |
| هر دو | ۲ |

پس اگر فقط `content` را بخوانید، حدود نصف فعالیت نادیده می‌ماند. برای دیدن ابزارها:

```powershell
python src/conversation_report.py <ConversationID> --tools
```

## ابزار جدیدتر `replace_file_content` و `write_to_file` را نمی‌بینم

نام ابزارها در نسخه‌های مختلف Antigravity فرق می‌کند. در رکورد `tool_calls`، نام از فیلد `name` خوانده می‌شود و اگر نبود از `tool_name`. هر ابزار ناشناخته را در گزارش فهرست کنید به‌جای اینکه نادیده بگیرید.

برای دیدن نام دقیق ابزارهای یک مکالمه، خط‌های دارای `tool_calls` را مستقیم بخوانید:

```powershell
Select-String -Path "$env:USERPROFILE\.gemini\antigravity\brain\<ConversationID>\.system_generated\logs\transcript.jsonl" -Pattern '"tool_calls":\[\{"name":"([a-z_]+)"' -AllMatches |
  ForEach-Object { $_.Matches } | ForEach-Object { $_.Groups[1].Value } | Group-Object | Sort-Object Count -Descending
```

## فایل `transcript_full.jsonl` وجود ندارد

بعضی مکالمه‌های کوچک فقط نسخه سبک دارند. اگر با `--full-log` خطا گرفتید، بدون آن سوئیچ اجرا کنید:

```powershell
python src/conversation_report.py <ConversationID>
```

## مسیرها یا نام‌های فارسی به‌هم‌ریخته نشان داده می‌شوند

خروجی را با UTF-8 تنظیم کنید. اسکریپت خودش این کار را انجام می‌دهد، ولی اگر در ترمینال قدیمی اجرا می‌کنید:

```powershell
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001
python src/conversation_report.py <ConversationID>
```

اگر فایل خروجی می‌سازید، با UTF-8 ذخیره کنید.

## روی لینوکس یا macOS کار نمی‌کند

مسیر پیش‌فرض خودکار از پوشه خانه کاربر ساخته می‌شود:

```text
~/.gemini/antigravity/brain/<ConversationID>/
```

اگر مکالمه‌ها جای دیگری هستند، `--brain-dir` یا متغیر `ANTIGRAVITY_BRAIN_DIR` را بدهید:

```bash
python3 src/conversation_report.py <ConversationID> --brain-dir "$HOME/other/location/brain"
```

لانچر `.cmd` فقط ویندوزی است؛ روی لینوکس و مک مستقیم اسکریپت پایتون را صدا بزنید.

## تاریخ‌ها با ساعت محلی نمی‌خوانند

فیلد `created_at` به وقت UTC است. برای تبدیل به وقت تهران سه ساعت و سی دقیقه اضافه کنید. مثال:

```text
created_at = 2026-10-17T11:20:58Z   →   وقت تهران ۱۴:۵۰:۵۸
```

در متن خود لاگ، بعضی رکوردهای `GENERIC` تاریخ محلی را هم داخل متن دارند و با `+03:30` علامت خورده است.

## مکالمه بزرگ کند است یا حافظه می‌خورد

اسکریپت خط‌به‌خط می‌خواند و کل فایل را در حافظه نگه نمی‌دارد. اگر با مکالمه‌های چند ده مگابایتی کار می‌کنید:

- از `--turns` و `--last` مقدار کوچک‌تر بدهید تا فهرست کوتاه شود.
- از `--full-log` استفاده نکنید، چون آن فایل بزرگ‌تر است.
- اگر فقط فهرست مکالمه‌ها را می‌خواهید، `--list` سریع‌تر است چون لاگ را باز نمی‌کند.

## خطوط خراب در فایل لاگ

اگر خطی JSON معتبر نبود، آن را نادیده بگیرید. وجود یک خط خراب، بقیه فایل را بی‌اعتبار نمی‌کند. این حالت در مکالمه‌هایی که وسط نوشتن بودند طبیعی است.

## گزارش حاوی اطلاعات حساس است

این طبیعی است؛ لاگ مکالمه می‌تواند شامل رمز سرورها، توکن‌ها و آدرس‌های داخلی باشد. قبل از اشتراک‌گذاری:

- خطوطی که رمز یا توکن دارند را حذف کنید.
- آدرس سرورهای داخلی را با جای‌نگهدار عوض کنید.
- اگر خروجی را در مخزن عمومی می‌گذارید، نام کاربری ویندوز داخل مسیرها را هم پاک کنید.

## `check-conversation.cmd` اجرا نمی‌شود

اگر پیام `'n.cmd' is not recognized` یا مشابهش را دیدید، فایل `.cmd` با پایان‌خط یونیکسی ذخیره شده است. cmd ویندوز به پایان‌خط CRLF نیاز دارد. فایل را با پایان‌خط ویندوزی بازنویسی کنید:

```powershell
$content = Get-Content "check-conversation.cmd" -Raw
[System.IO.File]::WriteAllText("$PWD\check-conversation.cmd", ($content -replace "`r?`n", "`r`n"), [System.Text.Encoding]::ASCII)
```

همچنین اگر مسیر پوشه والد شامل کاراکترهای غیر ASCII باشد، cmd ممکن است در پارس کردن مسیر مشکل داشته باشد. در آن حالت مسیر نصب را به یک پوشه با نام انگلیسی منتقل کنید یا مستقیم اسکریپت پایتون را صدا بزنید.
