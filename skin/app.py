#!/usr/bin/env python3
"""Local front door for the Book Machine. Bind localhost only."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import unicodedata
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
NOVELS = ROOT / "novels"
SKIN = Path(__file__).resolve().parent
SCRIPT = ROOT / "scripts" / "new-novel.sh"
HOST = "127.0.0.1"
PORT = 8765
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CHAPTER_FILE_RE = re.compile(r"^ch\d+", re.IGNORECASE)


def slugify(title: str) -> str:
    plain = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", plain).strip("-")


def novel_dirs() -> list[Path]:
    if not NOVELS.is_dir():
        return []
    found: list[Path] = []
    for path in sorted(NOVELS.iterdir()):
        if path.is_dir() and (path / "TODAY.md").is_file():
            found.append(path)
    return found


def read_text(path: Path, limit: int = 800) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return ""
    text = text.strip()
    if len(text) > limit:
        return text[: limit].rstrip() + "…"
    return text


def chapter_count(novel: Path) -> int:
    chapters = novel / "chapters"
    if not chapters.is_dir():
        return 0
    count = 0
    for path in chapters.iterdir():
        if path.suffix.lower() == ".md" and CHAPTER_FILE_RE.match(path.name):
            count += 1
    return count


BOARD_FIELDS = ("does", "eyes", "where", "tension", "status")
BOARD_LABELS = {
    "does": "Does",
    "eyes": "Eyes",
    "where": "Where",
    "tension": "Tension",
    "status": "Status",
}
BOARD_STATUSES = ("", "Drafting", "Revising", "Settled", "Needs a look")
CHAPTERS_HEADING_RE = re.compile(r"^## Chapters[ \t]*$", re.MULTILINE)
NEXT_HEADING_RE = re.compile(r"^## ", re.MULTILINE)
BOARD_NOTE = (
    "The board on the desk reads and writes this section. "
    "One block per chapter file. Keep the labels as they are."
)


def chapter_files(novel: Path) -> list[Path]:
    chapters = novel / "chapters"
    if not chapters.is_dir():
        return []
    files = [
        path
        for path in chapters.iterdir()
        if path.suffix.lower() == ".md" and CHAPTER_FILE_RE.match(path.name)
    ]
    return sorted(files, key=lambda p: p.name.lower())


def chapter_facts(path: Path) -> dict:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        text = ""
    lines = [line.strip() for line in text.splitlines()]
    number_match = re.match(r"^ch(\d+)", path.name, re.IGNORECASE)
    number = int(number_match.group(1)) if number_match else 0
    title = path.stem.split("-", 1)[-1].replace("-", " ").title()
    opening = ""
    for index, line in enumerate(lines):
        if not line:
            continue
        heading = re.match(r"^#*\s*Chapter\s+\w+\s*[:.\-—]\s*(.+)$", line, re.IGNORECASE)
        if index < 3 and heading:
            title = heading.group(1).strip()
            continue
        if line.startswith("#"):
            continue
        opening = line
        break
    if len(opening) > 220:
        opening = opening[:220].rsplit(" ", 1)[0] + "…"
    return {
        "file": path.name,
        "number": number,
        "title": title,
        "words": len(text.split()),
        "opening": opening,
    }


def story_map_path(novel: Path) -> Path:
    return novel / "back-office" / "STORY-MAP.md"


def chapters_section(text: str) -> tuple[int, int] | None:
    found = CHAPTERS_HEADING_RE.search(text)
    if not found:
        return None
    start = found.end()
    after = NEXT_HEADING_RE.search(text, start)
    end = after.start() if after else len(text)
    return start, end


def parse_board(text: str) -> dict[str, dict]:
    span = chapters_section(text)
    if not span:
        return {}
    section = text[span[0] : span[1]]
    entries: dict[str, dict] = {}
    for block in re.split(r"^### ", section, flags=re.MULTILINE)[1:]:
        values: dict[str, str] = {}
        for line in block.splitlines()[1:]:
            match = re.match(r"^-\s*(\w+):\s*(.*)$", line.strip())
            if match:
                values[match.group(1).lower()] = match.group(2).strip()
        name = values.get("file", "")
        if name:
            entries[name] = {key: values.get(key, "") for key in BOARD_FIELDS}
    return entries


def one_line(value: object) -> str:
    return " ".join(str(value or "").split())


def render_board(cards: list[dict]) -> str:
    parts = ["", "", BOARD_NOTE, ""]
    for card in cards:
        parts.append(f"### {card['number']}. {card['title']}")
        parts.append(f"- File: {card['file']}")
        for key in BOARD_FIELDS:
            parts.append(f"- {BOARD_LABELS[key]}: {one_line(card.get(key))}")
        parts.append("")
    return "\n".join(parts) + "\n"


def board_payload(novel: Path) -> dict:
    path = story_map_path(novel)
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    saved = parse_board(text)
    cards = []
    for chapter in chapter_files(novel):
        facts = chapter_facts(chapter)
        notes = saved.get(facts["file"], {})
        facts.update({key: notes.get(key, "") for key in BOARD_FIELDS})
        cards.append(facts)
    return {
        "slug": novel.name,
        "title": novel_title(novel),
        "mtime": path.stat().st_mtime if path.is_file() else 0,
        "statuses": list(BOARD_STATUSES),
        "cards": cards,
    }


def clean_card(card: dict) -> dict:
    cleaned = {key: one_line(card.get(key)) for key in BOARD_FIELDS}
    tension = cleaned["tension"]
    if tension and not (tension.isdigit() and 1 <= int(tension) <= 10):
        raise ValueError("tension must be 1 to 10")
    if cleaned["status"] not in BOARD_STATUSES:
        raise ValueError("unknown status")
    return cleaned


def save_board(novel: Path, data: dict) -> dict:
    path = story_map_path(novel)
    current = path.stat().st_mtime if path.is_file() else 0
    if abs(float(data.get("mtime") or 0) - current) > 0.001:
        raise FileExistsError(
            "The story map changed since you opened the board. Reload to see the new version."
        )
    sent = {str(card.get("file", "")): card for card in data.get("cards", []) if isinstance(card, dict)}
    cards = []
    for chapter in chapter_files(novel):
        facts = chapter_facts(chapter)
        if facts["file"] in sent:
            facts.update(clean_card(sent[facts["file"]]))
        else:
            facts.update({key: "" for key in BOARD_FIELDS})
        cards.append(facts)
    text = path.read_text(encoding="utf-8") if path.is_file() else "# Story map\n"
    span = chapters_section(text)
    body = render_board(cards)
    if span:
        tail = text[span[1] :]
        text = text[: span[0]] + body + ("\n" + tail if tail else "")
    else:
        text = text.rstrip() + "\n\n## Chapters" + body
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".md.tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)
    return board_payload(novel)


def open_chapter(novel: Path, name: str) -> None:
    if name not in {path.name for path in chapter_files(novel)}:
        raise FileNotFoundError("no such chapter")
    target = novel / "chapters" / name
    for cmd in (["cursor", "-r", str(target)], ["open", "-a", "Cursor", str(target)]):
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
        except OSError:
            continue
    subprocess.Popen(["open", str(target)])


def novel_title(novel: Path) -> str:
    today = read_text(novel / "TODAY.md", 4000)
    match = re.search(r"\*\*Novel:\*\*\s*(.+)", today)
    if match:
        return match.group(1).strip()
    readme = read_text(novel / "README.md", 200)
    match = re.search(r"^#\s+(.+)$", readme, re.MULTILINE)
    if match and match.group(1).strip().lower() != "novels":
        return match.group(1).strip()
    return novel.name.replace("-", " ").title()


def sitting_kind(chapters: int) -> str:
    if chapters == 0:
        return "new"
    return "in-motion"


def say_line(title: str, kind: str) -> str:
    if kind == "new":
        return f"Interview me. Title: {title}"
    if kind == "intake":
        return "This draft needs work. Intake it."
    return f"Continuing {title}."


def novel_payload(novel: Path) -> dict:
    chapters = chapter_count(novel)
    kind = sitting_kind(chapters)
    today_path = novel / "TODAY.md"
    mtime = today_path.stat().st_mtime if today_path.is_file() else 0
    title = novel_title(novel)
    return {
        "slug": novel.name,
        "title": title,
        "today": read_text(today_path, 700),
        "chapters": chapters,
        "kind": kind,
        "say": say_line(title, kind),
        "mtime": mtime,
    }


def desk() -> dict:
    novels = [novel_payload(path) for path in novel_dirs()]
    novels.sort(key=lambda item: item["mtime"], reverse=True)
    nxt = novels[0] if novels else None
    return {"continue": nxt, "novels": novels}


def open_workspace(slug: str) -> None:
    if not SLUG_RE.match(slug):
        raise ValueError("bad slug")
    workspace = NOVELS / slug / "OPEN-ME.code-workspace"
    if not workspace.is_file():
        raise FileNotFoundError("no desk for that book")
    opened = False
    for cmd in (
        ["cursor", str(workspace)],
        ["open", "-a", "Cursor", str(workspace)],
    ):
        try:
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            opened = True
            break
        except OSError:
            continue
    if not opened:
        subprocess.Popen(["open", str(workspace)])


def create_novel(title: str) -> dict:
    title = " ".join(title.split())
    if not title:
        raise ValueError("need a title")
    slug = slugify(title)
    if not slug:
        raise ValueError("could not name the folder")
    dest = NOVELS / slug
    if dest.exists():
        raise FileExistsError("that book already exists")
    result = subprocess.run(
        [str(SCRIPT), title],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        err = (result.stderr or result.stdout or "could not create").strip()
        raise RuntimeError(err)
    return novel_payload(dest)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, format: str, *args) -> None:
        sys.stderr.write("%s - %s\n" % (self.address_string(), format % args))

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, code: int, data: dict | list) -> None:
        raw = json.dumps(data).encode("utf-8")
        self._send(code, raw, "application/json; charset=utf-8")

    def _read_json(self) -> dict:
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length) if length else b"{}"
        if not raw:
            return {}
        data = json.loads(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("object required")
        return data

    def do_GET(self) -> None:
        path = unquote(self.path.split("?", 1)[0])
        if path in ("/", "/index.html"):
            html = (SKIN / "index.html").read_bytes()
            self._send(200, html, "text/html; charset=utf-8")
            return
        if path == "/how":
            html = (ROOT / "HOW-THIS-WORKS.html").read_bytes()
            self._send(200, html, "text/html; charset=utf-8")
            return
        if path == "/api/desk":
            self._json(200, desk())
            return
        match = re.fullmatch(r"/board/([a-z0-9-]+)", path)
        if match:
            html = (SKIN / "board.html").read_bytes()
            self._send(200, html, "text/html; charset=utf-8")
            return
        match = re.fullmatch(r"/api/novels/([a-z0-9-]+)/board", path)
        if match:
            novel = NOVELS / match.group(1)
            if not (novel / "TODAY.md").is_file():
                self._json(404, {"error": "no such book"})
                return
            self._json(200, board_payload(novel))
            return
        match = re.fullmatch(r"/api/novels/([a-z0-9-]+)", path)
        if match:
            slug = match.group(1)
            novel = NOVELS / slug
            if not (novel / "TODAY.md").is_file():
                self._json(404, {"error": "no such book"})
                return
            self._json(200, novel_payload(novel))
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = unquote(self.path.split("?", 1)[0])
        try:
            data = self._read_json()
        except (json.JSONDecodeError, ValueError):
            self._json(400, {"error": "bad request"})
            return
        if path == "/api/novels":
            try:
                payload = create_novel(str(data.get("title", "")))
                sit = bool(data.get("sit", True))
                if sit:
                    open_workspace(payload["slug"])
                self._json(201, payload)
            except FileExistsError as exc:
                self._json(409, {"error": str(exc)})
            except (ValueError, RuntimeError) as exc:
                self._json(400, {"error": str(exc)})
            return
        match = re.fullmatch(r"/api/novels/([a-z0-9-]+)/sit", path)
        if match:
            try:
                open_workspace(match.group(1))
                self._json(200, {"ok": True})
            except (ValueError, FileNotFoundError) as exc:
                self._json(404, {"error": str(exc)})
            return
        match = re.fullmatch(r"/api/novels/([a-z0-9-]+)/(board|open-chapter)", path)
        if match:
            novel = NOVELS / match.group(1)
            if not (novel / "TODAY.md").is_file():
                self._json(404, {"error": "no such book"})
                return
            try:
                if match.group(2) == "board":
                    self._json(200, save_board(novel, data))
                else:
                    open_chapter(novel, str(data.get("file", "")))
                    self._json(200, {"ok": True})
            except FileExistsError as exc:
                self._json(409, {"error": str(exc)})
            except FileNotFoundError as exc:
                self._json(404, {"error": str(exc)})
            except ValueError as exc:
                self._json(400, {"error": str(exc)})
            return
        self._json(404, {"error": "not found"})


def main() -> None:
    os.chdir(ROOT)
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/"
    print(f"The desk is open at {url}", flush=True)
    print("Leave this window running. Close it when you are done.", flush=True)
    try:
        webbrowser.open(url)
    except Exception:
        pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nDesk closed.")


if __name__ == "__main__":
    main()
