# Bài tập phụ: Dự đoán điểm thi cuối kỳ

## Nguồn yêu cầu

"Prediction of Final Exam Score Using Machine Learning Models" — Tran Dinh Que, LieNet Lab

## 5 Tasks

| Task | Mô tả |
|---|---|
| ML-01 | Construct dataset with peer influence |
| ML-02 | Train 3 models (GBoost, MLP, GraphSAGE) |
| ML-03 | Evaluate using 5 metrics (MAE, MSE, RMSE, MAPE, R²) |
| ML-04 | Compare under different social structures |
| ML-05 | Analyze peer influence propagation |

## CSV Input — Dữ liệu đánh giá

File: `data/evaluation.csv` (import sau)

| Cột | Mô tả | Ví dụ |
|---|---|---|
| STT | Số thứ tự | 1 |
| Sinh viên | Mã + tên sinh viên | B22DCCN001 - Nguyễn Văn A |
| Nhận xét | Nhận xét từ người đánh giá | Bạn học tốt, hỗ trợ nhóm |
| Điểm | Điểm đánh giá (số) | 8.5 |
| Chữ ký | Chữ ký xác nhận | NguyenA |

**Cột quan trọng:** Điểm (dùng làm peer scores) + Nhận xét (context phân tích)

## Dataset Specification

| Thuộc tính | Giá trị |
|---|---|
| N (số sinh viên) | 800 (synthetic) hoặc từ CSV |
| Academic features | 5: javaProg, pythonProg, dataStructure, sadDesign, intelligentSysDev |
| Peer scores | 10 điểm từ bạn bè (từ CSV hoặc synthetic) |
| Feature range | [4, 10) |
| Random seed | 42 |

**Target formula:**

```
y = 0.25*javaProg + 0.20*pythonProg + 0.10*dataStructure
  + 0.15*sadDesign + 0.10*intelligentSysDev
  + 0.15*peer_mean - 0.05*peer_std + noise(0, 0.25)
```

## Social Structures (Task 4)

| ID | Tên | Tham số |
|---|---|---|
| S1 | Random | p=0.1 |
| S2 | Academic Similarity | threshold=6 |
| S3 | Sparse | threshold=3 |
| S4 | Dense | threshold=9 |

## Models

| Version | Model | Framework |
|---|---|---|
| V1 | Gradient Boosting Regressor | sklearn |
| V2 | MLP (GNN-style) | PyTorch |
| V3 | GraphSAGE | PyTorch |

## Evaluation Metrics

MAE, MSE, RMSE, MAPE, R²

## File Structure

```
ml-exam-prediction/
├── README.md                           ← spec này
├── predict_exam_score.ipynb            ← notebook chính (5 tasks)
├── data/
│   └── evaluation.csv                  ← import sau
└── plots/
    ├── model_comparison.png
    ├── social_structure_comparison.png
    └── peer_influence_propagation.png
```

## How to Run (PowerShell - Windows)

```powershell
cd ml-exam-prediction

# Tạo virtual environment và cài dependencies
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install numpy pandas scikit-learn matplotlib torch jupyterlab

# Chạy notebook (mở trình duyệt tự động)
jupyter lab
```

Sau khi JupyterLab mở, chọn file `predict_exam_score.ipynb` → **Run → Run All Cells**.

> **Lưu ý:** Nếu gặp lỗi 500 ở JupyterLab, dùng `pip install notebook` rồi chạy `jupyter notebook` thay thế.
