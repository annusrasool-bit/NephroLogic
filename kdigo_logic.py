import streamlit as st
import kdigo_logic as core

st.set_page_config(page_title="NephroLogic AI", page_icon="kidney", layout="wide")

# --- APP HEADER ---
st.title("🏥 NephroLogic: KDIGO Evaluation Engine")
st.markdown("---")

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Clinical Settings")
    mode = st.radio("Select Workflow", ["Clinic (Chronic)", "ER (Acute)", "Dialysis Unit"])
    st.info("💡 **NephroLogic V3:** Includes AKI Staging & Etiology Logic.")

# --- SHARED PATIENT DATA ---
st.subheader("📝 Patient Demographics & Vitals")
col1, col2, col3, col4 = st.columns(4)
with col1:
    age = st.number_input("Age", value=55)
    sex = st.selectbox("Sex", ["Male", "Female"])
with col2:
    creatinine = st.number_input("Current Cr (mg/dL)", value=2.5, format="%.2f")
    # For AKI Staging, we need Baseline
    baseline_cr = st.number_input("Baseline Cr (mg/dL)", value=1.0, format="%.2f")
with col3:
    egfr = st.number_input("eGFR (Current)", value=25)
    potassium = st.number_input("Potassium (K+)", value=5.2, format="%.1f")
with col4:
    sbp = st.number_input("Systolic BP", value=138)
    dbp = st.number_input("Diastolic BP", value=85)

# --- WORKFLOW: ER (ACUTE) [UPGRADED] ---
if mode == "ER (Acute)":
    st.header("🚨 Acute Kidney Injury & Emergency Consult")
    
    # 1. IMMEDIATE TRIAGE (The "Killers")
    st.subheader("1. Triage & Life Threats")
    t1, t2 = st.columns(2)
    with t1:
        st.markdown("**AEIOU Checklist**")
        aeiou_a = st.checkbox("A - Acidosis (pH < 7.15)")
        aeiou_e = st.checkbox("E - Electrolytes (K > 6.5 or ECG changes)")
        aeiou_i = st.checkbox("I - Intoxications (Li, Methanol, etc)")
        aeiou_o = st.checkbox("O - Overload (Refractory Pulmonary Edema)")
        aeiou_u = st.checkbox("U - Uremia (Pericarditis/Encephalopathy)")
        
        urgent_dialysis = any([aeiou_a, aeiou_e, aeiou_i, aeiou_o, aeiou_u])
        
    with t2:
        st.markdown("**Acid-Base & Volume**")
        ph = st.number_input("pH", value=7.32, format="%.2f")
        bicarb = st.number_input("Bicarbonate", value=18)
        volume_status = st.select_slider("Volume Status", options=["Hypovolemic", "Euvolemic", "Hypervolemic (Edema)", "Anasarca"])

    # 2. DIAGNOSTIC WORKUP
    st.divider()
    st.subheader("2. Diagnostic Intelligence")
    d1, d2 = st.columns(2)
    with d1:
        st.markdown("**Urinalysis & Output**")
        urine_output = st.selectbox("Urine Output Trend", ["Non-Oliguric (>400ml/day)", "Oliguric (<400ml/day)", "Anuric (<100ml/day)"])
        sediment = st.selectbox("Urine Sediment Microscopy", 
                                ["Bland / Hyaline Casts", 
                                 "Muddy Brown Casts", 
                                 "RBC Casts / Dysmorphic RBCs", 
                                 "WBC Casts", 
                                 "Granular Casts"])
    with d2:
        st.markdown("**Imaging & History**")
        hydronephrosis = st.checkbox("Hydronephrosis on Ultrasound?")
        nephrotoxins = st.multiselect("Recent Exposures", ["NSAIDs", "Contrast", "Aminoglycosides", "Vancomycin", "ACEi/ARB", "Chemo"])

    # --- AI LOGIC ENGINE (Internal) ---
    # A. AKI Staging (KDIGO)
    aki_stage = "No AKI"
    ratio = creatinine / baseline_cr
    if ratio >= 3.0 or creatinine >= 4.0:
        aki_stage = "Stage 3 (Severe)"
    elif ratio >= 2.0:
        aki_stage = "Stage 2 (Moderate)"
    elif ratio >= 1.5 or (creatinine - baseline_cr) >= 0.3:
        aki_stage = "Stage 1 (Mild)"
        
    # B. Etiology Guesser
    etiology_guess = "Unknown / Multifactorial"
    if hydronephrosis:
        etiology_guess = "Post-Renal Obstruction"
    elif sediment == "Muddy Brown Casts":
        etiology_guess = "Acute Tubular Necrosis (ATN)"
    elif sediment == "RBC Casts / Dysmorphic RBCs":
        etiology_guess = "Glomerulonephritis (GN) / Vasculitis"
    elif sediment == "WBC Casts":
        etiology_guess = "Interstitial Nephritis (AIN) or Pyelonephritis"
    elif volume_status == "Hypovolemic" and sediment == "Bland / Hyaline Casts":
        etiology_guess = "Pre-Renal Azotemia"

    # --- DISPLAY AI ASSESSMENT ---
    st.divider()
    st.subheader("🤖 AI Assessment & Plan")
    
    # 1. Critical Alerts
    if urgent_dialysis:
        st.error("🛑 CRITICAL: Patient meets criteria for EMERGENT DIALYSIS (AEIOU).")
    if potassium > 6.0:
        st.error(f"🛑 CRITICAL: Hyperkalemia ({potassium}). Initiate HyperK Protocol immediately.")
        
    # 2. The Diagnosis Box
    st.info(f"**Calculated Diagnosis:** {aki_stage} AKI due to likely **{etiology_guess}**.")

    # 3. Generate The Consult Note
    er_note = f"""
    NEPHROLOGY ACUTE CONSULT NOTE
    -----------------------------
    PATIENT: {age}yo {sex}
    REASON: Acute Kidney Injury (Stage: {aki_stage})
    
    VITALS/DATA:
    - Cr Trend: {baseline_cr} -> {creatinine} (Ratio: {ratio:.1f})
    - K+: {potassium} | pH: {ph} | HCO3: {bicarb}
    - Volume: {volume_status}
    - Urine: {urine_output} | Sediment: {sediment}
    
    ASSESSMENT:
    1. {aki_stage} AKI
       - Likely Etiology: {etiology_guess}
       - Risk Factors: {', '.join(nephrotoxins) if nephrotoxins else 'None'}
       
    2. Indications for RRT:
       {'[X] YES - Emergent Dialysis Indicated (AEIOU met)' if urgent_dialysis else '[ ] NO emergent indications currently'}
    
    PLAN:
    1. {'Initiate HD/CRRT' if urgent_dialysis else 'Monitor urine output and chem panels q12h'}
    2. {'Fluid Resuscitation' if volume_status == 'Hypovolemic' else 'Diuresis / Fluid Restriction'}
    3. {'Foley catheter / Urology Consult' if hydronephrosis else 'Avoid Nephrotoxins'}
    4. Workup: { 'Vasculitis serologies / Biopsy consideration' if "GN" in etiology_guess else 'Renal Ultrasound / Urine lytes' }
    """
    
    st.text_area("📋 Copy Consult Note to EMR", er_note, height=400)


# --- WORKFLOW: CLINIC (CHRONIC) ---
elif mode == "Clinic (Chronic)":
    st.header("🛡️ Chronic Kidney Disease Management")
    
    # Simple CKD inputs for context
    uacr = st.number_input("uACR (mg/g)", value=450)
    
    # Initialize 'has_ckd' logic
    has_ckd_logic = True if egfr < 60 or uacr > 30 else False

    tab1, tab2 = st.tabs(["Clinical Data", "Assessment & Plan"])
    
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Comorbidities")
            has_dm = st.checkbox("Diabetes Mellitus (T2D)")
            has_htn = st.checkbox("Hypertension")
        with c2:
            st.subheader("Current Medications")
            on_ace_arb = st.checkbox("On ACEi or ARB")
            on_sglt2 = st.checkbox("On SGLT2 Inhibitor")
            on_mra = st.checkbox("On ns-MRA (Finerenone)")

    with tab2:
        # 1. Staging Engine
        g_stage = core.get_g_stage(egfr)
        a_stage = core.get_a_stage(uacr)
        risk_color = core.get_risk_color(g_stage, a_stage)
        
        st.subheader(f"Diagnosis: CKD {g_stage}{a_stage}")
        
        if risk_color == "Red":
            st.error(f"🚨 PROGNOSIS: Very High Risk")
        elif risk_color == "Orange":
            st.warning(f"⚠️ PROGNOSIS: High Risk")
        else:
            st.success(f"✅ PROGNOSIS: Low/Mod Risk")

        # 2. Recommendation Engine
        pt_data = {
            'age': age, 'sex': sex, 'creatinine': creatinine, 'egfr': egfr,
            'uacr': uacr, 'potassium': potassium, 'sbp': sbp, 'dbp': dbp,
            'has_dm': has_dm, 'has_htn': has_htn, 'has_ckd': has_ckd_logic,
            'on_ace_arb': on_ace_arb, 'on_sglt2': on_sglt2, 'on_mra': on_mra,
            'g_stage': g_stage, 'a_stage': a_stage
        }
        
        st.subheader("🤖 AI Management Suggestions")
        recs = core.check_renoprotection(pt_data)
        if recs:
            for r in recs:
                st.info(r)
        else:
            st.success("🌟 Guideline Adherence is Optimal.")
            
        note = core.generate_note(pt_data, recs, risk_color)
        st.text_area("Copy Clinic Note", note, height=300)

# --- WORKFLOW: DIALYSIS UNIT ---
elif mode == "Dialysis Unit":
    st.header("🩸 Hemodialysis Rounds")
    # Basic Placeholder for Dialysis logic (can be expanded later)
    st.info("Dialysis Module Loaded. Enter Kt/V and Dry Weight below.")
    spktv = st.number_input("spKt/V", value=1.2)
    idwg = st.number_input("Weight Gain (kg)", value=2.0)
    
    if spktv < 1.2:
        st.warning("⚠️ Adequacy Alert: Kt/V < 1.2")
    else:
        st.success("✅ Adequacy Target Met")
