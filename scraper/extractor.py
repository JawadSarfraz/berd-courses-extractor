import json
import os
import requests
from bs4 import BeautifulSoup

class CourseExtractor:
    def __init__(self, config_path):
        self.config = self.load_config(config_path)
        self.base_url = self.config["base_url"]
        self.output_file = self.config["output_file"]

        # Predefined topics and their keywords
        self.topics_map = {
            "Python": ["Python"],
            "Data Science": ["Data Science", "Data"],
            "R": ["R"],
            "Deep Learning": ["Deep Learning"],
            "NLP": ["NLP", "Natural Language Processing"],
            "Machine Learning": ["Machine Learning", "ML"]
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

    def extract_courses(self, soup):
        """ Extract courses from the page """
        courses = []
        course_sections = soup.find_all("div", class_="wp-block-column")

        for course in course_sections:
            title_elem = course.find("h3")
            title = title_elem.get_text(strip=True) if title_elem else "No Title"

            description_elem = course.find("p")
            description = description_elem.get_text(strip=True) if description_elem else "No Description"

            read_more_elem = course.find("a", string="READ MORE")
            url = read_more_elem["href"] if read_more_elem else "#"

            courses.append({
                "title": title,
                "url": url,
                "description": description
            })

        print(f"Extracted {len(courses)} courses.")
        return courses

    def categorize_courses(self, courses):
        """ Categorize courses based on keywords """
        categorized_data = {topic: [] for topic in self.topics_map.keys()}

        for course in courses:
            title = course["title"].lower()
            description = course["description"].lower()
            categories = set()

            for topic, keywords in self.topics_map.items():
                for keyword in keywords:
                    if keyword.lower() in title or keyword.lower() in description:
                        categories.add(topic)

            # Assign course to multiple categories
            for category in categories:
                categorized_data[category].append({
                    "title": course["title"],
                    "url": course["url"],
                    "description": course["description"],
                    "categories": list(categories)
                })

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
        with open(self.output_file, "w") as file:
            json.dump(data, file, indent=4)
        print(f"Data successfully saved to {self.output_file}")
