"""Converts the {main,srw,demo,cl,tacl}_papers.csv and {main,srw,demo,cl,tacl}_paper_sessions.yml
to a schedule file that can be used to create Zoom links.

Output file columns:
- id: the id of the paper (e.g., main.1)
- uniqueid: the unique Id of the link (e.g., main.1.3A)
- host_zoom_user_email: should be acl2020zoom+main-1@gmail.com
- alternative_hosts: should be acl2020zoom@gmail.com
- starttime: in the format of "%Y-%m-%dT%H:%M:%SZ" (e.g., 2020-07-06T05:00:00Z)
- endtime: in the format of "%Y-%m-%dT%H:%M:%SZ" (e.g., 2020-07-06T05:00:00Z)
- timezone: UTC (we hard code it because it is used in the ?_paper_sessions.yml by default)
- type: keep it empty
- meeting_or_webinar: should be "meeting"
- panelists: keep it empty
- title: the title of the paper
- abstract: the abstract of the paper
- authorString: authors (e.g., "First Author|Second Author|Third Author")
- zoomid: keep it empty
- join_link: keep it empty
- start_link: keep it empty
"""
import argparse
import csv
from datetime import datetime, timedelta

import pandas as pd
import yaml


def get_host_user_email(paper_id: str) -> str:
    prefix, idx = paper_id.split(".")
    assert prefix in ["main", "demo", "srw", "cl", "tacl"]
    assert int(idx) > 0
    return f"acl2020zoom+{prefix}-{idx}@gmail.com"


def main(
    papers_csv: str, sessions_yml: str, session_duration: int, outbase: str
) -> None:
    papers_df = pd.read_csv(
        papers_csv, sep=",", encoding="utf-8", na_values=None, keep_default_na=False
    )
    papers_df.set_index("UID", inplace=True, drop=True, verify_integrity=True)

    with open(sessions_yml) as fp:
        sessions = yaml.load(fp.read(), Loader=yaml.SafeLoader)

    rows = []
    for session_name, session_info in sessions.items():
        start_time = datetime.strptime(session_info["date"], "%Y-%m-%d_%H:%M:%S")
        end_time = start_time + timedelta(minutes=session_duration)
        start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        for paper_id in session_info["papers"]:
            paper = papers_df.loc[paper_id]
            rows.append(
                {
                    "id": paper_id,
                    "uniqueid": f"{paper_id}.{session_name}",
                    "host_zoom_user_email": get_host_user_email(paper_id),
                    "alternative_hosts": "acl2020zoom@gmail.com",
                    "starttime": start_time_str,
                    "endtime": end_time_str,
                    "timezone": "UTC",
                    "type": "",
                    "meeting_or_webinar": "meeting",
                    "panelists": "",
                    "title": paper.get("title"),
                    "abstract": paper.get("abstract"),
                    "authorString": paper.get("authors"),
                    "zoomid": "",
                    "join_link": "",
                    "start_link": "",
                }
            )
    data_df = pd.DataFrame(sorted(rows, key=lambda x: int(x["id"].split(".")[-1])))

    unique_ids = data_df.loc[:, "uniqueid"].tolist()
    assert len(unique_ids) == len(set(unique_ids))

    data_df.to_csv(
        outbase + ".tsv", sep="\t", index=False, encoding="utf-8", quoting=csv.QUOTE_ALL
    )
    data_df.to_excel(
        outbase + ".xlsx", index=False,
    )


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description=__doc__)
    cmdline_parser.add_argument("--papers_csv", help="papers csv file")
    cmdline_parser.add_argument("--sessions_yml", help="sessions yaml file")
    cmdline_parser.add_argument(
        "--session_duration",
        type=int,
        choices=[45, 60],
        help="session duration (in minutes)",
    )
    cmdline_parser.add_argument("--outbase", help="output file basename")
    args = cmdline_parser.parse_args()

    main(
        papers_csv=args.papers_csv,
        sessions_yml=args.sessions_yml,
        session_duration=args.session_duration,
        outbase=args.outbase,
    )
