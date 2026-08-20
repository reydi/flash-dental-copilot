"""Map Flash Dental's clinic cities to the nine service regions.

Single responsibility: the declarative city-to-region lookup the capacity analysis
uses to fold ticket demand up to the region level. No logic beyond the lookup.
"""
from __future__ import annotations

SERVICE_REGIONS = [
    "Sumatra",
    "Jabodetabek",
    "West Java",
    "Central Java",
    "East Java",
    "Bali & Nusa Tenggara",
    "Kalimantan",
    "Sulawesi",
    "Papua & Maluku",
]

_CITY_TO_REGION = {
    # Jabodetabek (greater Jakarta)
    "Jakarta Selatan": "Jabodetabek", "PIK Jakarta Utara": "Jabodetabek",
    "Jakarta": "Jabodetabek", "Bekasi": "Jabodetabek", "Karawang": "Jabodetabek",
    # West Java
    "Bandung": "West Java",
    # Central Java (incl. Yogyakarta)
    "Semarang": "Central Java", "Yogyakarta": "Central Java", "Purbalingga": "Central Java",
    # East Java
    "Surabaya": "East Java",
    # Bali & Nusa Tenggara
    "Denpasar": "Bali & Nusa Tenggara", "Mataram": "Bali & Nusa Tenggara",
    "Kupang": "Bali & Nusa Tenggara",
    # Kalimantan
    "Banjarbaru": "Kalimantan", "Tarakan": "Kalimantan", "Nunukan": "Kalimantan",
    "Ketapang": "Kalimantan", "Pontianak": "Kalimantan", "Balikpapan": "Kalimantan",
    "Samarinda": "Kalimantan", "Singkawang": "Kalimantan",
    # Sumatra
    "Medan": "Sumatra", "Palembang": "Sumatra", "Pekanbaru": "Sumatra", "Batam": "Sumatra",
    "Padang": "Sumatra", "Bandar Lampung": "Sumatra", "Jambi": "Sumatra",
    "Tanjung Pinang": "Sumatra",
    # Sulawesi
    "Makassar": "Sulawesi", "Manado": "Sulawesi", "Palu": "Sulawesi", "Kendari": "Sulawesi",
    # Papua & Maluku
    "Ambon": "Papua & Maluku", "Jayapura": "Papua & Maluku",
}


def region_for_city(city: str) -> str:
    """The service region a city belongs to, or 'Other' if it is unmapped."""
    return _CITY_TO_REGION.get(city, "Other")
