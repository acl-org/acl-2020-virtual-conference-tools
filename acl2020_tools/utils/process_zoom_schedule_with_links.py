import argparse

import pandas as pd


def main(schedule_csv: str, outbase: str) -> None:
    schedule_df = pd.read_csv(
        schedule_csv, sep=",", encoding="utf-8", na_values=None, keep_default_na=False
    )
    schedule_df.loc[:, "UID"] = schedule_df.loc[:, "id"]
    schedule_df.loc[:, "session_name"] = schedule_df.loc[:, "uniqueid"].apply(
        lambda x: x.split(".")[-1]
    )
    schedule_df.loc[:, "zoom_join_link"] = schedule_df.loc[
        :, "join_link(for Attendees)"
    ]

    colnames = [
        "UID",
        "session_name",
        "starttime",
        "endtime",
        "timezone",
        "zoom_join_link",
    ]

    schedule_df.to_csv(
        outbase + ".csv", sep=",", index=False, encoding="utf-8", columns=colnames
    )

    schedule_df.to_excel(outbase + ".xlsx", index=False, columns=colnames)


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description=__doc__)
    cmdline_parser.add_argument("--schedule_csv", help="input zoom schedule csv")
    cmdline_parser.add_argument("--outbase", help="output files basename")
    args = cmdline_parser.parse_args()

    main(
        schedule_csv=args.schedule_csv, outbase=args.outbase,
    )
