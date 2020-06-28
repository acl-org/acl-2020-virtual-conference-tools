import argparse
import re
from collections import defaultdict
from datetime import datetime

import pandas as pd
import yaml

re_session_extract = re.compile(
    r"\w+ (\w+) (\d+), (\d+) (\d+\w) [\w\d\s:\-.,()]+-\d+ (\d+):(\d\d) UTC(.*)"
)


def extract_date(x):
    (month, date, year, session, hour, mins, timezone,) = re_session_extract.match(
        x
    ).groups()
    month_int = datetime.strptime(month, "%B").month
    parsed_date = datetime(int(year), month_int, int(date), int(hour), int(mins))
    assert timezone == "+0"
    return parsed_date, session


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Format paper details into MiniConf format"
    )
    parser.add_argument(
        "--track_file",
        help="Excel spreadsheet giving paper track, QA session times, and ID in the proceedings",
        action="store",
        type=str,
        default="ACL 2020 live Q&A schedule (for authors).xlsx",
    )
    parser.add_argument(
        "--sheet_name",
        help="Excel sheet name for TACL and CL",
        action="store",
        type=str,
        default="TACLCL Q&A schedule",
    )
    return parser.parse_args()


def main():
    args = parse_arguments()
    track_details = pd.read_excel(args.track_file, args.sheet_name)
    track_details.rename(columns={"paper pub venue": "PaperPubVenue"}, inplace=True)

    track_details["Date1"], track_details["Session1"] = zip(
        *track_details["slot 1"].map(extract_date)
    )
    track_details["Date2"], track_details["Session2"] = zip(
        *track_details["slot 2"].map(extract_date)
    )

    cl_session_time_map = defaultdict(lambda: {"date": "", "papers": []})
    tacl_session_time_map = defaultdict(lambda: {"date": "", "papers": []})

    venue = {"Computational Linguistics": "cl", "TACL": "tacl"}

    for row in track_details.itertuples():
        # Strip 9 for CL papers and 99 for TACL papers.
        if venue[row.PaperPubVenue] == "cl":
            row_id = str(row.ID)[1:]
            cl_session_time_map[row.Session1]["date"] = row.Date1
            cl_session_time_map[row.Session1]["papers"].append(
                venue[row.PaperPubVenue] + "." + str(row_id)
            )
            cl_session_time_map[row.Session2]["date"] = row.Date2
            cl_session_time_map[row.Session2]["papers"].append(
                venue[row.PaperPubVenue] + "." + str(row_id)
            )
        elif venue[row.PaperPubVenue] == "tacl":
            row_id = str(row.ID)[2:]
            tacl_session_time_map[row.Session1]["date"] = row.Date1
            tacl_session_time_map[row.Session1]["papers"].append(
                venue[row.PaperPubVenue] + "." + str(row_id)
            )
            tacl_session_time_map[row.Session2]["date"] = row.Date2
            tacl_session_time_map[row.Session2]["papers"].append(
                venue[row.PaperPubVenue] + "." + str(row_id)
            )
        else:
            raise ValueError("Unknown venue")

    # Sort everything CL
    for session_info in cl_session_time_map.values():
        session_info["papers"].sort(key=lambda x: int(x.split(".")[1]))
    dict_items = list(cl_session_time_map.items())
    dict_items.sort(key=lambda x: x[1]["date"])
    cl_ordered_sessions = dict(dict_items)

    for session_info in cl_session_time_map.values():
        session_info["date"] = session_info["date"].strftime("%Y-%m-%d_%H:%M:%S")

    with open("cl_paper_sessions.yml", "w") as f:
        yaml.dump(cl_ordered_sessions, f, default_flow_style=False, sort_keys=False)

    # Sort everything TACL
    for session_info in tacl_session_time_map.values():
        session_info["papers"].sort(key=lambda x: int(x.split(".")[1]))
    dict_items = list(tacl_session_time_map.items())
    dict_items.sort(key=lambda x: x[1]["date"])
    tacl_ordered_sessions = dict(dict_items)

    for session_info in tacl_session_time_map.values():
        session_info["date"] = session_info["date"].strftime("%Y-%m-%d_%H:%M:%S")

    with open("tacl_paper_sessions.yml", "w") as f:
        yaml.dump(tacl_ordered_sessions, f, default_flow_style=False, sort_keys=False)


if __name__ == "__main__":
    main()
