import json
import os
import requests
from bs4 import BeautifulSoup

class CourseExtractor:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.base_url = self.config["base_url"]
        self.output_file = self.config["output_file"]
        self.categories_map = self.config["categories_map"]

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

    def extract_courses(self, category, soup):
        courses = []
        print(f"Looking for category: {category}")

        # Locate the category section using more robust search
        category_section = soup.find("h2", string=lambda text: text and category.lower() in text.lower())

        if not category_section:
            print(f"No section found for category: {category}")
            return courses

        course_list = category_section.find_next("div").find_all("div", recursive=False)

        for course in course_list:
            title = course.find("h3").get_text(strip=True) if course.find("h3") else "No Title"
            description = course.find("p").get_text(strip=True) if course.find("p") else "No Description"
            read_more = course.find("a", string="READ MORE")
            url = read_more["href"] if read_more else "#"

            courses.append({
                "title": title,
                "url": url,
                "description": description,
                "starting-date": "N/A"
            })

        print(f"Extracted {len(courses)} courses for category: {category}")
        return courses

    def extract_all(self):
        content = self.fetch_page(self.base_url)
        if not content:
            return

        soup = BeautifulSoup(content, "lxml")
        all_courses = {}

        for category, json_key in self.categories_map.items():
            courses = self.extract_courses(category, soup)
            all_courses[json_key] = courses

        self.save_to_json(all_courses)

    def save_to_json(self, data):
        os.makedirs(os.path.dirname(self.output_file), exist_ok=True)
        with open(self.output_file, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {self.output_file}")
