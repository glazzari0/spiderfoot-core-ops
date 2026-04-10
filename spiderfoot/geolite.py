import bisect
import csv
import ipaddress
from pathlib import Path


class GeoLiteWorkspace:
    def __init__(self, root_dir):
        self.root_dir = Path(root_dir).resolve()

    def _ensure_inside_root(self, relative_path):
        candidate = (self.root_dir / relative_path).resolve()
        if not str(candidate).startswith(str(self.root_dir)):
            raise ValueError("Invalid GeoLite path outside root directory.")
        if not candidate.is_file():
            raise FileNotFoundError(f"GeoLite file not found: {candidate}")
        return candidate

    def available_files(self):
        datasets = {
            "city_blocks": self._discover_files(["*City-Blocks-IPv4*.csv"]),
            "city_locations": self._discover_files(["*City-Locations-*.csv"]),
            "country_locations": self._discover_files(["*Country-Locations-*.csv"]),
            "asn_blocks": self._discover_files(["*ASN-Blocks-IPv4*.csv"]),
        }
        defaults = {key: files[0]["path"] if files else "" for key, files in datasets.items()}
        return {"datasets": datasets, "defaults": defaults}

    def _discover_files(self, patterns):
        matches = []
        seen = set()
        for pattern in patterns:
            for path in self.root_dir.rglob(pattern):
                if path.name.startswith("~$"):
                    continue
                if path.resolve() in seen:
                    continue
                seen.add(path.resolve())
                rel = path.resolve().relative_to(self.root_dir).as_posix()
                matches.append({
                    "name": path.name,
                    "path": rel,
                    "label": rel,
                    "mtime": path.stat().st_mtime,
                })

        matches.sort(key=lambda item: (item["mtime"], item["label"]), reverse=True)
        for item in matches:
            item.pop("mtime", None)
        return matches

    def preview_rows(
        self,
        city_blocks_file,
        city_locations_file=None,
        country_locations_file=None,
        asn_blocks_file=None,
        filters=None,
        limit=1000,
    ):
        filters = filters or {}
        city_blocks_path = self._ensure_inside_root(city_blocks_file)
        city_locations = self._load_locations(city_locations_file) if city_locations_file else {}
        country_locations = self._load_locations(country_locations_file) if country_locations_file else {}
        starts, records = self._load_asn_index(asn_blocks_file) if asn_blocks_file else ([], [])

        rows = []
        matched_rows = 0
        total_rows = 0

        with city_blocks_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row_number, row in enumerate(reader, start=1):
                total_rows += 1
                network_text = (row.get("network") or "").strip()
                if not network_text:
                    continue

                try:
                    network = ipaddress.ip_network(network_text, strict=False)
                except ValueError:
                    continue

                city_geoname_id = (row.get("geoname_id") or "").strip()
                country_geoname_id = (row.get("registered_country_geoname_id") or "").strip()
                city_info = city_locations.get(city_geoname_id, {})
                country_info = country_locations.get(country_geoname_id, {})
                asn, organization = self._lookup_asn(starts, records, int(network.network_address))

                merged = {
                    "row": row_number,
                    "network": network_text,
                    "prefixlen": network.prefixlen,
                    "num_addresses": network.num_addresses,
                    "geoname_id": city_geoname_id,
                    "registered_country_geoname_id": country_geoname_id,
                    "country_iso_code": (
                        city_info.get("country_iso_code")
                        or country_info.get("country_iso_code")
                        or ""
                    ),
                    "country_name": (
                        city_info.get("country_name")
                        or country_info.get("country_name")
                        or ""
                    ),
                    "subdivision_1_name": city_info.get("subdivision_1_name", ""),
                    "city_name": city_info.get("city_name", ""),
                    "postal_code": (row.get("postal_code") or "").strip(),
                    "latitude": (row.get("latitude") or "").strip(),
                    "longitude": (row.get("longitude") or "").strip(),
                    "asn": asn,
                    "organization": organization,
                }

                if not self._matches_filters(merged, filters):
                    continue

                matched_rows += 1
                if limit and len(rows) >= limit:
                    continue

                rows.append(merged)

        return {
            "rows": rows,
            "total_rows": total_rows,
            "matched_rows": matched_rows,
            "returned_rows": len(rows),
            "truncated": bool(limit and matched_rows > len(rows)),
        }

    def _matches_filters(self, row, filters):
        network_filter = (filters.get("network") or "").strip().lower()
        city_filter = (filters.get("city") or "").strip().lower()
        country_filter = (filters.get("country") or "").strip().lower()
        org_filter = (filters.get("organization") or "").strip().lower()
        asn_filter = (filters.get("asn") or "").strip().lower()

        if network_filter and network_filter not in row["network"].lower():
            return False
        if city_filter and city_filter not in row["city_name"].lower():
            return False
        if country_filter:
            haystack = f'{row["country_name"]} {row["country_iso_code"]}'.lower()
            if country_filter not in haystack:
                return False
        if org_filter and org_filter not in row["organization"].lower():
            return False
        if asn_filter and asn_filter not in str(row["asn"]).lower():
            return False
        return True

    def _load_locations(self, relative_path):
        path = self._ensure_inside_root(relative_path)
        results = {}
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                geoname_id = (row.get("geoname_id") or "").strip()
                if geoname_id:
                    results[geoname_id] = row
        return results

    def _load_asn_index(self, relative_path):
        path = self._ensure_inside_root(relative_path)
        entries = []
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                network_text = (row.get("network") or "").strip()
                if not network_text:
                    continue
                try:
                    network = ipaddress.ip_network(network_text, strict=False)
                except ValueError:
                    continue
                entries.append((
                    int(network.network_address),
                    int(network.broadcast_address),
                    (row.get("autonomous_system_number") or "").strip(),
                    (row.get("autonomous_system_organization") or "").strip(),
                ))

        entries.sort(key=lambda item: item[0])
        starts = [entry[0] for entry in entries]
        return starts, entries

    def _lookup_asn(self, starts, records, ip_int):
        if not starts:
            return "", ""

        index = bisect.bisect_right(starts, ip_int) - 1
        if index < 0:
            return "", ""

        start_ip, end_ip, asn, organization = records[index]
        if start_ip <= ip_int <= end_ip:
            return asn, organization
        return "", ""
