import pandas as pd
import requests
from datetime import datetime

from .config import RESULTS_HEADERS

# GANTI ini dengan URL Web App Apps Script kamu
APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbznrd_JaESwXtrHOZfYX-4CV4RsvBB13nU5_8Y8YgcGSvRcQTKgwqqCgKjlEtBs-ITr/exec"


class SheetsClient:
    """
    Integrasi ke Google Sheets via Apps Script Web App (form-data, e.parameter).
    """

    def __init__(self):
        self.url = APPS_SCRIPT_URL
        if not self.url:
            print("[SheetsClient] URL Apps Script kosong. Mode offline.")
            self.enabled = False
        else:
            self.enabled = True
            print(f"[SheetsClient] Terhubung ke Apps Script: {self.url}")

    def append_result(
        self,
        nim,
        nama,
        kelas,
        skor,
        benar,
        salah,
        fitur,
        status_ai,
        anomaly_score,
        session_id,
    ):
        if not self.enabled:
            print("[SheetsClient] Disabled – data tidak dikirim ke Apps Script.")
            return

        ts = datetime.now().isoformat()

        payload = {
            "mode": "append_result",
            "timestamp": ts,
            "session_id": session_id,
            "nim": str(nim),
            "nama": str(nama),
            "kelas": str(kelas),
            "skor": str(skor),
            "benar": str(benar),
            "salah": str(salah),
            "durasi_detik": str(fitur.get("durasi_detik", 0)),
            "tab_switch_count": str(fitur.get("tab_switch_count", 0)),
            "paste_attempt_count": str(fitur.get("paste_attempt_count", 0)),
            "status_ai": str(status_ai),
            "anomaly_score": str(anomaly_score),
        }

        try:
            print("[SheetsClient] Mengirim data ke Apps Script (append_result)...")
            resp = requests.post(self.url, data=payload, timeout=15)
            print(f"[SheetsClient] HTTP {resp.status_code}")
            print("[SheetsClient] Response text:", resp.text)

        except Exception as e:
            print(f"[SheetsClient] Exception append_result: {e}")

    def get_scores(self):
        if not self.enabled:
            return pd.DataFrame(columns=RESULTS_HEADERS)

        payload = {"mode": "get_scores"}
        try:
            resp = requests.post(self.url, data=payload, timeout=15)
            if resp.status_code != 200:
                print("[SheetsClient] GAGAL get_scores:", resp.text)
                return pd.DataFrame(columns=RESULTS_HEADERS)

            data = resp.json()
            if data.get("status") != "ok":
                print("[SheetsClient] get_scores error:", data)
                return pd.DataFrame(columns=RESULTS_HEADERS)

            rows = data.get("rows", [])
            if not rows:
                return pd.DataFrame(columns=RESULTS_HEADERS)

            df = pd.DataFrame(rows)
            for col in RESULTS_HEADERS:
                if col not in df.columns:
                    df[col] = None
            return df[RESULTS_HEADERS]

        except Exception as e:
            print(f"[SheetsClient] Exception get_scores: {e}")
            return pd.DataFrame(columns=RESULTS_HEADERS)
