import json
import sys
import unicodedata
from argparse import ArgumentParser
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

DATA_FILE = Path.home() / ".local/share/niri-tracker/usage.json"


def wcwidth(ch: str) -> int:
    if unicodedata.combining(ch) or unicodedata.category(ch) in ("Mn", "Me", "Cf"):
        return 0
    return 2 if unicodedata.east_asian_width(ch) in ("W", "F") else 1


def wcswidth(s: str) -> int:
    return sum(wcwidth(ch) for ch in s)


def fit_display_width(text: str, width: int, ellipsis: bool = True) -> str:
    cur = wcswidth(text)
    if cur <= width:
        return text + " " * (width - cur)
    cut = max(0, width - (3 if ellipsis and width >= 3 else 0))
    out, used = [], 0
    for ch in text:
        w = wcwidth(ch)
        if used + w > cut:
            break
        out.append(ch)
        used += w
    res = "".join(out)
    if ellipsis and width >= 3:
        res += "..."
    return res


def load_data() -> Dict[str, Any]:
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def format_duration(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


def get_date_range(start_date: str, end_date: str = None) -> List[str]:
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d") if end_date else start

    dates = []
    current = start
    while current <= end:
        dates.append(current.strftime("%Y-%m-%d"))
        current += timedelta(days=1)
    return dates


def aggregate_data(data: Dict[str, Any], dates: List[str]) -> Tuple[Dict[str, int], Dict[str, int]]:
    apps = {}
    titles = {}

    for date in dates:
        if date in data:
            day_data = data[date]
            for app_name, app_data in day_data.items():
                apps[app_name] = apps.get(app_name, 0) + app_data.get("total", 0)

                for title, duration in app_data.get("titles", {}).items():
                    titles[title] = titles.get(title, 0) + duration

    return apps, titles


def aggregate_tree_data(data: Dict[str, Any], dates: List[str]) -> Dict[str, Dict[str, int]]:
    tree = {}

    for date in dates:
        if date in data:
            day_data = data[date]
            for app_name, app_data in day_data.items():
                if app_name not in tree:
                    tree[app_name] = {"_total": 0, "_titles": {}}

                tree[app_name]["_total"] += app_data.get("total", 0)

                for title, duration in app_data.get("titles", {}).items():
                    if title not in tree[app_name]["_titles"]:
                        tree[app_name]["_titles"][title] = 0
                    tree[app_name]["_titles"][title] += duration

    return tree


def print_tree(tree_data: Dict[str, Dict[str, int]], limit_children: int = None) -> None:
    if not tree_data:
        print("No data found")
        return

    sorted_apps = sorted(tree_data.items(), key=lambda x: x[1]["_total"], reverse=True)

    grand_total = sum(app_data["_total"] for _, app_data in sorted_apps)

    for app_name, app_data in sorted_apps:
        app_total = app_data["_total"]
        app_percentage = (app_total / grand_total * 100) if grand_total > 0 else 0

        left_app = fit_display_width(app_name, 70)
        print(f"\n{left_app} {format_duration(app_total):>12} ({app_percentage:5.1f}%)")

        titles = app_data["_titles"]
        if titles:
            sorted_titles = sorted(titles.items(), key=lambda x: x[1], reverse=True)
            if limit_children:
                sorted_titles = sorted_titles[:limit_children]

            for i, (title, duration) in enumerate(sorted_titles):
                title_percentage = (duration / app_total * 100) if app_total > 0 else 0
                is_last = i == len(sorted_titles) - 1

                prefix = "  └─" if is_last else "  ├─"
                left_title = fit_display_width(title, 65)
                print(f"{prefix} {left_title} {format_duration(duration):>12} ({title_percentage:5.1f}%)")

            remaining = len(titles) - len(sorted_titles)
            if remaining > 0:
                print(f"  └─ ... and {remaining} more title(s)")

    print(f"\n{'Total Time':<79} {format_duration(grand_total):>12}")


def print_usage(usage_data: Dict[str, int], title: str, limit: int = None) -> None:
    if not usage_data:
        print(f"No {title.lower()} data found")
        return

    sorted_items = sorted(usage_data.items(), key=lambda x: x[1], reverse=True)
    if limit:
        sorted_items = sorted_items[:limit]

    print(f"\n{title}:")
    print("-" * 50)
    total_time = sum(usage_data.values())

    for name, duration in sorted_items:
        percentage = (duration / total_time * 100) if total_time > 0 else 0
        print(f"{name:<30} {format_duration(duration):>12} ({percentage:5.1f}%)")

    print("-" * 50)
    print(f"{'Total':<30} {format_duration(total_time):>12} (100.0%)")


def main():
    parser = ArgumentParser(description="View window focus usage statistics")
    parser.add_argument("--date", help="Specific date (YYYY-MM-DD)")
    parser.add_argument("--from", dest="start_date", help="Start date (YYYY-MM-DD)")
    parser.add_argument("--to", dest="end_date", help="End date (YYYY-MM-DD)")
    parser.add_argument("--yesterday", action="store_true", help="Show usage from yesterday")
    parser.add_argument("--apps-only", action="store_true", help="Show only app usage (flat list)")
    parser.add_argument("--titles-only", action="store_true", help="Show only title usage (flat list)")
    parser.add_argument("--limit", type=int, help="Limit number of results (for flat lists)")
    parser.add_argument("--tree", nargs="?", const=30, type=int, metavar="LIMIT", help="Show tree view with optional children limit (default: 30)")

    args = parser.parse_args()

    data = load_data()
    if not data:
        print("No usage data found")
        sys.exit(1)

    if args.date:
        dates = [args.date]
        period = args.date
    elif args.start_date:
        dates = get_date_range(args.start_date, args.end_date)
        period = f"{args.start_date}" + (f" to {args.end_date}" if args.end_date else "")
    else:
        today = datetime.now()
        if args.yesterday:
            today -= timedelta(days=1)
        dates = [today.strftime("%Y-%m-%d")]
        period = ["today", "yesterday"][args.yesterday]

    print(f"Usage statistics for {period}")

    if args.apps_only or args.titles_only:
        apps, titles = aggregate_data(data, dates)

        if not args.titles_only:
            print_usage(apps, "App Usage", args.limit)

        if not args.apps_only:
            print_usage(titles, "Title Usage", args.limit)
    else:
        tree_limit = args.tree if args.tree is not None else 30
        tree_data = aggregate_tree_data(data, dates)
        print_tree(tree_data, tree_limit)


if __name__ == "__main__":
    main()
