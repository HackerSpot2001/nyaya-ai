

from django.db import models

class SourceTypes(models.TextChoices):
    ACTS = "ACTS", "Acts / Bare Laws"
    JUDGMENTS = "JUDGMENTS", "Judgments / Cases"
    GAZETTES = "GAZETTES", "Gazettes / Notifications"
    NEWS = "NEWS", "Legal News"
    ARTICLES = "ARTICLES", "Legal Articles"
    BLOGS = "BLOGS", "Legal Blogs"
    OTHERS = "OTHERS", "Other Legal Sources"
    LEGAL_FORMS = "LEGAL_FORMS", "Legal Forms"
    REGULATIONS = "REGULATIONS", "Regulations"
    RULES = "RULES", "Rules"
    POLICIES = "POLICIES", "Policies"
    TREATIES = "TREATIES", "Treaties"
    CONTRACTS = "CONTRACTS", "Contracts / Agreements"
    STANDARDS = "STANDARDS", "Standards"
    MANUALS = "MANUALS", "Manuals / Handbooks"
    RECRUITMENT_NOTICES = "RECRUITMENT_NOTICES", "Recruitment Notices"
    GOVERNMENT_PORTAL = "GOVERNMENT_PORTAL", "Government Portals"