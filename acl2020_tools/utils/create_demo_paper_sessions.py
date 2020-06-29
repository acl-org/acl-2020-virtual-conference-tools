import argparse
import json
import re
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, DefaultDict, Dict

import pandas as pd
import yaml

re_session_extract = re.compile(r"(\w+), (\w+) (\d+), (\d+) UTC(.*)")


def extract_date(day_str: str, time: datetime):
    _, month, date, year, timezone = re_session_extract.match(day_str).groups()
    assert timezone == "+0"
    month_int = datetime.strptime(month, "%B").month
    parsed_date = datetime(int(year), month_int, int(date), time.hour, time.minute)
    return parsed_date


def get_session_name(session_full_name: str, date: datetime) -> str:
    assert session_full_name.startswith("Demo Session ")
    session_name = session_full_name[13:]
    if date.day == 6:
        session_sidx = 1
    elif date.day == 7:
        session_sidx = 2
    elif date.day == 8:
        session_sidx = 3
    else:
        raise ValueError(f"Unknown date {date}")

    return f"D{session_name}-{session_sidx}"


def main(demo_papers_xlsx: str, output_file: str, calendar_json: str):
    demo_papers_df = pd.read_excel(demo_papers_xlsx)

    session_time_map: DefaultDict[str, Dict[str, Any]] = defaultdict(
        lambda: {"date": "", "papers": []}
    )
    for _, row in demo_papers_df.iterrows():
        uid = f"demo.{row.get('UID')}"
        session_full_name = row.get("track")
        assert session_full_name.startswith("Demo ")
        date = extract_date(row.get("Day Date"), row.get("Ses Time"))
        session_name = get_session_name(session_full_name, date)
        if session_name not in session_time_map:
            session_time_map[session_name]["date"] = date
        else:
            registered_date = session_time_map[session_name]["date"]
            if date != registered_date:
                print(
                    f"{uid} {row.get('session')} {row.get('Day Date')} (previously seen {registered_date})"
                )
                continue
        session_time_map[session_name]["papers"].append(uid)

    # Sort everything
    for session_info in session_time_map.values():
        session_info["papers"].sort(key=lambda x: int(x.split(".")[1]))
    dict_items = list(sorted(session_time_map.items(), key=lambda x: x[1]["date"]))
    ordered_sessions = dict(dict_items)

    calendar_items = [
        {
            "title": f"Demo Session {item[0][1:]}",
            "start": item[1]["date"].strftime("%Y-%m-%dT%H:%M:%S+00:00"),
            "end": (item[1]["date"] + timedelta(minutes=45)).strftime(
                "%Y-%m-%dT%H:%M:%S+00:00"
            ),
            "location": "",
            "link": f"papers.html?session={item[0]}",
            "category": "time",
            "calendarId": "---",
            "type": "QA Sessions",
        }
        for item in dict_items
    ]

    for session_info in session_time_map.values():
        session_info["date"] = session_info["date"].strftime("%Y-%m-%d_%H:%M:%S")

    with open(output_file, "w") as f:
        yaml.dump(ordered_sessions, f, default_flow_style=False, sort_keys=False)

    with open(calendar_json, "w") as f:
        f.write(json.dumps(calendar_items, indent=2))
        f.write("\n")


def parse_arguments():
    cmdline_parser = argparse.ArgumentParser(description=__doc__)
    cmdline_parser.add_argument(
        "--demo-papers-file", help="DemoPapers_SHARED.xlsx from demo chairs"
    )
    cmdline_parser.add_argument(
        "--output-file", help="output demo_paper_sessions.yml file"
    )
    cmdline_parser.add_argument("--calendar-json", help="output calender json file")
    return cmdline_parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    main(
        demo_papers_xlsx=args.demo_papers_file,
        output_file=args.output_file,
        calendar_json=args.calendar_json,
    )
