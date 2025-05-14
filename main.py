import os
from scraper.extractor import CourseExtractor

def main():
    config_path = "config/config.json"

    if not os.path.exists(config_path):
        print(f"Configuration file not found at {config_path}")
        return

    extractor = CourseExtractor(config_path)
    extractor.extract_all()

if __name__ == "__main__":
    main()
