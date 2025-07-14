import pandas as pd
import numpy as np
from faker import Faker
import random
from datetime import datetime, timedelta

# Khởi tạo Faker với locale tiếng Việt
fake = Faker('vi_VN')

# Thiết lập seed để tái tạo dữ liệu
np.random.seed(42)
random.seed(42)

# Hàm tạo ngày ngẫu nhiên trong khoảng thời gian
def random_date(start_date, end_date):
    time_between = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, time_between))

# 1. Tạo bảng Departments
departments = [
    {"department_id": f"DEP{i:03d}", "department_name": name, "manager_id": f"NV{random.randint(1, 50):03d}"}
    for i, name in enumerate([
        "Phòng Tín dụng", "Phòng Giao dịch", "Phòng Quan hệ khách hàng", "Phòng Kế toán",
        "Phòng Nhân sự", "Phòng Kiểm toán", "Phòng Marketing", "Phòng Công nghệ thông tin",
        "Phòng Pháp chế", "Phòng Quản lý rủi ro"
    ], 1)
]
df_departments = pd.DataFrame(departments)

# 2. Tạo bảng Positions
positions = [
    {"position_id": f"POS{i:03d}", "position_name": name, "base_salary": salary, "description": f"Mô tả {name}"}
    for i, (name, salary) in enumerate([
        ("Giao dịch viên", 10000000), ("Chuyên viên tín dụng", 15000000), ("Chuyên viên quan hệ khách hàng", 18000000),
        ("Quản lý chi nhánh", 30000000), ("Chuyên viên kiểm toán", 20000000), ("Chuyên viên marketing", 15000000),
        ("Chuyên viên CNTT", 20000000), ("Nhân viên nhân sự", 12000000), ("Chuyên viên pháp chế", 18000000),
        ("Quản lý rủi ro", 25000000)
    ], 1)
]
df_positions = pd.DataFrame(positions)

# 3. Tạo bảng Branches
branches = [
    {"branch_id": f"BR{i:03d}", "branch_name": name, "address": fake.address(), "region": region}
    for i, (name, region) in enumerate([
        ("Chi nhánh Hà Nội", "Hà Nội"), ("Chi nhánh TP.HCM", "TP.HCM"), 
        ("Chi nhánh Đà Nẵng", "Đà Nẵng"), ("Chi nhánh Hải Phòng", "Hải Phòng"), 
        ("Chi nhánh Cần Thơ", "Cần Thơ")
    ], 1)
]
df_branches = pd.DataFrame(branches)

# 4. Tạo bảng Employees
employees = []
start_date = datetime(2020, 1, 1)
end_date = datetime(2025, 7, 1)
for i in range(1, 501):  # 500 nhân viên
    employees.append({
        "employee_id": f"NV{i:03d}",
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "date_of_birth": random_date(datetime(1970, 1, 1), datetime(2000, 1, 1)).strftime("%Y-%m-%d"),
        "gender": random.choice(["M", "F", "Other"]),
        "phone": fake.phone_number(),
        "email": fake.email(),
        "address": fake.address(),
        "hire_date": random_date(start_date, end_date).strftime("%Y-%m-%d"),
        "department_id": random.choice(departments)["department_id"],
        "position_id": random.choice(positions)["position_id"],
        "branch_id": random.choice(branches)["branch_id"],
        "status": random.choice(["Active", "On Leave", "Terminated"])
    })
df_employees = pd.DataFrame(employees)

# 5. Tạo bảng Allowances
allowances = []
allowance_types = ["Ăn trưa", "Đi lại", "Điện thoại", "Trách nhiệm"]
for emp in employees:
    for _ in range(random.randint(1, 3)):  # Mỗi nhân viên có 1-3 phụ cấp
        allowances.append({
            "allowance_id": f"ALW{len(allowances)+1:04d}",
            "employee_id": emp["employee_id"],
            "allowance_type": random.choice(allowance_types),
            "amount": random.randint(1000000, 5000000),
            "start_date": random_date(start_date, end_date).strftime("%Y-%m-%d"),
            "end_date": random.choice([None, random_date(end_date, datetime(2026, 1, 1)).strftime("%Y-%m-%d")])
        })
df_allowances = pd.DataFrame(allowances)

# 6. Tạo bảng KPIs
kpis = []
kpi_types = ["Huy động vốn", "Cho vay", "Bán sản phẩm"]
for emp in employees:
    for month in range(1, 13):  # 12 tháng trong năm 2025
        kpis.append({
            "kpi_id": f"KPI{len(kpis)+1:04d}",
            "employee_id": emp["employee_id"],
            "month_year": f"2025-{month:02d}",
            "kpi_type": random.choice(kpi_types),
            "target": random.randint(10000000000, 50000000000),  # 10-50 tỷ
            "achieved": random.randint(8000000000, 60000000000),  # 8-60 tỷ
            "bonus_rate": round(random.uniform(0.05, 0.2), 2),
            "bonus_amount": 0  # Sẽ tính sau
        })
df_kpis = pd.DataFrame(kpis)

# Tính bonus_amount dựa trên KPI
df_kpis["bonus_amount"] = df_kpis.apply(
    lambda row: int(row["achieved"] * row["bonus_rate"] * (row["achieved"] / row["target"])
                    if row["achieved"] >= row["target"] else 0), axis=1)

# 7. Tạo bảng Salaries
salaries = []
for emp in employees:
    position_salary = next(pos["base_salary"] for pos in positions if pos["position_id"] == emp["position_id"])
    for month in range(1, 13):
        emp_kpis = df_kpis[(df_kpis["employee_id"] == emp["employee_id"]) & (df_kpis["month_year"] == f"2025-{month:02d}")]
        total_bonus = emp_kpis["bonus_amount"].sum()
        emp_allowances = df_allowances[df_allowances["employee_id"] == emp["employee_id"]]
        total_allowances = emp_allowances["amount"].sum()
        
        # Tính thuế TNCN (giả định đơn giản theo biểu thuế lũy tiến)
        taxable_income = position_salary + total_allowances + total_bonus - 11000000  # Giảm trừ 11 triệu
        tax = 0
        if taxable_income > 0:
            if taxable_income <= 5000000:
                tax = taxable_income * 0.05
            elif taxable_income <= 10000000:
                tax = 250000 + (taxable_income - 5000000) * 0.1
            elif taxable_income <= 18000000:
                tax = 750000 + (taxable_income - 10000000) * 0.15
            else:
                tax = 1950000 + (taxable_income - 18000000) * 0.2  # Chỉ tính đến 35 triệu để đơn giản
        net_salary = position_salary + total_allowances + total_bonus - tax
        
        salaries.append({
            "salary_id": f"SAL{len(salaries)+1:04d}",
            "employee_id": emp["employee_id"],
            "month_year": f"2025-{month:02d}",
            "base_salary": position_salary,
            "allowances": total_allowances,
            "bonus": total_bonus,
            "tax": tax,
            "net_salary": net_salary,
            "payment_date": f"2025-{month:02d}-10"
        })
df_salaries = pd.DataFrame(salaries)

# 8. Tạo bảng Benefits
benefits = []
benefit_types = ["Bảo hiểm y tế", "Vay ưu đãi", "Nghỉ phép"]
for emp in employees:
    for _ in range(random.randint(1, 2)):
        benefits.append({
            "benefit_id": f"BEN{len(benefits)+1:04d}",
            "employee_id": emp["employee_id"],
            "benefit_type": random.choice(benefit_types),
            "details": f"Chi tiết {random.choice(benefit_types)}",
            "start_date": random_date(start_date, end_date).strftime("%Y-%m-%d"),
            "end_date": random.choice([None, random_date(end_date, datetime(2026, 1, 1)).strftime("%Y-%m-%d")])
        })
df_benefits = pd.DataFrame(benefits)

# 9. Tạo bảng Tax_Rates
tax_rates = [
    {"tax_id": f"TAX{i:03d}", "income_min": min_income, "income_max": max_income, "tax_rate": rate}
    for i, (min_income, max_income, rate) in enumerate([
        (0, 5000000, 0.05), (5000001, 10000000, 0.1), (10000001, 18000000, 0.15),
        (18000001, 32000000, 0.2), (32000001, 52000000, 0.25), (52000001, 80000000, 0.3),
        (80000001, float("inf"), 0.35)
    ], 1)
]
df_tax_rates = pd.DataFrame(tax_rates)

# Lưu dữ liệu vào các file CSV
df_departments.to_csv("departments.csv", index=False)
df_positions.to_csv("positions.csv", index=False)
df_branches.to_csv("branches.csv", index=False)
df_employees.to_csv("employees.csv", index=False)
df_allowances.to_csv("allowances.csv", index=False)
df_kpis.to_csv("kpis.csv", index=False)
df_salaries.to_csv("salaries.csv", index=False)
df_benefits.to_csv("benefits.csv", index=False)
df_tax_rates.to_csv("tax_rates.csv", index=False)

print("Dữ liệu đã được sinh và lưu vào các file CSV: departments.csv, positions.csv, branches.csv, employees.csv, allowances.csv, kpis.csv, salaries.csv, benefits.csv, tax_rates.csv")