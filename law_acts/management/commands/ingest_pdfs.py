from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from glob import glob
from django.core.management.base import BaseCommand
from law_acts.models import PDFDocument, PDFImage, PDFPage
import fitz
import pytesseract
from PIL import Image
import io
from nyaya_ai.utils import get_traceback
    

class Command(BaseCommand):
    help = "Ingests PDFs from a directory or a single file into the database."
    pdf_files = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--path', type=str, required=True,
            help='Path to a PDF file or a directory containing PDFs.',
        )
        parser.add_argument(
            '--max_workers', type=int, default=30,
            help='Number of workers to use for processing PDFs.'
        )


    def _list_pdf_files(self):
        if not os.path.exists(self.path):
            self.stdout.write(self.style.ERROR(f"The directory {self.path} does not exist."))
            return []
            
        self.pdf_files = glob(os.path.join(self.path, '**', '*.pdf'), recursive=True)
        
        

    def handle(self, *args, **options):
        self.path = options.get('path')
        self.max_workers = options.get('max_workers', 10)

        self._list_pdf_files()
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = [executor.submit(self.process_pdf, pdf_path) for pdf_path in self.pdf_files]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(get_traceback(e))
                    self.stdout.write(self.style.ERROR(f"[X] Error processing {pdf_path}: {e}"))
                    break


    
    def process_pdf(self, file_path):
        filename = os.path.basename(file_path)
        pdf_doc_model, created = PDFDocument.objects.get_or_create(
            file_path=file_path,
            defaults={'original_filename': filename}
        )
        if pdf_doc_model.is_processed:
            self.stdout.write(self.style.WARNING(f"-] PDF {file_path} already processed."))
            return True

        update_fields = []
        doc = fitz.open(file_path)
        total_pages = len(doc)
        pdf_doc_model.total_pages = total_pages
        update_fields.append("total_pages")

        for page_num in range(total_pages):
            page = doc.load_page(page_num)
            new_page = page_num+1

            # Fetched raw text from the page
            raw_text = page.get_text("text")
            pdf_page_model = PDFPage.objects.create(
                pdf=pdf_doc_model,
                page_number=page_num + 1,
                raw_text=raw_text
            )
                
            # Extract and OCR images
            ocr_text = ""
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]

                # Use PIL to open the image for OCR
                image = Image.open(io.BytesIO(image_bytes))
                ocr_text = pytesseract.image_to_string(image)
                
                if ocr_text.strip():
                    ocr_text = f"PAGE:{new_page}\n{ocr_text.strip()}\n"
                    
                PDFImage.objects.create(
                    pdf_page=pdf_page_model,
                    image_index=img_index,
                    ocr_text=ocr_text
                )

            if ocr_text:
                pdf_page_model.ocr_text = ocr_text
                pdf_page_model.save()

        pdf_doc_model.is_processed = True
        update_fields.append("is_processed")
        pdf_doc_model.save(update_fields=update_fields)
        self.stdout.write(self.style.SUCCESS(f"[✓] Successfully processed {file_path}"))
        return True