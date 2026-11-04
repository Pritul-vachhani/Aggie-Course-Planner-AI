# Decide stages of information

import json
import os
import re
import time
import requests
from datetime import datetime
from urllib.parse import urlencode
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup



TZ = ZoneInfo("America/Los_Angeles")
DATE_FMT = "%B, %d %Y %H:%M:%S"   # "January, 04 2027 00:00:00"
TIME_FMT = "%H%M"                 # "1340"
DAY_FIELDS = [                    # canonical order for the days string
    ("monday", "M"), ("tuesday", "T"), ("wednesday", "W"), ("thursday", "R"),
    ("friday", "F"), ("saturday", "S"), ("sunday", "U"),
]



def fetch(session, term_code, subject, timeout=5):
    add_filters = urlencode({
        "course_number": "", "subject": subject,
        "course_start_eval": "At", "course_start_time": "-",
        "course_end_eval": "At", "course_end_time": "-",
        "course_level": "-", "course_meet_type": "ALL",
        "course_units": "-", "course_status": "All",
        "sortBy": "", "showMe": "", "runMe": 1, "clearMe": "",
        "termCode": term_code, "expandFilters": "",
    })
    response = session.post(
        "https://my.ucdavis.edu/schedulebuilder/cf/search/search.cfc",
        headers={
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://my.ucdavis.edu",
            "Referer": f"https://my.ucdavis.edu/schedulebuilder/index.cfm?termCode={term_code}&helpTour=",
            "X-Requested-With": "XMLHttpRequest",
        },
        data={
            "method": "search",
            "termCode": term_code,
            "filters": json.dumps({"searchTerm": "", "addFilters": add_filters}),
            "pidm": "0",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    data = response.json()
    return list(data.values()) if isinstance(data, dict) else data



def clean(s):
    # Strip whitespace; turn empty strings into None
    if s is None:
        return None
    s = s.strip()
    return s or None

def to_date(s):
    # 'January, 04 2027 00:00:00' -> '2027-01-04' (or None)
    s = clean(s)
    return datetime.strptime(s, DATE_FMT).date().isoformat() if s else None

def to_timestamp(s):
    # 'March, 19 2027 15:30:00' -> '2027-03-19T15:30:00-07:00' (Pacific), or None
    s = clean(s)
    return datetime.strptime(s, DATE_FMT).replace(tzinfo=TZ).isoformat() if s else None

def to_time(s):
    # '1340' -> '13:40' (or None for TBA).
    s = clean(s)
    return datetime.strptime(s, TIME_FMT).strftime("%H:%M") if s else None

def split_ge(s):
    # 'QL,SE' -> ['QL', 'SE'].
    return [code.strip() for code in (s or "").split(",") if code.strip()]

def split_cross_listing(s):
    # 'CDM 012.' -> ['CDM 012'].
    return [c.strip().rstrip(".").strip() for c in re.split(r"[;,]", s or "") if c.strip().rstrip(".")]

def course_code(subject, number):
    return f"{subject} {number}"

def is_placeholder(rec):
    # Non-enrollable courses
    return rec["course"]["printCRN"] == "@"



def parse_meeting(m):
    days = "".join(letter for field, letter in DAY_FIELDS if m.get(field))
    is_tba = clean(m.get("daysString")) == "TBA"
    building_code = clean(m.get("buildingCode"))
    return {
        "activity_type": clean(m.get("type")),        # LEC, DIS, LAB, WVL, ...
        "activity_code": clean(m.get("meetCode")),    # A, D, C, 0, ...
        "activity_desc": clean(m.get("description")),
        "days": None if is_tba else (days or None),   # 'MWF', 'TR'
        "is_tba": is_tba,
        "start_time": to_time(m.get("startTime")),
        "end_time": to_time(m.get("endTime")),
        "start_date": to_date(m.get("startDate")),
        "end_date": to_date(m.get("endDate")),
        "building_code": building_code,
        "building_name": clean(m.get("building")),
        "room": (clean(m.get("room")) or "").lstrip("0") or None,  # '01003' -> '1003'; '00000' -> None
        "is_online": building_code == "ONLINE" or clean(m.get("type")) in ("WVL", "WED"),
    }

def parse_instructor(i):
    return {
        "email": clean(i.get("instructorEmail")).lower(),
        "first_name": clean(i.get("firstName")),
        "last_name": clean(i.get("lastName")),
        "full_name": clean(i.get("fullName")),
        "display_name": clean(i.get("instructorName")),
    }

def parse_record(rec):
    
    c, icms = rec["course"], rec["icmsData"]
    subject = clean(c["subjectCode"])
    number = clean(c["courseNum"])
    crn = clean(c["crn"])

    subject_data = {
        "name": clean(c["subjectDesc"]),
    }

    course_data = {
        "course_code": course_code(subject, number),
        "title": clean(c["title"]),
        "description": clean(icms.get("newDescription")),
        "ge_codes": split_ge(icms.get("ge3")),
        "cross_listings": split_cross_listing(icms.get("crossListing")),
        "credit_limit_text": clean(icms.get("creditLimit")),
        "prereq_text": clean(icms.get("prereq")),
    }

    variable = c.get("unitsInd") == "TO"
    section_data = {
        "seq_num": clean(c["seqNum"]),
        "is_placeholder": is_placeholder(rec),
        "units_min": c["unitsLow"],
        "units_max": c["unitsHigh"] if variable else c["unitsLow"],
        "grade_mode": clean(c.get("gradeMode")),
        "reserved_seating": bool(c.get("reservedSeating")),
        "drop_type": clean(c.get("dropDesc")),
        "drop_date": to_date(c.get("dropDate")),
        "final_exam_at": to_timestamp(rec.get("finalExam", {}).get("examDate")),
        "notes": {
            "important": rec.get("importantNotes", []),
            "crn": rec.get("crnNotes", []),
            "department": rec.get("courseDepartmentNotes", []),
            "subject": rec.get("courseSubjectNotes", []),
        },
        "instructors": [parse_instructor(i) for i in rec.get("instructor", []) if clean(i.get("instructorEmail"))],
        "meetings": [parse_meeting(m) for m in rec.get("meeting", [])],
    }

    return subject, number, crn, subject_data, course_data, section_data



def get_subjects(session, timeout=15):
    resp = session.get("https://catalog.ucdavis.edu/courses-subject-code/", timeout=timeout)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, 'html5lib')
    subjects = soup.select(".az_sitemap a[href^='/courses-subject-code']")
    return [x.get_text().split()[-1][1:-1] for x in subjects]

def build_tree(records):
    tree = {}
    for rec in records:
        subject, number, crn, subject_data, course_data, section_data = parse_record(rec)
        subj = tree.setdefault(subject, {**subject_data, "courses": {}})
        course = subj["courses"].setdefault(number, {**course_data, "sections": {}})
        course["sections"][crn] = section_data
    return tree



'''
Term Code: "YYYYTT"
    01 - Winter Quarter
    03 - Spring Quarter
    05 - Summer Session I
    06 - Summer Special Session
    07 - Summer Session II
    10 - Fall Quarter
'''

def main():
    
    SLEEP_INTERVAL = 1
    TERM = "202610"#"202701"

    records = []
    with requests.Session() as session:
        subjects = get_subjects(session)
        print(f"{len(subjects)} Subjects Found!")
        for n, subject in enumerate(subjects):
            if n: time.sleep(SLEEP_INTERVAL)
            try:
                batch = fetch(session, TERM, subject)
            except (requests.RequestException, ValueError) as e:
                print(f"{subject}: failed ({e})")
                continue
            print(f"{str(n).rjust(3, "0")} {subject}: {len(batch)} sections")
            records.extend(batch)

    tree = build_tree(records)
    out = f"schedule_{TERM}.json"
    curdir = os.path.dirname(__file__)
    with open(os.path.join(curdir, out), "w") as f: json.dump(tree, f)

if __name__ == "__main__": main()