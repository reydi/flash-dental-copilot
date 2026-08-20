"""Declarative source data for Flash Dental's organisation: roles and the people flow.

Single responsibility: the vocabulary the employee-directory generator draws from —
the business roles and their headcounts, the regions they cover, the name pools used
to synthesise staff, and the hand-authored documents that describe how a service
request flows through the company. No logic lives here.
"""
from __future__ import annotations

# Indonesia's service regions, the way Flash Dental splits its coverage.
SERVICE_REGIONS = [
    "Jabodetabek",
    "West Java",
    "Central Java",
    "East Java",
    "Bali & Nusa Tenggara",
    "Kalimantan",
    "Sumatra",
    "Sulawesi",
    "Papua & Maluku",
]

# Every role in the after-sales business flow, with a target headcount. Field
# Technicians are sourced from FIELD_TECHNICIANS so tickets and the directory agree;
# every other role is synthesised from the name pools below.
#   title, responsibility, headcount, source
ROLE_DIRECTORY = [
    ("Field Technician", "travel to clinics and repair units on-site", 24, "field_technicians"),
    ("Service Coordinator", "triage incoming faults and dispatch a technician by region", 26, "synth"),
    ("Warehouse / Parts Officer", "manage spare-part stock and ship parts to the field", 22, "synth"),
    ("Service Manager", "own regional service performance and balance the roster", 14, "synth"),
    ("Sales Representative", "sell the unit and own the invoice that starts the warranty clock", 52, "synth"),
    ("Finance Officer", "reconcile warranty claims and billing", 12, "synth"),
    ("Customer Support Agent", "take clinic calls and open the service ticket", 30, "synth"),
    ("Regional Admin", "keep the regional service log and paperwork", 18, "synth"),
    ("Executive", "steer the business across both operations (C-level)", 4, "synth"),
]

# Indonesian given names and surnames — combined to synthesise realistic staff names.
GIVEN_NAMES = [
    "Adi", "Agus", "Aisyah", "Andi", "Anita", "Bagus", "Bayu", "Bella", "Budi",
    "Cahya", "Citra", "Dewi", "Dian", "Dimas", "Eka", "Endang", "Fajar", "Fitri",
    "Gita", "Hadi", "Hendra", "Indah", "Intan", "Joko", "Kartika", "Lestari",
    "Maya", "Nadia", "Naufal", "Novi", "Oki", "Putra", "Putri", "Rahmat", "Rani",
    "Reza", "Rina", "Rizki", "Sari", "Sinta", "Surya", "Tari", "Wahyu", "Yusuf",
]
SURNAMES = [
    "Wijaya", "Santoso", "Kurniawan", "Pratama", "Nugroho", "Saputra", "Hidayat",
    "Gunawan", "Halim", "Wibowo", "Setiawan", "Permana", "Hakim", "Utomo", "Maulana",
    "Firmansyah", "Suryadi", "Iskandar", "Ramadhan", "Cahyono", "Anggraini", "Puspita",
    "Hartono", "Susanto", "Handoko", "Prasetyo", "Nurdin", "Siregar", "Nasution",
    "Tanjung", "Simanjuntak", "Hutapea", "Panjaitan", "Sitompul", "Ginting", "Tarigan",
    "Marpaung", "Sihombing", "Manurung", "Sinaga",
]

# Hand-authored documents describing the org and its flow, so questions about who does
# what — and how a request moves — always retrieve a grounded, cited answer.
CANONICAL_ORG_DOCUMENTS = [
    {"document_id": "org_business_flow", "category": "process",
     "text": "Service flow at Flash Dental: a clinic reports a fault to a Customer Support agent, "
             "who opens a ticket; a Service Coordinator triages it and dispatches a Field Technician "
             "by region; a Warehouse officer ships any spare part; the Service Manager tracks cycle "
             "time and first-time-fix; and Finance reconciles any warranty claim against the sales invoice."},
    {"document_id": "role_service_coordinator", "category": "role",
     "text": "Service Coordinators triage incoming faults and dispatch technicians by region. They own "
             "the hand-off from a reported fault to an assigned technician and chase spare-part status."},
    {"document_id": "role_warehouse", "category": "role",
     "text": "Warehouse and Parts officers manage spare-part stock — suction motors, hydraulic seals, "
             "footcovers, hoses, handpieces — and ship them to the field. A stockout is the main cause of long waits."},
    {"document_id": "role_sales", "category": "role",
     "text": "Sales Representatives sell the dental unit and own its sales invoice. That invoice date sets "
             "the warranty clock, so sales work is where each unit's warranty status begins."},
    {"document_id": "role_finance", "category": "role",
     "text": "Finance officers reconcile warranty claims against the sales invoice. Honouring an expired claim "
             "loses margin; denying a valid one risks a clinic churning — so warranty accuracy is a finance concern."},
    {"document_id": "role_service_manager", "category": "role",
     "text": "Service Managers own regional service performance: first-time-fix, cycle time, the outstanding "
             "backlog, and roster balance across their technicians. They do not see other regions' teams."},
    {"document_id": "role_customer_support", "category": "role",
     "text": "Customer Support agents take the clinic's call, capture the fault, and open the service ticket "
             "that the coordinator then triages. They are the first touch in the after-sales flow."},
    {"document_id": "org_regions", "category": "overview",
     "text": "Flash Dental splits coverage into regions: Jabodetabek, West Java, Central Java, East Java, "
             "Bali & Nusa Tenggara, Kalimantan, Sumatra, Sulawesi, and Papua & Maluku. Out-of-town work "
             "concentrates in Kalimantan and Sumatra."},
    {"document_id": "org_executives", "category": "overview",
     "text": "The executive team (C-level) steers both operations — field-service assets and technician "
             "people-performance — from one rolled-up cockpit."},
    {"document_id": "faq_sla_targets", "category": "policy",
     "text": "Target SLA by priority: Critical (unit dead, operations stopped) — first response 15 to 30 minutes, "
             "handled as soon as possible. High (main function disrupted) — 1 hour, within 1 working day. "
             "Medium (partial function) — 2 to 4 hours, 2 to 3 working days. Low (inquiry, training, minor) — "
             "1 working day, per schedule."},
    {"document_id": "faq_sla_metrics", "category": "policy",
     "text": "The SLA metrics tracked are first response time, assignment time, scheduling time, arrival time, "
             "resolution time, and closure time — each measured from when the report comes in. Today they are "
             "not measured at all; the system computes them without manual input."},
    {"document_id": "faq_ticket_types", "category": "process",
     "text": "Ticket types: new installation, preventive maintenance, breakdown or repair, warranty claim, "
             "relocation, training, component replacement, and follow-up of previous work."},
    {"document_id": "faq_ticket_close", "category": "process",
     "text": "What happens after a ticket is resolved? It moves Resolved, then Customer Confirmation, then Closed. "
             "A supervisor or admin verifies the closure, and all activity is written into the asset's history."},
]

ORG_PRESET_QUESTIONS = [
    "how many field technicians do we have?",
    "who dispatches a technician to a reported fault?",
    "how does a service request flow through the company?",
]
