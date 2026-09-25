"""
pipeline.py
===========

Ties the CrisisLens ingestion + NLP pieces together.

This is the hand-off point of the module. It turns one raw incoming report
into ONE clean, flat dictionary that the rest of the team can consume:

    report text + coordinates + source
                  |
                  v
          analyze_report()   (TF-IDF + Logistic Regression)
                  |
                  v
    { report_text, latitude, longitude, source, timestamp,
      disaster_type, severity, resource_need }

Deliberately NOT implemented here (owned by other teammates):
  - K-Means incident consolidation
  - GIS / exposure analysis
  - Risk / priority scoring
  - Dashboard

USAGE
-----
From the CrisisLens root:
    python src/pipeline.py

From another module in src/:
    from pipeline import process_report
"""

from datetime import datetime

# This file lives in src/, so we import its neighbours two ways depending on
# how it was started: "python src/pipeline.py" or "python -m src.pipeline".
try:  # imported as part of the src package
    from .nlp_classifier import analyze_report
except ImportError:  # run directly as a script
    from nlp_classifier import analyze_report


def _to_float(value, name):
    """Convert a coordinate to float, with a clear error if it is not numeric."""
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(
            f"process_report() needs a numeric '{name}', but received: {value!r}"
        )


def process_report(report_text, latitude, longitude, source="Unknown Source"):
    """
    Turn one incoming disaster report into a structured record.

    Parameters
    ----------
    report_text : str
        The raw report text, e.g. "Water entered homes and two people are
        stranded."
    latitude : float
        Latitude of the report location.
    longitude : float
        Longitude of the report location.
    source : str, optional
        Where the report came from, e.g. "Citizen Report", "SMS/SOS Alert".

    Returns
    -------
    dict
        {
            "report_text": "...",
            "latitude": 12.85,
            "longitude": 77.65,
            "source": "Citizen Report",
            "timestamp": "2026-09-25T21:53:18",
            "disaster_type": "Flood",
            "severity": "High",
            "resource_need": "Rescue"
        }
    """
    if report_text is None or not str(report_text).strip():
        raise ValueError("process_report() needs a non-empty report_text.")

    # 1. Let the NLP module figure out the three labels.
    analysis = analyze_report(report_text)

    # 2. Attach the reporting metadata. The timestamp is the moment THIS
    #    report entered the pipeline (not the time it happened).
    return {
        "report_text": str(report_text).strip(),
        "latitude": _to_float(latitude, "latitude"),
        "longitude": _to_float(longitude, "longitude"),
        "source": str(source),
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "disaster_type": analysis["disaster_type"],
        "severity": analysis["severity"],
        "resource_need": analysis["resource_need"],
    }


# ---------------------------------------------------------------------------
# Demo:  python src/pipeline.py
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    import json

    # A report arriving from a citizen in Bengaluru.
    sample_report_text = (
        "Water has entered the ground floor of our house after heavy rain "
        "and two people are stuck inside."
    )

    processed_report = process_report(
        report_text=sample_report_text,
        latitude=12.9352,
        longitude=77.6245,
        source="Citizen Report",
    )

    print("=" * 60)
    print("CrisisLens - pipeline demo")
    print("=" * 60)
    print("Structured record produced by my module:")
    print()
    print(json.dumps(processed_report, indent=4))
    print()

    # -----------------------------------------------------------------------
    # This is the hand-off point. The lines below show how my teammates'
    # modules will pick this dictionary up. They are commented out because
    # those modules belong to other people and are not written yet.
    # -----------------------------------------------------------------------
    print("Hand-off to the rest of the pipeline (not implemented here):")
    print()
    print("    processed_report = process_report(report_text, latitude,")
    print("                                        longitude, source)")
    print()
    print("    incidents = kmeans_module.process(processed_report)")
    print("    exposure  = gis_module.analyze(processed_report)")
    print("    priority  = risk_engine.calculate(processed_report)")
    print()
    print("=" * 60)
