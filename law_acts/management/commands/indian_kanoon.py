from django.core.management.base import BaseCommand
from law_acts.models import IndianKanoon
from bs4 import BeautifulSoup
from urllib.parse import urlencode
from time import time
from datetime import datetime
from nyaya_ai.utils import normalize_text, headers, generate_dates
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests import get as getReq

class Command(BaseCommand):
    help = "Scrapes indiankanoon.org for Act and Section details"
    domain = "https://indiankanoon.org"
    links_css = 'div.results_middle div.results-list article.result h4.result_title a'
    updated_headers = headers
    updated_headers.update({"Referer": domain})


    def add_arguments(self, parser):
        parser.add_argument(
            '--max_workers',
            type=int,
            required=True,
            default=20,
            help="Max-Workers to run multiple workers for a domain",
        )

        parser.add_argument(
            '--start_date',
            type=str,
            required=True,
            default='1-1-1947',
            help="start-date to fetch news from start",
        )

        parser.add_argument(
            '--end_date',
            type=str,
            required=True,
            default='today',
            help="end-date to fetch news upto end-date, to fetch news until today pass 'today' .",
        )



    def handle(self, *args, **options):
        start_date = options.get("start_date", "1-1-1947")
        end_date = options.get("end_date", "today")
        max_workers = options.get("max_workers", 30)

        date_range = generate_dates(start_date, end_date)
        futures = []
        doc_types = [
            "laws",
            "judgments",
            "tribunals",
            "supremecourt",
            "scorders",
            "highcourts",
            "supremecourt,scorders",
            "supremecourt,scorders,highcourts",
            "kerala",
            "bihar-section",
            "mh-section",
            "wb-section",
            "union-section",
            "gujarat-section",
            "tn-section",
            "jk-section",
            "mp-section",
            "rajasthan-section",
        ]
        author_ids = [
            "v-ramkumar",
            "p-r-raman",
            "k-k-denesan",
            "m-ramachandran",
            "j-m-james",
            "t-b-radhakrishnan",
            "k-t-sankaran",
            "r-basant",
        ]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            for date in date_range.to_list():
                date_str = date.strftime("%d-%m-%Y")
                for doc_type in doc_types:
                    futures.append(executor.submit(self.fetch_acts, date_str, extra_filters=f"doctypes:{doc_type}"))
                
                    for author_id in author_ids:
                        futures.append(executor.submit(self.fetch_acts, date_str, extra_filters=f"doctypes:{doc_type} authorid:{author_id}"))
                        futures.append(executor.submit(self.fetch_acts, date_str, extra_filters=f"doctypes:{doc_type} benchid:{author_id}"))
                        futures.append(executor.submit(self.fetch_acts, date_str, extra_filters=f"authorid:{author_id}"))
                        futures.append(executor.submit(self.fetch_acts, date_str, extra_filters=f"benchid:{author_id}"))

        for future in as_completed(futures):
            pass


    def fetch_acts(self, date:str, page=0, extra_filters=""):
        params = {
            "formInput": f"fromdate:{date} todate:{date} {extra_filters}",
            "pagenum": page,
        }
        full_url = f"{self.domain}/search/?{urlencode(params)}"
        date_obj = datetime.strptime(date, "%d-%m-%Y").date()
        filters = {"url": full_url, "is_page_url": True}

        indian_kanoon : IndianKanoon = IndianKanoon.objects.filter(**filters).first()
        if not indian_kanoon:
            filters['date'] = date_obj
            indian_kanoon : IndianKanoon = IndianKanoon.objects.create(**filters)

        if indian_kanoon.is_fetched:
            return True

        response = getReq(full_url, headers=self.updated_headers)
        code = response.status_code
        if code != 200:
            self.stdout.write(self.style.ERROR(f"[X] Failed to fetch {full_url}, Status Code: {code}"))
            return False

        soup = BeautifulSoup(response.text, "lxml")
        indian_kanoon.title = soup.select_one('title').get_text()
        indian_kanoon.is_fetched = True
        indian_kanoon.fetched_at = int(time())
        indian_kanoon.save()

        self.stdout.write(self.style.SUCCESS(f"[✓] Fetched {full_url}"))
        links = soup.select(self.links_css)
        for link_tag in links:
            link_href = link_tag.attrs.get("href", None)
            if not link_href:
                continue
            
            link_href = normalize_text(link_href)
            if not link_href.startswith("http"):
                link_href = f"{self.domain}{link_href}"

            title = link_tag.get_text(strip=True)
            if not IndianKanoon.objects.filter(url=link_href).exists():
                IndianKanoon.objects.create(
                    title = title,
                    url = link_href,
                    date = date_obj,
                    is_page_url = False,
                )

        if self.has_next_page(soup):
            self.fetch_acts(date, page + 1)
    

    def has_next_page(self, soup:BeautifulSoup):
        tag = soup.find(lambda t: t.name and t.get_text(strip=True).lower() == "next")
        return bool(tag)