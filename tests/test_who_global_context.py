from __future__ import annotations

from scripts.collect_who_global_context import parse_profile


def test_who_parser_preserves_context_only_and_missingness() -> None:
    text = """WHO estimated road traffic fatalities (95% CI) (year) 3 983 (95% CI 3 743 - 4 223) (2021)
WHO estimated rate per 100 000 population (year) 8.8 (2021)
National law setting a speed limit Yes
Maximum urban speed limit 60 km/h
Maximum rural speed limit - N/A
National law on drink-driving Yes
"""
    # The parser normally receives a PDF. Replace PdfReader at its boundary so
    # the extraction contract is tested without network or a binary fixture.
    class Page:
        def extract_text(self):
            return text

    class Reader:
        pages = [Page()]

    import scripts.collect_who_global_context as module

    original = module.PdfReader
    module.PdfReader = lambda _: Reader()
    try:
        record = parse_profile(b"pdf", {"Code": "TST", "Title": "Test", "ParentTitle": "Test Region"})
    finally:
        module.PdfReader = original
    assert record["context_only"] == "true"
    assert record["who_estimated_road_traffic_fatalities"] == "3 983"
    assert record["who_estimated_rate_per_100k"] == "8.8"
    assert record["max_rural_speed_kph"] is None
