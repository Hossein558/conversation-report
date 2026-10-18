# ساختار فایل‌های لاگ Antigravity

این سند بر پایه مشاهده واقعی فایل‌های `~/.gemini/antigravity/brain/<ConversationID>/` روی ویندوز نوشته شده است. همه نمونه‌ها از لاگ‌های واقعی گرفته شده‌اند.

## فهرست فایل‌ها

| مسیر | اندازه نمونه | توضیح |
| --- | --- | --- |
| `.system_generated/logs/transcript.jsonl` | ۲ تا ۲۹ مگابایت | لاگ اصلی، یک JSON در هر خط |
| `.system_generated/logs/transcript_full.jsonl` | کمی بزرگ‌تر | همان رکوردها با محتوای کامل‌تر |
| `.system_generated/logs/chunks/transcript/*.jsonl` | متغیر | بخش‌های همان لاگ |
| `.system_generated/logs/chunks/transcript_full/*.jsonl` | متغیر | بخش‌های همان لاگ کامل |
| `.system_generated/steps/<شماره>/output.txt` | چند بایت تا صدها کیلوبایت | خروجی متنی هر مرحله اجرایی |
| `.system_generated/tasks/task-<شماره>.log` | چند بایت تا صدها کیلوبایت | خروجی تسک‌های پس‌زمینه |
| `.system_generated/messages/*.json` | چند کیلوبایت | پیام‌های داخلی با فیلدهای `sender`, `recipient`, `content` |
| `.user_uploaded/media_*.png` | متغیر | تصاویر آپلودشده توسط کاربر |
| `scratch/` | متغیر | فایل‌های کاری موقت |
| `*.md` و `*.md.metadata.json` | چند کیلوبایت | مستندات و گزارش‌های تولیدشده |

## فیلدهای هر رکورد

`transcript.jsonl` و `transcript_full.jsonl` هر دو یک ساختار دارند:

| فیلد | نوع | توضیح |
| --- | --- | --- |
| `step_index` | عدد | شماره مرحله در مکالمه. صعودی است ولی پیوسته نیست. |
| `source` | رشته | منبع پیام: `MODEL`، `USER_EXPLICIT`، `SYSTEM`، `SYSTEM_SDK` |
| `type` | رشته | نوع رکورد. فهرست کامل در پایین. |
| `status` | رشته | وضعیت اجرا، معمولاً `DONE` |
| `created_at` | رشته ISO 8601 | زمان ثبت به وقت UTC |
| `content` | رشته | متن پیام. در رکوردهای ابزارمحور معمولاً وجود ندارد. |
| `thinking` | رشته | استدلال داخلی مدل |
| `tool_calls` | آرایه | ابزارهای فراخوانی‌شده در همان مرحله |
| `input_tokens` | عدد | توکن ورودی همان مرحله |
| `output_tokens` | عدد | توکن خروجی همان مرحله |
| `cache_read_tokens` | عدد | توکن خوانده‌شده از کش |
| `error` | رشته یا شیء | متن خطا در صورت وجود |
| `media` | آرایه | ارجاع به رسانه‌های پیوست |
| `truncated_fields` | آرایه | نام فیلدهایی که محتوایشان بریده شده |

نکته: همه فیلدها در همه رکوردها نیستند. تنها `step_index`, `source`, `type`, `status` و `created_at` تقریباً همیشه حاضرند.

## مقدارهای `source`

| مقدار | معنا | نکته |
| --- | --- | --- |
| `USER_EXPLICIT` | پیام واقعی کاربر | تنها منبعی که حرف کاربر است |
| `MODEL` | خروجی مدل | شامل پاسخ متنی و همچنین نتیجه اجرای ابزارها |
| `SYSTEM` | پیام سیستمی | اعلان‌های داخلی، نه کاربر و نه مدل |
| `SYSTEM_SDK` | رویداد SDK | نادر |

## مقدارهای `type`

| مقدار | معنا |
| --- | --- |
| `USER_INPUT` | ورودی کاربر، همیشه با `source=USER_EXPLICIT` |
| `PLANNER_RESPONSE` | پاسخ برنامه‌ریز مدل؛ یا `content` دارد یا `tool_calls` |
| `GENERIC` | خروجی عمومی، معمولاً نتیجه اجرای ابزار به‌شکل متن |
| `SYSTEM_MESSAGE` | پیام سیستم |
| `ERROR_MESSAGE` | رکورد خطا |
| `CHECKPOINT` | نقطه ذخیره مکالمه |
| `RUN_COMMAND` | رکورد اجرای دستور |
| `CODE_ACTION` | رکورد اقدام کدنویسی |
| `VIEW_FILE` | رکورد خواندن فایل |
| `CONVERSATION_HISTORY` | تاریخچه مکالمه |
| `EPHEMERAL_MESSAGE` | پیام گذرا |

## مقدارهای `tool_calls[].name`

ابزارهایی که در لاگ‌های واقعی مشاهده شدند:

| ابزار | کار |
| --- | --- |
| `run_command` | اجرای دستور در ترمینال |
| `view_file` | خواندن فایل |
| `manage_task` | مدیریت تسک‌های پس‌زمینه |
| `replace_file_content` | ویرایش محتوای فایل |
| `write_to_file` | نوشتن فایل جدید |
| `schedule` | زمان‌بندی کار |
| `call_mcp_tool` | فراخوانی ابزار MCP |
| `search_web` | جست‌وجوی وب |
| `read_url_content` | خواندن محتوای یک URL |
| `list_dir` | فهرست پوشه |
| `find_by_name` | جست‌وجوی فایل |

ساختار هر فراخوانی:

```json
{
  "name": "run_command",
  "args": {
    "CommandLine": "git status",
    "toolAction": "running command",
    "toolSummary": "check repo state"
  }
}
```

## نمونه رکوردهای واقعی

درخواست کاربر:

```json
{"step_index":1,"source":"USER_EXPLICIT","type":"USER_INPUT","status":"DONE","created_at":"2026-09-15T11:59:35Z","content":"<USER_REQUEST> E:\\6 وارد این پوشه شو … </USER_REQUEST> <ADDITIONAL_METADATA> The current local time is: … </ADDITIONAL_METADATA>"}
```

پاسخ مدل با فراخوانی ابزار:

```json
{"step_index":2,"source":"MODEL","type":"PLANNER_RESPONSE","status":"DONE","created_at":"2026-10-10T11:15:01Z","input_tokens":28528,"output_tokens":684,"thinking":"Initial assessment: …","tool_calls":[{"name":"read_url_content","args":{"Url":"https://github.com/morluto/rea"}}]}
```

پاسخ متنی مدل:

```json
{"step_index":3062,"source":"MODEL","type":"PLANNER_RESPONSE","status":"DONE","created_at":"2026-10-13T12:34:01Z","content":"اطلاعات پلتفرم **CData API Server 2026 Enterprise** …"}
```

## پاک‌سازی متن کاربر

محتوای پیام کاربر داخل تگ‌ها بسته‌بندی شده است. برای گزارش، این‌ها را حذف کنید:

```text
<USER_REQUEST> … </USER_REQUEST>
<ADDITIONAL_METADATA> … </ADDITIONAL_METADATA>
<SYSTEM_MESSAGE> … </SYSTEM_MESSAGE>
```

بخش `ADDITIONAL_METADATA` شامل زمان محلی و فهرست تصاویر آپلودی است، نه درخواست کاربر. اگر حذف نشود، گزارش آلوده می‌شود.

## تفاوت `transcript.jsonl` و `transcript_full.jsonl`

تعداد خط‌ها تقریباً یکی است، ولی محتوای فیلدهای حجیم متفاوت است. در یک نمونه واقعی:

```text
record 5  →  transcript.jsonl = 4,121 بایت   transcript_full.jsonl = 48,514 بایت
```

نسخه سبک محتوای بزرگ را می‌برد و جایش می‌گذارد:

```text
<truncated 44419 bytes>
```

همچنین در نسخه سبک مقادیر داخل `tool_calls` با نقل‌قول‌های اضافه ذخیره می‌شوند:

```json
"args": { "Url": "\"https://github.com/morluto/rea\"" }
```

و در نسخه کامل تمیز هستند:

```json
"args": { "Url": "https://github.com/morluto/rea" }
```

جمع‌بندی: برای خواندن متنی، نسخه سبک کافی است. برای متن کامل خروجی ابزار، خطاها، و آرگومان‌های تمیز، نسخه `full` را بخوانید.

## رابطه `step_index` با پوشه‌های `steps`

در یک مکالمه واقعی، `step_index` تا `1784` رفت ولی فقط `660` پوشه زیر `steps\` وجود داشت. علت این است که پوشه فقط برای مرحله‌هایی ساخته می‌شود که خروجی متنی داشته‌اند.

راه پیدا کردن فایل یک مرحله: رکورد `GENERIC` همان `step_index` را بخوانید. متن آن شامل مسیر کامل فایل خروجی است:

```text
Created At: 2026-10-13T16:04:00+03:30
File Path: `file:///C:/Users/<Username>/.gemini/antigravity/brain/<ID>/.system_generated/steps/3059/output.txt`
Total Lines: 7
```

## رابطه تسک‌های پس‌زمینه با مراحل

نام فایل تسک (`task-3048.log`) با `step_index` یکی نیست. برای یافتن تسک مربوط به یک مرحله، رکورد `GENERIC` را بخوانید که مسیر لاگ را داخل متن دارد:

```text
Tool is running as a background task with task id: <ID>/task-30354
Task Description: ssh -p 22 …
```

سپس رکورد بعدی وضعیت را اعلام می‌کند:

```text
Task: <ID>/task-30354 Status: DONE
Log: …\.system_generated\tasks\task-30354.log
Log output: ssh: connect to host 172.25.0.43 port 22: Connection timed out
```

## نکته‌های آماری

- طول خط‌های لاگ بسیار متغیر است: از چند صد بایت تا صدها کیلوبایت در یک خط.
- فایل‌های بزرگ باید خط‌به‌خط خوانده شوند؛ خواندن کل فایل در حافظه روی مکالمه‌های چند ده مگابایتی پرهزینه است.
- خطوط خراب یا ناقص ممکن است وجود داشته باشد. هر خطی که JSON معتبر نبود را باید نادیده گرفت، نه اینکه کل فایل را نامعتبر دانست.
