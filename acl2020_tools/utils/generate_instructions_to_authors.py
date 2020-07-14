"""Generates the instruction emails sent to authors.
"""

import argparse
import csv
from typing import Optional

import pandas as pd

OUTPUT_COLUMNS = [
    "Submission ID",
    "Note 0",  # "paper_url"
    "Note 1",  # "rocketchat_channel"
    "Note 2",  # "zoom_host_email"
    "Note 3",  # "zoom_host_password"
    "Note 4",  # "zoom_start_link_for_slot_1"
    "Note 5",  # "zoom_join_link_for_slot_1"
    "Note 6",  # "zoom_start_link_for_slot_2"
    "Note 7",  # "zoom_join_link_for_slot_2"
    # these two fields are used for sanity check
    # "session_name_for_slot_1
    # "session_name_for_slot_2",
    # "_title",
    # "_author_emails"
]


def get_webpage_url(paper_uid: str) -> str:
    return f"https://virtual.acl2020.org/paper_{paper_uid}.html"


def get_rockectchat_channel(paper_uid: str) -> str:
    return f"https://acl2020.rocket.chat/channel/paper-{paper_uid.replace('.', '-')}"


def get_submission_id(paper_uid: str, submission_id: Optional[str]) -> str:
    """Gets the submission ID for a paper UID.

    Unfortunately we have used the Anthology ID for main conference papers, and
    submission ID for all other papers.
    This is an adhoc method to get the submission ID.
    """
    if paper_uid.startswith("main."):
        assert submission_id is not None
        return submission_id
    return paper_uid.split(".")[1]


def main(accounts_tsv: str, schedule_csv: str, outbase: str) -> None:
    schedule_df = pd.read_csv(
        schedule_csv, sep=",", encoding="utf-8", na_values=None, keep_default_na=False
    )
    schedule_groups = schedule_df.groupby("id")

    accounts_df = pd.read_csv(
        accounts_tsv, sep="\t", encoding="utf-8", na_values=None, keep_default_na=False
    )
    output_rows = []
    for _, row in accounts_df.iterrows():
        uid = row.get("UID")
        username = row.get("username")
        password = row.get("passwords")
        assert username
        assert password
        session_infos = []
        for _, zoom_info in schedule_groups.get_group(uid).iterrows():
            assert username == zoom_info.get("host_zoom_user_email")
            units = zoom_info.get("uniqueid").split(".")
            assert len(units) == 3
            session_name = units[-1]
            assert ".".join(units[:2]) == uid
            session_infos.append(
                {
                    "session_name": session_name,
                    "start_link": zoom_info.get("start_link(for Hosts)"),
                    "join_link": zoom_info.get("join_link(for Attendees)"),
                    "title": zoom_info.get("Title"),
                    "author_emails": zoom_info.get("All Author Emails"),
                    "submission_id": zoom_info.get("ID"),
                }
            )
        if len(session_infos) == 2:
            assert session_infos[0]["title"] == session_infos[1]["title"]
        else:
            assert len(session_infos) == 1
            session_infos.append(
                {"session_name": "", "start_link": "", "join_link": "",}
            )

        # "Note 0",  # "paper_url"
        # "Note 1",  # "rocketchat_channel"
        # "Note 2",  # "zoom_host_email"
        # "Note 3",  # "zoom_host_password"
        # "Note 4",  # "zoom_start_link_for_slot_1"
        # "Note 5",  # "zoom_join_link_for_slot_1"
        # "Note 6",  # "zoom_start_link_for_slot_2"
        # "Note 7",  # "zoom_join_link_for_slot_2"
        output_row = {
            "Submission ID": get_submission_id(
                uid, session_infos[0].get("submission_id")
            ),
            "Note 0": get_webpage_url(uid),
            "Note 1": get_rockectchat_channel(uid),
            "Note 2": username,
            "Note 3": password,
            "Note 4": session_infos[0]["start_link"],
            "Note 5": session_infos[0]["join_link"],
            "Note 6": session_infos[1]["start_link"],
            "Note 7": session_infos[1]["join_link"],
            # "_session_name_for_slot_1": session_infos[0]["session_name"],
            # "_session_name_for_slot_2": session_infos[1]["session_name"],
            # "_title": session_infos[0]["title"],
            # "_author_emails": session_infos[0]["author_emails"],
        }
        output_rows.append(output_row)

    output_df = pd.DataFrame(output_rows)
    output_df.to_csv(
        outbase + ".tsv",
        sep="\t",
        index=False,
        encoding="utf-8",
        quoting=csv.QUOTE_ALL,
        columns=OUTPUT_COLUMNS,
    )
    output_df.to_csv(
        outbase + ".csv",
        sep="\t",
        index=False,
        encoding="utf-8",
        columns=OUTPUT_COLUMNS,
    )
    output_df.to_excel(
        outbase + ".xlsx", index=False, encoding="utf-8", columns=OUTPUT_COLUMNS
    )


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description=__doc__)
    cmdline_parser.add_argument("--accounts_tsv", help="account tsv file")
    cmdline_parser.add_argument("--schedule_csv", help="schedule csv file")
    # cmdline_parser.add_argument(
    #     '--venue',
    #     choices=["main", "demo", "srw", "cl", "tacl"],
    #     help='the venue of the papers'
    # )
    cmdline_parser.add_argument("--outbase", help="output basename")
    args = cmdline_parser.parse_args()

    main(
        accounts_tsv=args.accounts_tsv,
        schedule_csv=args.schedule_csv,
        outbase=args.outbase,
    )
