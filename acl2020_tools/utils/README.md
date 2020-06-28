This directory contains extensions to help support the mini-conf library.

For the updated procedure on getting similar papers + recommendations refer to README.recommendations.md


These include:

* `embeddings.py` : For turning abstracts into embeddings. Creates an `embeddings.torch` file. 

```bash
python embeddings.py ../sitedata/papers.csv
```

* `generate_version.py` : Generate version file for version tracking.  This script is used in [../Makefile](../Makefile)

```bash
python3 scripts/generate_version.py build/version.json
```

* `reduce.py` : For creating two-dimensional representations of the embeddings.

```bash
python reduce.py ../sitedata/papers.csv embeddings.torch > ../sitedata/papers_projection.json --projection-method umap
```

* `parse_calendar.py` : to convert a local or remote ICS file to JSON. -- more on importing calendars see [README_Schedule.md](README_Schedule.md)

```bash
python parse_calendar.py --in sample_cal.ics
```

* Image-Extraction: https://github.com/Mini-Conf/image-extraction for pulling images from PDF files. 

* `paper_import.py` : For creating `papers.csv` from conference sources

```bash
python paper_import.py --volume 1
```

* `qa_schedule_import.py` : For creating `poster_schedule.yml` 

```bash
python qa_schedule_import.py --volume 1
```

* Image-Extraction: https://github.com/Mini-Conf/image-extraction for pulling images from PDF files. 


### Zoom
* Generate random passwords for host accounts.
    ```bash
    ```
* Create files for Zoom python scripts.
    ```bash
    python -m acl2020_tools.utils.create_zoom_schedule \
        --papers_csv sitedata_acl2020/main_papers.csv \
        --sessions_yml sitedata_acl2020/main_paper_sessions.yml \
        --session_duration 60 \
        --outbase var/main_paper_schedule
    ```

