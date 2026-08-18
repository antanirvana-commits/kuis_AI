import streamlit as st
import pandas as pd
import altair as alt

from src.config import APP_TITLE, EXAM_DURATION_MINUTES, EXAM_DURATION_SECONDS
from src.config import RESULTS_HEADERS
from src.utils import get_or_create_session_id
from src.question_bank import load_questions
from src.sheets_client import SheetsClient
from src.scoring import evaluate
from src.anti_cheat import init_anti_cheat_state, get_time_remaining


N_SOAL_PER_UJIAN = 10  # jumlah soal yang muncul untuk mahasiswa


def render_mahasiswa_page(sheets_client: SheetsClient):
    st.header("Halaman Ujian Mahasiswa")

    # session id global
    session_id = get_or_create_session_id(st.session_state)

    # flag ujian dimulai
    if "ujian_dimulai" not in st.session_state:
        st.session_state["ujian_dimulai"] = False

    # form identitas
    if not st.session_state["ujian_dimulai"]:
        with st.form("form_identitas"):
            st.subheader("Identitas Mahasiswa")
            nim = st.text_input("NIM")
            nama = st.text_input("Nama")
            kelas = st.text_input("Kelas / Prodi")
            token = st.text_input("Token Ujian (opsional)")
            mulai = st.form_submit_button("Mulai Ujian")

        if mulai:
            if not nim or not nama:
                st.error("NIM dan Nama wajib diisi.")
                return

            st.session_state["nim"] = nim
            st.session_state["nama"] = nama
            st.session_state["kelas"] = kelas
            st.session_state["token"] = token
            st.session_state["ujian_dimulai"] = True

            # set durasi maksimum untuk scoring
            st.session_state["max_duration"] = EXAM_DURATION_SECONDS

            # inisialisasi anti cheat
            init_anti_cheat_state(st.session_state)

            st.rerun()

        st.info("Silakan isi identitas dan klik **Mulai Ujian**.")
        return

    # ==== UJIAN BERLANGSUNG ====
    nim = st.session_state.get("nim", "")
    nama = st.session_state.get("nama", "")
    kelas = st.session_state.get("kelas", "")

    st.markdown(f"**NIM:** {nim}  |  **Nama:** {nama}  |  **Kelas:** {kelas}")
    st.markdown("---")

    # Timer
    elapsed, remaining = get_time_remaining(st.session_state)
    menit_sisa = int(remaining // 60)
    detik_sisa = int(remaining % 60)

    st.subheader("Timer Ujian")
    st.write(
        f"Waktu tersisa: **{menit_sisa:02d}:{detik_sisa:02d}** "
        f"(dari {EXAM_DURATION_MINUTES} menit)"
    )
    st.progress(min(1.0, elapsed / EXAM_DURATION_SECONDS) if EXAM_DURATION_SECONDS > 0 else 0)

    if remaining <= 0:
        st.error("Waktu ujian telah habis. Silakan kumpulkan jawaban Anda.")
        disabled_submit = False  # boleh submit walau lewat waktu, nanti bisa ditandai
    else:
        disabled_submit = False

    st.markdown("---")
    st.subheader("Soal Ujian Struktur Data")

    # load soal sekali per sesi
    if "questions" not in st.session_state:
        seed = st.session_state.get("nim") or session_id
        st.session_state["questions"] = load_questions(
            num_questions=N_SOAL_PER_UJIAN,
            seed=seed,
            shuffle_options=True,
        )

    questions = st.session_state["questions"]
    answers = {}

    for i, q in enumerate(questions):
        st.markdown(f"**Soal {i+1}. ({q['level']}) {q['pertanyaan']}**")
        choice = st.radio(
            label=f"Jawaban Soal {i+1}",
            options=q["opsi"],
            key=f"q_{q['id']}",
        )
        answers[q["id"]] = choice
        st.markdown("---")

    if st.button("Kumpulkan Jawaban", disabled=disabled_submit):
        skor, benar, salah, fitur, status_ai, anomaly_score = evaluate(
            st.session_state, questions, answers
        )

        st.success(f"Jawaban terkumpul. Skor Anda: **{skor}** (Benar: {benar}, Salah: {salah})")
        st.info(f"Status analisis: **{status_ai}**  | anomaly_score={anomaly_score}")

        # kirim ke Google Sheets
        sheets_client.append_result(
            nim=nim,
            nama=nama,
            kelas=kelas,
            skor=skor,
            benar=benar,
            salah=salah,
            fitur=fitur,
            status_ai=status_ai,
            anomaly_score=anomaly_score,
            session_id=session_id,
        )

        # opsional: kunci ujian agar tidak dapat mengubah lagi
        st.session_state["ujian_dimulai"] = False
        # bisa juga reset session_state["questions"] kalau ingin
        # st.rerun()


def render_dosen_page(sheets_client: SheetsClient):
    st.header("Dashboard Dosen")

    st.markdown(
        """
        Dashboard ini menampilkan rekap nilai mahasiswa yang tersimpan di Google Sheets
        (sheet **HASIL_KUIS**). Grafik akan tampil otomatis setelah ada data.
        """
    )

    df = sheets_client.get_scores()

    if df.empty:
        st.warning("Belum ada data nilai di Google Sheets.")
        return

    st.subheader("Tabel Rekap Nilai")
    st.dataframe(df)

    # Konversi tipe data
    df["skor"] = pd.to_numeric(df["skor"], errors="coerce")
    df["benar"] = pd.to_numeric(df["benar"], errors="coerce")
    df["salah"] = pd.to_numeric(df["salah"], errors="coerce")
    df["durasi_detik"] = pd.to_numeric(df["durasi_detik"], errors="coerce")
    df["tab_switch_count"] = pd.to_numeric(df["tab_switch_count"], errors="coerce")
    df["paste_attempt_count"] = pd.to_numeric(df["paste_attempt_count"], errors="coerce")
    df["anomaly_score"] = pd.to_numeric(df["anomaly_score"], errors="coerce")

    st.markdown("---")
    st.subheader("Ringkasan Statistik")

    col1, col2, col3 = st.columns(3)
    col1.metric("Jumlah Peserta", len(df))
    col2.metric("Rata-rata Skor", f"{df['skor'].mean():.2f}")
    col3.metric("Skor Maksimum", f"{df['skor'].max():.2f}")

    st.markdown("### Distribusi Skor")

    hist_chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("skor:Q", bin=alt.Bin(maxbins=10), title="Skor"),
            y=alt.Y("count():Q", title="Jumlah Mahasiswa"),
        )
        .properties(height=300)
    )
    st.altair_chart(hist_chart, use_container_width=True)

    st.markdown("### Status Analisis AI (Normal vs Suspicious)")
    status_counts = df["status_ai"].value_counts().reset_index()
    status_counts.columns = ["status_ai", "count"]

    status_chart = (
        alt.Chart(status_counts)
        .mark_bar()
        .encode(
            x=alt.X("status_ai:N", title="Status"),
            y=alt.Y("count:Q", title="Jumlah"),
            color="status_ai:N",
        )
        .properties(height=300)
    )
    st.altair_chart(status_chart, use_container_width=True)

    st.markdown("### Korelasi Skor vs Durasi Ujian")
    scatter_chart = (
        alt.Chart(df)
        .mark_circle(size=60)
        .encode(
            x=alt.X("durasi_detik:Q", title="Durasi (detik)"),
            y=alt.Y("skor:Q", title="Skor"),
            color="status_ai:N",
            tooltip=["nim", "nama", "skor", "durasi_detik", "status_ai"],
        )
        .properties(height=300)
    )
    st.altair_chart(scatter_chart, use_container_width=True)


def main():
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    st.title(APP_TITLE)

    sheets_client = SheetsClient()

    menu = st.sidebar.radio("Pilih peran:", ["Mahasiswa", "Dosen"])

    if menu == "Mahasiswa":
        render_mahasiswa_page(sheets_client)
    else:
        # -------- PASSWORD DOSEN --------
        pwd = st.sidebar.text_input("Password Dosen", type="password")
        if pwd != "Nira@Anta889910":
            st.warning("Masukkan password dosen yang benar.")
            st.stop()
        # --------------------------------

        render_dosen_page(sheets_client)


if __name__ == "__main__":
    main()
