from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
import time
import re

class GoogleMapsExtractor:
    def __init__(self):
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        self.driver = webdriver.Chrome(options=options)
        self.wait = WebDriverWait(self.driver, 10)
    
    def extract_data(self, url):
        self.driver.get(url)
        time.sleep(3)  
        
        data = {
            'name': self.get_name(),
            'address': self.get_address(),
            'contact': self.get_contact(),
            'website': self.get_website(),
            'reviews': self.get_reviews(),
            'images': self.get_images(),
            'coordinates': self.get_coordinates(),
            'rating': self.get_rating()
        }
        return data
    
    def get_name(self):
        try:
            return self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "h1.fontHeadlineLarge")
            )).text
        except:
            return None

    def get_address(self):
        try:
            address_button = self.wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'button[data-item-id*="address"]')
            ))
            return address_button.text
        except:
            return None

    def get_contact(self):
        try:
            phone_button = self.driver.find_element(By.CSS_SELECTOR, 'button[data-item-id*="phone:tel:"]')
            return phone_button.text
        except:
            return None

    def get_website(self):
        try:
            website_link = self.driver.find_element(By.CSS_SELECTOR, 'a[data-item-id*="authority"]')
            return website_link.get_attribute('href')
        except:
            return None

    def get_reviews(self):
        reviews = []
        try:
            # Click on reviews to load them
            reviews_button = self.driver.find_element(By.CSS_SELECTOR, 'button[jsaction*="pane.rating.moreReviews"]')
            reviews_button.click()
            time.sleep(2)

            # Extract first 5 reviews
            review_elements = self.driver.find_elements(By.CSS_SELECTOR, 'div.jJc9Ad')[:5]
            for review in review_elements:
                try:
                    review_text = review.find_element(By.CSS_SELECTOR, 'span.wiI7pd').text
                    review_rating = len(review.find_elements(By.CSS_SELECTOR, 'img[src*="star_"]'))
                    reviews.append({
                        'text': review_text,
                        'rating': review_rating
                    })
                except:
                    continue
        except:
            pass
        return reviews

    def get_images(self):
        try:
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, 'img[src*="photo"]')
            return [img.get_attribute('src') for img in image_elements[:5]]  # Get first 5 images
        except:
            return []

    def get_coordinates(self):
        try:
            url = self.driver.current_url
            coords = re.findall(r'@(-?\d+\.\d+),(-?\d+\.\d+)', url)
            if coords:
                return {'latitude': coords[0][0], 'longitude': coords[0][1]}
        except:
            return None

    def get_rating(self):
        try:
            rating_element = self.driver.find_element(By.CSS_SELECTOR, 'div.F7nice span')
            return float(rating_element.text.split()[0])
        except:
            return None

    def save_to_json(self, data, filename='location_data.json'):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def close(self):
        self.driver.quit()

def main():
    url = "https://www.google.com/maps/place/Broadway+Pizza+-+Valencia+Town/@31.4087299,74.2603858,17z/data=!3m1!4b1!4m6!3m5!1s0x391901ab56cefab9:0x8f5bd27e31eaf234!8m2!3d31.4087299!4d74.2603858!16s%2Fg%2F11llcyvhcv!5m1!1e1"
    extractor = GoogleMapsExtractor()
    
    try:
        data = extractor.extract_data(url)
        extractor.save_to_json(data)
        print("Data extracted successfully!")
    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        extractor.close()

if __name__ == "__main__":
    main()