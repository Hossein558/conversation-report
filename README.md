# conversation-report

استخراج و خلاصه‌سازی مکالمه‌های Google Antigravity بر اساس `ConversationID`.

Antigravity هر مکالمه را به‌صورت فایل متنی JSON Lines روی دیسک نگه می‌دارد. این ابزار همان فایل‌ها را می‌خواند و یک گزارش خوانا می‌سازد: موضوع مکالمه، درخواست‌های کاربر، ابزارهای اجراشده، خطاها، آخرین وضعیت، و فایل‌هایی که در آن مکالمه تولید شده‌اند.

هیچ سرویسی اجرا نمی‌شود، هیچ درخواست شبکه‌ای زده نمی‌شود، و هیچ چیزی در پوشه مکالمه تغییر نمی‌کند. فقط کتابخانه استاندارد پایتون لازم است.

## چرا لازم است

وقتی می‌خواهید یک ایجنت دیگر (Claude Code، Cursor، Gemini CLI، Codex، یا هر ابزار دیگری) درباره کاری که در Antigravity انجام شده گزارش بدهد، آن ایجنت از محتوای مکالمه بی‌خبر است. این مخزن هم یک پرامپت آماده دارد که به ایجنت دیگر می‌دهید، و هم یک اسکریپت که بدون درگیر کردن هیچ مدلی، گزارش را می‌سازد.

## شروع سریع

```powershell
git clone https://github.com/Hossein558/conversation-report.git
cd conversation-report

# فهرست همه مکالمه‌های موجود روی این سیستم
python src/conversation_report.py --list

# گزارش یک مکالمه مشخص
python src/conversation_report.py cf795541-f47d-4888-9a43-4bc011e7d1ea

# گزارش کامل با آمار ابزارها و خطاها
python src/conversation_report.py cf795541-f47d-4888-9a43-4bc011e7d1ea --tools --errors
```

روی ویندوز از لانچر آماده هم می‌توانید استفاده کنید:

```powershell
.\examples\check-conversation.cmd cf795541-f47d-4888-9a43-4bc011e7d1ea --tools --errors
```

## مکالمه‌ها کجا ذخیره می‌شوند

مسیر پیش‌فرض:

```text
C:\Users\<Username>\.gemini\antigravity\brain\<ConversationID>\
├── .system_generated\
│   ├── logs\
│   │   ├── transcript.jsonl          لاگ سبک مکالمه
│   │   ├── transcript_full.jsonl     همان لاگ با محتوای کامل‌تر
│   │   └── chunks\                   بخش‌بندی همان لاگ‌ها
│   ├── steps\<شماره>\output.txt      خروجی متنی هر مرحله اجرایی
│   ├── tasks\task-<شماره>.log        خروجی تسک‌های پس‌زمینه
│   └── messages\                     پیام‌های داخلی
├── .user_uploaded\                   تصاویر و فایل‌های آپلودی کاربر
├── scratch\                          فایل‌های کاری موقت
└── *.md                              مستندات و گزارش‌های تولیدشده
```

روی سیستم‌های یونیکس همان مسیر زیر شاخه خانه کاربر است:

```text
~/.gemini/antigravity/brain/<ConversationID>/
```

اگر مکالمه‌ها جای دیگری هستند، مسیر را با سوئیچ یا متغیر محیطی بدهید:

```powershell
python src/conversation_report.py <ConversationID> --brain-dir "D:\path\to\brain"
```

```powershell
$env:ANTIGRAVITY_BRAIN_DIR = "D:\path\to\brain"
python src/conversation_report.py <ConversationID>
```

## سوئیچ‌ها

| سوئیچ | کار |
| --- | --- |
| `--list` | فهرست همه مکالمه‌های موجود با اندازه و ترتیب تازه‌ترین |
| `--tools` | آمار ابزارهای فراخوانی‌شده در کل مکالمه |
| `--errors` | خطاهای ثبت‌شده، پانزده مورد آخر |
| `--full` | متن کامل پیام‌های مدل بدون برش |
| `--last N` | تعداد پیام آخر مدل، پیش‌فرض ۶ |
| `--turns N` | تعداد درخواست آخر کاربر، پیش‌فرض ۱۵، مقدار صفر یعنی همه |
| `--width N` | طول نمایش هر متن، پیش‌فرض ۴۰۰ کاراکتر |
| `--full-log` | خواندن `transcript_full.jsonl` به‌جای نسخه سبک |
| `--brain-dir PATH` | مسیر پوشه مکالمه‌ها |

## نمونه خروجی

```text
==============================================================================
ConversationID : cf795541-f47d-4888-9a43-4bc011e7d1ea
فایل مکالمه   : C:\Users\<Username>\.gemini\antigravity\brain\cf795541-...\transcript.jsonl
حجم و رکورد    : 3.7 MB | 3051 رکورد
بازه زمانی     : 2026-09-15T11:59:35Z  →  2026-10-13T12:34:01Z
آخرین رکورد    : step=3062 source=MODEL type=PLANNER_RESPONSE status=DONE
==============================================================================

--- ترکیب رکوردها ---
source: MODEL=2873, SYSTEM=117, USER_EXPLICIT=61
type  : PLANNER_RESPONSE=1486, GENERIC=1387, SYSTEM_MESSAGE=99, USER_INPUT=61, ERROR_MESSAGE=11

--- درخواست‌های کاربر (61 مورد) ---
[1] 2026-09-15T11:59:35Z
    E:\6 وارد این پوشه شو و https://www.nsoftware.com/mcpsdk صفحات رو کامل مطالعه کن و گزارش بده چی هست
...

--- ابزارهای فراخوانی‌شده (مجموع 1399) ---
  523  run_command
  140  view_file
   68  manage_task

--- مستندات خروجی در ریشه مکالمه (4) ---
    8.6 KB  implementation_plan.md
   12.0 KB  walkthrough.md
```

## ساختار لاگ

هر خط از `transcript.jsonl` یک شیء JSON است:

```json
{
  "step_index": 3062,
  "source": "MODEL",
  "type": "PLANNER_RESPONSE",
  "status": "DONE",
  "created_at": "2026-10-13T12:34:01Z",
  "input_tokens": 12345,
  "output_tokens": 678,
  "content": "متن پاسخ مدل",
  "thinking": "استدلال داخلی مدل",
  "tool_calls": [{ "name": "run_command", "args": { "CommandLine": "..." } }],
  "error": null,
  "truncated_fields": ["content"]
}
```

مقدارهای مشاهده‌شده در لاگ‌های واقعی:

| فیلد | مقدارها |
| --- | --- |
| `source` | `MODEL`، `USER_EXPLICIT`، `SYSTEM`، `SYSTEM_SDK` |
| `type` | `PLANNER_RESPONSE`، `GENERIC`، `USER_INPUT`، `SYSTEM_MESSAGE`، `ERROR_MESSAGE`، `CHECKPOINT`، `RUN_COMMAND`، `CODE_ACTION`، `VIEW_FILE`، `CONVERSATION_HISTORY`، `EPHEMERAL_MESSAGE` |
| `status` | `DONE` و حالت‌های در جریان |
| `tool_calls[].name` | `run_command`، `view_file`، `manage_task`، `replace_file_content`، `write_to_file`، `schedule`، `call_mcp_tool`، `search_web`، `read_url_content`، `list_dir`، `find_by_name` |

توضیح کامل فیلدها در [docs/LOG-FORMAT.md](docs/LOG-FORMAT.md).

## پرامپت آماده برای ایجنت‌های دیگر

اگر می‌خواهید به ایجنت دیگری بگویید این بررسی را انجام بدهد، متن آماده در [docs/PROMPTS.md](docs/PROMPTS.md) است. نسخه کوتاهش این است:

```text
روی این سیستم، مکالمه‌های Antigravity به‌صورت فایل JSONL ذخیره می‌شوند:
~/.gemini/antigravity/brain/<ConversationID>/.system_generated/logs/transcript.jsonl

گزارش این ConversationID را بده: <ConversationID>

1. هر خط یک شیء JSON است.
2. "source":"USER_EXPLICIT" و "type":"USER_INPUT" یعنی درخواست کاربر.
3. "source":"MODEL" و "type":"PLANNER_RESPONSE" یعنی پاسخ مدل؛ اگر "tool_calls" پر بود ابزار اجراشده همان‌جاست.
4. محتوای طولانی ممکن است با «<truncated N bytes>» بریده شده باشد؛ متن کامل در transcript_full.jsonl همان پوشه است.
5. خروجی نهایی: موضوع مکالمه، بازه زمانی، تعداد پیام کاربر، آخرین تسک، اقدامات، نتیجه، و هر خطا یا کار نیمه‌تمام.

فایل‌ها خواندنی هستند؛ چیزی را تغییر نده و هرچه در لاگ نبود را «ثبت نشده» گزارش کن.
```

## نکاتی که باعث نتیجه غلط می‌شود

هنگام خواندن لاگ به این موارد دقت کنید، چون رایج‌ترین منبع خطا در تحلیل ایجنت‌های دیگر هستند:

1. `source` فقط `MODEL` و `USER_EXPLICIT` نیست؛ `SYSTEM` و `SYSTEM_SDK` هم وجود دارد. تنها مقدار `USER_EXPLICIT` حرف کاربر است.
2. هر رکورد یا `content` دارد یا `tool_calls`، تقریباً هیچ‌وقت هر دو. اگر فقط `content` را بخوانید، اکثر کارهای اجرایی دیده نمی‌شود و مکالمه بی‌فعالیت به نظر می‌رسد.
3. `transcript.jsonl` محتوای حجیم را بریده و با `<truncated N bytes>` علامت می‌زند. برای متن کامل خطا یا خروجی ابزار باید `transcript_full.jsonl` را خواند. اختلاف دو فایل فقط در نقل‌قول‌های داخل JSON است و برای متن کامل باید نسخه `full` را خواند.
4. شماره داخل نام فایل تسک (`task-3048.log`) با `step_index` یکی نیست. برای یافتن تسک مربوط به یک مرحله، رکورد `GENERIC` همان مرحله را بخوانید که مسیر لاگ را داخل متن دارد.
5. شماره‌های `step_index` پیوسته نیستند و پوشه `steps\<شماره>` فقط برای مرحله‌هایی ساخته می‌شود که خروجی متنی داشته‌اند.
6. `thinking` استدلال داخلی مدل است، نه پیام به کاربر. آن را در گزارش نباید به‌عنوان حرف کاربر یا نتیجه نهایی آورد.

## کارایی

خواندن خط‌به‌خط است و کل فایل در حافظه نگه داشته نمی‌شود. روی مکالمه‌های واقعی این سیستم اندازه‌گیری شد:

| مکالمه | رکورد | حجم | زمان اجرا |
| --- | --- | --- | --- |
| کوچک | ۲۶ | ۴۸ KB | زیر ۰.۱ ثانیه |
| متوسط | ۵۷۴ | ۷۹۸ KB | حدود ۰.۲ ثانیه |
| بزرگ | ۳٬۰۵۱ | ۳.۷ MB | حدود ۱ ثانیه |
| بزرگ‌ترین | ۲۴٬۲۶۴ | ۲۸.۲ MB | ۱.۰۷ ثانیه |

## محدودیت‌ها

- خروجی متن‌محور است و تصاویر آپلودی کاربر را تحلیل نمی‌کند؛ فقط مسیرشان را فهرست می‌کند.
- `transcript_full.jsonl` هم ممکن است فیلدهای بریده داشته باشد. این فایل بریدن را کمتر می‌کند ولی تضمین کامل نیست.
- فقط مکالمه‌هایی که فایل `transcript.jsonl` دارند دیده می‌شوند. مکالمه‌های در حال اجرا ممکن است هنوز فایل کامل نداشته باشند.
- ساختار فایل‌های Antigravity محصول رسمی گوگل نیست و ممکن است در نسخه‌های بعدی تغییر کند. این ابزار بر پایه مشاهدات نسخه فعلی نوشته شده است.

## ساختار مخزن

```text
conversation-report/
├── README.md
├── LICENSE
├── .gitignore
├── check-conversation.cmd            لانچر ویندوزی در ریشه
├── src/
│   └── conversation_report.py        اسکریپت اصلی
├── examples/
│   └── check-conversation.cmd        همان لانچر، برای اجرا از داخل پوشه examples
└── docs/
    ├── LOG-FORMAT.md                 مرجع کامل ساختار لاگ
    ├── PROMPTS.md                    پرامپت آماده برای ایجنت‌های دیگر
    └── TROUBLESHOOTING.md            رفع اشکال
```

## پیش‌نیاز

پایتون ۳.۹ یا بالاتر. هیچ بسته بیرونی لازم نیست.

```powershell
python --version
```

## مجوز و مالکیت

این ابزار فایل‌های محلی خود کاربر را می‌خواند. مسئولیت محرمانه بودن محتوای مکالمه‌ها بر عهده کاربر است؛ گزارش‌های تولیدشده ممکن است مسیرها، نام سرورها، توکن‌ها و اطلاعات حساس داخل مکالمه را در خود داشته باشند. قبل از اشتراک‌گذاری خروجی، آن را بازبینی کنید.
