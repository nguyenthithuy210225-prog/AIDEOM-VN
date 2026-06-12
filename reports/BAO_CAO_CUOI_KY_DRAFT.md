# Bao cao cuoi ky AIDEOM-VN - ban nguon

Ngay cap nhat: 31/05/2026

File nay la ban nguon de chuyen thanh Word/PDF. Noi dung duoc viet theo cau truc: input, cong thuc/mo hinh, output chinh, bieu do, policy brief, gia dinh va gioi han.

## 1. Thong tin chung

Ten de tai: AIDEOM-VN - Dashboard ho tro ra quyet dinh phat trien kinh te so va AI Viet Nam.

Phuong an thuc hien: Phuong an 3, xay dung web app co 12 menu tuong ung 12 bai tap. Moi trang co tham so dieu chinh, bang ket qua, bieu do va nhan xet chinh sach.

Cong nghe:

- Python cho phan tinh toan.
- Streamlit va Plotly cho dashboard.
- SciPy, PuLP, Pyomo, pymoo, TOPSIS, Q-learning cho cac mo hinh ra quyet dinh.
- Matplotlib cho bo hinh PNG phuc vu bao cao.

Du lieu:

- `data/vietnam_macro_2020_2025.csv`
- `data/vietnam_sectors_2024.csv`
- `data/vietnam_regions_2024.csv`

Thu muc ket qua:

- Bang CSV: `outputs/tables/`
- Hinh PNG: `outputs/figures/`
- Web app: `dashboard/app.py`

## 2. Kien truc he thong

Ung dung tach thanh hai lop:

- Lop mo hinh: cac file `src/aideom_vn/exercise01_...py` den `exercise12_...py`.
- Lop giao dien: `dashboard/app.py`, goi ham mo hinh, hien bang, ve bieu do va tao Policy Brief.

Quy trinh tai sinh ket qua:

```powershell
$env:PYTHONPATH='D:\Work\BaiTap\aideom_vn\src'
D:\Work\.venv\Scripts\python.exe scripts\generate_outputs.py
D:\Work\.venv\Scripts\python.exe scripts\generate_figures.py
D:\Work\.venv\Scripts\python.exe -m pytest -q
```

Ket qua kiem thu moi nhat:

- `generate_outputs.py`: OK.
- `generate_figures.py`: OK.
- `pytest -q`: 7 passed.
- Streamlit AppTest: 13/13 trang OK.

## 3. Tong hop 12 bai

| Bai | Mo hinh | Bang chinh | Hinh bao cao |
|---|---|---|---|
| 1 | Cobb-Douglas mo rong | `bai01_cobb_douglas.csv`, `bai01_forecast_2030.csv` | `bai01_tfp_trend.png`, `bai01_actual_vs_predicted_gdp.png`, `bai01_growth_contribution.png` |
| 2 | LP PuLP/CBC | `bai02_allocation.csv`, `bai02_constraints.csv`, `bai02_solver_summary.csv` | `bai02_budget_allocation.png`, `bai02_sensitivity_curve.png` |
| 3 | Priority Index | `bai03_priority.csv`, `bai03_sensitivity.csv` | `bai03_priority_ranking.png` |
| 4 | LP nganh-vung | `bai04_allocation.csv`, `bai04_region_summary.csv` | `bai04_region_allocation.png`, `bai04_item_mix.png` |
| 5 | MIP PuLP/CBC | `bai05_selected_projects.csv`, `bai05_projects.csv` | `bai05_selected_projects.png` |
| 6 | Entropy weight + TOPSIS | `bai06_topsis.csv`, `bai06_entropy_weights.csv` | `bai06_topsis_ranking.png` |
| 7 | NSGA-II Pareto | `bai07_pareto.csv`, `bai07_compromise.csv` | `bai07_pareto_frontier.png` |
| 8 | Toi uu dong lien thoi gian | `bai08_dynamic_plan.csv`, `bai08_dynamic_trajectory.csv`, `bai08_baseline_trajectory.csv` | `bai08_gdp_path_2026_2035.png` |
| 9 | Mo phong lao dong | `bai09_labor_impact.csv`, `bai09_threshold_result.csv` | `bai09_netjob_by_sector.png` |
| 10 | Stochastic programming Pyomo | `bai10_policy_table.csv`, `bai10_value_of_information.csv` | `bai10_scenario_values.png` |
| 11 | Q-learning | `bai11_q_table.csv`, `bai11_policy.csv` | `bai11_q_table_heatmap.png`, `bai11_reward_trace.png` |
| 12 | Dashboard tich hop | `bai12_scenarios.csv`, `bai12_module_design.csv` | `bai12_scenario_comparison.png` |

## 4. Noi dung tung bai

### Bai 1 - Cobb-Douglas mo rong

Input:

- GDP, ti le kinh te so, FDI, xuat nhap khau giai doan 2020-2025.
- Cac bien bo sung K, L, D, AI, H trong `exercise01_cobb_douglas.py`.

Mo hinh:

```text
Y = A * K^alpha * L^beta * D^gamma * AI^delta * H^theta
```

Trong do `A` la TFP, `K` la von, `L` la lao dong, `D` la muc do kinh te so, `AI` la nang luc AI, `H` la nhan luc so.

Output chinh:

- Bang TFP theo nam.
- Sai so MAPE cua du bao.
- Du bao GDP 2030 theo kich ban.
- Phan ra dong gop tang truong.

Policy brief:

- TFP va von van la nen tang tang truong.
- Kinh te so, AI va nhan luc so la nhom bien chinh sach co the tac dong trong dai han.
- Du bao 2030 nen duoc doc nhu kich ban mo phong, khong phai du bao chinh thuc.

Gia dinh/gioi han:

- He so Cobb-Douglas dat theo bo tham so lop hoc.
- Lao dong 2030 dung toc do 0,6%/nam de tranh phong dai luc luong lao dong.

### Bai 2 - LP phan bo ngan sach so

Input:

- Tong ngan sach mac dinh 100 nghin ty VND.
- Bon hang muc: ha tang so, AI va du lieu, nhan luc so, R&D cong nghe.
- Rang buoc toi thieu tung hang muc va rang buoc ty trong AI + R&D.

Mo hinh:

```text
Max Z = 0.85*x1 + 1.20*x2 + 0.95*x3 + 1.35*x4
s.t. x1 + x2 + x3 + x4 <= B
     x1 >= 25, x2 >= 15, x3 >= min_human, x4 >= 10
     x2 + x4 >= 0.35*B
```

Output chinh:

- Phan bo toi uu.
- Slack/surplus chuan hoa khong am va shadow price.
- Phan tich do nhay theo ngan sach.
- Solver summary: PuLP/CBC, shadow price lay tu `constraint pi`.

Policy brief:

- Ngan sach la rang buoc binding.
- Shadow price cua ngan sach cho biet loi ich bien khi tang ngan sach trong vung nghiem hien tai.
- Khi yeu cau nhan luc so tang, loi ich muc tieu co the giam vi bot ngan sach cho hang muc co he so cao.

Gia dinh/gioi han:

- He so loi ich la tham so mo phong phuc vu bai LP.
- SciPy/HiGHS duoc giu lam fallback, PuLP/CBC la mac dinh de phu hop ky vong LP coursework.

### Bai 3 - Chi so uu tien nganh

Input:

- Du lieu 10 nganh trong `vietnam_sectors_2024.csv`.
- Cac tieu chi: tang truong, viec lam, lan toa, xuat khau, AI readiness, rui ro tu dong hoa.

Mo hinh:

- Chuan hoa min-max tung tieu chi.
- Tinh diem uu tien bang tong trong so.
- Chay do nhay khi thay doi trong so.

Output chinh:

- Bang xep hang nganh.
- Bang chuan hoa.
- Bang do nhay top nganh.

Policy brief:

- Nganh uu tien cao nen co tang truong, lan toa va muc san sang AI tot.
- Nganh co rui ro tu dong hoa cao can di kem dao tao lai lao dong.

Gia dinh/gioi han:

- Trong so la lua chon chinh sach; can trinh bay do nhay thay vi chi dua mot thu hang.

### Bai 4 - LP phan bo nganh-vung

Input:

- Du lieu 6 vung va 10 nganh.
- Ngan sach, san vung yeu, tran vung, tran nganh.
- He so vung-nganh-hang muc mo phong tu digital index, AI readiness va priority score.

Mo hinh:

- Bien quyet dinh la phan bo theo vung, nganh va hang muc.
- Muc tieu toi da hoa loi ich ky vong.
- Rang buoc tong ngan sach, cong bang vung, gioi han tap trung nganh.

Output chinh:

- Bang phan bo chi tiet.
- Tong hop theo vung.
- Tong hop theo hang muc.

Policy brief:

- Rang buoc cong bang giup tranh don ngan sach vao mot vung/nganh.
- Ket qua la ban do uu tien, chua thay the tham dinh du an cu the.

Gia dinh/gioi han:

- He so beta la tham so mo phong do de bai khong cung cap ma tran chi tiet.

### Bai 5 - MIP chon du an

Input:

- Danh muc 15 du an mo phong.
- Cost, benefit, risk va cac rang buoc logic.
- Ngan sach va tran rui ro.

Mo hinh:

```text
Max sum benefit_i * y_i
s.t. sum cost_i * y_i <= budget
     sum risk_i * y_i <= risk_cap
     precedence/exclusion constraints
     y_i in {0,1}
```

Output chinh:

- Danh muc du an duoc chon.
- Tong chi phi, tong loi ich, tong rui ro.

Policy brief:

- MIP phu hop khi quyet dinh la chon/khong chon du an.
- Rang buoc logic giup dam bao du an nen tang duoc chon truoc du an phu thuoc.

Gia dinh/gioi han:

- Danh muc 15 du an la bo mo phong vi de bai khong cung cap danh sach chi tiet.

### Bai 6 - TOPSIS xep hang vung

Input:

- Du lieu 6 vung kinh te.
- Cac tieu chi kinh te, ha tang so, nhan luc, AI readiness va rui ro.

Mo hinh:

- Entropy weight de tinh trong so khach quan.
- TOPSIS tinh khoang cach den diem ly tuong va phan ly tuong am.

Output chinh:

- Bang trong so entropy.
- Bang diem TOPSIS va xep hang 6 vung.

Policy brief:

- Vung co diem TOPSIS cao nen duoc uu tien cho trung tam AI/kinh te so.
- Vung diem thap khong nen bi bo qua; co the can goi bao trum so.

Gia dinh/gioi han:

- TOPSIS phu thuoc vao bo tieu chi dau vao; can giai thich chieu loi ich/chi phi cua tung tieu chi.

### Bai 7 - Toi uu da muc tieu Pareto

Input:

- Ngan sach va ty trong K, D, AI, H.
- Cac ham muc tieu GDP gain, inclusion, green score, data security va risk.

Mo hinh:

- NSGA-II sinh tap nghiem Pareto.
- Moi ty trong bi chan trong khoang 10%-70%.
- Nghiem thoa hiep chon theo diem chuan hoa co phat rui ro va phat lech co cau.

Output chinh:

- Tap nghiem Pareto.
- Nghiem thoa hiep.
- Bieu do frontier GDP gain - inclusion, mau theo risk.

Policy brief:

- Khong co mot nghiem toi uu duy nhat khi co nhieu muc tieu cong.
- Can neu ro ly do chon nghiem thoa hiep tu frontier.

Gia dinh/gioi han:

- Ham muc tieu Pareto la mo phong nhat quan voi boi canh chinh sach, khong phai uoc luong thuc nghiem.

### Bai 8 - Toi uu dong 2026-2035

Input:

- Du lieu macro den 2025.
- Ngan sach hang nam mac dinh 650 nghin ty VND.
- Bien trang thai K, L, D, AI, H va TFP.

Mo hinh:

- Bien quyet dinh: ty trong K, D, AI, H theo tung nam 2026-2035.
- Rang buoc: tong ty trong bang 1, moi hang muc trong khoang 10%-60%.
- Ham muc tieu: toi da hoa GDP chiet khau tren quy dao lien thoi gian, co phat AI qua cao va thuong nhe cho nhan luc so.

Output chinh:

- `bai08_dynamic_plan.csv`: ke hoach ty trong theo nam.
- `bai08_dynamic_trajectory.csv`: quy dao GDP va bien trang thai.
- Solver hien tai trong venv: `scipy.SLSQP_intertemporal_NLP`; neu co CVXPY thi code uu tien CVXPY.

Policy brief:

- Quyet dinh nam dau anh huong trang thai cac nam sau, nen can toi uu lien thoi gian.
- Mo hinh tranh cach doc ngan han chi toi da hoa GDP mot nam.

Gia dinh/gioi han:

- Day la NLP mo phong phuc vu coursework; khong thay the mo hinh kinh te luong chinh thuc.
- Venv hien tai chua co CVXPY, nen SLSQP dang la solver thuc thi.

### Bai 9 - Tac dong AI toi lao dong

Input:

- Lao dong theo nganh.
- Rui ro tu dong hoa.
- AI readiness, adoption rate, training budget, AI investment.

Mo hinh:

```text
NetJob = NewJobs + JobsSaved - JobLoss
```

Output chinh:

- Job loss, job creation, jobs saved va NetJob theo nganh.
- Nguong ngan sach dao tao de tat ca nganh khong am NetJob.

Policy brief:

- AI co the tao viec lam moi, nhung khong tu dam bao NetJob duong.
- Dao tao lai la bien chinh sach quan trong nhat de giam mat viec rong.

Gia dinh/gioi han:

- He so tao viec/giu viec la tham so mo phong theo readiness va training allocation.

### Bai 10 - Stochastic programming hai giai doan

Input:

- Ngan sach 80.000 ty VND mac dinh.
- Ba kich ban: lac quan, co so, bi quan.
- Bien bat dinh: demand factor, FDI factor, risk factor.

Mo hinh:

- First-stage: chon ty trong K, D, AI, H.
- Second-stage: recourse cost khi cau thap.
- Rang buoc hap thu chinh sach: AI <= 50%, H >= 15%.
- Solver: Pyomo `appsi_highs`.

Output chinh:

- Policy table.
- Gia tri theo kich ban.
- VSS va EVPI.
- `bai10_value_of_information.csv` giai thich `VSS = 0`, `EVPI > 0`.

Policy brief:

- Stochastic programming chon quyet dinh here-and-now tot tren nhieu kich ban.
- VSS bang 0 trong bo tham so hien tai nghia la chinh sach expected-value trung hoac khong kem chinh sach stochastic.
- EVPI duong nghia la thong tin hoan hao van co gia tri neu co the doi quyet dinh theo tung kich ban.

Gia dinh/gioi han:

- Ba kich ban la mo phong noi bo; xac suat kich ban can duoc neu ro trong bao cao.

### Bai 11 - Q-learning chinh sach thich nghi

Input:

- Tap trang thai kinh te mo phong.
- Tap hanh dong la 5 cau hinh K, D, AI, H.
- Reward can bang GDP, so hoa, AI, bao trum va rui ro.

Mo hinh:

```text
Q(s,a) <- Q(s,a) + alpha * [r + gamma * max_a' Q(s',a') - Q(s,a)]
```

Output chinh:

- Q-table.
- Policy hoc duoc theo trang thai.
- Reward trace.

Policy brief:

- Q-learning minh hoa chinh sach thich nghi theo trang thai thay vi mot nghiem co dinh.
- Ket qua nen dung de giai thich logic hoc tang cuong, khong thay the quyet dinh ngan sach cuoi cung.

Gia dinh/gioi han:

- MDP va reward la mo phong noi bo, chua duoc hieu chinh bang du lieu thuc nghiem.

### Bai 12 - AIDEOM-VN tich hop

Input:

- Output logic tu cac module M1-M5.
- Sau kich ban chinh sach S1-S6.
- Tong ngan sach kich ban mac dinh 80.000 ty VND.

Mo hinh:

- Tinh KPI cho moi kich ban: GDP gain, inclusion, risk index, NetJob.
- Tinh overall score tu rank percentile cua GDP, inclusion, NetJob va risk.
- Thiet ke 6 module he thong: du bao kinh te, san sang so, toi uu phan bo, lao dong, rui ro, dashboard.

Output chinh:

- `bai12_scenarios.csv`: xep hang 6 kich ban.
- S6 Reskilling manh co NetJob duong trong bo tham so mac dinh.
- `bai12_module_design.csv`: thiet ke module he thong.

Policy brief:

- S6 cho thay neu muon NetJob duong can co goi reskilling manh, khong chi dau tu AI/so hoa.
- S3 AI dan dat co the co GDP gain cao nhung risk cao va NetJob yeu.
- S5 la phuong an can bang de so sanh khi hoi dong uu tien tang truong hon bao trum.

Gia dinh/gioi han:

- Overall score la thang diem tong hop theo trong so rank ngang nhau; neu doi trong so, thu hang co the thay doi.
- Training multiplier cua S6 la kich ban chinh sach tang cuong, can ghi ro la mo phong.

## 5. Noi dung can dua vao ket luan bao cao

1. Web app da dap ung phuong an 3: 12 menu, tham so chinh duoc, bang, bieu do, Policy Brief va luu figures.
2. Cac bai rui ro hoc thuat cao da duoc nang cap: Bai 2 PuLP/CBC, Bai 5 PuLP/CBC, Bai 7 NSGA-II, Bai 8 toi uu lien thoi gian, Bai 10 Pyomo stochastic.
3. Ket qua chinh sach can duoc doc nhu mo phong ho tro ra quyet dinh, khong phai du bao thong ke chinh thuc.
4. Diem can nhan manh khi bao ve: neu khong co reskilling du manh, AI/so hoa co the lam NetJob am; S6 minh hoa dieu kien de dao chieu ket qua nay.
5. VSS = 0 trong Bai 10 khong phai loi; do bo tham so hien tai lam expected-value policy trung/khong kem stochastic policy, trong khi EVPI duong van cho thay gia tri cua thong tin hoan hao.

## 6. Checklist chen hinh vao Word/PDF

- Bai 1: chen 2-3 hinh ve TFP, GDP thuc te-du bao, dong gop tang truong.
- Bai 2: chen phan bo ngan sach va sensitivity.
- Bai 3: chen ranking nganh.
- Bai 4: chen phan bo vung va co cau hang muc.
- Bai 5: chen du an duoc chon.
- Bai 6: chen TOPSIS ranking.
- Bai 7: chen Pareto frontier.
- Bai 8: chen GDP path 2026-2035 va bang plan ty trong.
- Bai 9: chen NetJob theo nganh.
- Bai 10: chen gia tri theo kich ban va bang VSS/EVPI.
- Bai 11: chen Q-table heatmap va reward trace.
- Bai 12: chen so sanh 6 kich ban va bang module design.

## 7. Viec con lai truoc khi nop

- Ra browser that bang mat tung trang neu can chat luong trinh bay cao.
- Doi cac tieu de/nhan khong dau thanh co dau neu muon ban Word dep hon; hien tai output CSV va hinh uu tien on dinh render.
- Xuat Word/PDF tu file nay va cac hinh trong `outputs/figures/`.
- Chi dong goi zip/rar sau khi da chot bao cao va giao dien.
