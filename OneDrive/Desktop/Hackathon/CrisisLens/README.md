# CrisisLens 🔍

**An AI-powered disaster intelligence system — hackathon prototype.**

CrisisLens takes incoming disaster reports (citizen SOS messages, helpline
calls, volunteer reports), understands them with NLP, and turns them into
structured data that a responder dashboard can act on.

---

## ⚠️ Read this first

**The dataset is 100% synthetic.** Every report in
`data/raw/disaster_reports.csv` was written by hand for this hackathon
prototype. They are **not** real emergency reports, the coordinates are
approximate/illustrative locations around Karnataka, and nothing in this
repository is connected to any live disaster API.

**The accuracy numbers are prototype numbers.** They are measured on ~100
hand-written synthetic sentences. They are a sanity check that the code
works — they are **not** validated real-world emergency-response accuracy
and should never be presented as such.

---

## 1. What CrisisLens is

The full system is a pipeline that goes from a raw report to a prioritised
responder dashboard:

```
Disaster Report
      ↓
Data Ingestion            ← this repo
      ↓
AI / NLP Analysis         ← this repo
      ↓
Disaster Type + Severity + Resource Need   ← this repo (hand-off point)
      ↓
K-Means Incident Consolidation             ← teammate
      ↓
GIS Exposure Analysis                      ← teammate
      ↓
Risk / Priority Score                      ← teammate
      ↓
Responder Dashboard                        ← teammate
```

## 2. What this module is responsible for

This repository covers **three components only**:

| # | Component | File(s) |
|---|-----------|---------|
| 1 | Data ingestion + synthetic dataset | `data/raw/disaster_reports.csv`, `src/data_ingestion.py` |
| 2 | AI / NLP classification | `src/nlp_classifier.py` |
| 3 | Pipeline integration | `src/pipeline.py` |

It **stops** at producing one clean structured record per report.
It deliberately does **not** implement K-Means consolidation, GIS/exposure
analysis, risk scoring, or the dashboard — those belong to other teammates.

### What is inside the NLP module

Three independent **TF-IDF + Logistic Regression** classifiers. No deep
learning, no external API calls, no internet needed after installation.

| Model | Predicts | Values |
|-------|----------|--------|
| `disaster_classifier.pkl` | Disaster type | Flood, Fire, Landslide, Earthquake, Cyclone, Building Collapse, Road Accident |
| `severity_classifier.pkl` | Severity | Low, Medium, High, Critical |
| `resource_classifier.pkl` | Resource need | Rescue, Medical, Fire Services, Evacuation, Food/Water, Shelter, Road Clearance, None |

Each classifier has its own matching `*_vectorizer.pkl` file. The vectorizer
must be saved alongside the model, because at prediction time the text has to
be converted into the exact same numeric features the model was trained on.

---

## 3. Project structure

```
CrisisLens/
│
├── data/
│   ├── raw/
│   │   └── disaster_reports.csv     ← 100 synthetic reports
│   └── processed/                   ← (empty, kept for later use)
│
├── models/                          ← the 6 .pkl files land here after training
│
├── notebooks/                       ← (empty, optional exploration)
│
├── src/
│   ├── __init__.py
│   ├── data_ingestion.py            ← Task 1: load + clean the CSV
│   ├── nlp_classifier.py            ← Task 2: train + analyze_report()
│   ├── test_nlp.py                  ← Task 3: test on 5 unseen reports
│   └── pipeline.py                  ← Task 4: process_report()
│
├── requirements.txt
└── README.md
```

The empty folders contain a small `.gitkeep` file so that Git keeps them
around. They will fill up as the project grows (`models/` gets the `.pkl`
files as soon as you train).

### The dataset columns

| Column | Meaning |
|--------|---------|
| `report_id` | Unique id, `R001` … `R100` |
| `timestamp` | When the report came in (synthetic date/time) |
| `report_text` | The free-text report — this is what the NLP models read |
| `latitude`, `longitude` | Approximate location (Karnataka / Bengaluru area) |
| `source` | Where it came from, e.g. "Citizen Report", "SMS/SOS Alert" |
| `disaster_type` | Label: the disaster category |
| `severity` | Label: Low / Medium / High / Critical |
| `trapped_persons` | People reported trapped or awaiting extraction (0 if none) |
| `resource_need` | Label: the resource that is needed |

---

## 4. Step 1 — Create a virtual environment

Open a terminal **in the `CrisisLens` folder** (in VS Code: `Terminal → New
Terminal`, then `cd CrisisLens` if needed).

```bash
python -m venv venv
```

This creates a `venv/` folder holding an isolated copy of Python for this
project, so the packages you install here cannot break anything else on your
machine.

> On some Windows setups the `python` command opens the Microsoft Store
> instead. If that happens, use `py -m venv venv` instead.

## 5. Step 2 — Activate it (Windows)

**PowerShell** (the default VS Code terminal on Windows):

```powershell
venv\Scripts\activate
```

**Command Prompt (cmd):**

```cmd
venv\Scripts\activate.bat
```

**Git Bash:**

```bash
source venv/Scripts/activate
```

When it worked, your prompt starts with `(venv)`.

> If PowerShell complains that *running scripts is disabled on this system*,
> allow it for the current window only:
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`
> then run the activate command again.

## 6. Step 3 — Install the requirements

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

That installs `pandas`, `numpy`, `scikit-learn` and `joblib`. Nothing else is
needed, and the project runs completely offline afterwards.

> **Python 3.13 note:** 3.13 needs recent versions of these libraries. If pip
> picks something old and fails to build, upgrade pip first (as above) and
> retry. The requirements file is intentionally unpinned so pip can choose a
> wheel that matches your Python version.

---

## 7. Step 4 — Train the models

**This must happen before `analyze_report()` is used.** Run it from the
`CrisisLens` root:

```bash
python src/nlp_classifier.py
```

What it does:

1. Loads `data/raw/disaster_reports.csv`.
2. Splits it into training and testing sets (75% / 25%, `random_state=42`).
3. Fits a TF-IDF vectorizer on the training text.
4. Trains a Logistic Regression on the resulting features.
5. Repeats steps 3–4 for each of the three labels.
6. Saves six files into `models/`.
7. Prints prototype accuracy for each classifier.

Expected output (your exact numbers may differ slightly if you edit the CSV):

```
============================================================
PROTOTYPE ACCURACY (synthetic dataset - not real-world accuracy)
============================================================
Disaster Type Accuracy: 0.xx
Severity Accuracy: 0.xx
Resource Need Accuracy: 0.xx
```

Because `random_state` is fixed, re-running this gives the same numbers
every time.

You do **not** have to run this by hand: if the `.pkl` files are missing,
`analyze_report()` will detect that and train them automatically the first
time it is called. Running it yourself first is still recommended so you can
see the accuracy report.

> **The task difficulty is not equal.** Disaster type is the easiest, because
> words like *flood*, *flames* and *landslide* are strongly tied to one label.
> Severity and resource need are harder, partly because several labels overlap
> in meaning (Rescue vs Medical vs Evacuation) and partly because the synthetic
> dataset only has a handful of examples for the rarest labels.

---

## 8. Step 5 — Test the five unseen reports

```bash
python src/test_nlp.py
```

This feeds five reports that are **not** in the training CSV and prints the
three predictions for each one:

```
REPORT:
Heavy rainfall has caused water to enter homes and several residents are stranded.

Predicted Disaster Type:
Flood

Predicted Severity:
High

Predicted Resource Need:
Rescue
```

Each block ends with the human-written label for comparison, and the script
finishes with a count of how many predictions matched.

You can sanity-check the ingestion step on its own too:

```bash
python src/data_ingestion.py
```

It prints the row count, the label distributions, and any remaining missing
values.

---

## 9. Step 6 — Calling `process_report()`

`process_report()` is the single entry point for an incoming report. It runs
the NLP analysis, attaches the reporting metadata, and returns one flat
dictionary.

```python
from src.pipeline import process_report

processed_report = process_report(
    report_text="Water has entered the ground floor of our house after heavy rain and two people are stuck inside.",
    latitude=12.9352,
    longitude=77.6245,
    source="Citizen Report",
)
```

Or run the built-in demo:

```bash
python src/pipeline.py
```

### Full parameter list

| Parameter | Type | Required | Notes |
|-----------|------|----------|-------|
| `report_text` | str | yes | The raw report. Must not be empty. |
| `latitude` | float | yes | Numeric; a non-numeric value raises a clear error. |
| `longitude` | float | yes | Numeric. |
| `source` | str | no | Defaults to `"Unknown Source"`. |

### What you get back

```python
{
    "report_text": "Water has entered the ground floor of our house after heavy rain and two people are stuck inside.",
    "latitude": 12.9352,
    "longitude": 77.6245,
    "source": "Citizen Report",
    "timestamp": "2026-09-25T21:53:18",
    "disaster_type": "Flood",
    "severity": "High",
    "resource_need": "Rescue"
}
```

Notes on the output:

- `timestamp` is an ISO-8601 string for the moment the report entered the
  pipeline — not the moment the disaster happened.
- All eight keys are always present, so downstream code never has to guess.
- The values are plain Python `str` / `float`, so the dictionary is directly
  JSON-serialisable — `json.dumps(processed_report)` works as-is.

---

## 10. Handing the output to your teammates

The dictionary above **is** the interface. Nothing else needs to be shared —
your teammates just call your function, or read the dictionary you pass them.

Because the record is a flat dictionary with no custom classes, it moves
between modules without any conversion work:

```python
from src.pipeline import process_report

# ---- your module ----
processed_report = process_report(report_text, latitude, longitude, source)

# ---- teammate modules (not implemented in this repo) ----
incidents = kmeans_module.process(processed_report)   # K-Means consolidation
exposure  = gis_module.analyze(processed_report)      # GIS exposure analysis
priority  = risk_engine.calculate(processed_report)   # risk / priority score
```

Suggested division of the keys:

| Keys | Used by |
|------|---------|
| `latitude`, `longitude` | K-Means (clustering reports into incidents), GIS (exposure analysis) |
| `disaster_type`, `severity` | Risk engine (which hazard, how urgent) |
| `resource_need` | Risk engine / dashboard (what to dispatch) |
| `timestamp` | Dashboard (recency, ordering) |
| `report_text`, `source` | Dashboard (evidence shown to the responder) |

Two practical tips for the hand-off:

1. To process a whole CSV in one go, loop over the reports and collect the
   results in a list, then hand the list to the K-Means module:
   ```python
   records = [
       process_report(row.report_text, row.latitude, row.longitude, row.source)
       for row in load_reports().itertuples()
   ]
   ```
2. The K-Means and GIS modules need coordinates, so rows without coordinates
   are dropped during ingestion rather than filled with placeholder values —
   a made-up location would be worse than no location for a mapping step.

---

## 11. Limitations (please state these honestly in the demo)

- **The data is synthetic.** 100 hand-written reports, so the vocabulary is
  far narrower than real emergency traffic. Real reports contain typos,
  regional languages, abbreviations and voice-transcription noise — none of
  which this prototype has seen.
- **Accuracy is prototype-only.** A high number here means the code runs and
  the labels are internally consistent. It says nothing about field
  performance.
- **Class imbalance.** Some resource labels have only ~5 examples in the
  whole dataset, so those classes are unreliable.
- **English only.** Reports in Kannada or other languages are not handled.
- **No geocoding.** Latitude and longitude come from the report itself; text
  such as "near the market" is not converted into coordinates.
- **Sarcasm, ambiguity and multiple simultaneous disasters** are not handled —
  each report gets exactly one type, one severity and one resource need.

---

## Quick reference

```bash
# one-time setup (from the CrisisLens folder)
python -m venv venv
venv\Scripts\activate          # PowerShell / cmd
pip install -r requirements.txt

# train the three classifiers (writes 6 files into models/)
python src/nlp_classifier.py

# run the five unseen test reports
python src/test_nlp.py

# see the structured record for one report
python src/pipeline.py

# check the dataset loads cleanly
python src/data_ingestion.py
```
