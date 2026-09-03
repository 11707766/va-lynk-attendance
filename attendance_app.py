import json
from datetime import datetime, time
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk


COMPANY_NAME = "VA Lynk Job Pvt. Ltd."
DATA_FILE = Path(__file__).with_name("attendance_data.json")
OFFICE_IN = time(9, 30)
OFFICE_OUT = time(18, 30)


def load_data():
    if DATA_FILE.exists():
        try:
            return json.loads(DATA_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {
        "employees": [
            {
                "id": "EMP001",
                "name": "Aarav Sharma",
                "position": "Executive",
                "salary": 25000,
                "contact": "9876543210",
            }
        ],
        "attendance": [],
    }


def save_data():
    DATA_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")


def worked_hours(record):
    if not record.get("punch_out"):
        return 0
    punch_in = datetime.fromisoformat(record["punch_in"])
    punch_out = datetime.fromisoformat(record["punch_out"])
    return round((punch_out - punch_in).total_seconds() / 3600, 2)


def deduction(record, employee):
    hours = worked_hours(record)
    if not hours:
        return 0
    hourly_rate = float(employee["salary"]) / (26 * 9)
    return round(max(0, 9 - hours) * hourly_rate, 2)


data = load_data()


class AttendanceApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{COMPANY_NAME} | Attendance")
        self.geometry("980x640")
        self.minsize(860, 560)
        self.configure(bg="#f5f7f4")
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=(14, 8), background="#e4a84a", foreground="#173f3a", borderwidth=0)
        style.map("TButton", background=[("active", "#d79532"), ("disabled", "#d8dfda")])
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=34, background="white", fieldbackground="white", foreground="#203532", borderwidth=0)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), background="#dfe9e3", foreground="#173f3a", relief="flat", padding=9)
        style.map("Treeview", background=[("selected", "#cae6da")], foreground=[("selected", "#173f3a")])
        self.selected_employee = tk.StringVar()
        self.login_role = tk.StringVar(value="employee")
        self.dashboard_date = tk.StringVar(value=datetime.now().date().isoformat())
        self.build_login()

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def build_login(self):
        self.clear_window()
        container = tk.Frame(self, bg="#f5f7f4", padx=40, pady=38)
        container.place(relx=0.5, rely=0.5, anchor="center")
        tk.Label(container, text=COMPANY_NAME, font=("Segoe UI", 23, "bold"), bg="#f5f7f4", fg="#173f3a").pack()
        tk.Label(container, text="Employee Attendance Portal", font=("Segoe UI", 12), bg="#f5f7f4", fg="#50635e").pack(pady=(6, 26))

        card = tk.Frame(container, bg="white", padx=30, pady=27, highlightbackground="#d6ded9", highlightthickness=1)
        card.pack()
        tk.Label(card, text="Sign in", font=("Segoe UI", 16, "bold"), bg="white", fg="#173f3a").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 18))
        tk.Radiobutton(card, text="Employee", variable=self.login_role, value="employee", bg="white", activebackground="white").grid(row=1, column=0, sticky="w")
        tk.Radiobutton(card, text="Manager", variable=self.login_role, value="manager", bg="white", activebackground="white").grid(row=1, column=1, sticky="w")
        tk.Label(card, text="Employee", bg="white").grid(row=2, column=0, columnspan=2, sticky="w", pady=(18, 4))
        self.employee_combo = ttk.Combobox(card, textvariable=self.selected_employee, state="readonly", width=31)
        self.employee_combo.grid(row=3, column=0, columnspan=2, sticky="ew")
        self.refresh_employee_choices()
        tk.Label(card, text="Manager PIN", bg="white").grid(row=4, column=0, columnspan=2, sticky="w", pady=(14, 4))
        self.pin_entry = ttk.Entry(card, show="*", width=34)
        self.pin_entry.grid(row=5, column=0, columnspan=2, sticky="ew")
        tk.Label(card, text="Demo manager PIN: 1234", font=("Segoe UI", 9), bg="white", fg="#687873").grid(row=6, column=0, columnspan=2, sticky="w", pady=(5, 15))
        ttk.Button(card, text="Continue", command=self.login).grid(row=7, column=0, columnspan=2, sticky="ew")

    def refresh_employee_choices(self):
        values = [f"{employee['id']} - {employee['name']}" for employee in data["employees"]]
        self.employee_combo["values"] = values
        if values and not self.selected_employee.get():
            self.selected_employee.set(values[0])

    def login(self):
        if self.login_role.get() == "manager":
            if self.pin_entry.get() != "1234":
                messagebox.showerror("Access denied", "Enter the correct manager PIN.")
                return
            self.build_manager_dashboard()
            return
        if not self.selected_employee.get():
            messagebox.showerror("Employee required", "Add an employee before signing in.")
            return
        employee_id = self.selected_employee.get().split(" - ", 1)[0]
        self.build_employee_dashboard(employee_id)

    def header(self, title, subtitle):
        top = tk.Frame(self, bg="#173f3a", padx=28, pady=18)
        top.pack(fill="x")
        tk.Label(top, text=COMPANY_NAME, font=("Segoe UI", 17, "bold"), bg="#173f3a", fg="white").pack(anchor="w")
        tk.Label(top, text=f"{title} | {subtitle}", font=("Segoe UI", 10), bg="#173f3a", fg="#c5ddd4").pack(anchor="w", pady=(2, 0))
        ttk.Button(top, text="Sign out", command=self.build_login).pack(anchor="e", side="right")

    def employee_by_id(self, employee_id):
        return next(employee for employee in data["employees"] if employee["id"] == employee_id)

    def today_record(self, employee_id):
        return self.attendance_record(employee_id, datetime.now().date().isoformat())

    def attendance_record(self, employee_id, attendance_date):
        return next((record for record in data["attendance"] if record["employee_id"] == employee_id and record["date"] == attendance_date), None)

    def refresh_dashboard_date(self):
        try:
            datetime.strptime(self.dashboard_date.get(), "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Invalid date", "Use the YYYY-MM-DD date format.")
            return
        self.build_manager_dashboard()

    def build_employee_dashboard(self, employee_id):
        self.clear_window()
        employee = self.employee_by_id(employee_id)
        self.header("Employee dashboard", employee["name"])
        content = tk.Frame(self, bg="#f5f7f4", padx=28, pady=26)
        content.pack(fill="both", expand=True)
        tk.Label(content, text=f"Welcome, {employee['name']}", font=("Segoe UI", 20, "bold"), bg="#f5f7f4", fg="#173f3a").pack(anchor="w")
        tk.Label(content, text="Office hours: 9:30 AM to 6:30 PM", font=("Segoe UI", 11), bg="#f5f7f4", fg="#50635e").pack(anchor="w", pady=(4, 22))

        record = self.today_record(employee_id)
        status_frame = tk.Frame(content, bg="white", padx=24, pady=22, highlightbackground="#d6ded9", highlightthickness=1)
        status_frame.pack(fill="x")
        now_text = datetime.now().strftime("%A, %d %B %Y")
        tk.Label(status_frame, text=now_text, font=("Segoe UI", 12, "bold"), bg="white", fg="#173f3a").grid(row=0, column=0, sticky="w")
        if not record:
            status = "You have not punched in today."
        elif not record.get("punch_out"):
            status = f"Punched in at {datetime.fromisoformat(record['punch_in']).strftime('%I:%M %p')}"
        else:
            status = f"Completed: {worked_hours(record):.2f} hours worked"
        tk.Label(status_frame, text=status, font=("Segoe UI", 12), bg="white", fg="#50635e").grid(row=1, column=0, sticky="w", pady=(9, 18))
        action_text = "Punch in" if not record else "Punch out" if not record.get("punch_out") else "Punch complete"
        ttk.Button(status_frame, text=action_text, command=lambda: self.punch(employee_id), state="normal" if action_text != "Punch complete" else "disabled").grid(row=2, column=0, sticky="w")

    def punch(self, employee_id):
        record = self.today_record(employee_id)
        now = datetime.now().isoformat(timespec="seconds")
        if not record:
            data["attendance"].append({"employee_id": employee_id, "date": datetime.now().date().isoformat(), "punch_in": now, "punch_out": None})
            messagebox.showinfo("Punch in recorded", f"Punch in recorded at {datetime.now().strftime('%I:%M %p')}.")
        else:
            record["punch_out"] = now
            messagebox.showinfo("Punch out recorded", f"Punch out recorded at {datetime.now().strftime('%I:%M %p')}.")
        save_data()
        self.build_employee_dashboard(employee_id)

    def build_manager_dashboard(self):
        self.clear_window()
        self.header("Manager dashboard", "Attendance and payroll overview")
        content = tk.Frame(self, bg="#f5f7f4", padx=28, pady=22)
        content.pack(fill="both", expand=True)
        toolbar = tk.Frame(content, bg="#f5f7f4")
        toolbar.pack(fill="x", pady=(0, 12))
        tk.Label(toolbar, text="Today's workforce", font=("Segoe UI", 19, "bold"), bg="#f5f7f4", fg="#173f3a").pack(side="left")
        ttk.Button(toolbar, text="Add employee", command=self.employee_form).pack(side="right")

        date_bar = tk.Frame(content, bg="white", padx=15, pady=11, highlightbackground="#d6ded9", highlightthickness=1)
        date_bar.pack(fill="x", pady=(0, 14))
        tk.Label(date_bar, text="ATTENDANCE DATE", font=("Segoe UI", 9, "bold"), bg="white", fg="#50635e").pack(side="left")
        saved_dates = sorted({record["date"] for record in data["attendance"]}, reverse=True)
        date_choices = [datetime.now().date().isoformat()] + [date for date in saved_dates if date != datetime.now().date().isoformat()]
        date_picker = ttk.Combobox(date_bar, textvariable=self.dashboard_date, values=date_choices, width=14)
        date_picker.pack(side="left", padx=(12, 8))
        ttk.Button(date_bar, text="View date", command=self.refresh_dashboard_date).pack(side="left")
        try:
            display_date = datetime.strptime(self.dashboard_date.get(), "%Y-%m-%d").strftime("%A, %d %B %Y")
        except ValueError:
            display_date = self.dashboard_date.get()
        tk.Label(date_bar, text=display_date, font=("Segoe UI", 10), bg="white", fg="#25835f").pack(side="right")

        records = {record["employee_id"]: record for record in data["attendance"] if record["date"] == self.dashboard_date.get()}
        checked_in = sum(1 for record in records.values() if record.get("punch_in"))
        completed = sum(1 for record in records.values() if record.get("punch_out"))
        total_deductions = sum(deduction(record, self.employee_by_id(employee_id)) for employee_id, record in records.items() if record.get("punch_out"))
        metrics = tk.Frame(content, bg="#f5f7f4")
        metrics.pack(fill="x", pady=(0, 20))
        for index, (label, value, color) in enumerate((
            ("TOTAL EMPLOYEES", str(len(data["employees"])), "#173f3a"),
            ("PUNCHED IN", str(checked_in), "#25835f"),
            ("DAY COMPLETE", str(completed), "#3f7390"),
            ("TODAY'S DEDUCTIONS", f"Rs. {total_deductions:,.0f}", "#b56132"),
        )):
            card = tk.Frame(metrics, bg="white", padx=16, pady=13, highlightbackground="#d6ded9", highlightthickness=1)
            card.grid(row=0, column=index, sticky="ew", padx=(0, 10) if index < 3 else 0)
            metrics.grid_columnconfigure(index, weight=1)
            tk.Label(card, text=label, font=("Segoe UI", 8, "bold"), bg="white", fg="#6b7c76").pack(anchor="w")
            tk.Label(card, text=value, font=("Segoe UI", 18, "bold"), bg="white", fg=color).pack(anchor="w", pady=(5, 0))

        tk.Label(content, text="Employee register", font=("Segoe UI", 13, "bold"), bg="#f5f7f4", fg="#173f3a").pack(anchor="w", pady=(0, 3))
        tk.Label(content, text="Review attendance, worked hours, and salary impact for the selected date.", font=("Segoe UI", 9), bg="#f5f7f4", fg="#50635e").pack(anchor="w", pady=(0, 8))

        columns = ("id", "name", "position", "contact", "salary", "today", "hours", "deduction")
        tree = ttk.Treeview(content, columns=columns, show="headings", height=14)
        headings = {"id": "ID", "name": "Name", "position": "Position", "contact": "Contact", "salary": "Monthly salary", "today": "Today", "hours": "Hours", "deduction": "Deduction"}
        for column in columns:
            tree.heading(column, text=headings[column])
            tree.column(column, width=105, anchor="center")
        tree.column("name", width=150, anchor="w")
        tree.column("position", width=125, anchor="w")
        for employee in data["employees"]:
            record = self.attendance_record(employee["id"], self.dashboard_date.get())
            state = "Not punched" if not record else "Working" if not record.get("punch_out") else "Complete"
            tag = "absent" if not record else "working" if not record.get("punch_out") else "complete"
            tree.insert("", "end", iid=employee["id"], tags=(tag,), values=(employee["id"], employee["name"], employee["position"], employee["contact"], f"Rs. {float(employee['salary']):,.0f}", state, f"{worked_hours(record):.2f}" if record else "-", f"Rs. {deduction(record, employee):,.2f}" if record and record.get("punch_out") else "-"))
        tree.tag_configure("absent", background="#fff6ed")
        tree.tag_configure("working", background="#edf8f2")
        tree.tag_configure("complete", background="#eef5fa")
        tree.pack(fill="both", expand=True)
        actions = tk.Frame(content, bg="#f5f7f4")
        actions.pack(fill="x", pady=12)
        ttk.Button(actions, text="Edit selected", command=lambda: self.employee_form(tree.selection()[0] if tree.selection() else None)).pack(side="left")
        ttk.Button(actions, text="Delete selected", command=lambda: self.delete_employee(tree.selection()[0] if tree.selection() else None)).pack(side="left", padx=8)
        tk.Label(content, text="Deduction is calculated from the 9-hour daily target using monthly salary / 26 working days / 9 hours.", bg="#f5f7f4", fg="#50635e", font=("Segoe UI", 9)).pack(anchor="w")

    def employee_form(self, employee_id=None):
        existing = self.employee_by_id(employee_id) if employee_id else None
        dialog = tk.Toplevel(self)
        dialog.title("Edit employee" if existing else "Add employee")
        dialog.transient(self)
        dialog.grab_set()
        form = tk.Frame(dialog, padx=22, pady=20)
        form.pack()
        fields = {}
        for row, (key, label) in enumerate((("name", "Full name"), ("position", "Position"), ("salary", "Monthly salary (Rs.)"), ("contact", "Contact number"))):
            tk.Label(form, text=label).grid(row=row, column=0, sticky="w", pady=5)
            entry = ttk.Entry(form, width=31)
            entry.grid(row=row, column=1, pady=5)
            if existing:
                entry.insert(0, str(existing[key]))
            fields[key] = entry

        def save_employee():
            values = {key: entry.get().strip() for key, entry in fields.items()}
            if not all(values.values()):
                messagebox.showerror("Missing details", "Complete every employee field.", parent=dialog)
                return
            try:
                values["salary"] = float(values["salary"])
            except ValueError:
                messagebox.showerror("Invalid salary", "Salary must be a number.", parent=dialog)
                return
            if existing:
                existing.update(values)
            else:
                values["id"] = f"EMP{len(data['employees']) + 1:03d}"
                data["employees"].append(values)
            save_data()
            dialog.destroy()
            self.build_manager_dashboard()

        ttk.Button(form, text="Save employee", command=save_employee).grid(row=4, column=0, columnspan=2, sticky="ew", pady=(14, 0))

    def delete_employee(self, employee_id):
        if not employee_id:
            messagebox.showwarning("Select an employee", "Select an employee row first.")
            return
        employee = self.employee_by_id(employee_id)
        if not messagebox.askyesno("Delete employee", f"Delete {employee['name']} and their attendance records?"):
            return
        data["employees"] = [item for item in data["employees"] if item["id"] != employee_id]
        data["attendance"] = [item for item in data["attendance"] if item["employee_id"] != employee_id]
        save_data()
        self.build_manager_dashboard()


if __name__ == "__main__":
    AttendanceApp().mainloop()