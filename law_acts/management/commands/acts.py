from django.core.management.base import BaseCommand
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests import get as getReq
from bs4 import BeautifulSoup
from nyaya_ai.utils import (
    headers,
    convert_to_english,
    download_pdf,
    normalize_text,
)


class Command(BaseCommand):
    help = "Fetches acts and downloads PDFs"
    domain = "https://www.indiacode.nic.in"
    total_acts = []
    updated_headers = headers
    updated_headers.update({
        "Referer": "https://www.indiacode.nic.in/", 
    })

    def handle(self, *args, **options):
        self.fetch_central_acts()
        self.fetch_repealed_acts()
        self.fetch_spent_acts()
        self.stdout.write(f"Acts data fetched, total acts: {len(self.total_acts)}...")
        self.download_pdfs_multithread()

    def fetch_central_acts(self, count=1000):
        cental_act_url = (
            f"{self.domain}/handle/123456789/1362/browse?type=shorttitle&rpp={count}"
        )
        res = getReq(cental_act_url, allow_redirects=True, headers=self.updated_headers)
        if res.status_code != 200:
            self.stdout.write(f"status: {res.status_code}")
            return

        soup = BeautifulSoup(res.text, "lxml")
        rows = soup.select("tr")
        for tr in rows:
            tds = tr.select("td")
            if len(tds) < 4:
                continue

            pdf_url = f"{self.domain}{tds[3].find('a')['href']}"
            downloadable_urls = []
            pdfpage_res = getReq(pdf_url, headers=self.updated_headers, allow_redirects=True)
            if pdfpage_res.status_code != 200:
                self.stdout.write(self.style.ERROR(f"status: {pdfpage_res.status_code} for {pdf_url}"))
                continue

            pdfpage_soup = BeautifulSoup(pdfpage_res.text, "lxml")
            pdfpage_links = pdfpage_soup.select("a")
            for page_link in pdfpage_links:
                link = page_link.attrs.get("href","#")
                if not link.endswith(".pdf") or link.startswith("#") or link.endswith("userGuide.pdf"):
                    continue

                obj = {
                    "pdf_url": f"{self.domain}{link}",
                    "filename": page_link.get_text(strip=True),
                }
                downloadable_urls.append(obj)


            act_name = tds[2].get_text(strip=True)
            filename = convert_to_english(act_name)
            self.stdout.write(self.style.SUCCESS(f"Fetched PDF-URLs : {downloadable_urls}"))
            self.total_acts.append(
                {
                    "metadata": {
                        "Enactment Date": tds[0].get_text(strip=True),
                        "Act Number": tds[1].get_text(strip=True),
                        "Short Title": act_name,
                        "View": pdf_url,
                    },
                    "pdf_urls": downloadable_urls,
                    "save_dir": "resources/pdfs/central_acts/",
                }
            )

        self.stdout.write(
            f"Central-Acts data fetched, total acts: {len(rows)}..."
        )


    def fetch_repealed_acts(self):
        url = f"{self.domain}/repealed-act/repealed-act.jsp"
        res = getReq(url, headers=self.updated_headers, allow_redirects=True)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "lxml")
        rows = soup.find_all("tr")
        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) < 4:
                continue

            act_name = convert_to_english(tds[1].get_text(strip=True))
            obj = {
                "metadata": {
                    "Sno": tds[0].get_text(strip=True),
                    "Act Name": act_name,
                    "Year": tds[2].get_text(strip=True),
                },
                "pdf_urls" : [
                    {
                        "pdf_url": f"{self.domain}{tds[3].find('a')['href']}",
                        "filename": act_name,
                    }
                ],
                "save_dir": "resources/pdfs/repealed_acts/",
            }
            self.total_acts.append(obj)
            self.stdout.write(self.style.SUCCESS(f"Fetched PDF-URLs : {obj['pdf_urls']}"))

        self.stdout.write(
            f"Repealed-Acts data fetched, total acts: {len(rows)}..."
        )

    def fetch_spent_acts(self):
        url = f"{self.domain}/spent-act/spent-act.jsp"
        res = getReq(url, headers=self.updated_headers, allow_redirects=True)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "lxml")
        rows = soup.find_all("tr")
        for tr in rows:
            tds = tr.find_all("td")
            if len(tds) < 4:
                continue

            act_name = convert_to_english(tds[1].get_text(strip=True))
            obj = {
                "metadata": {
                    "Sno": tds[0].get_text(strip=True),
                    "Act Name": act_name,
                    "Year": tds[2].get_text(strip=True),
                },
                "pdf_urls" : [
                    {
                        "pdf_url": f"{self.domain}{tds[3].find('a')['href']}",
                        "filename": act_name,
                    }
                ],
                "save_dir": "resources/pdfs/spent_acts/",
            }
            self.total_acts.append(obj)
            self.stdout.write(self.style.SUCCESS(f"Fetched PDF-URLs : {obj['pdf_urls']}"))

        self.stdout.write(
            f"Spent-Acts data fetched, total acts: {len(rows)}..."
        )

    def download_pdfs_multithread(self):
        for act in self.total_acts:
            for pdf in act['pdf_urls']:
                data = {
                    "pdf_url": normalize_text(pdf['pdf_url']),
                    "filename": normalize_text(pdf['filename']),
                    "updated_headers": self.updated_headers,
                    "save_dir": normalize_text(act['save_dir']),
                }
                self.stdout.write(self.style.SUCCESS(f"Downloaded PDF \t {data['pdf_url']}"))
                download_pdf(data)