import requests
import streamlit as st
import pandas as pd
from datetime import datetime
import streamlit.components.v1 as components

# ==========================
# KONFIGURASI GLOBAL
# ==========================

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
IPAPI_URL = "https://ipapi.co/json/"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"

# User-Agent WAJIB untuk Nominatim (ganti email-mu)
NOMINATIM_HEADERS = {
    "User-Agent": "weather-app/1.0 (YOUR_EMAIL@example.com)"
}

# ==========================
# FUNGSI GPS
# ==========================

def get_gps_coordinates():
    """Mengambil GPS menggunakan JavaScript + Browser."""
    gps_js = """
    <script>
    function sendToStreamlit(lat, lon) {
        const msg = {
            isStreamlitMessage: true,
            lat: lat,
            lon: lon
        };
        window.parent.postMessage(msg, "*");
    }

    function getLocation() {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    sendToStreamlit(pos.coords.latitude, pos.coords.longitude);
                },
                (err) => {
                    alert("Gagal mengambil lokasi: " + err.message);
                }
            );
        } else {
            alert("Browser tidak mendukung GPS");
        }
    }

    getLocation();
    </script>
    """
    components.html(gps_js, height=0, width=0)

# ==========================
# FUNGSI UTILITAS
# ==========================

def get_location_from_ip():
    """Ambil lokasi menggunakan IP."""
    try:
        resp = requests.get(IPAPI_URL, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            lat = data.get("latitude")
            lon = data.get("longitude")
            return {
                "lat": lat,
                "lon": lon,
                "city": data.get("city"),
                "region": data.get("region"),
                "country": data.get("country_name")
            }
    except:
        return None
    return None


def reverse_geocode(lat, lon):
    """Reverse geocoding koordinat."""
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "addressdetails": 1,
        "zoom": 18
    }
    try:
        resp = requests.get(NOMINATIM_URL, params=params, headers=NOMINATIM_HEADERS)
        if resp.status_code == 200:
            data = resp.json()
            address = data.get("address", {})

            kelurahan = (
                address.get("village")
                or address.get("suburb")
                or address.get("neighbourhood")
                or address.get("hamlet")
            )

            return {
                "display_name": data.get("display_name"),
                "kelurahan": kelurahan,
                "kecamatan": address.get("city_district"),
                "kota": address.get("city") or address.get("town"),
                "provinsi": address.get("state"),
                "negara": address.get("country"),
                "raw": data
            }
    except:
        return None
    return None


def get_weather(lat, lon, timezone="auto"):
    """Ambil cuaca dari Open-Meteo."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "current_weather": True,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation,cloud_cover",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum",
        "timezone": timezone
    }
    try:
        resp = requests.get(OPEN_METEO_URL, params=params)
        if resp.status_code == 200:
            return resp.json()
    except:
        return None
    return None


def build_hourly_dataframe(weather_json):
    """Convert hourly ke DataFrame."""
    try:
        hourly = weather_json.get("hourly", {})
        df = pd.DataFrame({
            "time": pd.to_datetime(hourly.get("time", [])),
            "temperature_2m": hourly.get("temperature_2m", []),
            "relative_humidity_2m": hourly.get("relative_humidity_2m", []),
            "precipitation": hourly.get("precipitation", []),
            "cloud_cover": hourly.get("cloud_cover", [])
        })
        return df
    except:
        return None

# ==========================
# UI STREAMLIT
# ==========================

st.set_page_config(page_title="Aplikasi Prakiraan Cuaca", page_icon="⛅", layout="wide")

st.title("⛅ Aplikasi Prakiraan Cuaca Berbasis Open-Meteo")
st.write(
    """
Aplikasi ini:
- Menentukan lokasi Anda menggunakan **GPS** atau **IP**  
- Menggunakan **OpenStreetMap Nominatim** untuk mendapatkan nama kelurahan  
- Menampilkan **cuaca saat ini** dan **prakiraan**  
"""
)

st.sidebar.header("🔍 Pilih Sumber Lokasi")

location_mode = st.sidebar.radio(
    "Gunakan lokasi dari:",
    ("Deteksi otomatis dari IP", "Gunakan GPS Perangkat")
)

lat = None
lon = None

# --------------------------
# LOKASI: IP
# --------------------------
if location_mode == "Deteksi otomatis dari IP":
    if st.sidebar.button("📡 Deteksi Lokasi dari IP"):
        info = get_location_from_ip()
        if info:
            lat = info["lat"]
            lon = info["lon"]
            st.success(f"Lokasi IP: {info['city']} (lat={lat}, lon={lon})")

# --------------------------
# LOKASI: GPS
# --------------------------
if location_mode == "Gunakan GPS Perangkat":
    if st.sidebar.button("📱 Ambil Lokasi GPS"):
        st.info("Meminta izin GPS dari browser...")
        get_gps_coordinates()

    gps_data = st.experimental_get_query_params()
    if "lat" in gps_data and "lon" in gps_data:
        lat = float(gps_data["lat"][0])
        lon = float(gps_data["lon"][0])
        st.success(f"GPS OK! Latitude={lat}, Longitude={lon}")

# Tombol ambil cuaca
get_weather_btn = st.button("🌦 Ambil Cuaca Sekarang")

# --------------------------
# PROSES CUACA
# --------------------------
if get_weather_btn:
    if lat is None or lon is None:
        st.error("Lokasi belum tersedia. Gunakan IP atau GPS.")
    else:
        st.subheader("📍 Lokasi Anda")

        addr = reverse_geocode(lat, lon)
        if addr:
            st.markdown(f"""
**Kelurahan:** {addr['kelurahan'] or '-'}  
**Kecamatan:** {addr['kecamatan'] or '-'}  
**Kota/Kab:** {addr['kota'] or '-'}  
**Provinsi:** {addr['provinsi'] or '-'}  
**Negara:** {addr['negara'] or '-'}  
""")
        else:
            st.warning("Tidak bisa reverse geocoding.")

        weather_json = get_weather(lat, lon)

        if weather_json:
            # CUACA SAAT INI
            st.subheader("🌤️ Cuaca Saat Ini")
            current = weather_json.get("current_weather", {})

            col1, col2, col3 = st.columns(3)
            col1.metric("Suhu (°C)", current.get("temperature"))
            col2.metric("Angin (m/s)", current.get("windspeed"))
            col3.metric("Arah Angin (°)", current.get("winddirection"))

            # PRAKIRAAN
            st.subheader("📆 Prakiraan Harian")
            daily = weather_json.get("daily", {})

            df_daily = pd.DataFrame({
                "date": pd.to_datetime(daily.get("time", [])),
                "temp_max": daily.get("temperature_2m_max", []),
                "temp_min": daily.get("temperature_2m_min", []),
                "precipitation_sum": daily.get("precipitation_sum", []),
            })
            st.dataframe(df_daily, use_container_width=True)

            # PER JAM
            st.subheader("🕒 Prakiraan Per Jam")
            df_hourly = build_hourly_dataframe(weather_json)

            if df_hourly is not None:
                now = datetime.utcnow()
                df_24 = df_hourly[df_hourly["time"] >= now].head(24)

                st.line_chart(df_24.set_index("time")[["temperature_2m"]])
                st.line_chart(df_24.set_index("time")[["precipitation"]])

        else:
            st.error("Gagal mengambil data cuaca.")
