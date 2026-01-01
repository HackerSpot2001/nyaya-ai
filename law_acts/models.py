from django.db import models
from django.utils import timezone
from pgvector.django import VectorField


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class Source(BaseModel):
    SOURCE_TYPES = [
        ('ACTS', 'Acts / Bare Laws'),
        ('JUDGMENTS', 'Judgments / Cases'),
        ('GAZETTES', 'Gazettes / Notifications'),
        ('NEWS', 'Legal News'),
        ('ARTICLES', 'Legal Articles'),
        ('BLOGS', 'Legal Blogs'),
        ('OTHERS', 'Other Legal Sources'),
        ('LEGAL_FORMS', 'Legal Forms'),
        ('REGULATIONS', 'Regulations'),
        ('RULES', 'Rules'),
        ('POLICIES', 'Policies'),
        ('TREATIES', 'Treaties'),
        ('CONTRACTS', 'Contracts / Agreements'),
        ('STANDARDS', 'Standards'),
        ('MANUALS', 'Manuals / Handbooks'),
        ('RECRUITMENT_NOTICES', 'Recruitment Notices'),
        ('GOVERNMENT_PORTAL', 'Government Portals'),
    ]
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    base_url = models.URLField(blank=True, null=True)
    source_type = models.CharField(choices=SOURCE_TYPES, default='ACTS', max_length=20)
    license_info = models.JSONField(blank=True, default=dict)
    last_crawled_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Source"
        verbose_name_plural = "Sources"
        db_table = "law_sources"

class Document(BaseModel):
    id = models.AutoField(primary_key=True)
    source = models.ForeignKey(Source, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=500)
    doc_id = models.CharField(blank=True, max_length=100, null=True, unique=True)
    document_urls = models.JSONField(blank=True, default=list, null=True)
    metadata = models.JSONField(blank=True, default=dict, null=True)
    response = models.TextField(blank=True, null=True)
    is_url_external = models.BooleanField(default=False)
    saved_metadata = models.JSONField(blank=True, default=dict, null=True)
    doc_content = models.TextField(blank=True, null=True)
    content_type = models.CharField(blank=True, max_length=50, null=True)

    class Meta:
        verbose_name = "Document"
        verbose_name_plural = "Documents"
        db_table = "documents"

class Act(BaseModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, unique=True)
    metadata = models.JSONField(blank=True, default=dict)
    pdf_urls = models.JSONField(default=list)
    is_pdf_fetched = models.BooleanField(default=False)
    pdf_fetched_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        verbose_name = "Act"
        verbose_name_plural = "Acts"
        db_table = "law_acts"

class IndianKanoon(BaseModel):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    url = models.URLField(unique=True)
    date = models.DateField(null=True)
    content = models.TextField(null=True)
    is_page_url = models.BooleanField(default=False)
    is_fetched = models.BooleanField(default=False)
    fetched_at = models.IntegerField(null=True)

    class Meta:
        verbose_name = "IndianKanoon"
        verbose_name_plural = "IndianKanoon"
        db_table = "indian_kanoon"
        indexes = [
            models.Index(fields=['url', 'is_page_url'], name='ik_url_is_page_url_idx'),
        ]


# --- New Models for PDF Ingestion and RAG ---
class PDFDocument(BaseModel):
    """Represents a PDF file saved in the system."""
    file_path = models.CharField(max_length=1024, unique=True)
    original_filename = models.CharField(max_length=512)
    total_pages = models.IntegerField(default=0)
    is_processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = "pdf_documents"


class PDFPage(BaseModel):
    """Extracted text per page from a PDF."""
    pdf = models.ForeignKey(PDFDocument, on_delete=models.CASCADE, related_name='pages')
    page_number = models.IntegerField()
    raw_text = models.TextField(blank=True, null=True)
    ocr_text = models.TextField(blank=True, null=True) # Text from images via OCR
    
    class Meta:
        db_table = "pdf_pages"
        unique_together = ('pdf', 'page_number')


class PDFImage(BaseModel):
    """Metadata for images found within PDF pages."""
    pdf_page = models.ForeignKey(PDFPage, on_delete=models.CASCADE, related_name='images')
    image_index = models.IntegerField()
    ocr_text = models.TextField(blank=True, null=True)
    image_path = models.CharField(max_length=1024, blank=True, null=True)
    
    class Meta:
        db_table = "pdf_images"


class TextChunk(BaseModel):
    """Chunked text for RAG."""
    pdf_page = models.ForeignKey(PDFPage, on_delete=models.CASCADE, related_name='chunks')
    chunk_text = models.TextField()
    vector_embedding = VectorField(dimensions=384, null=True)
    chunk_index = models.IntegerField()
    
    class Meta:
        db_table = "text_chunks"
