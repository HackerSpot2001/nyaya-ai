from datetime import datetime
from json import dumps

from django.core.management.base import BaseCommand
from requests import get as getReq

from law_acts.choices import SourceTypes
from law_acts.models import Document, Source
from nyaya_ai.utils import headers
from concurrent.futures import ThreadPoolExecutor
from nyaya_ai.utils import download_pdf



class Command(BaseCommand):
    help = "Download PDFs from legislative.gov.in"
    default_base_url = "https://www.legislative.gov.in"
    current_date = datetime.now().strftime("%Y-%m-%d")
    taxonomy_categories = []
    updated_headers = headers
    updated_headers.update({
        "Referer": "https://www.legislative.gov.in/",
    })
    posts = []

    def handle(self, *args, **options):
        # Fetch Directories
        self.fetch_directory_posts()
        self.fetch_taxonomy_categories("documents_category")
        self.fetch_taxonomy_categories("schemes_services_category")
        self.fetch_taxonomy_categories("vacancy_category")
        self.fetch_taxonomy_categories("tender_category")
        self.fetch_taxonomy_categories("initiative_category")
        self.fetch_all_posts()
        for post in self.posts:
            self.fetch_post(post)

        self.stdout.write(self.style.SUCCESS(f"Total posts fetched: {len(self.posts)}"))
        self.download_pdfs()

    def fetch_directory_posts(
        self, count=1000, page=1, order="menu_order", path="directory_post"
    ):
        url = f"{self.default_base_url}/cms/wp-json/post-page/{path}?limit={count}&page={page}&orderby={order}"
        res = getReq(url, headers=self.updated_headers)
        if res.status_code != 200:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to fetch posts for category {path}. Status: {res.status_code}"
                )
            )
            return

        data = res.json()
        posts = data.get("posts", [])
        source_args = {
            "name": "LEGISLATIVE_DIRECTORY_POST",
            "source_type": SourceTypes.GOVERNMENT_PORTAL,
            "base_url": self.default_base_url,
        }

        source = Source.objects.filter(**source_args).first()
        if not source:
            source = Source.objects.create(**source_args)

        self.stdout.write(
            self.style.SUCCESS(f"Fetched posts:{len(posts)} for {path}?page={page},")
        )

        for post in posts:
            post["category_type"] = path
            post_id = post.get("ID")
            doc_id = f"LEGISLATIVE-DIRECTORY-POST-{post_id}"
            if not Document.objects.filter(doc_id=doc_id).exists():
                Document.objects.create(
                    title=post.get("post_title", ""),
                    doc_id=doc_id,
                    document_urls=None,
                    source_id=source.id,
                    response=dumps(post),
                )

        if len(posts) == count:
            self.fetch_directory_posts(count, page + 1, order, path)

    def fetch_taxonomy_categories(self, category_type):
        url = f"{self.default_base_url}/cms/wp-json/taxonomy/{category_type}"
        res = getReq(url, headers=self.updated_headers)
        if res.status_code != 200:
            print(f"Failed to fetch categories. Status: {res.status_code}")
            return

        sub_categories = res.json()
        self.taxonomy_categories += sub_categories.get(category_type, [])
        self.stdout.write(
            self.style.SUCCESS(
                f"Fetched {len(sub_categories.get(category_type, []))} sub-categories for '{category_type}'"
            )
        )

    def fetch_document_posts(self, subcategory, category_type, page=1, count=1000):
        category_slug = subcategory.get("slug")
        if not category_slug:
            return

        url = f"{self.default_base_url}/cms/wp-json/document/documents?document_category={category_slug}&limit={count}&page={page}&sort=acf&order=DESC&search="
        res = getReq(url, headers=self.updated_headers)
        if res.status_code != 200:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to fetch posts for category {category_slug}. Status: {res.status_code}"
                )
            )
            return

        data = res.json()
        posts = data.get("posts", [])
        if not posts:
            return

        for post in posts:
            post["category_type"] = category_type
            self.posts.append(post)

        if len(posts) == count:
            self.fetch_document_posts(
                subcategory, category_type, page=page + 1, count=count
            )

        # self.stdout.write(self.style.SUCCESS(f"Fetched {len(posts)} posts from category '{category_slug}', page {page}"))

    def fetch_post_pages(
        self,
        subcategory,
        post_page_source="schemes_and_services",
        category_type="",
        page=1,
        count=1000,
        order_by="menu_order",
    ):
        category_slug = subcategory.get("slug")
        if not category_slug:
            return

        url = f"{self.default_base_url}/cms/wp-json/post-page/{post_page_source}?limit={count}&page={page}&orderby={order_by}"
        res = getReq(url, headers=self.updated_headers)
        if res.status_code != 200:
            self.stdout.write(
                self.style.ERROR(
                    f"Failed to fetch posts for category {category_slug}. Status: {res.status_code}"
                )
            )
            return

        data = res.json()
        posts = data.get("posts", [])
        if not posts:
            return

        for post in posts:
            post["category_type"] = category_type
            self.posts.append(post)

        if len(posts) == count:
            self.fetch_post_pages(
                subcategory, post_page_source, page + 1, count, order_by
            )

        # self.stdout.write(self.style.SUCCESS(f"Fetched {len(posts)} posts from category '{category_slug}', page {page}"))

    def fetch_all_posts(self):
        for subcategory in self.taxonomy_categories:
            cat_type = subcategory.get("taxonomy", "")
            self.stdout.write(
                self.style.SUCCESS(
                    f"fetching posts for name: {subcategory.get('slug')} , category_type: '{cat_type}' "
                )
            )
            if cat_type == "documents_category":
                self.fetch_document_posts(subcategory, cat_type)

            if cat_type == "schemes_services_category":
                self.fetch_post_pages(
                    subcategory, "schemes_and_services", cat_type, order_by="menu_order"
                )

            if cat_type == "vacancy_category":
                self.fetch_post_pages(
                    subcategory, "careers_post", cat_type, order_by="DESC"
                )

            if cat_type == "tender_category":
                self.fetch_post_pages(
                    subcategory, "tenders_post", cat_type, order_by="DESC"
                )

            if cat_type == "initiative_category":
                self.fetch_post_pages(subcategory, "initiatives", cat_type, order_by="")

    def fetch_post(self, post_obj: dict):
        post_id = post_obj.get("ID")
        post_id = post_obj.get("acf_data", {}).get("post_id", post_id)
        if not post_id:
            return None

        post_data = {"post_obj": post_obj}
        file_objs = post_obj.get("acf_data", {}).get("file", [])
        fileids = []
        for file_obj in file_objs:
            if isinstance(file_obj, int):
                fileids.append(str(file_obj))

            if isinstance(file_obj, dict) and isinstance(
                file_obj.get("file", []), list
            ):
                for id_ in file_obj.get("file", []):
                    fileids.append(str(id_))

        pdf_urls = []
        if len(fileids) > 0:
            file_url = f"{self.default_base_url}/cms/wp-json/post-page/post?id={','.join(fileids)}"
            res = getReq(file_url, headers=self.updated_headers)
            if res.status_code != 200:
                self.stdout.write(
                    self.style.ERROR(
                        f"Failed to fetch file for post ID {post_id}. Status: {res.status_code}"
                    )
                )

                return None

            data = res.json()
            posts = data.get("posts", [])
            post_data["file_obj"] = posts
            if not posts:
                return None

            if isinstance(posts, list):
                for post_tmp in posts:
                    pdf_url = (
                        post_tmp.get("acf_data", {}).get("pdf", {}).get("url", None)
                    )
                    if pdf_url:
                        pdf_urls.append(pdf_url)

            if isinstance(posts, dict):
                pdf_url = posts.get("acf_data", {}).get("pdf", {}).get("url", None)
                if pdf_url:
                    pdf_urls.append(pdf_url)

        source_args = {
            "name": "LEGISLATIVE_DOCUMENTS_POST",
            "source_type": SourceTypes.GOVERNMENT_PORTAL,
            "base_url": self.default_base_url,
        }
        source = Source.objects.filter(**source_args).first()
        if not source:
            source = Source.objects.create(**source_args)

        doc_id = f"LEGISLATIVE-DOCUMENT-POST-{post_id}"

        if not Document.objects.filter(doc_id=doc_id).exists():
            Document.objects.create(
                title=post_obj.get("post_title", ""),
                doc_id=doc_id,
                source_id=source.id,
                document_urls=pdf_urls,
                response=dumps(post_data),
                content_type="PDF" if pdf_urls else None,
            )

    def download_pdfs(self):
        qs = Document.objects.filter(document_urls__isnull=False)
        pdf_urls = []
        for doc in qs:
            pdf_urls.append(
                {
                    "urls": doc.document_urls,
                    "save_dir": "resources/legislative_docs/",
                    "filename": doc.title,
                }
            )

        count = 0
        total = 0
        with ThreadPoolExecutor(max_workers=20) as executor:
            for pdf_obj in pdf_urls:
                urls = pdf_obj.get("urls")
                save_dir = pdf_obj.get("save_dir")
                filename = pdf_obj.get("filename")
                count += 1
                total += len(urls)
                for url in urls:
                    item = {
                        "pdf_url": url,
                        "save_dir": save_dir,
                        "filename": filename,
                        "formatter": f"PDF-DOWNLOADER-{count}/{total}",
                        "updated_headers": self.updated_headers,
                    }
                    executor.submit(download_pdf, item)
