APP_TITLE = "Kuis TBO"

EXAM_DURATION_MINUTES = 10  # durasi ujian
EXAM_DURATION_SECONDS = EXAM_DURATION_MINUTES * 60

# Nama sheet di Google Spreadsheet (harus sama dengan Apps Script)
SHEET_RESULTS_NAME = "HASIL_KUIS"
SHEET_LOG_NAME = "LOG_AKTIVITAS"

# Header hasil ujian
RESULTS_HEADERS = [
    "timestamp",
    "session_id",
    "nim",
    "nama",
    "kelas",
    "skor",
    "benar",
    "salah",
    "durasi_detik",
    "tab_switch_count",
    "paste_attempt_count",
    "status_ai",
    "anomaly_score",
]

# Header log aktivitas
LOG_HEADERS = [
    "timestamp",
    "session_id",
    "nim",
    "nama",
    "durasi_detik",
    "tab_switch_count",
    "paste_attempt_count",
]
