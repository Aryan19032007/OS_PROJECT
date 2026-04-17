from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from flask import Flask, render_template

APP_ROOT = Path(__file__).resolve().parent
SCRIPT_PATH = APP_ROOT / "page_replacement (1).py"

app = Flask(__name__)


def launch_page_replacement_gui() -> tuple[bool, str]:
    if not SCRIPT_PATH.exists():
        return (False, f"Missing script at: {SCRIPT_PATH}")

    try:
        subprocess.Popen(
            [sys.executable, str(SCRIPT_PATH)],
            cwd=str(APP_ROOT),
            # Avoid detached launch so the Tk window shows immediately on screen.
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception as e:  # pragma: no cover
        return (False, f"Failed to launch GUI: {e}")

    return (True, "Tkinter GUI launched successfully.")


@app.get("/")
def index():
    return render_template(
        "index.html",
        default_ref="7 0 1 2 0 3 0 4 2 3 0 3 2",
        default_frames=3,
    )


@app.post("/run")
def run():
    ok, message = launch_page_replacement_gui()
    return render_template(
        "output.html",
        launch_ok=ok,
        launch_message=message,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
