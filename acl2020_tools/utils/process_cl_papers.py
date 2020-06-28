import argparse
import csv

import pandas as pd

from acl2020_tools.utils.paper_import import clean_abstract, clean_title, extract_slot


def format_author_names(csv_authors):
    return "|".join(x.strip() for x in csv_authors.split(","))


def process_cl_papers(cl_xlsx: str, slot_xlsx: str, output_file: str):
    raw_df = pd.read_excel(cl_xlsx)

    slots_df = pd.read_excel(slot_xlsx, 1)
    cl_slots = slots_df.loc[
        slots_df["paper pub venue"].apply(lambda x: x.strip().lower())
        == "computational linguistics"
    ]
    cl_slots["Submission ID"] = cl_slots["ID"].apply(lambda x: int(str(x)[1:])).copy()
    concatenated_df = pd.merge(raw_df, cl_slots, on="Submission ID")

    cl_clean_df = pd.DataFrame()

    cl_clean_df["UID"] = "cl." + raw_df["Submission ID"].astype("str")
    cl_clean_df.set_index("UID", verify_integrity=True)

    cl_clean_df["title"] = concatenated_df["Title_x"].apply(clean_title)
    cl_clean_df["authors"] = concatenated_df["Authors_x"].apply(format_author_names)
    cl_clean_df["abstract"] = concatenated_df["Abstract"].apply(clean_abstract)
    cl_clean_df["paper_track"] = concatenated_df["slot 1"].apply(extract_slot)
    cl_clean_df["paper_type"] = "CL"
    cl_clean_df["pdf_url"] = concatenated_df["URL"]

    cl_clean_df.to_csv(
        output_file, sep=",", index=False, encoding="utf-8", quoting=csv.QUOTE_ALL
    )


if __name__ == "__main__":

    cmdline_parser = argparse.ArgumentParser(description=__doc__)

    cmdline_parser.add_argument(
        "--cl_xlsx_file",
        help="ACL2020.CL.papers.xlsx from https://github.com/acl-org/acl-2020-virtual-conference-sitedata/pull/73/files",
    )
    cmdline_parser.add_argument("--output_file", help="output cl_papers.csv file")
    cmdline_parser.add_argument(
        "--qa_session_xlsx",
        help="ACL 2020 live Q&A schedule (for authors).xlsx file to extract slots",
    )
    args = cmdline_parser.parse_args()

    process_cl_papers(
        cl_xlsx=args.cl_xlsx_file,
        slot_xlsx=args.qa_session_xlsx,
        output_file=args.output_file,
    )
