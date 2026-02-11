import json
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

DATA_FILE = Path.home() / ".local/share/niri-tracker/usage.json"


def run_niri_command() -> Optional[Dict[str, Any]]:
    try:
        result = subprocess.run(["niri", "msg", "--json", "focused-window"], capture_output=True, text=True, check=True)
        return parse_niri_output(result.stdout)
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def parse_niri_output(output: str) -> Optional[Dict[str, Any]]:
    if not (parsed_json := json.loads(output)):
        return

    data = {}
    data["app_id"] = parsed_json.get("app_id")
    data["title"] = parsed_json.get("title")

    return data if "app_id" in data else None


def extract_app_name(app_id: str) -> str:
    return app_id.split(".")[-1] if "." in app_id else app_id


def load_data() -> Dict[str, Any]:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_data(data: Dict[str, Any]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1, ensure_ascii=False)


def update_usage(data: Dict[str, Any], app_name: str, title: str, duration: int) -> None:
    today = datetime.now().strftime("%Y-%m-%d")

    if today not in data:
        data[today] = {}

    day_data = data[today]
    if app_name not in day_data:
        day_data[app_name] = {"total": 0, "titles": {}}

    day_data[app_name]["total"] += duration
    day_data[app_name]["titles"][title] = day_data[app_name]["titles"].get(title, 0) + duration


def main():
    data = load_data()
    last_window = None
    last_time = time.time()

    while True:
        current_window = run_niri_command()
        current_time = time.time()

        if last_window and current_window:
            duration = int(current_time - last_time)
            if duration > 0:
                app_name = extract_app_name(last_window["app_id"])
                update_usage(data, app_name, last_window["title"], duration)
                save_data(data)

        last_window = current_window
        last_time = current_time
        time.sleep(20)


if __name__ == "__main__":
    main()
