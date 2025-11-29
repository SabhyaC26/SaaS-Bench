"""Web scraper for extracting tutorial content from Databricks documentation."""

import re
from typing import Optional

import requests
from bs4 import BeautifulSoup


def scrape_tutorial(url: str) -> str:
    """Extract tutorial content from Databricks documentation pages."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        raise ValueError(f"Failed to fetch URL: {e}")

    soup = BeautifulSoup(response.content, "html.parser")

    # Remove script and style elements
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()

    # Try to find main content area (Databricks docs structure)
    main_content = soup.find("main") or soup.find("article") or soup.find("div", class_=re.compile("content|main"))

    if not main_content:
        # Fallback: use body
        main_content = soup.find("body")

    if not main_content:
        raise ValueError("Could not find main content area")

    # Extract text preserving some structure
    text_parts = []

    # Extract title
    title = main_content.find("h1")
    if title:
        text_parts.append(f"# {title.get_text().strip()}\n")

    # Extract prerequisites/requirements section
    prerequisites_section = None
    for heading in main_content.find_all(["h2", "h3"]):
        heading_text = heading.get_text().strip().lower()
        if "before you begin" in heading_text or "requirements" in heading_text or "prerequisites" in heading_text:
            prerequisites_section = heading
            text_parts.append(f"\n## {heading.get_text().strip()}\n")
            # Get content until next heading
            for sibling in heading.next_siblings:
                if sibling.name in ["h2", "h3"]:
                    break
                if hasattr(sibling, "get_text"):
                    text = sibling.get_text().strip()
                    if text:
                        text_parts.append(text + "\n")
            break

    # Extract step-by-step instructions
    step_pattern = re.compile(r"step \d+", re.IGNORECASE)
    for heading in main_content.find_all(["h2", "h3"]):
        heading_text = heading.get_text().strip()
        if step_pattern.search(heading_text):
            text_parts.append(f"\n## {heading_text}\n")
            # Get content until next heading
            for sibling in heading.next_siblings:
                if sibling.name in ["h2", "h3"]:
                    break
                if hasattr(sibling, "get_text"):
                    text = sibling.get_text().strip()
                    if text:
                        text_parts.append(text + "\n")
                # Extract code blocks
                if sibling.name == "pre" or (sibling.name == "div" and "code" in str(sibling.get("class", []))):
                    code_text = sibling.get_text().strip()
                    if code_text:
                        text_parts.append(f"```\n{code_text}\n```\n")

    # If no structured extraction worked, just get all text
    if len(text_parts) < 3:
        text_parts = [main_content.get_text(separator="\n", strip=True)]

    # Clean up text
    full_text = "\n".join(text_parts)
    # Remove excessive whitespace
    full_text = re.sub(r"\n{3,}", "\n\n", full_text)
    # Remove excessive spaces
    full_text = re.sub(r" {2,}", " ", full_text)

    return full_text.strip()


def extract_sql_commands(text: str) -> list[str]:
    """Extract SQL commands from tutorial text."""
    sql_pattern = re.compile(r"```(?:sql)?\s*\n(.*?)\n```", re.DOTALL | re.IGNORECASE)
    matches = sql_pattern.findall(text)
    return [match.strip() for match in matches if match.strip()]

