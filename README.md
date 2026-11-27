# Kasus A: Deteksi Penipuan Pembukaan Rekening Bank

Model ini memberi skor peluang penipuan untuk setiap pengajuan buka rekening. Datanya Bank Account Fraud (BAF) varian Base, bulan 0-3: 547.975 pengajuan, sekitar 1% di antaranya penipuan.

## Hasil di data validasi (bulan 3, 150.936 pengajuan)

| Model | TPR@FPR5% | ROC-AUC |
|---|---|---|
| Logistic Regression (pembanding) | 0.519 | 0.894 |
| LightGBM | 0.577 | 0.914 |

Kalau nasabah jujur yang ikut tertandai dibatasi 5%, LightGBM menangkap 57,7% penipu (interval kepercayaan 95% dengan bootstrap: 55,0% sampai 60,3%).

## Metode

Saya memakai LightGBM. Datanya tabel yang mencampur kolom angka dan kategori, dan LightGBM bisa membaca kolom kategori langsung serta cepat dilatih di ratusan ribu baris. Kelas yang tidak seimbang tidak saya resampling, karena TPR@FPR5% hanya melihat urutan skor. Nilai -1 (data tidak ada) saya biarkan, karena tree model bisa memisahkannya sendiri.

Saya mencoba 12 kombinasi hyperparameter dengan early stopping, dan terpilih `num_leaves=15` dan `min_child_samples=500`. Model final dilatih ulang di bulan 0-2 dengan iterasi terbaik dikali 1,5, karena datanya 1,5 kali lebih banyak.

## Cara membagi data

Data latih adalah bulan 0-2, data validasi bulan 3. Di produksi, model menilai pengajuan yang datang setelah data latihnya, dan BAF sengaja memuat pergeseran distribusi antar bulan. Split acak akan membuat skor terlihat lebih bagus dari kenyataan. Hyperparameter dipilih di dalam bulan 0-2 saja (latih di bulan 0-1, nilai di bulan 2), jadi bulan 3 tidak dipakai untuk latih atau tuning.

## Catatan

Ambang skor perlu dikalibrasi ulang tiap bulan, karena ambang dari bulan 2 membuat FPR di bulan 3 naik jadi 8,7%. Dengan satu ambang, nasabah jujur berumur 50 tahun ke atas tertandai 12,0%, sedangkan yang lebih muda 3,3%. Ambang per kelompok umur membuat keduanya 4,9%, dengan harga TPR turun ke 53,0%. Rinciannya ada di notebook bagian 10-12.

## Cara menjalankan

Python 3.12, jalankan dari folder root repo. Data diunduh otomatis lewat `kagglehub` kalau `data/Base.csv` belum ada. Model tersimpan di `models/lgbm_fraud.joblib` dan `models/lgbm_fraud.txt`.

```bash
pip install -r requirements.txt
jupyter nbconvert --to notebook --execute notebook.ipynb
```

## API

`POST /predict` menerima satu pengajuan (29 fitur, semua wajib, kirim -1 untuk data yang tidak ada) dan butuh header `x-api-key`. Contoh body ada di Swagger `http://localhost:8000/docs` (tombol Authorize lalu Try it out). Skema OpenAPI ada di `openapi.json` dan bisa di-import ke Postman.

```bash
uvicorn app.main:app --port 8000 --env-file .env   # .env berisi API_KEY=<kunci>
curl -X POST localhost:8000/predict -H "x-api-key: <kunci>" -H "Content-Type: application/json" -d @pengajuan.json
# {"model_name":"fraud-lgbm","model_version":"987ca8b198b2","fraud_score":0.00047,"is_fraud":false,"threshold":0.05603}
python -m pytest   # test; perbarui skema: python -c "import json; from app.main import app; print(json.dumps(app.openapi(), indent=2))" > openapi.json
```

## Deploy (Docker + GitHub Actions)

Setiap push ke `main`, `.github/workflows/deploy.yml` menjalankan test, build image ke `ghcr.io/<owner>/<repo>`, lalu SSH ke VPS dan menjalankan container `fraud-api` di port 8000. VPS cukup terpasang Docker. Secrets repo yang dibutuhkan: `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY` (private key), `API_KEY`, dan opsional `VPS_PORT`. Jalankan lokal: `docker build -t fraud-api . && docker run -p 8000:8000 --env-file .env fraud-api`.
