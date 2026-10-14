# Subjects: https://catalog.ucdavis.edu/courses-subject-code/
# Course Schema: https://catalog.ucdavis.edu/about-courses/
# Alt: https://catalog.ucdavis.edu/course-search/

from bs4 import BeautifulSoup
import requests
import json
import os

TIMEOUT_S = 15
OUTPUT_NAME = "catalog.json"
HOST_URI = "https://catalog.ucdavis.edu"

def fetch_and_parse(url):
    resp = requests.get(url, timeout=TIMEOUT_S)
    resp.raise_for_status()
    return BeautifulSoup(resp.content, 'html5lib')

def parse_subject(subject_elem):
    block = subject_elem.get_text().split()
    return f"{HOST_URI}{subject_elem.get("href")}", " ".join(block[:-1]), block[-1][1:-1]

def parse_course(course_elem):
    title_block = course_elem.select("h3 > span")
    detail_block = course_elem.select("div")[1:]
    return {
        "code": title_block[0].get_text(),
        "title": title_block[1].get_text()[2:],
        "units":  title_block[2].get_text().split(" unit")[0].replace("(", ""),
        "desc": detail_block[0].find("p").get_text().replace("Course Description: ", ""),
        "prereqs": detail_block[1].get_text().replace("Prerequisite(s): ", ""),
        "details": detail_block[2].find("ul").get_text()[1:]
    }

def update_catalog():
    catalog = []
    soup = fetch_and_parse(f"{HOST_URI}/courses-subject-code/")
    for subj in soup.select(".az_sitemap a[href^='/courses-subject-code']"):
        url, subj, code = parse_subject(subj)
        soup = fetch_and_parse(url)
        catalog.append({ 
            "code": code,
            "subj": subj,
            "url": url,
            "courses": [parse_course(x) for x in soup.select(".sc_sccoursedescs .courseblock")]
        })
    return catalog

if __name__ == "__main__":
    curdir = os.path.dirname(__file__)
    fp = os.path.join(curdir, OUTPUT_NAME)
    with open(fp, "w") as f: json.dump(update_catalog(), f, indent=4)