# Colab Setup

Dung file nay nhu checklist khi chay tren Google Colab.

## 1. Mount Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

## 2. Cau hinh duong dan

```python
BASE_DIR = "/content/drive/MyDrive/aideom_vn"
DATA_DIR = f"{BASE_DIR}/data"
OUTPUT_DIR = f"{BASE_DIR}/outputs"
FIGURE_DIR = f"{BASE_DIR}/outputs/figures"
TABLE_DIR = f"{BASE_DIR}/outputs/tables"
```

## 3. Cai thu vien

```python
!pip install numpy pandas scipy matplotlib seaborn pulp cvxpy pymoo pyomo highspy plotly streamlit openpyxl tqdm pytest
```

Neu can solver LP/MIP:

```python
!apt-get update -qq
!apt-get install -y -qq glpk-utils coinor-cbc
```

Neu can hoc tang cuong:

```python
!pip install gymnasium stable-baselines3 torch
```

## 4. Import source code tu Drive

```python
import sys
sys.path.append(f"{BASE_DIR}/src")
```

## 5. Kiem tra data

```python
from aideom_vn.data_loader import check_data_files
print(check_data_files())
```
