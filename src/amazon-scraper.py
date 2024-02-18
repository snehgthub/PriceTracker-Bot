import os
import re
import json
import time
import requests
from dotenv import load_dotenv
from termcolor import colored


class AmazonScraper:

    def __init__(self):
        # Load environment variables from .env file
        load_dotenv()

        # Load API key from environment variables
        self.api_key = os.getenv("APIKEY")

        # List of domain names associated with Amazon
        self.domain_names = ["amazon", "amzn"]

        # URL for the scraper API
        self.scraper_url = "https://api.scraperapi.com/structured/amazon/product"

    def get_domain(self, url: str) -> str:
        try:
            # Extract domain name from URL
            domain_name = url.split("/")[2][::-1].split(".")[1][::-1]

            if domain_name in self.domain_names:
                return domain_name
            else:
                raise ValueError("The domain name is not valid.")

        # Raise error when exception occurs while trying to extract domain name from URL
        except IndexError:
            raise ValueError("Please enter a valid URL with a domain name.")

        except Exception as e:
            raise ValueError(f"{e}")

    def extract_asin(self, url: str) -> str:
        # Regular expression pattern to extract ASIN from URL
        asin_pattern = r"/([A-Z0-9]{10})(?:[/?]|$)"

        # Search for ASIN pattern in URL
        match = re.search(asin_pattern, url)

        if match:
            return match.group(1)
        else:
            return None

    def fetch_product_asin(self, url: str, domain_name: str) -> str:
        if domain_name == self.domain_names[0]:
            # If domain is "amazon", directly extract ASIN from URL
            product_asin = self.extract_asin(url)

        elif domain_name == self.domain_names[1]:
            # If domain is "amzn", follow redirects to actual Amazon URL and then extract ASIN
            response = requests.get(url, allow_redirects=True)
            product_asin = self.extract_asin(response.url)

        return product_asin

    def fetch_product_image(self, imageUrl: str) -> str:
        try:
            response = requests.get(imageUrl)

            if response.status_code == 200:
                with open("static/images/Amazon/image.jpg", "wb") as f:
                    f.write(response.content)
            else:
                print(f"Failed to fetch image. Status code: {response.status_code}")

        except Exception as e:
            print(f"An error occurred while fetching the image: {e}")

    def fetch_product_data(self, payload: dict) -> str:
        try:
            # Send request to scraper API with payload
            response = requests.get(self.scraper_url, params=payload)
            response.raise_for_status()  # Raise HTTPError for status codes 4xx or 5xx

            data = json.loads(response.text)

            product_name = data.get("name")
            product_price = data.get("pricing")
            product_image_url = data.get("images")[0]

            if product_name and product_price and product_image_url:
                print(
                    colored("\nProduct Name: ", "yellow")
                    + colored(f"{product_name}", "cyan")
                )
                print(
                    colored("Product Price: ", "yellow")
                    + colored(f"{product_price}\n", "cyan")
                )
                self.fetch_product_image(product_image_url)

            else:
                print("Incomplete data received from the Scraper API")

        except requests.exceptions.RequestException as e:
            print(f"Error occurred while making the request to the Scraper API: {e}")

        except (KeyError, json.JSONDecodeError) as e:
            print(
                f"Error occurred while parsing the response from the Scraper API: {e}"
            )

        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def main():
    # Create object of AmazonScraper class
    scraper = AmazonScraper()

    try:
        # Get target product URL from user
        targetUrl = input(
            colored("\nEnter the URL of the product to track it's price: ", "yellow")
        )

        print(time.strftime("%X"))
        # Determine domain from URL
        domain_name = scraper.get_domain(targetUrl)

        if domain_name:
            # Fetch ASIN of the product
            product_asin = scraper.fetch_product_asin(targetUrl, domain_name)

            if product_asin:
                # Prepare payload for fetching product data
                payload = {
                    "api_key": scraper.api_key,
                    "asin": product_asin,
                    "country": "in",
                    "tld": "in",
                    "autoparse": "true",
                }
                # Fetch product data using payload
                scraper.fetch_product_data(payload)
            else:
                print(
                    colored("Error: ", "red") + "Failed to extract ASIN from given URL"
                )
        else:
            print(
                colored("Error: ", "red")
                + "Failed to determine domain from provided URL"
            )

    except ValueError as ve:
        print(colored("Error: ", "red") + f"{ve}")

    except Exception as e:
        print(colored("Error: ", "red") + f"{e}")

    print(time.strftime("%X"))

# Entry point of the script
if __name__ == "__main__":
    main()
