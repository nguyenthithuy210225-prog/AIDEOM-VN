# Figure Index

Các hình trong thư mục này được sinh tự động bằng `scripts/generate_figures.py`.
Nguồn số liệu là các CSV trong `outputs/tables/` được sinh bởi `scripts/generate_outputs.py`.

| File | Tiêu đề | Nguồn | Model | Ghi chú |
|---|---|---|---|---|
| `bai01_tfp_trend.png` | Bài 1 - Xu hướng TFP A_t | `bai01_cobb_douglas.csv` | `run_cobb_douglas()` | TFP tính ngược từ hàm Cobb-Douglas mở rộng. |
| `bai01_actual_vs_predicted_gdp.png` | Bài 1 - GDP thực tế và dự báo | `bai01_cobb_douglas.csv` | `run_cobb_douglas()` | So sánh GDP thực tế với GDP dự báo bằng TFP trung bình. |
| `bai01_growth_contribution.png` | Bài 1 - Tỷ trọng đóng góp tăng trưởng | `bai01_growth_accounting.csv` | `growth_contribution()` | Phân rã tăng trưởng theo TFP, K, L, D, AI và H. |
| `bai02_budget_allocation.png` | Bài 2 - Phân bổ ngân sách tối ưu | `bai02_allocation.csv` | `solve_simple_budget_lp()` | Nghiệm LP cho bốn hạng mục đầu tư số. |
| `bai02_sensitivity_curve.png` | Bài 2 - Độ nhạy ngân sách | `bai02_sensitivity.csv` | `sensitivity_by_budget()` | Giá trị mục tiêu tối ưu khi tăng ngân sách tổng. |
| `bai03_priority_ranking.png` | Bài 3 - Xếp hạng ưu tiên 10 ngành | `bai03_priority.csv` | `run_priority_model()` | Chỉ số ưu tiên sau chuẩn hóa min-max và trọng số chính sách. |
| `bai04_region_allocation.png` | Bài 4 - Phân bổ ngân sách theo vùng | `bai04_region_summary.csv` | `solve_region_sector_lp()` | Tổng phân bổ sau ràng buộc công bằng vùng miền. |
| `bai04_item_mix.png` | Bài 4 - Cơ cấu hạng mục | `bai04_item_summary.csv` | `solve_region_sector_lp()` | Tỷ trọng ngân sách theo I, D, AI và H. |
| `bai05_selected_projects.png` | Bài 5 - Lợi ích các dự án được chọn | `bai05_selected_projects.csv` | `solve_project_mip() / PuLP_CBC` | Danh mục dự án tối ưu dưới ngân sách, rủi ro và ràng buộc logic. |
| `bai06_topsis_ranking.png` | Bài 6 - TOPSIS xếp hạng ưu tiên vùng AI | `bai06_topsis.csv` | `run_topsis()` | Điểm gần phương án lý tưởng tốt theo TOPSIS. |
| `bai07_pareto_frontier.png` | Bài 7 - Pareto frontier | `bai07_pareto.csv` | `run_pareto_search() / pymoo.NSGA2` | Mẫu cố định từ tập nghiệm Pareto để báo cáo dễ đọc. |
| `bai08_gdp_path_2026_2035.png` | Bài 8 - Quỹ đạo GDP 2026-2035 | `bai08_dynamic_trajectory.csv + bai08_baseline_trajectory.csv` | `optimize_dynamic_policy() / CVXPY-or-SLSQP` | Đường GDP dưới mô hình tối ưu liên thời gian formal. |
| `bai09_netjob_by_sector.png` | Bài 9 - NetJob theo ngành | `bai09_labor_impact.csv` | `simulate_labor_impact()` | NetJob = việc làm mới + việc làm giữ lại - việc làm mất đi. |
| `bai10_scenario_values.png` | Bài 10 - Giá trị theo kịch bản | `bai10_scenario_values.csv` | `solve_stochastic_policy() / Pyomo appsi_highs` | Giá trị quyết định stochastic trong ba trạng thái bất định. |
| `bai11_q_table_heatmap.png` | Bài 11 - Q-table heatmap | `bai11_q_table.csv` | `train_q_learning()` | Giá trị Q theo trạng thái và hành động. |
| `bai11_reward_trace.png` | Bài 11 - Reward trace | `train_q_learning() regenerated with default seed` | `train_q_learning()` | Reward được tái tạo bằng cùng seed mặc định để phục vụ báo cáo. |
| `bai12_scenario_comparison.png` | Bài 12 - So sánh kịch bản | `bai12_scenarios.csv` | `evaluate_scenarios()` | So sánh GDP gain, KPI bao trùm và NetJob của 6 kịch bản. |
