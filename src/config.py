"""
Shared settings for the whole project: file paths and column names.

Every other file imports from here, so if a path or column name changes,
we only have to fix it in ONE place.
"""

from pathlib import Path

# ---------------------------------------------------------------------------
# File paths (built from this file's location, so scripts work from any folder)
# ---------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_ROOT / "College_Scorecard_Raw_Data_10152026"
RAW_CSV = RAW_DIR / "Most-Recent-Cohorts-Institution.csv"

DATA_DIR = PROJECT_ROOT / "data"
FIGURES_DIR = PROJECT_ROOT / "figures"
CLEAN_CSV = DATA_DIR / "clean_colleges.csv"
RESULTS_CSV = DATA_DIR / "results.csv"
RANKINGS_CSV = DATA_DIR / "rankings.csv"  # optional, only if a librarian approves

# The Scorecard uses these strings to mean "no data" (listed in data.yaml).
# "PS" and "PrivacySuppressed" mean the value was hidden because too few students.
NULL_MARKERS = ["NULL", "PrivacySuppressed", "PS", "NA"]

# ---------------------------------------------------------------------------
# Columns we keep from the raw CSV, and the friendly names we give them.
# Raw Scorecard name  ->  our name
# ---------------------------------------------------------------------------
COLUMN_RENAMES = {
    # Identity and location
    "UNITID": "unitid",
    "INSTNM": "name",
    "STABBR": "state",
    "LATITUDE": "lat",
    "LONGITUDE": "lon",
    "CONTROL": "control",            # 1 = public, 2 = private nonprofit, 3 = for-profit
    "PREDDEG": "pred_degree",        # 3 = mostly bachelor's degrees
    "CURROPER": "currently_operating",  # 1 = open, 0 = closed
    # Who the students are
    "ADM_RATE": "admit_rate",
    "SAT_AVG": "sat_avg",
    "UGDS": "undergrads",
    "PCTPELL": "pct_pell",           # share of undergrads with a Pell grant (low-income)
    "PAR_ED_PCT_1STGEN": "pct_first_gen",
    # Money and resources
    "COSTT4_A": "sticker_price",
    "NPT4_PUB": "net_price_public",
    "NPT4_PRIV": "net_price_private",
    "INEXPFTE": "spend_per_student",  # instructional spending per full-time student
    "AVGFACSAL": "fac_salary_monthly",  # NOTE: this is a MONTHLY salary
    "PFTFAC": "pct_fulltime_faculty",
    # Outcomes
    "C150_4": "grad_rate",           # finished within 6 years (150% of 4 years)
    "C150_4_PELL": "pell_grad_rate",  # same, but only Pell students
    "D150_4": "grad_cohort_size",    # how many students the grad rate is based on
    "RET_FT4": "retention_rate",
    "GRAD_DEBT_MDN": "median_debt",
    "MD_EARN_WNE_P10": "earnings_10yr",  # median earnings 10 years after starting
}

# A school must have ALL of these or it is dropped (we can't judge it without them).
REQUIRED_OUTCOMES = ["grad_rate", "earnings_10yr"]

# Some grad rates are based on a cohort of 1 student, which makes them 0% or
# 100% by luck. We drop schools whose grad-rate cohort is smaller than this.
MIN_GRAD_COHORT = 100

# Readable labels for the "control" codes
CONTROL_LABELS = {1: "Public", 2: "Private nonprofit", 3: "For-profit"}

# Boston University's ID, used to highlight BU in printouts and charts
BU_UNITID = 164988
