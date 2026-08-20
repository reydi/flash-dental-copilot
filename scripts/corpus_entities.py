"""Declarative source data for the corpus generator: real Flash Dental entities.

Single responsibility: the vocabulary the generator draws from — models, clinics,
technicians, fault symptoms — plus the hand-authored "canonical" documents that
carry the FD-1042 story the demo is told around. No logic lives here.
"""
from __future__ import annotations

SERVICE_MODELS = [
    "DC-300", "DC-500", "DC-600", "A6-Cart", "A4-Cart", "A8-Cart",
    "S60-Panoramic", "S80-Panoramic", "Tealth-Lite", "Tealth-Pro", "Esay-E5", "Joinchamp-JC7",
]

# (clinic_name, city) — the first fourteen are Flash Dental's real June service log;
# the rest fill out a nationwide install base across Indonesia's service regions.
DENTAL_CLINICS = [
    ("drg. Iffah, Klinik Darusyifa Mulia", "Jakarta Selatan"),
    ("drg. Lidya", "Banjarbaru"),
    ("drg. Zeddin Ronald", "Tarakan"),
    ("drg. Annisa, Klinik QSmile", "Tanjung Pinang"),
    ("drg. Andi Iskandar", "Nunukan"),
    ("drg. Riris", "Ketapang"),
    ("drg. Billy", "Karawang"),
    ("drg. Ni Made Zatphika", "Purbalingga"),
    ("RS Fatmawati", "Jakarta Selatan"),
    ("drg. Cecilia Angelina", "PIK Jakarta Utara"),
    ("drg. Kartini", "Surabaya"),
    ("drg. Muhammad Adnen", "Bekasi"),
    ("drg. Karolina Br Kaban", "Pontianak"),
    ("drg. Androw Tandean", "Medan"),
    ("drg. Bakti", "Bandung"),
    ("Klinik Gigi Senyum", "Bandung"),
    ("drg. Wulan", "Semarang"),
    ("RS Kariadi", "Semarang"),
    ("drg. Prasetya", "Yogyakarta"),
    ("Klinik Dentalia", "Yogyakarta"),
    ("drg. Komang", "Denpasar"),
    ("Klinik Bali Dental", "Denpasar"),
    ("drg. Hasrul", "Makassar"),
    ("RS Wahidin", "Makassar"),
    ("drg. Ferry", "Balikpapan"),
    ("drg. Sri Wahyuni", "Samarinda"),
    ("Klinik Sriwijaya", "Palembang"),
    ("drg. Zulkifli", "Pekanbaru"),
    ("Klinik Batam Dental", "Batam"),
    ("drg. Ronny", "Manado"),
    ("drg. Josephine", "Ambon"),
    ("drg. Marthen", "Jayapura"),
    ("drg. Yohana", "Kupang"),
    ("Klinik Mataram Sehat", "Mataram"),
    ("drg. Reza", "Padang"),
    ("drg. Lukman", "Bandar Lampung"),
    ("Klinik Jambi Sehat", "Jambi"),
    ("drg. Palupi", "Palu"),
    ("Klinik Kendari Gigi", "Kendari"),
    ("drg. Effendi", "Singkawang"),
]

# The five flagship technicians the story names, then a wider field team across regions.
FIELD_TECHNICIANS = [
    "Yudi Pratama",
    "Dedi Kurniawan",
    "Febri Santoso",
    "Arga Wibowo",
    "Arman Hakim",
    "Rudi Hartanto",
    "Bambang Sutrisno",
    "Eko Prasetyo",
    "Agus Salim",
    "Hendra Gunawan",
    "Wayan Sudira",
    "Made Adnyana",
    "Rizal Fahmi",
    "Toni Wijaya",
    "Bagus Setiawan",
    "Ivan Kurnia",
    "Doni Saputra",
    "Fajar Nugraha",
    "Rendi Pranata",
    "Slamet Riyadi",
    "Gilang Ramadhan",
    "Wahyu Utomo",
    "Bayu Firmansyah",
    "Andre Simatupang",
]

# (complaint_phrase, spare_part, root_cause_hint)
FAULT_SYMPTOMS = [
    ("suction motor failure", "suction motor", "a clogged suction filter"),
    ("hydraulic leak on the chair", "hydraulic seal", "a worn hydraulic seal"),
    ("footcover cracked", "footcover", "material fatigue on the footcover"),
    ("low-speed water hose misrouted", "water hose", "a split low-speed water hose"),
    ("panoramic adaptor dead", "panoramic adaptor", "a failed S60 panoramic adaptor"),
    ("compressor overheating", "compressor filter", "a blocked compressor filter"),
    ("handpiece not spinning", "handpiece", "worn handpiece bearings"),
    ("LED operatory light out", "LED light module", "a failed LED light module"),
    ("foot pedal unresponsive", "foot pedal", "a worn foot-pedal switch"),
    ("air compressor pressure drop", "compressor pressure valve", "a leaking compressor pressure valve"),
    ("x-ray sensor miscalibrated", "x-ray sensor", "an x-ray sensor out of calibration"),
    ("autoclave not sealing", "autoclave gasket", "a perished autoclave door gasket"),
]

# The FD-1042 story, hand-authored so the demo's headline questions always land.
CANONICAL_ASSET_DOCUMENTS = [
    {"document_id": "service_log_FD-1042_2024-03", "category": "service_log",
     "text": "Dental unit FD-1042 (model DC-300) at Klinik Sehat, Surabaya. 2024-03 service: suction motor failure; replaced the suction motor; resolved same visit."},
    {"document_id": "service_log_FD-1042_2024-09", "category": "service_log",
     "text": "Dental unit FD-1042 (model DC-300) service 2024-09: hydraulic leak on the chair; sealed the hydraulic line; resolved same visit."},
    {"document_id": "service_log_FD-1042_2025-01", "category": "service_log",
     "text": "Dental unit FD-1042 (model DC-300) service 2025-01: suction motor failure recurred, the third time; replaced the suction motor; resolved same visit."},
    {"document_id": "manual_DC-300_suction", "category": "manual",
     "text": "DC-300 suction motor: recurring failure is usually caused by a clogged filter; check and replace the filter on every service to prevent repeats."},
    {"document_id": "warranty_rule_general", "category": "warranty_rule",
     "text": "Main machine warranty is 2 years from installation; components are 1 year. The suction motor is treated as a component, so it is out of warranty after the first year."},
    {"document_id": "invoice_FD-1042", "category": "invoice",
     "text": "Invoice INV-2023-118: dental unit serial FD-1042 (model DC-300) purchased 2023-06-15 for Rp 85,000,000; sold by sales rep Rina Putri; installed at Klinik Sehat, Surabaya."},
    {"document_id": "faq_warranty_check", "category": "policy",
     "text": "How to check a unit's warranty: find its sales invoice for the purchase date; the main machine is covered for 2 years and components for 1 year. A unit past those dates is out of warranty and its repairs are billable."},
    {"document_id": "faq_spare_parts", "category": "policy",
     "text": "Spare parts stocked in the warehouse include suction motors, hydraulic seals, footcovers, water hoses, and handpieces. A spare-part stockout is the main cause of a long wait between a reported fault and the repair."},
    {"document_id": "faq_spare_part_lead_time", "category": "policy",
     "text": "A spare part typically ships in 7 to 17 days across the archipelago; when the warehouse is out of stock, that lead time is the top cause of the wait between a reported fault and its repair."},
    {"document_id": "pattern_DC-300_warranty_end", "category": "pattern",
     "text": "DC-300 units tend to fail close to their warranty end date. Review a DC-300 before a renewal so a repair that is about to become billable is not wrongly honoured as warranty."},
    {"document_id": "faq_install_training", "category": "policy",
     "text": "A new dental unit is installed on-site, then covered by scheduled preventive maintenance. After installation, technicians also run basic training for the clinic's staff on daily care and cleaning."},
    {"document_id": "faq_warranty_length", "category": "policy",
     "text": "How long is the warranty on a dental unit? The main machine is covered for 2 years from installation, and its components for 1 year. After that the unit is out of warranty and its repairs are billable."},
]

# Hand-authored technician records so "how is Yudi doing" always retrieves.
CANONICAL_TECHNICIAN_DOCUMENTS = [
    {"document_id": "tech_yudi_june", "category": "monthly_log",
     "text": "Technician Yudi Pratama June log: closed 16 jobs across Jabodetabek and out-of-town Kalimantan (Tarakan, Nunukan). First-time-fix on 14 of 16 jobs. Two jobs still waiting on spare parts."},
    {"document_id": "tech_yudi_review", "category": "review_note",
     "text": "Yudi Pratama review note: carries most of the out-of-town installs; flagged that spare-part stockouts are his single biggest delay; strong ownership on the Kalimantan trips."},
    {"document_id": "tech_dedi_june", "category": "monthly_log",
     "text": "Technician Dedi Kurniawan June log: closed 10 jobs, mostly Jabodetabek service and scheduled maintenance; first-time-fix on 9 of 10; one job outstanding on a water-hose stockout."},
    {"document_id": "tech_roster_balance", "category": "roster_note",
     "text": "Roster balance: out-of-town jobs concentrate on Yudi Pratama. If he is unavailable, Kalimantan coverage is a risk — spread the out-of-town roster across technicians."},
    {"document_id": "tech_coverage", "category": "overview",
     "text": "Coverage: Yudi Pratama handles most of the out-of-town Kalimantan and Sumatra work; Jabodetabek jobs spread across Dedi Kurniawan, Febri Santoso, Arga Wibowo, and Arman Hakim."},
    {"document_id": "tech_arman_note", "category": "review_note",
     "text": "Technician Arman Hakim has the lowest first-time-fix on the team this period. Pair him with a senior on complex jobs and review his diagnostic steps before he leaves for a callout."},
]

# A deliberate mix: on-topic questions that should be answered, and off-topic /
# PII questions that should be refused — so the demo shows the copilot discriminating.
ASSET_PRESET_QUESTIONS = [
    "asset FD-1042 keeps failing — show its service history",
    "who sold FD-1042 and when was it purchased?",
    "how long is the warranty on a dental unit?",
    "how many units have overdue maintenance?",
    "what is the wifi password?",
    "what's the capital of France?",
]

TECHNICIAN_PRESET_QUESTIONS = [
    "who is the least-performing technician this period?",
    "how many field technicians do we have?",
    "which clinics did Yudi service?",
    "who dispatches a technician to a reported fault?",
    "what is Yudi's home address?",
    "who is the best football player?",
]
