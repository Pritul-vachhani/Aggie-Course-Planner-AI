from bs4 import BeautifulSoup
import requests
import json
import copy
import os

TIMEOUT_S = 15
OUTPUT_BASENAME = "prereqs"
HOST_URI = "https://catalog.ucdavis.edu"

season_to_ind = {
    "WINTER": "01",
    "SPRING": "03",
    "SUMMER": "05",
    "FALL"  : "10"
}

def parse_effective(x):
    x = x.upper().split()
    return x[-1] + season_to_ind[x[0]]

QUARTER_OF_INTEREST = parse_effective("Winter 2027") # None

def fetch_and_parse(url):
    resp = requests.get(url, timeout=TIMEOUT_S)
    resp.raise_for_status()
    return BeautifulSoup(resp.content, 'html5lib')

def clean(s):
    return " ".join(s.replace("\xa0", " ").split())

def label_value(li):
    li = copy.copy(li)
    li.select_one(".label").extract()
    return clean(li.get_text())

def parse_course(block):
    
    code = clean(block.select_one(".detail-code b").get_text())
    
    current = None
    prereqs = block.select_one(".detail-prerequisite")
    if prereqs:
        prereqs = copy.copy(prereqs)
        if prereqs.i: prereqs.i.extract()
        current = clean(prereqs.get_text())

    updated_uls = block.select(".notinpdf ul:has(h5)")
    if not updated_uls: return code, current if QUARTER_OF_INTEREST is not None else {"prereqs": current}
    
    prereqs = {"Initial": current}
    prev_prereqs = current
    for ul in updated_uls:
        li = ul.select_one('li:has(> .label:-soup-contains("Prerequisite"))')
        eff = ul.select_one('li:-soup-contains("effective from")')
        new_prereqs = label_value(li) if li else None
        effective = clean(eff.get_text()).split(":", 1)[-1].strip(" .") if eff else None
        if QUARTER_OF_INTEREST is not None and parse_effective(effective) > QUARTER_OF_INTEREST: break
        if new_prereqs != prev_prereqs:
            prereqs[effective] = new_prereqs
            prev_prereqs = new_prereqs
    if QUARTER_OF_INTEREST is not None:
        return code, prev_prereqs
    return code, {"prereqs": prereqs}

def update_catalog():
    catalog = {}
    soup = fetch_and_parse(f"{HOST_URI}/courses-subject-code/")
    for subj in soup.select(".az_sitemap a[href^='/courses-subject-code']"):
        url = f"{HOST_URI}{subj.get('href')}"
        soup = fetch_and_parse(url)
        for x in soup.select(".sc_sccoursedescs .courseblock"):
            code, prereqs = parse_course(x)
            catalog[code] = prereqs
    return catalog

if __name__ == "__main__":
    curdir = os.path.dirname(__file__)
    fp = os.path.join(curdir, OUTPUT_BASENAME + ("" if QUARTER_OF_INTEREST is None else f"_{QUARTER_OF_INTEREST}") + ".json")
    with open(fp, "w") as f: json.dump(update_catalog(), f, indent=4)