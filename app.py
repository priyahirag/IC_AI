import os

from pathlib import Path

import random



import streamlit as st

import pandas as pd

import pydeck as pdk



from priority import calculate_priority, get_priority_level





# ==========================================

# PAGE SETUP

# ==========================================



st.set_page_config(
    page_title="CrisisLens | Disaster Intelligence Command Center",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root{
  --bg:#050b14;
  --panel:#0a1422;
  --panel2:#0d1929;
  --line:rgba(148,163,184,.13);
  --text:#f8fafc;
  --muted:#8495aa;
  --cyan:#22d3ee;
  --red:#ef4444;
  --orange:#f59e0b;
  --yellow:#facc15;
  --green:#22c55e;
}

html,body,[class*="css"]{font-family:Inter,Arial,sans-serif;color:#f8fafc !important}
.stMarkdown,.stMarkdown p,.stMarkdown div,.stMarkdown span,.stText{color:#f8fafc}
label,[data-testid="stWidgetLabel"] p{color:#e2e8f0 !important}
.stApp{
  background:
    radial-gradient(circle at 78% -8%,rgba(34,211,238,.08),transparent 25%),
    radial-gradient(circle at -5% 38%,rgba(37,99,235,.06),transparent 26%),
    var(--bg);
  color:var(--text);
}
.block-container{max-width:1500px;padding:1.25rem 1.5rem 3rem}
[data-testid="stHeader"]{background:rgba(5,11,20,.8)}
[data-testid="stToolbar"]{display:none}

.command-header{
  border:1px solid var(--line);
  border-radius:18px;
  background:linear-gradient(135deg,#0d1b2d,#081321);
  padding:16px 20px;
  margin-bottom:14px;
  box-shadow:0 16px 40px rgba(0,0,0,.20);
}
.command-row{display:flex;align-items:center;justify-content:space-between;gap:18px}
.brand{display:flex;align-items:center;gap:12px}
.brand-icon{
  width:44px;height:44px;border-radius:12px;
  display:flex;align-items:center;justify-content:center;
  background:linear-gradient(135deg,#ef4444,#991b1b);
  box-shadow:0 8px 22px rgba(239,68,68,.2);
  font-size:21px
}
.brand-title{font-size:52px !important;font-weight:900 !important;letter-spacing:-1.8px;line-height:.98;color:#ffffff !important;text-shadow:0 3px 22px rgba(0,0,0,.55);display:block;white-space:nowrap}
.brand-sub{font-size:16px !important;color:#e2e8f0 !important;font-weight:800 !important;letter-spacing:2.2px;margin-top:10px;text-transform:uppercase;line-height:1.25}
.status{
  display:flex;align-items:center;gap:8px;
  border:1px solid rgba(34,197,94,.24);
  background:rgba(34,197,94,.06);
  color:#86efac;border-radius:999px;
  padding:9px 13px;font-size:11px;font-weight:900;letter-spacing:1px
}
.status-dot{width:7px;height:7px;border-radius:50%;background:#22c55e;box-shadow:0 0 9px #22c55e}

.kpi{
  min-height:88px;border:1px solid var(--line);border-radius:14px;
  background:linear-gradient(145deg,#0d1b2d,#091321);
  padding:13px 14px;position:relative;overflow:hidden
}
.kpi:after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:var(--accent)}
.kpi-label{font-size:13px !important;letter-spacing:1.7px;color:#d5dfeb !important;font-weight:900 !important}
.kpi-value{font-size:42px;color:#ffffff !important;font-weight:900;line-height:1;margin-top:9px}

.section-label{font-size:12px;line-height:1.2;letter-spacing:2px;color:#67e8f9 !important;font-weight:900;text-transform:uppercase}
.section-title{font-size:34px !important;line-height:1.12;font-weight:900 !important;color:#ffffff !important;letter-spacing:-.7px;margin:6px 0 16px;text-shadow:0 3px 16px rgba(0,0,0,.55);display:block}

.section-subtitle{font-size:13px;color:#a9b8c9 !important;margin-top:-8px;margin-bottom:16px;letter-spacing:.2px}

.map-card{
  border:1px solid var(--line);border-radius:17px;
  background:#07111e;padding:6px;overflow:hidden;
  box-shadow:0 14px 35px rgba(0,0,0,.18)
}
.command-card{
  border:1px solid var(--line);border-radius:17px;
  background:linear-gradient(145deg,#0d1b2d,#081321);
  padding:16px;min-height:100%
}
.command-top{display:flex;justify-content:space-between;gap:12px;align-items:flex-start}
.case-id{font-size:32px !important;color:#ffffff !important;font-weight:900 !important;letter-spacing:-.7px}
.case-meta{font-size:15px !important;color:#d2dce8 !important;margin-top:6px;font-weight:600}
.badge{display:inline-block;padding:5px 9px;border-radius:999px;font-size:10px;font-weight:900;letter-spacing:.8px}
.critical{color:#fecaca;background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.28)}
.high{color:#fde68a;background:rgba(245,158,11,.12);border:1px solid rgba(245,158,11,.28)}
.medium{color:#fef08a;background:rgba(250,204,21,.10);border:1px solid rgba(250,204,21,.24)}
.low{color:#bbf7d0;background:rgba(34,197,94,.09);border:1px solid rgba(34,197,94,.22)}

.score-box{
  margin:12px 0;border-radius:14px;padding:14px;text-align:center;
  border:1px solid rgba(34,211,238,.15);
  background:radial-gradient(circle at 50% 40%,rgba(34,211,238,.10),transparent 65%)
}
.score{font-size:54px !important;color:#ffffff !important;font-weight:900 !important;line-height:1}
.score-caption{font-size:11px !important;color:#c1cfdd !important;letter-spacing:1.7px;font-weight:900 !important;margin-top:8px}

.signal-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px}
.signal{
  padding:8px 9px;border-radius:10px;
  background:rgba(255,255,255,.025);
  border:1px solid rgba(148,163,184,.09)
}
.signal-label{font-size:10px !important;color:#aebdcd !important;text-transform:uppercase;letter-spacing:1.1px;font-weight:900 !important}
.signal-value{font-size:16px !important;color:#ffffff !important;font-weight:800 !important;margin-top:5px}

.evidence{
  margin-top:8px;padding:9px;border-radius:10px;
  background:rgba(255,255,255,.022);
  border:1px solid rgba(148,163,184,.09)
}
.evidence-label{font-size:9px;color:#93a4b8 !important;letter-spacing:1.2px;font-weight:900;text-transform:uppercase}
.evidence-text{font-size:15px !important;color:#f1f5f9 !important;line-height:1.6;margin-top:6px;font-weight:500}

.cv-card{
  border:1px solid var(--line);border-radius:17px;
  background:linear-gradient(145deg,#0d1b2d,#081321);
  padding:15px
}
.cv-chip{
  display:inline-block;padding:8px 11px;border-radius:9px;margin:3px;
  color:#dff9ff !important;background:rgba(34,211,238,.07);
  border:1px solid rgba(34,211,238,.2);font-size:13px !important;font-weight:900 !important
}
.image-frame{
  border-radius:13px;overflow:hidden;
  border:1px solid rgba(148,163,184,.14);
  background:#050b14;padding:5px
}

.queue-card{
  border:1px solid var(--line);border-radius:17px;
  background:linear-gradient(145deg,#0d1b2d,#081321);
  padding:7px;overflow:auto
}
.queue{width:100%;border-collapse:separate;border-spacing:0 4px}
.queue th{padding:9px 10px;color:#94a3b8 !important;font-size:10px;text-align:left;text-transform:uppercase;letter-spacing:1.2px;font-weight:900}
.queue td{padding:9px;background:rgba(255,255,255,.025);border-top:1px solid rgba(148,163,184,.07);border-bottom:1px solid rgba(148,163,184,.07);font-size:12px;color:#f1f5f9 !important}
.queue td:first-child{border-left:1px solid rgba(148,163,184,.07);border-radius:8px 0 0 8px}
.queue td:last-child{border-right:1px solid rgba(148,163,184,.07);border-radius:0 8px 8px 0}
.queue-score{font-weight:900;color:#ffffff !important;font-size:13px}

div[data-testid="stSelectbox"]>div{background:#0a1422;border:1px solid rgba(148,163,184,.2);border-radius:10px}
div[data-testid="stSelectbox"] [data-baseweb="select"] *{color:#f8fafc !important;font-size:15px !important}
div[data-testid="stSelectbox"] svg{fill:#cbd5e1 !important}
div[data-testid="stButton"] button{
  border-radius:10px;border:1px solid rgba(34,211,238,.23);
  background:linear-gradient(135deg,rgba(34,211,238,.09),rgba(37,99,235,.08));
  color:#e0f2fe;font-weight:700
}
div[data-testid="stButton"] button:hover{border-color:rgba(34,211,238,.55)}
.footer{text-align:center;color:#71839a;font-size:10px;letter-spacing:.7px;margin-top:18px}
@media(max-width:900px){
  .brand-title{font-size:38px}
  .brand-sub{font-size:11px;letter-spacing:1.2px}
  .section-title{font-size:25px}
  .command-row{flex-direction:column;align-items:flex-start}
  .signal-grid{grid-template-columns:1fr}
}

/* V6 PROFESSIONAL KPI + CV OVERRIDES */

.kpi-grid{
  display:grid;
  grid-template-columns:repeat(5,minmax(0,1fr));
  gap:12px;
  margin:8px 0 24px;
}
.kpi-card{
  position:relative;
  min-height:132px;
  padding:17px 18px 15px;
  border-radius:16px;
  background:linear-gradient(145deg,#101f32,#091421);
  border:1px solid rgba(148,163,184,.18);
  box-shadow:0 12px 30px rgba(0,0,0,.18);
  overflow:hidden;
}
.kpi-card:after{
  content:"";
  position:absolute;
  left:0;right:0;bottom:0;height:3px;
}
.kpi-active:after{background:#22d3ee}
.kpi-critical:after{background:#ef4444}
.kpi-high:after{background:#f59e0b}
.kpi-medium:after{background:#facc15}
.kpi-low:after{background:#22c55e}
.kpi-top{
  display:flex;
  align-items:center;
  gap:9px;
}
.kpi-dot{
  width:9px;height:9px;border-radius:50%;display:inline-block;
  box-shadow:0 0 10px currentColor;
}
.kpi-active .kpi-dot{background:#22d3ee;color:#22d3ee}
.kpi-critical .kpi-dot{background:#ef4444;color:#ef4444}
.kpi-high .kpi-dot{background:#f59e0b;color:#f59e0b}
.kpi-medium .kpi-dot{background:#facc15;color:#facc15}
.kpi-low .kpi-dot{background:#22c55e;color:#22c55e}
.kpi-label{
  color:#f8fafc !important;
  font-size:12px !important;
  font-weight:900 !important;
  letter-spacing:1.5px !important;
}
.kpi-number{
  color:#ffffff !important;
  font-size:43px !important;
  line-height:1 !important;
  font-weight:900 !important;
  margin-top:14px;
}
.kpi-caption{
  color:#aebdcd !important;
  font-size:10px !important;
  font-weight:700 !important;
  letter-spacing:.4px;
  margin-top:8px;
}

.cv-command-card{
  border:1px solid rgba(148,163,184,.18);
  border-radius:20px;
  background:linear-gradient(145deg,#0e1c2e,#081321);
  padding:22px;
  box-shadow:0 18px 42px rgba(0,0,0,.22);
}
.cv-command-header{
  display:flex;
  align-items:flex-start;
  justify-content:space-between;
  gap:18px;
  padding-bottom:18px;
  border-bottom:1px solid rgba(148,163,184,.12);
}
.cv-eyebrow{
  color:#67e8f9 !important;
  font-size:10px !important;
  font-weight:900 !important;
  letter-spacing:2.2px !important;
  text-transform:uppercase;
}
.cv-main-title{
  color:#ffffff !important;
  font-size:25px !important;
  line-height:1.15 !important;
  font-weight:900 !important;
  margin-top:5px;
}
.cv-main-sub{
  color:#aebdcd !important;
  font-size:13px !important;
  margin-top:6px;
  line-height:1.5;
}
.cv-status{
  flex:0 0 auto;
  padding:9px 12px;
  border-radius:999px;
  color:#fde68a !important;
  background:rgba(250,204,21,.08);
  border:1px solid rgba(250,204,21,.22);
  font-size:10px !important;
  font-weight:900 !important;
  letter-spacing:1px;
  white-space:nowrap;
}
.cv-status strong{color:#fff7a8 !important;margin-left:5px}

.cv-metrics{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:10px;
  margin:17px 0;
}
.cv-metric{
  display:flex;
  align-items:center;
  gap:11px;
  min-height:70px;
  padding:11px 13px;
  border-radius:13px;
  background:rgba(255,255,255,.035);
  border:1px solid rgba(148,163,184,.11);
}
.cv-metric-icon{
  width:38px;height:38px;
  display:flex;align-items:center;justify-content:center;
  border-radius:10px;
  background:rgba(34,211,238,.08);
  font-size:18px;
}
.cv-metric-label{
  color:#9fb0c3 !important;
  font-size:9px !important;
  font-weight:900 !important;
  letter-spacing:1.2px;
}
.cv-metric-value{
  color:#ffffff !important;
  font-size:21px !important;
  font-weight:900 !important;
  margin-top:2px;
}

.cv-info-grid{
  display:grid;
  grid-template-columns:1fr 1fr 1.25fr;
  gap:10px;
}
.cv-info-panel{
  padding:14px 15px;
  border-radius:13px;
  background:rgba(255,255,255,.025);
  border:1px solid rgba(148,163,184,.10);
  min-height:116px;
}
.cv-info-label{
  color:#67e8f9 !important;
  font-size:9px !important;
  font-weight:900 !important;
  letter-spacing:1.5px;
}
.cv-info-title{
  color:#ffffff !important;
  font-size:14px !important;
  font-weight:800 !important;
  margin-top:7px;
}
.cv-info-text{
  color:#cbd5e1 !important;
  font-size:12px !important;
  line-height:1.55;
  margin-top:6px;
}
.cv-info-text strong{color:#ffffff !important}

@media (max-width: 1050px){
  .kpi-grid{grid-template-columns:repeat(3,1fr)}
  .cv-metrics{grid-template-columns:repeat(2,1fr)}
  .cv-info-grid{grid-template-columns:1fr}
}
@media (max-width: 650px){
  .kpi-grid{grid-template-columns:repeat(2,1fr)}
  .cv-command-header{flex-direction:column}
  .cv-metrics{grid-template-columns:1fr 1fr}
}



/* V8 CLEAN COMMAND-CENTER UI */

.native-kpi{
  min-height:118px;
  box-sizing:border-box;
  padding:16px 16px 14px;
  border:1px solid rgba(148,163,184,.18);
  border-radius:14px;
  background:linear-gradient(145deg,#102036,#0a1524);
  border-bottom:3px solid var(--accent);
  box-shadow:0 10px 26px rgba(0,0,0,.18);
}
.native-kpi-label{
  color:#f8fafc !important;
  font-size:11px !important;
  font-weight:900 !important;
  letter-spacing:1.4px !important;
  white-space:nowrap;
}
.native-kpi-dot{
  display:inline-block;
  width:8px;height:8px;
  margin-right:7px;
  border-radius:50%;
  background:var(--accent);
  box-shadow:0 0 9px var(--accent);
}
.native-kpi-value{
  color:#ffffff !important;
  font-size:38px !important;
  font-weight:900 !important;
  line-height:1 !important;
  margin-top:15px;
}
.native-kpi-caption{
  color:#aebdcd !important;
  font-size:9px !important;
  font-weight:700 !important;
  letter-spacing:.8px;
  margin-top:7px;
}
.section-gap{height:10px}

[data-testid="stVerticalBlockBorderWrapper"]{
  border-color:rgba(148,163,184,.18) !important;
  background:linear-gradient(145deg,#0d1b2d,#081321) !important;
  border-radius:18px !important;
}

.cv-overline{
  color:#67e8f9 !important;
  font-size:10px !important;
  font-weight:900 !important;
  letter-spacing:2px !important;
}
.cv-title{
  color:#ffffff !important;
  font-size:24px !important;
  font-weight:900 !important;
  margin-top:5px;
}
.cv-description{
  color:#aebdcd !important;
  font-size:12px !important;
  margin-top:5px;
}
.cv-description strong{color:#ffffff !important}
.cv-severity-badge{
  text-align:center;
  padding:9px 8px;
  border:1px solid rgba(250,204,21,.25);
  background:rgba(250,204,21,.07);
  border-radius:10px;
  color:#facc15 !important;
  font-size:9px !important;
  font-weight:900 !important;
  letter-spacing:1px;
}
.cv-severity-badge strong{
  color:#ffffff !important;
  font-size:12px !important;
}
.cv-divider{
  height:1px;
  background:rgba(148,163,184,.13);
  margin:15px 0;
}
.cv-stat{
  min-height:84px;
  padding:12px;
  border-radius:12px;
  background:#0a1727;
  border:1px solid rgba(148,163,184,.12);
}
.cv-stat-icon{
  font-size:17px;
  line-height:1;
  margin-bottom:8px;
}
.cv-stat-label{
  color:#9fb0c3 !important;
  font-size:9px !important;
  font-weight:900 !important;
  letter-spacing:1.2px !important;
}
.cv-stat-value{
  color:#ffffff !important;
  font-size:20px !important;
  font-weight:900 !important;
  margin-top:3px;
}
.cv-info{
  min-height:115px;
  padding:14px;
  border-radius:12px;
  background:#0a1727;
  border:1px solid rgba(148,163,184,.12);
}
.cv-info-label{
  color:#67e8f9 !important;
  font-size:9px !important;
  font-weight:900 !important;
  letter-spacing:1.5px !important;
}
.cv-info-title{
  color:#ffffff !important;
  font-size:14px !important;
  font-weight:800 !important;
  margin-top:7px;
}
.cv-info-body{
  color:#cbd5e1 !important;
  font-size:11px !important;
  line-height:1.55 !important;
  margin-top:6px;
}
.cv-info-body strong{color:#ffffff !important}

[data-baseweb="select"] > div{
  background:#0d1929 !important;
  color:#ffffff !important;
  border-color:rgba(148,163,184,.25) !important;
}
[data-baseweb="select"] *{color:#ffffff !important}
.stButton button{
  color:#ffffff !important;
  background:#102238 !important;
  border:1px solid rgba(34,211,238,.30) !important;
}
</style>
""", unsafe_allow_html=True)





st.markdown(
    """
    <div class="command-header">
      <div class="command-row">
        <div class="brand">
          <div class="brand-icon">🚨</div>
          <div>
            <div class="brand-title">CRISISLENS</div>
            <div class="brand-sub">DISASTER INTELLIGENCE COMMAND CENTER</div>
          </div>
        </div>
        <div class="status"><span class="status-dot"></span>SYSTEM ONLINE</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)



# ==========================================

# YOLO IMAGE / CV PROFILES

# ==========================================

#

# These are Nikhil's three existing YOLO

# outputs.

#

# Each profile contains:

# - image

# - person count

# - car count

# - boat count

# - CV severity

#

# A simulated incident will randomly receive

# one of these profiles.

# ==========================================



YOLO_PROFILES = [



    {

        "yolo_image": "flood1_detected.jpg",

        "person_count": 0,

        "car_count": 8,

        "boat_count": 0,

        "cv_severity": "MEDIUM"

    },



    {

        "yolo_image": "flood2_detected.jpg",

        "person_count": 1,

        "car_count": 2,

        "boat_count": 0,

        "cv_severity": "LOW"

    },



    {

        "yolo_image": "flood3_detected.jpg",

        "person_count": 0,

        "car_count": 0,

        "boat_count": 4,

        "cv_severity": "LOW"

    }



]





# ==========================================

# URGENCY CALCULATION

# ==========================================



def calculate_urgency(evidence):



    text = str(evidence).lower()



    if "trapped" in text or "immediate danger" in text:

        return 100



    elif "rescue" in text or "people affected" in text:

        return 90



    elif "blocked" in text or "rapid response" in text:

        return 75



    elif "damage" in text:

        return 60



    else:

        return 40





# ==========================================

# COMPUTER VISION URGENCY ADJUSTMENT

# ==========================================



def calculate_cv_adjustment(row):



    adjustment = 0



    person_count = pd.to_numeric(

        row.get("person_count", 0),

        errors="coerce"

    )



    car_count = pd.to_numeric(

        row.get("car_count", 0),

        errors="coerce"

    )



    boat_count = pd.to_numeric(

        row.get("boat_count", 0),

        errors="coerce"

    )



    if pd.isna(person_count):

        person_count = 0



    if pd.isna(car_count):

        car_count = 0



    if pd.isna(boat_count):

        boat_count = 0



    cv_severity = str(

        row.get("cv_severity", "N/A")

    ).upper()





    # --------------------------------------

    # PEOPLE

    # --------------------------------------



    if person_count >= 5:

        adjustment += 15



    elif person_count >= 1:

        adjustment += 10





    # --------------------------------------

    # CARS

    # --------------------------------------



    if car_count >= 10:

        adjustment += 15



    elif car_count >= 5:

        adjustment += 10



    elif car_count >= 1:

        adjustment += 5





    # --------------------------------------

    # BOATS

    # --------------------------------------



    if boat_count >= 5:

        adjustment += 15



    elif boat_count >= 1:

        adjustment += 10





    # --------------------------------------

    # CV SEVERITY

    # --------------------------------------



    if cv_severity == "HIGH":

        adjustment += 10



    elif cv_severity == "MEDIUM":

        adjustment += 5





    # Maximum CV contribution

    adjustment = min(

        adjustment,

        25

    )



    return adjustment





# ==========================================

# LOAD DATA

# ==========================================



if "data" not in st.session_state:



    # --------------------------------------

    # Load main incident CSV

    # --------------------------------------



    st.session_state.data = pd.read_csv(

        "final_incidents.csv"

    )





    # --------------------------------------

    # Load CV results

    # --------------------------------------



    if os.path.exists(

        "cv_results.csv"

    ):



        cv_df = pd.read_csv(

            "cv_results.csv"

        )



        st.session_state.data = (

            st.session_state.data.merge(

                cv_df,

                on="incident_id",

                how="left"

            )

        )



    else:



        st.session_state.data[

            "person_count"

        ] = 0



        st.session_state.data[

            "car_count"

        ] = 0



        st.session_state.data[

            "boat_count"

        ] = 0



        st.session_state.data[

            "cv_severity"

        ] = "N/A"





# ==========================================

# ENSURE CV COLUMNS

# ==========================================



if "person_count" not in st.session_state.data.columns:

    st.session_state.data["person_count"] = 0



if "car_count" not in st.session_state.data.columns:

    st.session_state.data["car_count"] = 0



if "boat_count" not in st.session_state.data.columns:

    st.session_state.data["boat_count"] = 0



if "cv_severity" not in st.session_state.data.columns:

    st.session_state.data["cv_severity"] = "N/A"





# ==========================================

# ASSIGN EXISTING YOLO IMAGES TO KNOWN

# INCIDENTS

# ==========================================



known_yolo_images = {

    "INC001": "flood1_detected.jpg",

    "INC002": "flood2_detected.jpg",

    "INC003": "flood3_detected.jpg"

}





if "yolo_image" not in st.session_state.data.columns:



    st.session_state.data[

        "yolo_image"

    ] = st.session_state.data[

        "incident_id"

    ].map(

        known_yolo_images

    )





# ==========================================

# BASE URGENCY

# ==========================================



if "base_urgency" not in st.session_state.data.columns:



    st.session_state.data[

        "base_urgency"

    ] = st.session_state.data[

        "evidence"

    ].apply(

        calculate_urgency

    )





# ==========================================
# SIMULATE NEW INCIDENT
# ==========================================

if st.button("🚨 Simulate New Incident"):

    # Cycle through all four priority levels for the demo.
    # priority.py remains unchanged.
    demo_profiles = [
        {
            "priority_target": "MEDIUM",
            "severity": 55,
            "exposure": 50,
            "vulnerability": 45,
            "evidence": "Floodwater is affecting the area"
        },
        {
            "priority_target": "HIGH",
            "severity": 70,
            "exposure": 65,
            "vulnerability": 60,
            "evidence": "Heavy flooding reported, people affected"
        },
        {
            "priority_target": "CRITICAL",
            "severity": 95,
            "exposure": 90,
            "vulnerability": 85,
            "evidence": "People are trapped and immediate rescue is required"
        },
        {
            "priority_target": "LOW",
            "severity": 30,
            "exposure": 25,
            "vulnerability": 25,
            "evidence": "Minor floodwater reported in the area"
        }
    ]

    if "demo_priority_index" not in st.session_state:
        st.session_state.demo_priority_index = 0

    demo = demo_profiles[
        st.session_state.demo_priority_index % len(demo_profiles)
    ]
    st.session_state.demo_priority_index += 1

    # Reuse Nikhil's existing YOLO outputs.
    selected_yolo = YOLO_PROFILES[
        st.session_state.demo_priority_index % len(YOLO_PROFILES)
    ]

    # Create a unique incident ID.
    new_id = f"INC{random.randint(100, 999)}"

    existing_ids = set(
        st.session_state.data["incident_id"].astype(str)
    )

    while new_id in existing_ids:
        new_id = f"INC{random.randint(100, 999)}"

    new_evidence = demo["evidence"]
    new_base_urgency = calculate_urgency(new_evidence)

    new_incident = {
        "incident_id": new_id,
        "disaster_type": "Flood",
        "severity": demo["severity"],
        "evidence": new_evidence,

        "location": random.choice([
            "Electronic City",
            "Whitefield",
            "Peenya",
            "Kengeri",
            "Bommanahalli"
        ]),

        "latitude": round(
            random.uniform(12.85, 13.05), 4
        ),

        "longitude": round(
            random.uniform(77.45, 77.75), 4
        ),

        "population_exposed": random.randint(
            1000, 8000
        ),

        "exposure": demo["exposure"],
        "vulnerability": demo["vulnerability"],
        "base_urgency": new_base_urgency,

        # Existing Nikhil YOLO/CV evidence.
        "person_count": selected_yolo["person_count"],
        "car_count": selected_yolo["car_count"],
        "boat_count": selected_yolo["boat_count"],
        "cv_severity": selected_yolo["cv_severity"],
        "yolo_image": selected_yolo["yolo_image"]
    }

    st.session_state.data = pd.concat(
        [
            st.session_state.data,
            pd.DataFrame([new_incident])
        ],
        ignore_index=True
    )

    st.rerun()


# ==========================================

# CURRENT DATA

# ==========================================



data = st.session_state.data





# ==========================================

# CALCULATE CV ADJUSTMENT

# ==========================================



data[

    "cv_adjustment"

] = data.apply(

    calculate_cv_adjustment,

    axis=1

)





# ==========================================

# CALCULATE FINAL URGENCY

# ==========================================



data[

    "urgency"

] = (

    data["base_urgency"]

    + data["cv_adjustment"]

).clip(

    upper=100

)





# ==========================================

# CALCULATE PRIORITY

# ==========================================



data[

    "priority_score"

] = data.apply(



    lambda row:

        calculate_priority(



            row["severity"],



            row["exposure"],



            row["vulnerability"],



            row["urgency"]



        ),



    axis=1



)





data[

    "priority"

] = data[

    "priority_score"

].apply(

    get_priority_level

)





# ==========================================

# DASHBOARD SUMMARY

# ==========================================



critical = len(

    data[

        data["priority"]

        == "CRITICAL"

    ]

)



high = len(

    data[

        data["priority"]

        == "HIGH"

    ]

)



medium = len(

    data[

        data["priority"]

        == "MEDIUM"

    ]

)



low = len(

    data[

        data["priority"]

        == "LOW"

    ]

)






# ==========================================
# COMMAND CENTER KPI STRIP
# ==========================================

kpi_data = [
    ("ACTIVE", len(data), "LIVE INCIDENTS", "#22d3ee"),
    ("CRITICAL", critical, "IMMEDIATE ATTENTION", "#ef4444"),
    ("HIGH", high, "PRIORITY RESPONSE", "#f59e0b"),
    ("MEDIUM", medium, "MONITOR CLOSELY", "#facc15"),
    ("LOW", low, "ROUTINE MONITORING", "#22c55e"),
]

kpi_cols = st.columns(5, gap="small")

for col, (label, value, caption, accent) in zip(kpi_cols, kpi_data):
    with col:
        st.markdown(
            f"""
            <div class="native-kpi" style="--accent:{accent};">
                <div class="native-kpi-label">
                    <span class="native-kpi-dot"></span>{label}
                </div>
                <div class="native-kpi-value">{value}</div>
                <div class="native-kpi-caption">{caption}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)

# ==========================================
# COMMAND CENTER: MAP + INCIDENT COMMAND
# ==========================================

st.markdown(
    '<div class="section-label">GEOSPATIAL COMMAND</div>'
    '<div class="section-title">Live Incident Map</div>',
    unsafe_allow_html=True
)

incident_options = data["incident_id"].tolist()

if (
    "selected_incident_id" not in st.session_state
    or st.session_state["selected_incident_id"] not in incident_options
):
    st.session_state["selected_incident_id"] = incident_options[0]

selected_incident_id = st.selectbox(
    "Select incident",
    incident_options,
    index=incident_options.index(st.session_state["selected_incident_id"]),
    key="incident_selector",
    label_visibility="collapsed"
)

st.session_state["selected_incident_id"] = selected_incident_id

selected_incident = data[
    data["incident_id"] == selected_incident_id
].iloc[0]

def get_marker_color(priority):
    if priority == "CRITICAL":
        return [255, 0, 0]
    elif priority == "HIGH":
        return [255, 140, 0]
    elif priority == "MEDIUM":
        return [255, 200, 0]
    return [0, 180, 0]

map_data = data.copy()
map_data["color"] = map_data["priority"].apply(get_marker_color)
map_data["radius"] = map_data["incident_id"].apply(
    lambda x: 1000 if x == selected_incident_id else 500
)

layer = pdk.Layer(
    "ScatterplotLayer",
    data=map_data,
    get_position=["longitude", "latitude"],
    get_fill_color="color",
    get_radius="radius",
    pickable=True,
    auto_highlight=True
)

view_state = pdk.ViewState(
    latitude=selected_incident["latitude"],
    longitude=selected_incident["longitude"],
    zoom=11
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    tooltip={
        "text":
            "Incident: {incident_id}\n"
            "Type: {disaster_type}\n"
            "Priority: {priority}\n"
            "Score: {priority_score}\n"
            "Urgency: {urgency}\n"
            "CV Severity: {cv_severity}\n"
            "Location: {location}"
    }
)

map_col, command_col = st.columns([1.55, 1], gap="medium")

with map_col:
    st.markdown('<div class="section-label">LIVE INCIDENT MAP</div>', unsafe_allow_html=True)
    st.markdown('<div class="map-card">', unsafe_allow_html=True)
    map_event = st.pydeck_chart(
        deck,
        width="stretch",
        on_select="rerun",
        selection_mode="single-object"
    )
    st.markdown('</div>', unsafe_allow_html=True)

if map_event and map_event.selection:
    selected_objects = map_event.selection.get("objects", [])
    if selected_objects:
        clicked_id = selected_objects[0].get("incident_id")
        if clicked_id and clicked_id in incident_options:
            st.session_state["selected_incident_id"] = clicked_id
            st.rerun()

priority_value = str(selected_incident["priority"]).upper()
badge_class = {
    "CRITICAL": "critical",
    "HIGH": "high",
    "MEDIUM": "medium",
    "LOW": "low"
}.get(priority_value, "low")

person_count = selected_incident.get("person_count", 0)
car_count = selected_incident.get("car_count", 0)
boat_count = selected_incident.get("boat_count", 0)
cv_severity = selected_incident.get("cv_severity", "N/A")
yolo_image_name = selected_incident.get("yolo_image", "N/A")

with command_col:
    st.markdown(f"""
    <div class="command-card">
      <div class="section-label">INCIDENT COMMAND</div>
      <div class="command-top">
        <div>
          <div class="case-id">{selected_incident['incident_id']}</div>
          <div class="case-meta">{selected_incident['disaster_type']} · {selected_incident['location']}</div>
        </div>
        <span class="badge {badge_class}">{priority_value}</span>
      </div>

      <div class="score-box">
        <div class="score">{selected_incident['priority_score']}</div>
        <div class="score-caption">PRIORITY SCORE / 100</div>
      </div>

      <div class="signal-grid">
        <div class="signal"><div class="signal-label">Severity</div><div class="signal-value">{selected_incident['severity']}/100</div></div>
        <div class="signal"><div class="signal-label">Exposure</div><div class="signal-value">{selected_incident['exposure']}/100</div></div>
        <div class="signal"><div class="signal-label">Vulnerability</div><div class="signal-value">{selected_incident['vulnerability']}/100</div></div>
        <div class="signal"><div class="signal-label">Urgency</div><div class="signal-value">{selected_incident['urgency']}/100</div></div>
        <div class="signal"><div class="signal-label">Population Exposed</div><div class="signal-value">{selected_incident['population_exposed']:,}</div></div>
        <div class="signal"><div class="signal-label">CV Adjustment</div><div class="signal-value">+{selected_incident['cv_adjustment']}</div></div>
      </div>

      <div class="evidence">
        <div class="evidence-label">FIELD EVIDENCE</div>
        <div class="evidence-text">{selected_incident['evidence']}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ==========================================

# ==========================================
# COMPUTER VISION EVIDENCE
# ==========================================

st.markdown(
    '<div class="section-label">COMPUTER VISION</div>'
    '<div class="section-title">Computer Vision Evidence Intelligence</div>'
    '<div class="section-subtitle">YOLO detections used as supporting evidence for incident urgency and priority</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    cv_header_left, cv_header_right = st.columns([4, 1], gap="medium")

    with cv_header_left:
        st.markdown(
            '<div class="cv-overline">VISION ANALYTICS</div>'
            '<div class="cv-title">Incident Evidence Profile</div>'
            f'<div class="cv-description">Computer-vision observations linked to <strong>{selected_incident_id}</strong></div>',
            unsafe_allow_html=True,
        )

    with cv_header_right:
        st.markdown(
            f'<div class="cv-severity-badge">CV SEVERITY<br><strong>{cv_severity}</strong></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div class='cv-divider'></div>", unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4, gap="small")

    cv_items = [
        (m1, "PERSONS", person_count, "👤"),
        (m2, "VEHICLES", car_count, "🚗"),
        (m3, "BOATS", boat_count, "🚤"),
        (m4, "CV SEVERITY", cv_severity, "🧠"),
    ]

    for col, label, value, icon in cv_items:
        with col:
            st.markdown(
                f"""
                <div class="cv-stat">
                    <div class="cv-stat-icon">{icon}</div>
                    <div class="cv-stat-label">{label}</div>
                    <div class="cv-stat-value">{value}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("<div class='cv-divider'></div>", unsafe_allow_html=True)

    info1, info2, info3 = st.columns(3, gap="small")

    with info1:
        st.markdown(
            f"""
            <div class="cv-info">
                <div class="cv-info-label">MODEL SIGNAL</div>
                <div class="cv-info-title">Urgency contribution</div>
                <div class="cv-info-body">
                    Computer vision contributed
                    <strong>+{selected_incident['cv_adjustment']}</strong>
                    points to final urgency.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with info2:
        st.markdown(
            f"""
            <div class="cv-info">
                <div class="cv-info-label">YOLO ASSET</div>
                <div class="cv-info-title">Annotated evidence</div>
                <div class="cv-info-body">
                    <strong>{yolo_image_name}</strong><br>
                    Bounding boxes identify detected objects.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with info3:
        st.markdown(
            f"""
            <div class="cv-info">
                <div class="cv-info-label">ANALYTIC CONTEXT</div>
                <div class="cv-info-title">How evidence is used</div>
                <div class="cv-info-body">
                    Visual detections support the incident priority assessment.
                    Current CV severity: <strong>{cv_severity}</strong>.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# YOLO DETECTION IMAGE

# ==========================================



st.markdown(
    '<div class="section-label">DETECTION OUTPUT</div>'
    '<div class="section-title">YOLO Detection Evidence</div>'
    '<div class="section-subtitle">Detected objects and annotated visual evidence from the computer vision model</div>',
    unsafe_allow_html=True
)





BASE_DIR = Path(

    __file__

).resolve().parent





OUTPUT_DIR = (

    BASE_DIR / "output"

)





# ------------------------------------------

# Get image assigned to selected incident

# ------------------------------------------



selected_yolo_image = selected_incident.get(

    "yolo_image",

    None

)





if pd.isna(selected_yolo_image):



    selected_yolo_image = None





if selected_yolo_image:



    image_path = (

        OUTPUT_DIR

        / str(selected_yolo_image)

    )





    if image_path.is_file():



        st.image(



            str(image_path),



            caption=(

                f"YOLO Detection — "

                f"{selected_incident_id}"

                f" — "

                f"{selected_yolo_image}"

            ),



            width="stretch"



        )



    else:



        st.error(

            "YOLO image could not be found."

        )



        st.write(

            f"Expected: "

            f"{image_path}"

        )





else:



    st.info(

        "No YOLO detection image "

        "assigned to this incident."

    )





# ==========================================

# ==========================================
# RESPONSE QUEUE
# ==========================================

st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
st.markdown(
    '<div class="section-label">RESPONSE OPERATIONS</div>'
    '<div class="section-title">Priority Response Queue</div>',
    unsafe_allow_html=True
)

queue = data.sort_values("priority_score", ascending=False).head(8)
rows = []

for _, incident in queue.iterrows():
    p = str(incident["priority"]).upper()
    cls = {
        "CRITICAL": "critical",
        "HIGH": "high",
        "MEDIUM": "medium",
        "LOW": "low"
    }.get(p, "low")

    rows.append(
        f"<tr>"
        f"<td><strong>{incident['incident_id']}</strong></td>"
        f"<td>{incident['disaster_type']}</td>"
        f"<td><span class='badge {cls}'>{p}</span></td>"
        f"<td class='queue-score'>{incident['priority_score']}</td>"
        f"<td>{incident['location']}</td>"
        f"<td>{incident['urgency']}</td>"
        f"</tr>"
    )

st.markdown(
    "<div class='queue-card'><table class='queue'>"
    "<thead><tr><th>Incident</th><th>Type</th><th>Priority</th><th>Score</th><th>Location</th><th>Urgency</th></tr></thead>"
    "<tbody>" + "".join(rows) + "</tbody></table></div>",
    unsafe_allow_html=True
)

st.markdown(
    '<div class="footer">CRISISLENS · AI-ASSISTED DISASTER INTELLIGENCE · HACKATHON PROTOTYPE</div>',
    unsafe_allow_html=True
)
