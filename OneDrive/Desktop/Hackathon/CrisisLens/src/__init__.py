"""
CrisisLens - source package.

Modules in this package:

    data_ingestion.py   Load and clean the synthetic disaster report dataset.
    nlp_classifier.py   TF-IDF + Logistic Regression classifiers
                        (disaster type, severity, resource need).
    pipeline.py         process_report(): raw report -> structured record.
    test_nlp.py         Smoke test on five unseen reports.

Typical imports:

    from src.pipeline import process_report
    from src.nlp_classifier import train_models, analyze_report
    from src.data_ingestion import load_reports

Or, when working from inside this folder:

    from pipeline import process_report
"""

__all__ = [
    "data_ingestion",
    "nlp_classifier",
    "pipeline",
    "test_nlp",
]
