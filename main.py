from flask import Flask, redirect, render_template, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

"""
Do this when scraping a website to avoid getting blocked.

headers = {
      'User-Agent':
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
      'Accept':
      'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
      'Accept-Language': 'en-US,en;q=0.5',
}

response = requests.get(URL, headers=headers)
"""


class set_site_urls:
    """Set Search URLs"""

    def __init__(self, keyword):
        self.keyword = keyword

    # 작동하지 않음
    # def set_site_berlin(self):
    #     return f"https://berlinstartupjobs.com/skill-areas/{self.keyword}/"

    def set_site_web3(self):
        return f"https://web3.career/{self.keyword}-jobs"

    def set_site_wework(self):
        return f"https://weworkremotely.com/remote-jobs/search?utf8=%E2%9C%93&term={self.keyword}"

    def set_list(self):
        list = []
        # list.append(self.set_site_berlin())
        list.append(self.set_site_web3())
        list.append(self.set_site_wework())

        return list


class scrape_site:
    """Scrape Site from URL"""

    def __init__(self, url):
        self.url = url

    def parse_html(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        response = requests.get(self.url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        return soup

    def scrape_web3(self):
        print(f"Scrapping {self.url}...")
        job_data = []
        soup = self.parse_html()
        job_table = soup.find("table", class_="table")
        if job_table == None:
            return []
        jobs = job_table.find_all("tr", class_="table_row")
        for job in jobs:
            title = job.find("h2")
            if title == None:
                continue
            url = job.find("div", class_="job-title-mobile").find("a")["href"]
            company = job.find("h3")
            desc = (
                job.find("span", class_="my-badge").find("a")
                if job.find("span", class_="my-badge")
                else ""
            )
            job_data.append(
                {
                    "title": title.text.strip(),
                    "url": f"https://web3.career{url}",
                    "company": company.text.strip(),
                    "desc": desc.text.strip() if desc else "",
                }
            )

        return job_data

    def scrape_wework(self):
        print(f"Scrapping {self.url}...")
        job_data = []
        soup = self.parse_html()
        jobs = soup.find_all("li", class_="new-listing-container")
        if jobs == None:
            return []
        for job in jobs:
            title = job.find("h3", class_="new-listing__header__title")
            url = job.find("a", class_="listing-link--unlocked")["href"]
            company = job.find("p", class_="new-listing__company-name")
            desc = job.find("p", class_="new-listing__company-headquarters")
            job_data.append(
                {
                    "title": title.text.strip(),
                    "url": f"https://weworkremotely.com{url}",
                    "company": company.text.strip(),
                    "desc": desc.text.strip(),
                }
            )

        return job_data


job_list = []


def scrape_all(keyword):
    sites = set_site_urls(keyword).set_list()

    job_list.extend(scrape_site(sites[0]).scrape_web3())
    job_list.extend(scrape_site(sites[1]).scrape_wework())

    return job_list


db_keywords = {}


@app.route("/")
def root_page():
    return render_template("home.html")


@app.route("/search")
def search_page():
    keyword = request.args.get("keyword")
    if keyword == None or keyword == "":
        return redirect("/")
    db = scrape_all(keyword)
    return render_template("search.html", keyword=keyword, db=db)


if __name__ == "__main__":
    app.run()
