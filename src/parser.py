# src/parser.py

import re
from typing import Dict, Optional

import pandas as pd
from bs4 import BeautifulSoup

# Regex to extract lesson information from the header
LESSON_REGEX = re.compile(r"Lesson\s+(\d+)\.(\d+)\.(\d+)\s+(.*)")

# Regex to extract footer details: collection, document id, and self-paced id.
FOOTER_REGEX = re.compile(r"Collection:\s*(\d+).*Document ID:\s*(\d+).*Self-paced ID:\s*(\d+)", re.DOTALL)


def clean_text(text: str) -> str:
    """Collapse whitespace and trim."""
    return re.sub(r"\s+", " ", text).strip()


def parse_footer(footer_text: str) -> Dict[str, Optional[str]]:
    """Extract footer metadata."""
    match = FOOTER_REGEX.search(footer_text)
    if match:
        collection, document_id, self_paced_id = match.groups()
        return {"collection": collection, "document_id": document_id, "self_paced_id": self_paced_id}
    return {"collection": None, "document_id": None, "self_paced_id": None}


def parse_card(card) -> Optional[Dict]:
    """Parse a single feedback card."""
    header_div = card.find("div", class_="card-header")
    if not header_div:
        return None
    header_text = clean_text(header_div.get_text())
    lesson_match = LESSON_REGEX.search(header_text)
    if not lesson_match:
        return None
    chapter, section, item, lesson_title = lesson_match.groups()

    body_div = card.find("div", class_="card-body")
    if not body_div:
        return None
    body_text = clean_text(body_div.get_text(separator=" "))

    num_responses_match = re.search(r"(\d+)\s+students responded", body_text)
    yes_match = re.search(r"(\d+)%\s+'yes", body_text)
    no_match = re.search(r"(\d+)%\s+'no", body_text)
    num_responses = int(num_responses_match.group(1)) if num_responses_match else 0
    yes_percentage = int(yes_match.group(1)) if yes_match else 0
    no_percentage = int(no_match.group(1)) if no_match else 0

    # Find all italicized comments
    comments = [clean_text(i_tag.get_text()) for i_tag in body_div.find_all("i") if clean_text(i_tag.get_text())]

    footer_div = card.find("div", class_="card-footer")
    footer_text = clean_text(footer_div.get_text(separator=" ")) if footer_div else ""
    footer_data = parse_footer(footer_text)

    return {
        "chapter": chapter,
        "section": section,
        "item": item,
        "lesson_title": lesson_title,
        "num_responses": num_responses,
        "yes_percentage": yes_percentage,
        "no_percentage": no_percentage,
        "comments": comments,
        "collection": footer_data.get("collection"),
        "document_id": footer_data.get("document_id"),
        "self_paced_id": footer_data.get("self_paced_id"),
    }


def parse_feedback(html: str) -> pd.DataFrame:
    soup = BeautifulSoup(html, "html.parser")
    records = []
    # Find all cards regardless of their container.
    cards = soup.find_all("div", class_="card mb-4")
    for card in cards:
        record = parse_card(card)
        if record:
            # Look for the closest preceding h3 with class "p-0 m-0"
            course_header = card.find_previous("h3", class_="p-0 m-0")
            if course_header:
                course = clean_text(course_header.get_text())
            else:
                course = "Unknown Course"
            record["course"] = course
            records.append(record)
    return pd.DataFrame(records)


if __name__ == "__main__":
    with open("feedback_page.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    df = parse_feedback(html_content)
    pd.set_option("display.max_colwidth", None)
    print(df)
