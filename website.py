from flask import Flask, request, jsonify, render_template
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import geocoder
import math

# Koneksi MongoDB
uri = "mongodb+srv://kapiarso:kapiarso@mahasiswa.v2wsc.mongodb.net/?retryWrites=true&w=majority&appName=Mahasiswa"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client["mahasiswa"]
collection = db["ipaddress"]

# Inisialisasi Flask
app = Flask(__name__)

# Fungsi Perhitungan Arah Qiblat
def hitung_arah_qiblat(lintang, bujur):
    kaabah_lat = 21.4225
    kaabah_lon = 39.8262
    kaabah_lat_rad = math.radians(kaabah_lat)
    kaabah_lon_rad = math.radians(kaabah_lon)
    user_lat_rad = math.radians(lintang)
    user_lon_rad = math.radians(bujur)

    delta_lon = kaabah_lon_rad - user_lon_rad

    x = math.sin(delta_lon) * math.cos(kaabah_lat_rad)
    y = math.cos(user_lat_rad) * math.sin(kaabah_lat_rad) - \
        math.sin(user_lat_rad) * math.cos(kaabah_lat_rad) * math.cos(delta_lon)

    qiblat_angle_rad = math.atan2(x, y)
    qiblat_angle_deg = math.degrees(qiblat_angle_rad)

    if qiblat_angle_deg < 0:
        qiblat_angle_deg += 360

    return qiblat_angle_deg

# Route Utama
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nama = request.form.get("nama")
        auto_detect = request.form.get("auto_detect")

        if auto_detect:
            lokasi = geocoder.ip('me')
            if lokasi.ok:
                lintang, bujur = lokasi.latlng
                ip_address = lokasi.ip
                region = lokasi.region
                city = lokasi.city
                isp = lokasi.provider
            else:
                return "Gagal mendeteksi lokasi", 400
        else:
            lintang = float(request.form.get("lintang"))
            bujur = float(request.form.get("bujur"))
            ip_address, region, city, isp = None, None, None, None

        arah_qiblat = hitung_arah_qiblat(lintang, bujur)
        data = {
            "nama": nama,
            "lintang": lintang,
            "bujur": bujur,
            "ip_address": ip_address,
            "region": region,
            "city": city,
            "isp": isp,
            "arah_qiblat": arah_qiblat
        }
        collection.insert_one(data)

        return render_template("result.html", nama=nama, arah_qiblat=arah_qiblat)

    return render_template("index.html")
