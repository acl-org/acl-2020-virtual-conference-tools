import argparse
import csv

import pandas as pd

from acl2020_tools.utils.paper_import import clean_abstract, clean_title, extract_slot


def reformat_to_psv(org_format: str, sep: str):
    return "|".join(x.strip() for x in org_format.split(sep))


def process_tacl_papers(tacl_xlsx: str, slot_xlsx: str, output_file: str):
    raw_df = pd.read_excel(tacl_xlsx)

    slots_df = pd.read_excel(slot_xlsx, 1)
    tacl_slots = slots_df.loc[
        slots_df["paper pub venue"].apply(lambda x: x.strip().lower()) == "tacl"
    ]
    tacl_slots["ID"] = tacl_slots["ID"].apply(lambda x: int(str(x)[2:]))
    concatenated_df = pd.merge(raw_df, tacl_slots, on="ID")

    tacl_clean_df = pd.DataFrame()

    tacl_clean_df["UID"] = "tacl." + concatenated_df["ID"].astype("str")
    tacl_clean_df.set_index("UID", verify_integrity=True)

    tacl_clean_df["title"] = concatenated_df["Title_x"].apply(clean_title)
    tacl_clean_df["authors"] = concatenated_df["Authors_x"].apply(
        reformat_to_psv, args=(",")
    )
    tacl_clean_df["abstract"] = concatenated_df["Abstract"].apply(clean_abstract)
    tacl_clean_df["paper_track"] = concatenated_df["slot 1"].apply(extract_slot)
    tacl_clean_df["paper_type"] = "TACL"
    tacl_clean_df["pdf_url"] = concatenated_df["Links"]
    tacl_clean_df["emails"] = concatenated_df["Emails"].apply(
        reformat_to_psv, args=(";")
    )

    tacl_clean_df.to_csv(
        output_file, sep=",", index=False, encoding="utf-8", quoting=csv.QUOTE_ALL
    )


if __name__ == "__main__":

    cmdline_parser = argparse.ArgumentParser(description=__doc__)

    cmdline_parser.add_argument(
        "--tacl_xlsx_file",
        help="ACL2020.TACL.papers.xlsx from https://github.com/acl-org/acl-2020-virtual-conference-sitedata/pull/73/files",
    )
    cmdline_parser.add_argument(
        "--qa_session_xlsx",
        help="ACL 2020 live Q&A schedule (for authors).xlsx file to extract slots",
    )
    cmdline_parser.add_argument("--output_file", help="output tacl_papers.csv file")
    args = cmdline_parser.parse_args()

    process_tacl_papers(
        tacl_xlsx=args.tacl_xlsx_file,
        slot_xlsx=args.qa_session_xlsx,
        output_file=args.output_file,
    )
