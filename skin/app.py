#!/usr/bin/env python3
"""Local front door for the Book Machine. Bind localhost only."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
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


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug


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
        if path.suffix == ".md" and path.name.lower() != "readme.md":
            count += 1
    return count


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
