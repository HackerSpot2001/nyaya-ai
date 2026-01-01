Here are **all possible ways** you can get information for your project **LegalFinderAI**, including **old case laws, all Acts, laws for every field**, and structured data sources. I’ve also included **categories, APIs, databases, and scrapers** you can plug directly into your system.

---

# ✅ **1. Sources for Old Case Information (Judgments, Orders, Case History)**

### **A. Official Government Sources (100% Legal & Free)**

These are the most reliable and legally safe sources.

#### **1. eCourts / ECIS**

* District & state court cases (civil + criminal)
* Case number, party name, FIR info, hearing dates
* URL structure, captchas involved
* Can scrape with Puppeteer/Playwright + anti-captcha

#### **2. Supreme Court of India — SCI**

* Judgments, daily orders, cause lists
* API-like structure in JSON (undocumented)
* You can index by:

  * Bench
  * Subject
  * Citation
  * Year

#### **3. High Courts Websites**

Each High Court maintains its own database:

* Judgments PDFs
* Daily orders
* Cause lists
* Old archive (up to 1950s)

Examples:

* Delhi High Court
* Bombay High Court
* Madras High Court
* Calcutta HC
* Allahabad HC (largest archive)

---

### **B. Private Case Law Databases (Paid / Premium)**

Useful for datasets + citation search.

#### **1. Indian Kanoon**

* Search by:

  * Judge name
  * Case number
  * Keywords
  * Topics
* Has an unofficial API (used via query params + scraping)
* Very easy to index

#### **2. Manupatra**

* Most detailed legal search engine
* Requires license
* Data includes:

  * Digest notes
  * Headnotes
  * Precedents

#### **3. SCC Online**

* Supreme Court Cases
* Highly reputed
* Requires subscription
* Acts + Rules + Regulations included

#### **4. LiveLaw / Bar & Bench**

* Latest case updates
* Not official judgments, but summaries.
* Useful for LLM training on “legal news”

---

---

# ✅ **2. Sources for All Indian Laws, Acts, Bare Acts, Rules & Regulations**

Here’s the **FULL LIST OF DATA SOURCES** for law texts.

---

### **A. Government Sources (Free & Official)**

#### **1. India Code (GOI)**

**[https://www.indiacode.nic.in](https://www.indiacode.nic.in)**
Contains:

✅ * All Central Acts
✅ * All State Acts 
✅ * Subordinate legislation:
  ✅ * Rules
  ✅ * Notifications
  ✅ * Orders
  ✅ * Regulations

✅ * Download in PDF/HTML

You can create a scraper using:

* `api/v1/acts?search=actname`
* `downloadPdf?actid=…`

#### **2. Legislative Department**

**[https://legislative.gov.in](https://legislative.gov.in)**

✅ * Constitution
✅ * Amendments
✅ * Act history
✅ * Gazette notifications

#### **3. Ministry of Law & Justice**

✅ * Official Acts
✅ * Bill PDFs
✅ * Amendments

#### **4. eGazette**

**[https://egazette.gov.in](https://egazette.gov.in)**

* All government notifications
* Good for “latest law updates”

#### **5. Government Sites**

**[https://igod.gov.in](https://igod.gov.in)**

* All government departments
* Good for “latest law updates”

---

### **B. Private Law Repositories (Easy Scraping)**

#### **1. LawMint / LegalCrystal**

* Judgments + Acts
* Good for structured metadata

---

---

# ✅ **3. Laws / Acts for Every Field of Work (Industry-Wise List)**

Here is a **complete category-wise breakdown**.

---

## **A. Criminal Law**

✅ * Indian Penal Code (IPC), 1860
✅ * Code of Criminal Procedure (CrPC), 1973
✅ * Evidence Act, 1872
✅ * NDPS Act
✅ * POCSO Act
✅ * SC/ST Atrocities Act
✅ * Arms Act
✅ * Juvenile Justice Act

---

## **B. Civil Law**

✅ * CPC, 1908
✅ * Contract Act, 1872
✅ * Specific Relief Act
✅ * Transfer of Property Act
✅ * Limitation Act
✅ * Arbitration & Conciliation Act
✅ * Consumer Protection Act

---

## **C. Corporate & Business Law**

✅ * Companies Act
✅ * LLP Act
✅ * GST Act
✅ * Income Tax Act
✅ * SEBI Act
✅ * FEMA
✅ * Insolvency & Bankruptcy Code (IBC)
✅ * Competition Act

---

## **D. Banking & Finance**

✅ * RBI Act
✅ * Banking Regulation Act
✅ * SARFAESI Act
✅ * Negotiable Instruments Act (Cheque Bounce)

---

## **E. Family & Personal Laws**

✅ * Hindu Marriage Act
✅ * Muslim Personal Law
✅ * Special Marriage Act
✅ * Hindu Succession Act
✅ * Guardianship Act
✅ * Domestic Violence Act

---

## **F. Labour & Employment**

✅ * Industrial Disputes Act
✅ * Minimum Wages Act
✅ * Factories Act
✅ * Occupational Safety Code
✅ * Employee Provident Fund Act
✅ * Payment of Wages Act
✅ * Maternity Benefit Act

---

## **G. Cyber & Technology Law**

✅ * IT Act, 2000
✅ * Digital Personal Data Protection Act (DPDP Act), 2023
* IT Rules
* CERT-In guidelines

---

## **H. Media, Press, and Digital Content**

✅ * Cable TV Regulation Act
✅ * Cinematograph Act
* OTT Guidelines 2021

---

## **I. Property & Real Estate**

✅ * RERA Act
✅ * Registration Act
✅ * Stamp Act
✅ * Land Acquisition Act
✅ * Benami Property Act

---

## **J. Transportation**

✅ * Motor Vehicles Act
✅ * Railway Act
✅ * Aviation Act

---

## **K. Environment & Health**

✅ * Environment Protection Act
✅ * Forest Act
✅ * Wildlife Protection Act
✅ * Biodiversity Act
✅ * Food Safety and Standards Act (FSSAI)

---

## **L. Education**

✅ * RTE Act
✅ * UGC Act
✅ * AICTE Act

---

## **M. Miscellaneous**

✅ * Passport Act
✅ * Foreigners Act
✅ * Disaster Management Act
✅ * RTI Act

---

# **4. How LegalFinderAI Can Use This Data**

Here’s the optimal structure:

### **📌 A. Create Your Own Database**

Tables:

* `laws`
* `sections`
* `cases`
* `judgments`
* `industries`
* `sections_to_cases_map`
* `acts_to_industry_map`

### **📌 B. LLM Tasks**

1. Read a user’s event/case
2. Classify the domain
3. Suggest Acts & Sections
4. Suggest similar past cases
5. Predict possible outcomes
6. Suggest legal steps
7. FAQs & step-by-step guidance

---

### ✔ Full **BRD + System Architecture**
### ✔ Database schema (PostgreSQL/MySQL)
### ✔ LLM prompts for “event → IPC/CrPC/Acts/Case Laws”


### https://articles.manupatra.com/
### https://sansad.in/api_ls/member?page=1&size=10&locale=en
