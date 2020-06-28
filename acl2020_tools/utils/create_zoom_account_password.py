"""Generate random passwords for each host account.

Under https://zoom.us/account/setting/security
Basic Password Requirement
- Minimum of 8 characters
- Have at least 1 letter (a, b, c...)
- Have at least 1 number (1, 2, 3...)
- Include both upper case and lower case characters
"""

import argparse
import csv
import random
import string

import pandas as pd

from acl2020_tools.utils.create_zoom_schedule import get_host_user_email

LOWERCASE_LETTERS = list(string.ascii_lowercase)
UPPERCASE_LETTERS = list(string.ascii_uppercase)
NUMBERS = [str(i) for i in range(10)]
MERGED = LOWERCASE_LETTERS + UPPERCASE_LETTERS + NUMBERS


def generate_random_password() -> str:
    lowercase_letter = random.choice(LOWERCASE_LETTERS)
    uppercase_letter = random.choice(UPPERCASE_LETTERS)
    number = random.choice(NUMBERS)
    remaining = [random.choice(MERGED) for _ in range(5)]
    password_chars = [lowercase_letter, uppercase_letter, number] + remaining
    random.shuffle(password_chars)
    return "".join(password_chars)


def main(papers_csv: str, outbase: str) -> None:
    papers_df = pd.read_csv(
        papers_csv, sep=",", encoding="utf-8", na_values=None, keep_default_na=False
    )
    paper_ids = papers_df.loc[:, "UID"].tolist()
    assert len(paper_ids) == len(set(paper_ids))

    usernames = [get_host_user_email(paper_id) for paper_id in paper_ids]
    passwords = [generate_random_password() for _ in paper_ids]

    df = pd.DataFrame({"UID": paper_ids, "username": usernames, "passwords": passwords})
    df.to_csv(
        outbase + ".tsv", sep="\t", index=False, encoding="utf-8", quoting=csv.QUOTE_ALL
    )
    df.to_excel(outbase + ".xlsx", index=False)


if __name__ == "__main__":
    cmdline_parser = argparse.ArgumentParser(description=__doc__)
    cmdline_parser.add_argument("--papers_csv", help="papers csv file")
    cmdline_parser.add_argument("--outbase", help="output file basename")
    args = cmdline_parser.parse_args()

    main(papers_csv=args.papers_csv, outbase=args.outbase)
