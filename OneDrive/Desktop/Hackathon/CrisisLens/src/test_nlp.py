"""
test_nlp.py
===========

A quick smoke test for the CrisisLens NLP module.

It feeds five disaster reports that were NOT used to train the models and
prints what the models predict for each one. This is how you demonstrate
the NLP part works.

Run it from the CrisisLens project root:
    python src/test_nlp.py

If the models have not been trained yet, analyze_report() will train them
automatically the first time it is called.
"""

# This file lives in src/, so we import its neighbours two ways depending on
# how it was started: "python src/test_nlp.py" or "python -m src.test_nlp".
try:  # imported as part of the src package
    from .nlp_classifier import analyze_report
except ImportError:  # run directly as a script
    from nlp_classifier import analyze_report


# ---------------------------------------------------------------------------
# Five unseen reports.
#
# "Unseen" means these exact sentences do not appear in
# data/raw/disaster_reports.csv. The expected labels below were written by
# hand, so you can eyeball whether the model agrees with a human.
# ---------------------------------------------------------------------------
TEST_REPORTS = [
    {
        "report_text": "Heavy rainfall has caused water to enter homes and "
                       "several residents are stranded.",
        "expected_disaster_type": "Flood",
    },
    {
        "report_text": "Smoke and flames are coming from the second floor of "
                       "a residential building.",
        "expected_disaster_type": "Fire",
    },
    {
        "report_text": "A large section of the hillside has collapsed and "
                       "blocked the road.",
        "expected_disaster_type": "Landslide",
    },
    {
        "report_text": "Gale force winds have uprooted trees and electric "
                       "poles along the coastal highway.",
        "expected_disaster_type": "Cyclone",
    },
    {
        "report_text": "A truck ran into a crowd waiting at the bus stop and "
                       "at least three people are bleeding badly.",
        "expected_disaster_type": "Road Accident",
    },
]


def main():
    print("=" * 60)
    print("CrisisLens - NLP classifier test on unseen reports")
    print("=" * 60)
    print(f"Number of unseen test reports: {len(TEST_REPORTS)}")
    print("(These sentences are not part of the training dataset.)")
    print()

    correct = 0

    for number, item in enumerate(TEST_REPORTS, start=1):
        text = item["report_text"]

        # One call does all the work: text in, three labels out.
        prediction = analyze_report(text)

        print(f"[Report {number} of {len(TEST_REPORTS)}]")
        print("REPORT:")
        print(text)
        print()
        print("Predicted Disaster Type:")
        print(prediction["disaster_type"])
        print()
        print("Predicted Severity:")
        print(prediction["severity"])
        print()
        print("Predicted Resource Need:")
        print(prediction["resource_need"])
        print()
        print(f"(Human label for reference: {item['expected_disaster_type']})")
        print("-" * 60)
        print()

        if prediction["disaster_type"] == item["expected_disaster_type"]:
            correct += 1

    print("=" * 60)
    print(f"Disaster type matched the human label in {correct} of "
          f"{len(TEST_REPORTS)} unseen reports.")
    print()
    print("NOTE: This is a prototype running on a small synthetic dataset.")
    print("It is a demonstration that the pipeline works end to end - it is")
    print("NOT evidence of real-world emergency classification accuracy.")
    print("=" * 60)


if __name__ == "__main__":
    main()
