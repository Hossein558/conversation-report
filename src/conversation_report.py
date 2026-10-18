#!/usr/bin/env python3
"""گزارش خوانا از یک مکالمه Antigravity بر اساس ConversationID.

استفاده:
    python conversation_report.py cf795541-f47d-4888-9a43-4bc011e7d1ea
    python conversation_report.py cf795541-f47d-4888-9a43-4bc011e7d1ea --tools --errors
    python conversation_report.py cf795541-f47d-4888-9a43-4bc011e7d1ea --full
    python conversation_report.py --list

فقط از کتابخانه استاندارد پایتون استفاده می‌کند؛ هیچ چیزی اجرا یا به شبکه ارسال نمی‌شود.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from pathlib import Path

DEFAULT_BRAIN_DIR = Path(os.path.expanduser("~")) / ".gemini" / "antigravity" / "brain"
BRAIN_DIR = DEFAULT_BRAIN_DIR


def configure_brain_dir(override: str | None) -> None:
    """مسیر پوشه مکالمه‌ها را تعیین می‌کند: سوئیچ خط فرمان، سپس متغیر محیطی، سپس پیش‌فرض."""
    global BRAIN_DIR
    candidate = override or os.environ.get("ANTIGRAVITY_BRAIN_DIR")
    if candidate:
        BRAIN_DIR = Path(candidate).expanduser()
    else:
        BRAIN_DIR = DEFAULT_BRAIN_DIR


def configure_stdout() -> None:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


def transcript_path(conversation_id: str, full: bool) -> Path:
    name = "transcript_full.jsonl" if full else "transcript.jsonl"
    return BRAIN_DIR / conversation_id / ".system_generated" / "logs" / name


def conversation_root(conversation_id: str) -> Path:
    return BRAIN_DIR / conversation_id


def read_records(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8", errors="replace") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(record, dict):
                record["_line"] = line_number
                records.append(record)
    return records


def clean_user_text(text: str) -> str:
    text = text.replace("<USER_REQUEST>", "").replace("</USER_REQUEST>", "")
    for marker in ("<ADDITIONAL_METADATA>", "<SYSTEM_MESSAGE>"):
        if marker in text:
            text = text.split(marker, 1)[0]
    return " ".join(text.split())


def clip(text: str, width: int) -> str:
    text = " ".join(str(text).split())
    if width > 0 and len(text) > width:
        return text[:width].rstrip() + " …"
    return text


def is_user_turn(record: dict) -> bool:
    return record.get("source") == "USER_EXPLICIT" and record.get("type") == "USER_INPUT"


def model_text(record: dict) -> str:
    content = record.get("content")
    return content if isinstance(content, str) else ""


def tool_names(record: dict) -> list[str]:
    names: list[str] = []
    calls = record.get("tool_calls")
    if isinstance(calls, list):
        for call in calls:
            if isinstance(call, dict):
                name = call.get("name") or call.get("tool_name")
                if name:
                    names.append(str(name))
    return names


def human_size(byte_count: int) -> str:
    size = float(byte_count)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024 or unit == "GB":
            return f"{size:.1f} {unit}" if unit != "B" else f"{int(size)} B"
        size /= 1024
    return f"{size:.1f} GB"


def print_header(conversation_id: str, transcript: Path, records: list[dict]) -> None:
    print("=" * 78)
    print(f"ConversationID : {conversation_id}")
    print(f"فایل مکالمه   : {transcript}")
    print(f"حجم و رکورد    : {human_size(transcript.stat().st_size)} | {len(records)} رکورد")

    stamps = [record.get("created_at", "") for record in records if record.get("created_at")]
    if stamps:
        print(f"بازه زمانی     : {stamps[0]}  →  {stamps[-1]}")

    last = records[-1] if records else {}
    print(
        "آخرین رکورد    : "
        f"step={last.get('step_index')} "
        f"source={last.get('source')} "
        f"type={last.get('type')} "
        f"status={last.get('status')}"
    )
    print("=" * 78)


def show_counts(records: list[dict]) -> None:
    sources = Counter(str(record.get("source")) for record in records)
    types = Counter(str(record.get("type")) for record in records)
    print("\n--- ترکیب رکوردها ---")
    print("source: " + ", ".join(f"{name}={count}" for name, count in sources.most_common()))
    print("type  : " + ", ".join(f"{name}={count}" for name, count in types.most_common()))


def show_user_requests(records: list[dict], width: int, tail: int) -> None:
    turns = [record for record in records if is_user_turn(record)]
    print(f"\n--- درخواست‌های کاربر ({len(turns)} مورد) ---")
    selected = turns[-tail:] if tail > 0 else turns
    start_index = len(turns) - len(selected) + 1
    for offset, record in enumerate(selected):
        text = clean_user_text(str(record.get("content", "")))
        print(f"[{start_index + offset}] {record.get('created_at')}")
        print(f"    {clip(text, width)}")


def show_tools(records: list[dict]) -> None:
    counter = Counter()
    for record in records:
        counter.update(tool_names(record))
    total = sum(counter.values())
    print(f"\n--- ابزارهای فراخوانی‌شده (مجموع {total}) ---")
    if not counter:
        print("هیچ فراخوانی ابزاری ثبت نشده است.")
        return
    for name, count in counter.most_common():
        print(f"{count:5d}  {name}")


def show_errors(records: list[dict], width: int) -> None:
    errors = [record for record in records if record.get("error")]
    print(f"\n--- خطاها ({len(errors)} مورد) ---")
    if not errors:
        print("خطایی ثبت نشده است.")
        return
    for record in errors[-15:]:
        detail = json.dumps(record.get("error"), ensure_ascii=False)
        print(f"step={record.get('step_index')} at={record.get('created_at')}")
        print(f"    {clip(detail, width)}")


def show_model_messages(records: list[dict], tail: int, width: int, full: bool) -> None:
    messages = [
        record
        for record in records
        if record.get("source") == "MODEL" and record.get("type") == "PLANNER_RESPONSE" and model_text(record)
    ]
    print(f"\n--- پیام‌های متنی مدل ({len(messages)} مورد) ---")
    if not messages:
        print("پیام متنی ثبت نشده است.")
        return
    for record in messages[-tail:]:
        print(f"\n### step={record.get('step_index')} at={record.get('created_at')}")
        text = model_text(record)
        print(text if full else clip(text, width * 3))


def show_tasks(conversation_id: str, tail: int, width: int) -> None:
    tasks_dir = conversation_root(conversation_id) / ".system_generated" / "tasks"
    if not tasks_dir.is_dir():
        return
    task_files = sorted(tasks_dir.glob("*.log"), key=lambda item: item.stat().st_mtime, reverse=True)[:tail]
    if not task_files:
        return
    print(f"\n--- آخرین تسک‌های پس‌زمینه ({len(task_files)}) ---")
    for path in task_files:
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError as error:
            print(f"{path.name}: قابل خواندن نیست ({error})")
            continue
        print(f"{path.name}: {clip(body, width)}")


def show_artifacts(conversation_id: str, tail: int) -> None:
    root = conversation_root(conversation_id)
    if not root.is_dir():
        return
    documents = [
        path
        for path in root.glob("*")
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json", ".html", ".docx", ".xlsx", ".pdf"}
    ]
    if documents:
        print(f"\n--- مستندات خروجی در ریشه مکالمه ({len(documents)}) ---")
        for path in sorted(documents, key=lambda item: item.name):
            print(f"{human_size(path.stat().st_size):>10}  {path.name}")

    steps_dir = root / ".system_generated" / "steps"
    if not steps_dir.is_dir():
        return
    step_dirs = sorted(
        (item for item in steps_dir.iterdir() if item.is_dir()),
        key=lambda item: item.stat().st_mtime,
        reverse=True,
    )[:tail]
    print(f"\n--- آخرین stepهای اجرایی ({len(step_dirs)}) ---")
    for step_dir in step_dirs:
        output = step_dir / "output.txt"
        if not output.is_file():
            continue
        try:
            body = output.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        print(f"step {step_dir.name}: {clip(body, 240)}")


def list_conversations() -> None:
    if not BRAIN_DIR.is_dir():
        print(f"مسیر یافت نشد: {BRAIN_DIR}")
        return
    entries = []
    for folder in BRAIN_DIR.iterdir():
        transcript = folder / ".system_generated" / "logs" / "transcript.jsonl"
        if transcript.is_file():
            entries.append((folder.stat().st_mtime, folder.name, transcript.stat().st_size))
    entries.sort(reverse=True)
    print(f"{len(entries)} مکالمه در {BRAIN_DIR}\n")
    for _, name, size in entries:
        print(f"{human_size(size):>10}  {name}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="گزارش مکالمه Antigravity بر اساس ConversationID")
    parser.add_argument("conversation_id", nargs="?", help="شناسه مکالمه (ConversationID)")
    parser.add_argument("--list", action="store_true", help="فهرست همه مکالمه‌های موجود")
    parser.add_argument("--full", action="store_true", help="متن کامل پیام‌های مدل")
    parser.add_argument("--tools", action="store_true", help="نمایش آمار ابزارها")
    parser.add_argument("--errors", action="store_true", help="نمایش خطاها")
    parser.add_argument("--last", type=int, default=6, help="تعداد پیام‌های آخر مدل (پیش‌فرض ۶)")
    parser.add_argument("--turns", type=int, default=15, help="تعداد درخواست‌های آخر کاربر (۰ = همه)")
    parser.add_argument("--width", type=int, default=400, help="طول نمایش هر متن")
    parser.add_argument("--full-log", action="store_true", help="خواندن transcript_full.jsonl به‌جای transcript.jsonl")
    parser.add_argument(
        "--brain-dir",
        help="مسیر پوشه مکالمه‌ها (پیش‌فرض: ~/.gemini/antigravity/brain یا مقدار ANTIGRAVITY_BRAIN_DIR)",
    )
    return parser


def main() -> int:
    configure_stdout()
    args = build_parser().parse_args()
    configure_brain_dir(args.brain_dir)

    if args.list or not args.conversation_id:
        list_conversations()
        return 0

    transcript = transcript_path(args.conversation_id, args.full_log)
    if not transcript.is_file():
        print(f"فایل مکالمه یافت نشد: {transcript}")
        folder = conversation_root(args.conversation_id)
        if not folder.is_dir():
            print(f"پوشه مکالمه هم وجود ندارد: {folder}")
            print("برای دیدن شناسه‌های موجود: python conversation_report.py --list")
        return 1

    records = read_records(transcript)
    if not records:
        print(f"رکوردی در فایل نبود: {transcript}")
        return 1

    print_header(args.conversation_id, transcript, records)
    show_counts(records)
    show_user_requests(records, args.width, args.turns)
    if args.tools:
        show_tools(records)
    if args.errors:
        show_errors(records, args.width)
    show_model_messages(records, args.last, args.width, args.full)
    show_artifacts(args.conversation_id, args.last)
    show_tasks(args.conversation_id, args.last, args.width)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
