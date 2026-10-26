"""Refresh the local, public-domain airport reference used by dev autocomplete."""

import csv
import io
import json
import urllib.request
from datetime import date
from pathlib import Path


SOURCE_URL = "https://raw.githubusercontent.com/davidmegginson/ourairports-data/main/airports.csv"
OUTPUT_PATH = (
    Path(__file__).resolve().parents[1]
    / "frontend/src/entities/offers/model/airportReference.json"
)


def main() -> None:
    with urllib.request.urlopen(SOURCE_URL, timeout=30) as source:
        rows = csv.DictReader(io.TextIOWrapper(source, encoding="utf-8", newline=""))
        airports_by_iata: dict[str, dict[str, str]] = {}
        for row in rows:
            if row.get("type") not in {"large_airport", "medium_airport"}:
                continue
            if row.get("scheduled_service") != "yes":
                continue
            iata = (row.get("iata_code") or "").strip().upper()
            if len(iata) != 3:
                continue
            name = (row.get("name") or "").strip()
            municipality = (row.get("municipality") or "").strip()
            country_code = (row.get("iso_country") or "").strip().upper()
            if not name or not country_code:
                continue
            airports_by_iata.setdefault(iata, {
                "iata": iata,
                "name": name,
                "city": municipality or name,
                "country_code": country_code,
            })

    data = {
        "source": "OurAirports",
        "source_url": "https://ourairports.com/data/",
        "license": "Public Domain",
        "generated_on": date.today().isoformat(),
        "airports": sorted(
            airports_by_iata.values(),
            key=lambda airport: (airport["city"].casefold(), airport["iata"]),
        ),
    }
    OUTPUT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(data['airports'])} airport references to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
