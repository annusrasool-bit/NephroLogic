{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import kdigo_logic as core\
\
st.set_page_config(page_title="NephroLogic AI", page_icon="kidney", layout="wide")\
\
# Title\
st.title("\uc0\u55356 \u57317  NephroLogic: KDIGO Evaluation Engine")\
st.markdown("---")\
\
# Sidebar: Setting Selection\
mode = st.sidebar.radio("Select Mode", ["Clinic (Chronic)", "ER (Acute)", "Dialysis Unit"])\
\
# --- SHARED INPUTS ---\
col1, col2, col3 = st.columns(3)\
with col1:\
    age = st.number_input("Age", value=50)\
    sex = st.selectbox("Sex", ["Male", "Female"])\
with col2:\
    creatinine = st.number_input("Creatinine (mg/dL)", value=1.0, format="%.2f")\
    # Simple eGFR calc (CKD-EPI approximation for demo)\
    egfr = st.number_input("eGFR (Auto-calc or Manual)", value=90)\
with col3:\
    uacr = st.number_input("uACR (mg/g)", value=20)\
    potassium = st.number_input("Potassium (mmol/L)", value=4.0)\
\
# --- CLINIC MODE LOGIC ---\
if mode == "Clinic (Chronic)":\
    st.header("\uc0\u55357 \u57057 \u65039  Renoprotection & Progression")\
    \
    # Clinical Context\
    c1, c2 = st.columns(2)\
    with c1:\
        has_dm = st.checkbox("Diabetes Mellitus")\
        has_htn = st.checkbox("Hypertension")\
        sbp = st.number_input("Systolic BP", value=125)\
        dbp = st.number_input("Diastolic BP", value=80)\
    with c2:\
        on_ace_arb = st.checkbox("On ACEi / ARB?")\
        on_sglt2 = st.checkbox("On SGLT2 Inhibitor?")\
        on_mra = st.checkbox("On Finerenone/MRA?")\
\
    # --- PROCESS DATA ---\
    g_stage = core.get_g_stage(egfr)\
    a_stage = core.get_a_stage(uacr)\
    risk_color = core.get_risk_color(g_stage, a_stage)\
    \
    # Pack data for logic\
    patient_data = \{\
        'age': age, 'sex': sex, 'creatinine': creatinine, 'egfr': egfr,\
        'uacr': uacr, 'potassium': potassium, 'has_dm': has_dm,\
        'has_htn': has_htn, 'sbp': sbp, 'dbp': dbp,\
        'on_ace_arb': on_ace_arb, 'on_sglt2': on_sglt2, 'on_mra': on_mra,\
        'g_stage': g_stage, 'a_stage': a_stage\
    \}\
\
    # --- DISPLAY RESULTS ---\
    st.divider()\
    r1, r2 = st.columns([1, 2])\
    \
    with r1:\
        st.subheader("Staging")\
        st.metric(label="KDIGO Stage", value=f"\{g_stage\} / \{a_stage\}")\
        if risk_color == "Red":\
            st.error(f"RISK: \{risk_color\} (Very High)")\
        elif risk_color == "Orange":\
            st.warning(f"RISK: \{risk_color\} (High)")\
        elif risk_color == "Yellow":\
            st.warning(f"RISK: \{risk_color\} (Moderate)")\
        else:\
            st.success(f"RISK: \{risk_color\} (Low)")\
\
    with r2:\
        st.subheader("\uc0\u55358 \u56598  AI Recommendations")\
        recs = core.check_renoprotection(patient_data)\
        if recs:\
            for r in recs:\
                st.write(r)\
        else:\
            st.success("\uc0\u9989  Excellent Guideline Adherence!")\
\
    # --- GENERATE NOTE ---\
    st.divider()\
    note = core.generate_note(patient_data, recs, risk_color)\
    st.text_area("Copy Note to EMR", note, height=300)\
\
# --- ER MODE LOGIC ---\
elif mode == "ER (Acute)":\
    st.header("\uc0\u55357 \u57000  Acute Threat Assessment")\
    st.error("Checking Life Threats (AEIOU)...")\
    \
    if potassium > 6.0:\
        st.error(f"\uc0\u55357 \u57041  CRITICAL: Hyperkalemia (K+ \{potassium\}). Order ECG & Shift K+.")\
    \
    aeiou_check = st.expander("Dialysis Urgency Checklist", expanded=True)\
    with aeiou_check:\
        st.checkbox("Acidosis (pH < 7.15)")\
        st.checkbox("Electrolytes (Refractory HyperK)")\
        st.checkbox("Intoxication")\
        st.checkbox("Overload (Pulm Edema)")\
        st.checkbox("Uremia (Pericarditis/Encephalopathy)")}