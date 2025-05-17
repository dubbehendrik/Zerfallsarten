import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import requests
from io import BytesIO

# -----------------------------
# Funktionen für Berechnungen
# -----------------------------

def berechne_omega(n):
    return 2 * np.pi * n / 60

def berechne_filmdicke(V_LK, eta_LK, rho_LK, omega, r, beta_deg):
    beta_rad = np.radians(beta_deg)
    delta = ((3 * V_LK * eta_LK) / (rho_LK * 2 * np.pi * omega**2 * r**2 * np.sin(beta_rad))) ** (1/3)
    return delta * 1e6  # in µm

def berechne_kennzahlen(eta_LK, rho_LK, sigma, D, v_LK, omega):
    Oh = eta_LK / np.sqrt(rho_LK * sigma * D)
    Kb = (v_LK**2 * rho_LK) / (sigma * D**3 * omega**2 * D**3 * rho_LK)
    We = (rho_LK * v_LK**2 * D) / sigma
    B = (We**0.5) * (Kb**(5/6)) * (Oh**(10/36))
    return Oh, Kb, We, B

# -----------------------------
# App Layout & Benutzeroberfläche
# -----------------------------

st.set_page_config(layout="wide")

st.title("Zerfallsarten an Rotationsglocke")

with st.expander("ℹ️ Hinweise zur Verwendung"):
    st.markdown("""
Diese App berechnet dimensionslose Kennzahlen für die Lackzerstäubung an Rotationsglocken:

- **Ohnesorge-Zahl (Oh)**
- **Kantenbelastung (K_b)**
- **Weber-Zahl (We)**
- **Betriebskennzahl (B)**

Zusätzlich wird die **Filmdicke am Glockenrand (δ)** berechnet.

Formel für die Filmdicke:
""")
    st.latex(r"\delta = \sqrt[3]{ \frac{3 \cdot \dot{V}_{LK} \cdot \eta_{LK} }{ \rho_{LK} \cdot 2\pi \omega^2 r^2 \cdot \sin(\beta) } }")
    st.markdown("""
Abbildung in Anlehnung an:  
Weckerle, G., Dissertation, Universität Stuttgart, 2003 (Pulver-Slurry).
""")

# -----------------------------
# Eingabefelder für Parameter
# -----------------------------
col_plot, col_values = st.columns([0.6, 0.4])

with col_values:
    st.subheader("Parameter")

    V_LK = st.number_input("Lackvolumenstrom [ml/min]", value=60.0)
    n = st.number_input("Drehzahl [1/min]", value=50000.0)
    d = st.number_input("Glockendurchmesser [mm]", value=60.0)
    beta = st.number_input("Konturwinkel [°]", value=55.0)
    rho_LK = st.number_input("Lackdichte [kg/m³]", value=1300.0)
    eta_LK = st.number_input("Viskosität [mPa·s]", value=20.0)
    sigma = st.number_input("Oberflächenspannung [mN/m]", value=30.0)

# -----------------------------
# Umrechnungen & Berechnungen
# -----------------------------
# Umrechnungen in SI-Einheiten
V_LK_m3s = V_LK / 1e6 / 60  # ml/min -> m³/s
eta_LK_Pas = eta_LK / 1000   # mPa·s -> Pa·s
sigma_Npm = sigma / 1000     # mN/m -> N/m
D_m = d / 1000               # mm -> m
r_m = D_m / 2                # Radius in m

omega = berechne_omega(n)
delta = berechne_filmdicke(V_LK_m3s, eta_LK_Pas, rho_LK, omega, r_m, beta)

# Für Betriebspunkt beliebige v_LK (z.B. Umfangsgeschwindigkeit)
v_LK = omega * r_m

Oh, Kb, We, B = berechne_kennzahlen(eta_LK_Pas, rho_LK, sigma_Npm, D_m, v_LK, omega)

# -----------------------------
# Anzeige der Ergebnisse
# -----------------------------
st.markdown("### Berechnete Kennzahlen:")

col1, col2 = st.columns(2)

with col1:
    st.latex(f"Oh = {Oh:.2e}")
    st.latex(f"K_b = {Kb:.2e}")
with col2:
    st.latex(f"We = {We:.2e}")
    st.latex(f"B = {B:.2e}")

st.markdown("### Filmdicke am Glockenrand:")
st.latex(f"\\delta = {delta:.2f} \\, \\mu m")

# -----------------------------
# Plot: Diagramm & Betriebspunkt
# -----------------------------
with col_plot:
    fig, ax = plt.subplots(figsize=(10, 6))

    # Hintergrundbild laden (dein Diagramm, z.B. von GitHub)
    img_url = "https://raw.githubusercontent.com/dubbehendrik/Zerfallsarten/main/Diagramm.jpg"
    response = requests.get(img_url)
    
    if response.status_code == 200 and response.headers['Content-Type'].startswith('image'):
        image_pil = Image.open(BytesIO(response.content))
        img = np.array(image_pil)
    else:
        st.error("Fehler: Bild konnte nicht geladen werden. Prüfe den Link.")

    ax.imshow(img, extent=[1e-4, 1e2, 1e-2, 3e0], aspect='auto', zorder=0)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(1e-4, 1e2)
    ax.set_ylim(1e-2, 3e0)

    ax.set_xlabel("Lackkennzahl")
    ax.set_ylabel("Betriebskennzahl")

    # Betriebspunkt plotten
    ax.plot(Kb, B, 'ro', markersize=10, label="Betriebspunkt", zorder=1)

    ax.legend()
    st.pyplot(fig)
