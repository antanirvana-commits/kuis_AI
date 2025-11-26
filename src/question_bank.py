import os
import random
import pandas as pd

DATA_PATH = os.path.join("data", "bank_soal_AI.csv")


def load_questions(num_questions=None, seed=None, shuffle_options=True):
    """
    Membaca bank soal struktur data dengan kolom:
    id_soal,level,pertanyaan,opsi_a,opsi_b,opsi_c,opsi_d,kunci

    - num_questions: jumlah soal yang diambil (subset)
    - seed: untuk randomisasi deterministik (misal berdasarkan NIM)
    """

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"File bank soal tidak ditemukan: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    questions = []
    for _, row in df.iterrows():
        opsi = [row["opsi_a"], row["opsi_b"], row["opsi_c"], row["opsi_d"]]
        if shuffle_options:
            random.shuffle(opsi)

        questions.append(
            {
                "id": int(row["id_soal"]),
                "level": row["level"],
                "pertanyaan": row["pertanyaan"],
                "opsi": opsi,
                "kunci": row["kunci"],  # teks jawaban benar
            }
        )

    # Randomisasi urutan soal
    if seed is not None:
        rnd = random.Random(str(seed))
        rnd.shuffle(questions)
    else:
        random.shuffle(questions)

    if num_questions is not None and num_questions < len(questions):
        questions = questions[:num_questions]

    return questions
