{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;\f1\fnil\fcharset0 AppleColorEmoji;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # kdigo_logic.py\
def get_g_stage(egfr):\
    if egfr >= 90: return "G1"\
    elif egfr >= 60: return "G2"\
    elif egfr >= 45: return "G3a"\
    elif egfr >= 30: return "G3b"\
    elif egfr >= 15: return "G4"\
    else: return "G5"\
\
def get_a_stage(uacr):\
    if uacr < 30: return "A1"\
    elif uacr <= 300: return "A2"\
    else: return "A3"\
\
def get_risk_color(g_stage, a_stage):\
    # Logic based on KDIGO Heatmap\
    # Returns: Green (Low), Yellow (Mod), Orange (High), Red (Very High)\
    \
    # Red Zone (Very High Risk)\
    if g_stage in ["G4", "G5"]: return "Red"\
    if a_stage == "A3": return "Red"\
    \
    # Orange Zone (High Risk)\
    if g_stage == "G3b" and a_stage == "A1": return "Orange"\
    if g_stage == "G3a" and a_stage == "A2": return "Orange"\
    \
    # Yellow Zone (Moderate Risk)\
    if g_stage == "G3a" and a_stage == "A1": return "Yellow"\
    if g_stage in ["G1", "G2"] and a_stage == "A2": return "Yellow"\
    \
    # Green Zone (Low Risk)\
    return "Green"\
\
def check_renoprotection(data):\
    recommendations = []\
    \
    # 1. ACEi/ARB Check\
    if data['uacr'] > 300 or (data['has_htn'] and data['uacr'] > 30):\
        if not data['on_ace_arb']:\
            recommendations.append("
\f1 \uc0\u9888 \u65039 
\f0  **MISSING:** ACEi or ARB indicated for Albuminuria/HTN.")\
\
    # 2. SGLT2i Check (The "Flozin" Rule)\
    if data['egfr'] >= 20 and (data['has_dm'] or data['has_ckd']):\
        if not data['on_sglt2']:\
            recommendations.append("
\f1 \uc0\u9888 \u65039 
\f0  **MISSING:** SGLT2 Inhibitor indicated (eGFR > 20).")\
\
    # 3. BP Check\
    if data['sbp'] > 120:\
        recommendations.append(f"
\f1 \uc0\u9888 \u65039 
\f0  **BP ALERT:** SBP \{data['sbp']\} > 120 mmHg (KDIGO Target).")\
        \
    return recommendations\
\
def generate_note(data, recommendations, risk_color):\
    rec_text = "\\n".join(recommendations)\
    return f"""\
    NEPHROLOGY CONSULT NOTE\
    -----------------------\
    Patient Age: \{data['age']\} | Sex: \{data['sex']\}\
    KDIGO Staging: \{data['g_stage']\} / \{data['a_stage']\} (Risk: \{risk_color\})\
    \
    VITALS & LABS\
    -------------\
    BP: \{data['sbp']\}/\{data['dbp']\}\
    Cr: \{data['creatinine']\} | eGFR: \{data['egfr']\}\
    uACR: \{data['uacr']\} | K+: \{data['potassium']\}\
    \
    ASSESSMENT\
    ----------\
    1. Chronic Kidney Disease (\{data['g_stage']\}\{data['a_stage']\})\
       - Progression Risk: \{risk_color\}\
    \
    2. Renoprotection Gaps:\
    \{rec_text if rec_text else " - Current regimen optimal."\}\
    \
    PLAN\
    ----\
    [ ] Target SBP < 120 mmHg\
    [ ] Repeat labs in 3 months\
    """}