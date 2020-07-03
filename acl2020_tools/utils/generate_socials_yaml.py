import csv

import yaml


def main():
    bofs = []

    def str_presenter(dumper, data):
        if len(data) > 100:  # check for multiline string
            return dumper.represent_scalar("tag:yaml.org,2002:str", data, style=">")
        return dumper.represent_scalar("tag:yaml.org,2002:str", data)

    yaml.add_representer(str, str_presenter)

    schedule_map = {
        "S1": {"day": "July 6th", "time": "02:00-03:00 PDT",},
        "S2": {"day": "July 6th", "time": "11:00-12:00 PDT",},
        "S3": {"day": "July 6th", "time": "13:00-14:00 PDT",},
        "S4": {"day": "July 6th", "time": "22:00-23:00 PDT",},
        "S5": {"day": "July 7th", "time": "11:00-12:00 PDT",},
        "S6": {"day": "July 7th", "time": "13:00-14:00 PDT",},
    }
    with open("inbox/socials_excl_bof.yml") as f:
        socials_base = yaml.load(f)

    bof_template = socials_base[-1]
    description = bof_template["description"]
    bofs.extend(socials_base[:-1])
    with open("inbox/BoFScheduleInternal - LinksSchedule.csv") as f:
        rows = csv.DictReader(f)
        for row in rows:
            if not row["Theme"] or row["Theme"][:4] == "NOTE":
                continue
            bof = bof_template.copy()
            bof["name"] = "Birds of a feather - " + row["Theme"]
            bof["description"] = description
            schedules = []
            for key in row:
                if row[key]:
                    session_id = key.split(" ")[0]
                    if session_id in schedule_map:
                        schedule = schedule_map[session_id].copy()
                        schedule["link"] = row[key].split(": ")[-1].strip()
                        schedules.append(schedule)
            bof["schedules"] = schedules
            bofs.append(bof)
    print(len(bofs))
    with open("socials.yml", "w") as f:
        yaml.dump(bofs, f, default_flow_style=False)


if __name__ == "__main__":
    main()
