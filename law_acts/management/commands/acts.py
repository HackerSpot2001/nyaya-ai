from django.core.management.base import BaseCommand
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests import get as getReq
from bs4 import BeautifulSoup
from nyaya_ai.utils import (
    headers,
    convert_to_english,
    download_pdf,
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
            if len(tds) >= 4:
                pdf_url = f"https://www.indiacode.nic.in{tds[3].find('a')['href']}"
                act_name = tds[2].get_text(strip=True)
                filename = convert_to_english(act_name)
                self.total_acts.append(
                    {
                        "metadata": {
                            "Enactment Date": tds[0].get_text(strip=True),
                            "Act Number": tds[1].get_text(strip=True),
                            "Short Title": act_name,
                            "View": pdf_url,
                        },
                        "filename": filename,
                        "pdf_url": pdf_url,
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
                "pdf_url": f"{self.domain}{tds[3].find('a')['href']}",
                "filename": act_name,
                "save_dir": "resources/pdfs/repealed_acts/",
            }
            self.total_acts.append(obj)

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
                "pdf_url": f"{self.domain}{tds[3].find('a')['href']}",
                "filename": act_name,
                "save_dir": "resources/pdfs/spent_acts/",
            }
            self.total_acts.append(obj)

        self.stdout.write(
            f"Spent-Acts data fetched, total acts: {len(rows)}..."
        )

    def download_pdfs_multithread(self, max_workers=20):
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for act in self.total_acts:
                act["updated_headers"] = self.updated_headers
                futures.append(executor.submit(download_pdf, act))

            for future in as_completed(futures):
                try:
                    save_path = future.result()
                    self.stdout.write(f"✔ Downloaded: {save_path}")
                except Exception as e:
                    self.stdout.write(f"❌ Error downloading {str(e)}")

