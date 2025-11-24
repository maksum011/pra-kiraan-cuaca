import streamlit as st
import requests
import pandas as pd


# ==========================
# KONFIGURASI LOKASI
# ==========================
LAT = -3.404254
LON = 119.305072
LOCATION_NAME = "Kelurahan Madatte"

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


# ==========================
# MAP KODE CUACA → KETERANGAN
# ==========================
WEATHER_DESCRIPTION = {
    0: "Cerah",
    1: "Cerah Berawan",
    2: "Berawan",
    3: "Mendung",
    45: "Berkabut",
    48: "Berkabut (Intens)",
    51: "Gerimis Ringan",
    53: "Gerimis Sedang",
    55: "Gerimis Lebat",
    61: "Hujan Ringan",
    63: "Hujan Sedang",
    65: "Hujan Lebat",
    71: "Salju Ringan",
    80: "Hujan Lokal",
    81: "Hujan Sedang",
    82: "Hujan Lebat",
    95: "Badai Petir",
    96: "Badai Petir (Ringan)",
    99: "Badai Petir (Hebat)"
}


# ==========================
# MAP KODE CUACA → IKON
# ==========================
WEATHER_ICON = {
    0: "https://img.icons8.com/ios-filled/150/FFA500/sun.png",
    1: "https://img.icons8.com/ios-filled/150/87CEEB/partly-cloudy-day.png",
    2: "https://img.icons8.com/ios-filled/150/87CEEB/cloud.png",
    3: "https://img.icons8.com/ios-filled/150/708090/clouds.png",
    45: "https://img.icons8.com/ios-filled/150/9E9E9E/fog-day.png",
    48: "https://img.icons8.com/ios-filled/150/9E9E9E/fog-night.png",
    51: "https://img.icons8.com/ios-filled/150/76b4ff/light-rain.png",
    53: "https://img.icons8.com/ios-filled/150/76b4ff/rain.png",
    55: "https://img.icons8.com/ios-filled/150/76b4ff/heavy-rain.png",
    61: "https://img.icons8.com/ios-filled/150/76b4ff/rain.png",
    63: "https://img.icons8.com/ios-filled/150/76b4ff/rain.png",
    65: "https://img.icons8.com/ios-filled/150/76b4ff/heavy-rain.png",
    80: "https://img.icons8.com/ios-filled/150/76b4ff/rain.png",
    81: "https://img.icons8.com/ios-filled/150/76b4ff/rain.png",
    82: "https://img.icons8.com/ios-filled/150/76b4ff/heavy-rain.png",
    95: "https://img.icons8.com/ios-filled/150/ffcc00/storm.png",
    96: "https://img.icons8.com/ios-filled/150/ffcc00/storm.png",
    99: "https://img.icons8.com/ios-filled/150/ffcc00/storm.png"
}


# ==========================
# AMBIL DATA DARI API
# ==========================
def get_weather_data():
    params = {
        "latitude": LAT,
        "longitude": LON,
        "current_weather": True,
        "hourly": [
            "temperature_2m",
            "relativehumidity_2m",
            "rain",
            "cloudcover",
            "windspeed_10m"
        ],
        "timezone": "Asia/Makassar"
    }
    response = requests.get(OPEN_METEO_URL, params=params)
    return response.json()


# ==========================
# CSS TEMA MODERN ELEGAN
# ==========================
st.markdown("""
    <style>

    .stApp {
        background: #f5f9ff;
    }

    body, h1, h2, h3, p, span, div {
        color: #0a1a2a !important;
        font-family: 'Segoe UI', sans-serif;
    }

    h1, h2, h3 {
        font-weight: 700;
        text-align: center;
        color: #0a1a2a !important;
    }

    .glass-card {
        background: rgba(255, 255, 255, 0.92);
        padding: 25px;
        border-radius: 18px;
        box-shadow: 0 8px 22px rgba(0,0,0,0.08);
        margin-bottom: 18px;
        backdrop-filter: blur(6px);
    }

    [data-testid="stMetric"] div {
        background: #dde7f7;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
        color: #0a1a2a !important;
    }

    .stDataFrame {
        background: white;
        border-radius: 12px;
        padding: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.07);
    }

    .weather-center {
        text-align: center;
    }

    </style>
""", unsafe_allow_html=True)



# ==========================
# SETUP PAGE
# ==========================
st.set_page_config(page_title="Cuaca Madatte", page_icon="⛅")

st.markdown("<h1>⛅ Prakiraan Cuaca – Kelurahan Madatte</h1>", unsafe_allow_html=True)
st.write(f"<p style='text-align:center'>📍 Koordinat: {LAT}, {LON}</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)



# ==========================
# GET DATA
# ==========================
data = get_weather_data()
current = data.get("current_weather", {})
weather_code = current.get("weathercode", 0)

cuaca_text = WEATHER_DESCRIPTION.get(weather_code, "Tidak diketahui")
cuaca_icon = WEATHER_ICON.get(weather_code)



# ==========================
# CUACA SAAT INI
# ==========================
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)

st.subheader("🌤 Cuaca Saat Ini")

# Tampilkan ikon dinamis
st.markdown(
    f"<div class='weather-center'><img src='{cuaca_icon}' width='120'></div>",
    unsafe_allow_html=True
)

# Tampilkan teks keterangan cuaca
st.markdown(
    f"<h3 class='weather-center'>{cuaca_text}</h3>",
    unsafe_allow_html=True
)

col1, col2, col3 = st.columns(3)
col1.metric("Suhu", f"{current.get('temperature', '--')}°C")
col2.metric("Angin", f"{current.get('windspeed', '--')} km/jam")
col3.metric("Arah Angin", f"{current.get('winddirection', '--')}°")

st.markdown("</div>", unsafe_allow_html=True)



# ==========================
# PRAKIRAAN PER JAM
# ==========================
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader("🕒 Prakiraan Cuaca Per Jam")

hourly = data.get("hourly", {})

if "time" in hourly:
    df = pd.DataFrame({
        "Waktu": hourly["time"],
        "Suhu (°C)": hourly["temperature_2m"],
        "Kelembaban (%)": hourly["relativehumidity_2m"],
        "Awan (%)": hourly["cloudcover"],
        "Hujan (mm)": hourly["rain"],
        "Angin (km/jam)": hourly["windspeed_10m"]
    })

    df["Waktu"] = pd.to_datetime(df["Waktu"])
    st.dataframe(df)
else:
    st.warning("Data prakiraan tidak tersedia.")

st.markdown("</div>", unsafe_allow_html=True)



# ==========================
# GRAFIK SUHU
# ==========================
st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
st.subheader("📈 Grafik Suhu Harian")

if "temperature_2m" in hourly:
    st.line_chart(df.set_index("Waktu")["Suhu (°C)"])

st.markdown("</div>", unsafe_allow_html=True)



# ==========================
# FOOTER
# ==========================
st.write("<p style='text-align:center; color:#0a1a2a;'>Sumber: Open-Meteo API (Gratis, Tanpa API Key)</p>", unsafe_allow_html=True)
