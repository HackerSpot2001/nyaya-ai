from concurrent.futures import ThreadPoolExecutor, as_completed
from django.core.management.base import BaseCommand
from requests import get as getReq
from nyaya_ai.utils import headers, download_pdf, sanitize_and_shorten
from bs4 import BeautifulSoup
from law_acts.models import Document, Source

class Command(BaseCommand):
    help = 'LawMin Docs'
    domain = 'https://lawmin.gov.in'
    updated_headers = headers
    updated_headers.update({'Referer': domain})
    pdf_urls = []
    save_dir = 'resources/pdfs/lawmin/'
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Successfully executed LawMin'))
        # self.fetch_speech()
        # self.fetch_annual_reports()
        # self.fetch_demand_grants()
        # self.fetch_budgets()
        # self.fetch_electoral_reforms()
        # self.fetch_archived_notifications()
        # self.save_documents()
        self.download_pdfs()

    def save_documents(self):
        source = Source.objects.filter(name='lawmin_documents').first()
        if not source:
            source = Source.objects.create(
                name='lawmin_documents',
                base_url='https://lawmin.gov.in',
                source_type='GOVERNMENT_PORTAL',
            )

        for pdf_url in self.pdf_urls:
            doc_id = sanitize_and_shorten(pdf_url['title'],80)
            if not Document.objects.filter(doc_id=doc_id).exists():
                Document.objects.create(
                    doc_id = doc_id,
                    document_urls = [pdf_url],
                    source_id = source.id,
                )

            self.stdout.write(self.style.SUCCESS(f'Successfully saved {pdf_url["pdf_url"]}'))

    def fetch_archived_notifications(self):
        res = getReq(f'{self.domain}/archives-notification', headers=self.updated_headers)
        if res.status_code != 200:
            self.stdout.write(self.style.ERROR('Failed to fetch archived notifications'))
            return

        soup = BeautifulSoup(res.text, 'lxml')
        tr_tags = soup.select('table tbody tr')
        for tr_tag in tr_tags:
            tds = tr_tag.select('td')
            title = tds[0].get_text(strip=True)
            link = tds[1].select_one('a').attrs['href']
            obj = {
                "title": title,
                "pdf_url": link,
            }
            self.pdf_urls.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Successfully fetched archived_notification {obj["pdf_url"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully fetched archived notifications'))


    def fetch_demand_grants(self, page=0):
        res = getReq(f'{self.domain}/documents/demand-for-grants?page={page}', headers=self.updated_headers)
        if res.status_code != 200:
            self.stdout.write(self.style.ERROR('Failed to fetch demand grants'))
            return

        soup = BeautifulSoup(res.text, 'lxml')
        tr_tags = soup.select('table tbody tr')
        for tr_tag in tr_tags:
            tds = tr_tag.select('td')
            link = tds[2].select_one('a').attrs['href']
            obj = {
                "title": tds[1].get_text(strip=True),
                "pdf_url": link,
            }
            self.pdf_urls.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Successfully fetched demand grant {obj["pdf_url"]}'))
        if tr_tags.__len__() > 0:
            self.fetch_demand_grants(page + 1)
        else:
            self.stdout.write(self.style.SUCCESS('Successfully fetched demand grants'))
            

    def fetch_speech(self, page=0):
        res = getReq(f'{self.domain}/speeches-of-ministers?page={page}', headers=self.updated_headers)
        if res.status_code != 200:
            self.stdout.write(self.style.ERROR('Failed to fetch speeches'))
            return

        soup = BeautifulSoup(res.text, 'lxml')
        tr_tags = soup.select('table tbody tr')
        for tr_tag in tr_tags:
            tds = tr_tag.select('td')
            title = tds[0].get_text(strip=True)
            link = tds[1].select_one('a').attrs['href']
            obj = {
                "title": title,
                "pdf_url": link,
            }
            self.pdf_urls.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Successfully fetched speech {obj["pdf_url"]}'))
        if tr_tags.__len__() > 0:
            self.fetch_speech(page + 1)
        else:
            self.stdout.write(self.style.SUCCESS('Successfully fetched speeches'))
            


        
    def fetch_annual_reports(self):
        res = getReq(f'{self.domain}/documents/annualreports', headers=self.updated_headers)
        if res.status_code != 200:
            self.stdout.write(self.style.ERROR('Failed to fetch annual reports'))
            return

        soup = BeautifulSoup(res.text, 'lxml')
        tr_tags = soup.select('table tbody tr')
        for tr_tag in tr_tags:
            tds = tr_tag.select('td')
            link = tds[2].select_one('a').attrs['href']
            obj = {
                "title": tds[1].get_text(strip=True),
                "pdf_url": link,
            }
            self.pdf_urls.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Successfully fetched annual report {obj["pdf_url"]}'))
        self.stdout.write(self.style.SUCCESS('Successfully fetched annual reports'))



        
    def fetch_budgets(self):
        res = getReq(f'{self.domain}/documents/outcomebudgets', headers=self.updated_headers)
        if res.status_code != 200:
            self.stdout.write(self.style.ERROR('Failed to fetch budgets'))
            return

        soup = BeautifulSoup(res.text, 'lxml')
        tr_tags = soup.select('table tbody tr')
        for tr_tag in tr_tags:
            tds = tr_tag.select('td')
            link = tds[2].select_one('a').attrs['href']
            obj = {
                "title": tds[1].get_text(strip=True),
                "pdf_url": link,
            }
            self.pdf_urls.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Successfully fetched budget {obj["pdf_url"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully fetched budgets'))



    def fetch_electoral_reforms(self):
        res = getReq(f'{self.domain}/documents/electoralreforms', headers=self.updated_headers)
        if res.status_code != 200:
            self.stdout.write(self.style.ERROR('Failed to fetch electoral reforms'))
            return

        soup = BeautifulSoup(res.text, 'lxml')
        tr_tags = soup.select('table tbody tr')
        for tr_tag in tr_tags:
            tds = tr_tag.select('td')
            link = tds[2].select_one('a').attrs['href']
            obj = {
                "title": tds[1].get_text(strip=True),
                "pdf_url": link,
            }
            self.pdf_urls.append(obj)
            self.stdout.write(self.style.SUCCESS(f'Successfully fetched electoral reform {obj["pdf_url"]}'))

        self.stdout.write(self.style.SUCCESS('Successfully fetched electoral reforms'))



    def download_pdfs(self):
        self.stdout.write(self.style.SUCCESS("Downloading PDFs..."))
        qs = Document.objects.filter(source__name="lawmin_documents", document_urls__isnull=False)
        futures = []
        with ThreadPoolExecutor(max_workers=20) as executor:
            for obj in qs.all():
                pdf_url = obj.document_urls[0]['pdf_url']
                filename = sanitize_and_shorten(obj.document_urls[0]['title'])
                item = {
                    "pdf_url": pdf_url,
                    "save_dir": self.save_dir,
                    "filename": filename,
                    "updated_headers": self.updated_headers,
                }
                futures.append(executor.submit(download_pdf, item))


            for future in as_completed(futures):
                pass
                # self.stdout.write(self.style.SUCCESS(f"Successfully downloaded PDF {future.result()}"))