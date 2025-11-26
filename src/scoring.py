from .anti_cheat import get_exam_features


def evaluate(session_state, questions, answers):
    benar = 0
    salah = 0

    for q in questions:
        qid = q["id"]
        kunci = q["kunci"]
        jawaban = answers.get(qid)
        if jawaban is None:
            continue
        if jawaban == kunci:
            benar += 1
        else:
            salah += 1

    total = benar + salah
    skor = 0
    if total > 0:
        skor = round(100 * benar / float(total), 2)

    fitur = get_exam_features(session_state)
    durasi_detik = fitur.get("durasi_detik", 0)
    tab_switch = fitur.get("tab_switch_count", 0)
    paste_count = fitur.get("paste_attempt_count", 0)
    max_duration = session_state.get("max_duration", 1)

    # ------------------------------
    # 1) Hitung risk_score berbasis aturan sederhana
    # ------------------------------
    risk_score = 0

    # Durasi sangat cepat → curiga
    if durasi_detik < 0.2 * max_duration:
        risk_score += 2
    elif durasi_detik < 0.4 * max_duration:
        risk_score += 1

    # Tab switching banyak → curiga
    if tab_switch >= 15:
        risk_score += 2
    elif tab_switch >= 8:
        risk_score += 1

    # Paste attempt banyak → curiga
    if paste_count >= 8:
        risk_score += 2
    elif paste_count >= 3:
        risk_score += 1

    # Skor sangat tinggi + durasi cepat → tambahkan risiko
    if skor >= 90 and durasi_detik < 0.4 * max_duration:
        risk_score += 1

    # ------------------------------
    # 2) Mapping risk_score → kategori status_ai
    # ------------------------------
    if risk_score <= 1:
        status_ai = "Normal"
    elif risk_score <= 3:
        status_ai = "Low Suspicion"
    elif risk_score <= 5:
        status_ai = "Medium Suspicion"
    else:
        status_ai = "High Suspicion"

    # ------------------------------
    # 3) Skor anomali 0.0 – 1.0 (dinormalisasi dari risk_score)
    # ------------------------------
    # Maksimal risiko teoritis 7 (2+2+2+1), kita clamp ke [0, 1]
    anomaly_score = min(risk_score / 7.0, 1.0)

    return skor, benar, salah, fitur, status_ai, anomaly_score
