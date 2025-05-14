import json
import os
import requests
from bs4 import BeautifulSoup
import re
import codecs

class CourseExtractor:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.base_url = self.config["base_url"]
        self.output_file = self.config["output_file"]

        # Predefined topics and their keywords
        self.topics_map = {
            "Python": ["Python"],
            "Data Science": ["Data Science"],
            "R": ["R"],
            "Deep Learning": ["Deep Learning"],
            "NLP": ["NLP", "Natural Language Processing"],
            "Machine Learning": ["Machine Learning", "ML", "AutoML"]
        }

    def load_config(self, path):
        with open(path, "r") as file:
            return json.load(file)

    def fetch_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            print(f"Successfully fetched data from {url}")
            return response.content
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def clean_text(self, text):
        """ Clean and normalize the text """
        # Convert \u2013 to hyphen
        text = text.replace("\u2013", "-")
        # Decode other Unicode sequences
        try:
            text = codecs.decode(text, 'unicode_escape')
        except Exception as e:
            print(f"Unicode decode error: {e}")
        
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def extract_courses(self, soup):
        """ Extract courses by directly capturing the text under the <li> tag """
        courses = []
        course_list = soup.find_all("ul", class_="berd_course_list")

        for course_container in course_list:
            course_items = course_container.find_all("li")

            for course in course_items:
                link_elem = course.find("a")
                if link_elem:
                    url = link_elem["href"]
                    text_content = self.clean_text(link_elem.get_text(separator=" ").strip())

                    # Capture associated metadata (if available)
                    meta_elem = course.find("div", class_="berd_meta")
                    meta_info = self.clean_text(meta_elem.get_text(separator=" ").strip()) if meta_elem else ""

                    # Combine text and meta info for easier processing
                    full_text = f"{text_content} {meta_info}".strip()

                    # Append to the courses list
                    courses.append({
                        "title": full_text,
                        "url": url,
                        "description": full_text
                    })

        print(f"Extracted {len(courses)} courses.")
        return courses

    def categorize_courses(self, courses):
        """ Categorize courses based on keywords """
        categorized_data = {topic: [] for topic in self.topics_map.keys()}

        for course in courses:
            title = course["title"].lower()
            categories = set()

            for topic, keywords in self.topics_map.items():
                for keyword in keywords:
                    if keyword.lower() in title:
                        categories.add(topic)

            # Assign course to multiple topics
            for category in categories:
                categorized_data[category].append({
                    "title": course["title"],
                    "url": course["url"],
                    "description": course["description"],
                    "categories": list(categories)
                })

        # Remove empty categories
        categorized_data = {k: v for k, v in categorized_data.items() if v}
        return categorized_data

    def extract_all(self):
        content = self.fetch_page(self.base_url)
        if not content:
            return

        soup = BeautifulSoup(content, "lxml")
        courses = self.extract_courses(soup)
        categorized_data = self.categorize_courses(courses)
        self.save_to_json(categorized_data)

    def save_to_json(self, data):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
        print(f"Data successfully saved to {self.output_file}")
