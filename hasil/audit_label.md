# Audit label dan kebocoran (N4)

## A. data_terlabel.csv, label Mongso (12 kelas, 7.306 baris)
Baris tidak berurutan waktu dan tidak punya kolom tanggal, jadi split kronologis tidak mungkin; semua split di bawah acak. Itu sendiri batasan data ini.

| Skenario | Akurasi | Macro-F1 |
| --- | --- | --- |
| Protokol draft IES: scaler pada semua data, SMOTE sebelum split, split acak | 0.9957 | 0.9957 |
| Split acak, tanpa SMOTE, scaler dari data latih | 0.9904 | 0.9875 |
| Split acak, SMOTE hanya di data latih | 0.9897 | 0.9873 |
| Duplikat dibuang (6.849 baris), tanpa SMOTE | 0.9861 | 0.9857 |
| Duplikat dan kelas Kasadasa dibuang, tanpa SMOTE | 0.9821 | 0.9783 |

Pohon keputusan tunggal pada split acak (tanpa SMOTE): jika akurasi tinggi pada kedalaman kecil, label adalah aturan atas fitur.

| Kedalaman | Akurasi uji |
| --- | --- |
| 2 | 0.5088 |
| 4 | 0.8650 |
| 6 | 0.9620 |
| 8 | 0.9854 |
| 12 | 0.9869 |

Kepentingan fitur pohon: Kecepatan Angin rata-rata (m/s) 0.438, Arah Angin (derajat) 0.416, Temperatur 0.085, Kelembaban 0.059, Curah Hujan (mm) 0.002

(waktu bagian A: 42 dtk)

## B. dataset_cuaca_hama_final_v2, label risk_level dan pest_type (26.304 jam, 2022-2024)

- risk_score direkonstruksi regresi linear dari 7 fitur cuaca: R2 = 1.0000
- Pasangan pest_type dan risk_level: 1 risk_level per pest_type (1 berarti satu jenis hama selalu satu level)
- Latih 2022-2023, uji 2024 (kronologis):

| Target | Model | Akurasi uji |
| --- | --- | --- |
| risk_level | pohon kedalaman 3 | 0.9529 |
| risk_level | pohon kedalaman 6 | 0.9768 |
| risk_level | pohon kedalaman 10 | 0.9885 |
| pest_type | pohon kedalaman 3 | 0.8435 |
| pest_type | pohon kedalaman 6 | 0.9713 |
| pest_type | pohon kedalaman 10 | 0.9911 |
| risk_level | hanya jam dalam sehari (tanpa cuaca), kedalaman 6 | 0.6925 |
| pest_type | hanya jam dalam sehari (tanpa cuaca), kedalaman 6 | 0.4727 |

- Rata-rata risk_numeric per jam pada kolom waktu: 00:1.5, 01:1.0, 02:0.6, 03:0.2, 04:0.1, 05:0.1, 06:0.1, 07:0.2, 08:0.3, 09:0.4, 10:0.6, 11:0.8, 12:1.0, 13:1.2, 14:1.3, 15:1.4, 16:1.5, 17:1.6, 18:1.6, 19:1.7, 20:1.7, 21:1.8, 22:1.8, 23:1.8

Kesimpulan: label di kedua dataset dapat direkonstruksi dari fitur cuaca oleh pohon dangkal (jam dalam sehari saja sudah memberi 69% untuk risk_level dan 47% untuk pest_type), jadi akurasi tinggi tidak menunjukkan kemampuan memprediksi serangan hama. Protokol draft IES (SMOTE sebelum split) mereplikasi angka draft (0,9957 vs 0,9958 di draft), tetapi kebocoran SMOTE hanya menambah sekitar 0,6 poin; masalah utamanya adalah labelnya sendiri.
