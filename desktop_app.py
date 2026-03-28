import customtkinter as ctk
from tkinter import messagebox
from datetime import datetime
from sqlalchemy.orm import Session
from database import engine, SessionLocal, Base
from models import Patient, PatientLog

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class PsychoApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Психо-Учет (Desktop)")
        self.geometry("1100x700")

        self.init_database()

        self.edit_patient_id = None
        self.current_patient_id = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)


        self.sidebar = ctk.CTkFrame(self, width=200)
        self.sidebar.grid(row=0, column=0, sticky="ns", padx=10, pady=10)

        ctk.CTkLabel(self.sidebar, text="Меню", font=ctk.CTkFont(size=20)).pack(pady=20)
        ctk.CTkButton(self.sidebar, text="📋 Пациенты", command=self.show_patients).pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(self.sidebar, text="➕ Добавить", command=self.show_add_form).pack(pady=10, padx=10, fill="x")
        ctk.CTkButton(self.sidebar, text="📝 Журнал", command=self.show_logs).pack(pady=10, padx=10, fill="x")

        self.update_sidebar_stats()

        self.main_area = ctk.CTkFrame(self)
        self.main_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.show_patients()

    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        Base.metadata.create_all(bind=engine)
        self.db = SessionLocal()

    def update_sidebar_stats(self):
        """Обновление статистики в боковой панели"""
        total = self.db.query(Patient).count()
        active = self.db.query(Patient).filter(Patient.status == "Активен").count()

        for widget in self.sidebar.winfo_children():
            if isinstance(widget, ctk.CTkLabel) and (
                    "Всего" in widget.cget("text") or "Активных" in widget.cget("text")):
                widget.destroy()

        ctk.CTkLabel(self.sidebar, text=f"Всего: {total}",
                     font=ctk.CTkFont(size=12), text_color="gray").pack(pady=5, padx=10)
        ctk.CTkLabel(self.sidebar, text=f"Активных: {active}",
                     font=ctk.CTkFont(size=12), text_color="green").pack(pady=5, padx=10)


    def show_patients(self, search_term=""):
        """Отображение списка пациентов"""
        for widget in self.main_area.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_area, text="📋 Список пациентов", font=ctk.CTkFont(size=24)).pack(pady=20)

        search_frame = ctk.CTkFrame(self.main_area)
        search_frame.pack(fill="x", padx=10, pady=10)

        self.search_entry = ctk.CTkEntry(search_frame, placeholder_text="Поиск по ФИО...", width=300)
        self.search_entry.pack(side="left", padx=10)
        ctk.CTkButton(search_frame, text="🔍 Найти", command=self.search_patient).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="🔄 Сброс", command=self.show_patients, fg_color="gray").pack(side="left",
                                                                                                      padx=5)

        header_frame = ctk.CTkFrame(self.main_area)
        header_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(header_frame, text="ФИО", width=250, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Дата рождения", width=120, font=ctk.CTkFont(weight="bold")).pack(side="left",
                                                                                                          padx=10)
        ctk.CTkLabel(header_frame, text="Палата", width=80, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Диагноз", width=300, font=ctk.CTkFont(weight="bold")).pack(side="left",
                                                                                                    padx=10)
        ctk.CTkLabel(header_frame, text="Статус", width=100, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Действия", width=200, font=ctk.CTkFont(weight="bold")).pack(side="left",
                                                                                                     padx=10)

        if search_term:
            patients = self.db.query(Patient).filter(Patient.full_name.contains(search_term)).all()
        else:
            patients = self.db.query(Patient).all()

        if not patients:
            ctk.CTkLabel(self.main_area, text="📭 Нет пациентов в базе", text_color="gray").pack(pady=20)
        else:
            for patient in patients:
                frame = ctk.CTkFrame(self.main_area)
                frame.pack(fill="x", padx=10, pady=3)

                ctk.CTkLabel(frame, text=patient.full_name, width=250, anchor="w").pack(side="left", padx=10)
                ctk.CTkLabel(frame, text=patient.birth_date or "Не указана", width=120, text_color="gray").pack(
                    side="left", padx=10)
                ctk.CTkLabel(frame, text=patient.ward_number, width=80).pack(side="left", padx=10)
                ctk.CTkLabel(frame, text=patient.diagnosis, width=300, anchor="w").pack(side="left", padx=10)

                status_color = "green" if patient.status == "Активен" else "orange"
                ctk.CTkLabel(frame, text=patient.status, width=100, text_color=status_color).pack(side="left", padx=10)

                btn_frame = ctk.CTkFrame(frame, fg_color="transparent")
                btn_frame.pack(side="left", padx=10)

                ctk.CTkButton(btn_frame, text="✏️", width=40, command=lambda p=patient: self.show_edit_form(p),
                              fg_color="blue", hover_color="darkblue").pack(side="left", padx=2)

                ctk.CTkButton(btn_frame, text="🗑️", width=40,
                              command=lambda p=patient: self.delete_patient(p),
                              fg_color="red", hover_color="darkred").pack(side="left", padx=2)

                ctk.CTkButton(btn_frame, text="📝", width=40,
                              command=lambda p=patient: self.show_patient_logs(p),
                              fg_color="purple", hover_color="darkpurple").pack(side="left", padx=2)

        self.update_sidebar_stats()

    def search_patient(self):
        """Поиск пациентов"""
        search_term = self.search_entry.get()
        self.show_patients(search_term)

    def show_add_form(self):
        """Форма добавления пациента"""
        self.edit_patient_id = None
        for widget in self.main_area.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_area, text="➕ Новый пациент", font=ctk.CTkFont(size=24)).pack(pady=20)

        form_frame = ctk.CTkFrame(self.main_area)
        form_frame.pack(pady=10, padx=20)

        ctk.CTkLabel(form_frame, text="ФИО: ").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.entry_name = ctk.CTkEntry(form_frame, placeholder_text="Иванов Иван Иванович", width=400)
        self.entry_name.grid(row=0, column=1, pady=5, padx=5)

        ctk.CTkLabel(form_frame, text="Дата рождения: ").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.entry_birth = ctk.CTkEntry(form_frame, placeholder_text="ДД.ММ.ГГГГ", width=400)
        self.entry_birth.grid(row=1, column=1, pady=5, padx=5)

        ctk.CTkLabel(form_frame, text="Палата: ").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.entry_ward = ctk.CTkEntry(form_frame, placeholder_text="Например: 305", width=400)
        self.entry_ward.grid(row=2, column=1, pady=5, padx=5)

        ctk.CTkLabel(form_frame, text="Диагноз: ").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.entry_diag = ctk.CTkEntry(form_frame, placeholder_text="Клинический диагноз", width=400)
        self.entry_diag.grid(row=3, column=1, pady=5, padx=5)

        ctk.CTkLabel(form_frame, text="Статус: ").grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.entry_status = ctk.CTkComboBox(form_frame, values=["Активен", "Выписан", "Переведен"], width=400)
        self.entry_status.set("Активен")
        self.entry_status.grid(row=4, column=1, pady=5, padx=5)

        ctk.CTkButton(form_frame, text="💾 Сохранить", command=self.save_patient,
                      fg_color="green", hover_color="darkgreen").grid(row=5, column=1, pady=20, sticky="e")

        ctk.CTkButton(form_frame, text="← Назад", command=self.show_patients,
                      fg_color="gray").grid(row=5, column=0, pady=20)

    def show_edit_form(self, patient):
        """Форма редактирования пациента"""
        self.edit_patient_id = patient.id
        for widget in self.main_area.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_area, text="✏️ Редактирование пациента", font=ctk.CTkFont(size=24)).pack(pady=20)

        form_frame = ctk.CTkFrame(self.main_area)
        form_frame.pack(pady=10, padx=20)

        ctk.CTkLabel(form_frame, text="ФИО: ").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        self.entry_name = ctk.CTkEntry(form_frame, width=400)
        self.entry_name.insert(0, patient.full_name)
        self.entry_name.grid(row=0, column=1, pady=5, padx=5)

        ctk.CTkLabel(form_frame, text="Дата рождения: ").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.entry_birth = ctk.CTkEntry(form_frame, width=400)
        self.entry_birth.insert(0, patient.birth_date or "")
        self.entry_birth.grid(row=1, column=1, pady=5, padx=5)

        ctk.CTkLabel(form_frame, text="Палата: ").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.entry_ward = ctk.CTkEntry(form_frame, width=400)
        self.entry_ward.insert(0, patient.ward_number)
        self.entry_ward.grid(row=2, column=1, pady=5, padx=5)

        ctk.CTkLabel(form_frame, text="Диагноз: ").grid(row=3, column=0, sticky="w", pady=5, padx=5)
        self.entry_diag = ctk.CTkEntry(form_frame, width=400)
        self.entry_diag.insert(0, patient.diagnosis)
        self.entry_diag.grid(row=3, column=1, pady=5, padx=5)

        ctk.CTkLabel(form_frame, text="Статус: ").grid(row=4, column=0, sticky="w", pady=5, padx=5)
        self.entry_status = ctk.CTkComboBox(form_frame, values=["Активен", "Выписан", "Переведен"], width=400)
        self.entry_status.set(patient.status)
        self.entry_status.grid(row=4, column=1, pady=5, padx=5)

        ctk.CTkButton(form_frame, text="💾 Обновить", command=self.update_patient,
                      fg_color="blue", hover_color="darkblue").grid(row=5, column=1, pady=20, sticky="e")

        ctk.CTkButton(form_frame, text="← Отмена", command=self.show_patients,
                      fg_color="gray").grid(row=5, column=0, pady=20)

    def save_patient(self):
        """Сохранение нового пациента"""
        name = self.entry_name.get()
        birth = self.entry_birth.get()
        ward = self.entry_ward.get()
        diag = self.entry_diag.get()
        status = self.entry_status.get() if hasattr(self, 'entry_status') else "Активен"

        if not name or not ward or not diag:
            messagebox.showerror("Ошибка", "Заполните обязательные поля!")
            return

        try:
            new_patient = Patient(
                full_name=name,
                birth_date=birth if birth else None,
                ward_number=ward,
                diagnosis=diag,
                status=status
            )
            self.db.add(new_patient)
            self.db.commit()

            messagebox.showinfo("Успех", "Пациент успешно добавлен!")
            self.show_patients()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")

    def update_patient(self):
        """Обновление данных пациента"""
        if not self.edit_patient_id:
            return

        name = self.entry_name.get()
        birth = self.entry_birth.get()
        ward = self.entry_ward.get()
        diag = self.entry_diag.get()
        status = self.entry_status.get()

        if not name or not ward or not diag:
            messagebox.showerror("Ошибка", "Заполните обязательные поля!")
            return

        try:
            patient = self.db.query(Patient).filter(Patient.id == self.edit_patient_id).first()
            if patient:
                patient.full_name = name
                patient.birth_date = birth if birth else None
                patient.ward_number = ward
                patient.diagnosis = diag
                patient.status = status

                self.db.commit()
                messagebox.showinfo("Успех", "Данные обновлены!")
                self.edit_patient_id = None
                self.show_patients()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Ошибка", f"Не удалось обновить: {str(e)}")

    def delete_patient(self, patient):
        """Удаление пациента"""
        confirm = messagebox.askyesno("Подтверждение",
                                      f"Вы действительно хотите удалить пациента:\n{patient.full_name}?\n\nЭто действие нельзя отменить!")

        if confirm:
            try:
                logs = self.db.query(PatientLog).filter(PatientLog.patient_id == patient.id).all()
                for log in logs:
                    self.db.delete(log)

                self.db.delete(patient)
                self.db.commit()

                messagebox.showinfo("Успех", "Пациент удалён")
                self.show_patients()
            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Ошибка", f"Не удалось удалить: {str(e)}")


    def show_logs(self):
        """Отображение всех записей журнала"""
        for widget in self.main_area.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_area, text="📝 Журнал записей", font=ctk.CTkFont(size=24)).pack(pady=20)

        ctk.CTkButton(self.main_area, text="➕ Добавить запись", command=self.show_add_log_form,
                      fg_color="green", hover_color="darkgreen").pack(pady=10)

        logs = self.db.query(PatientLog).order_by(PatientLog.created_at.desc()).limit(100).all()

        if not logs:
            ctk.CTkLabel(self.main_area, text="📭 Нет записей в журнале", text_color="gray").pack(pady=20)
            return

        header_frame = ctk.CTkFrame(self.main_area)
        header_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(header_frame, text="Пациент", width=250, font=ctk.CTkFont(weight="bold")).pack(side="left",
                                                                                                    padx=10)
        ctk.CTkLabel(header_frame, text="Врач", width=150, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Запись", width=400, font=ctk.CTkFont(weight="bold")).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Дата/время", width=150, font=ctk.CTkFont(weight="bold")).pack(side="left",
                                                                                                       padx=10)

        for log in logs:
            frame = ctk.CTkFrame(self.main_area)
            frame.pack(fill="x", padx=10, pady=3)

            patient = self.db.query(Patient).filter(Patient.id == log.patient_id).first()
            patient_name = patient.full_name if patient else "❌ Удалён"

            ctk.CTkLabel(frame, text=f"👤 {patient_name}", width=250, anchor="w").pack(side="left", padx=10)
            ctk.CTkLabel(frame, text=f"👨‍⚕️ {log.doctor_name}", width=150).pack(side="left", padx=10)
            ctk.CTkLabel(frame, text=f"📄 {log.content[:50]}...", width=400, anchor="w").pack(side="left", padx=10)

            date_str = log.created_at.strftime("%d.%m.%Y %H:%M") if log.created_at else "Не указана"
            ctk.CTkLabel(frame, text=f"🕐 {date_str}", width=150, text_color="gray").pack(side="left", padx=10)

        self.update_sidebar_stats()

    def show_patient_logs(self, patient):
        """Отображение записей журнала для конкретного пациента"""
        self.current_patient_id = patient.id
        for widget in self.main_area.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_area, text=f"📝 Журнал пациента: {patient.full_name}",
                     font=ctk.CTkFont(size=24)).pack(pady=20)

        ctk.CTkButton(self.main_area, text="➕ Добавить запись",
                      command=lambda p=patient: self.show_add_log_form(p),
                      fg_color="green", hover_color="darkgreen").pack(pady=10)

        ctk.CTkButton(self.main_area, text="← Назад к пациентам", command=self.show_patients,
                      fg_color="gray").pack(pady=5)

        logs = self.db.query(PatientLog).filter(PatientLog.patient_id == patient.id).order_by(
            PatientLog.created_at.desc()).all()

        if not logs:
            ctk.CTkLabel(self.main_area, text="📭 Нет записей для этого пациента", text_color="gray").pack(pady=20)
            return

        for log in logs:
            frame = ctk.CTkFrame(self.main_area)
            frame.pack(fill="x", padx=10, pady=3)

            ctk.CTkLabel(frame, text=f"👨‍⚕️ {log.doctor_name}", width=150).pack(side="left", padx=10)
            ctk.CTkLabel(frame, text=f"📄 {log.content}", width=500, anchor="w").pack(side="left", padx=10)

            date_str = log.created_at.strftime("%d.%m.%Y %H:%M") if log.created_at else "Не указана"
            ctk.CTkLabel(frame, text=f"🕐 {date_str}", width=150, text_color="gray").pack(side="left", padx=10)

            ctk.CTkButton(frame, text="🗑️", width=40,
                          command=lambda l=log: self.delete_log(l),
                          fg_color="red", hover_color="darkred").pack(side="left", padx=10)

        self.update_sidebar_stats()

    def show_add_log_form(self, patient=None):
        """Форма добавления записи в журнал"""
        for widget in self.main_area.winfo_children():
            widget.destroy()

        ctk.CTkLabel(self.main_area, text="➕ Новая запись в журнал", font=ctk.CTkFont(size=24)).pack(pady=20)

        form_frame = ctk.CTkFrame(self.main_area)
        form_frame.pack(pady=10, padx=20)

        ctk.CTkLabel(form_frame, text="Пациент: ").grid(row=0, column=0, sticky="w", pady=5, padx=5)

        if patient:
            self.log_patient_id = patient.id
            patient_label = ctk.CTkLabel(form_frame, text=patient.full_name, width=400)
            patient_label.grid(row=0, column=1, pady=5, padx=5)
        else:
            self.log_patient_id = None
            patients = self.db.query(Patient).all()
            patient_options = {p.full_name: p.id for p in patients}

            self.log_patient_combo = ctk.CTkComboBox(form_frame, values=list(patient_options.keys()), width=400)
            self.log_patient_combo.grid(row=0, column=1, pady=5, padx=5)
            self.patient_options = patient_options

        ctk.CTkLabel(form_frame, text="Врач: ").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        self.entry_doctor = ctk.CTkEntry(form_frame, placeholder_text="ФИО врача", width=400)
        self.entry_doctor.grid(row=1, column=1, pady=5, padx=5)

        ctk.CTkLabel(form_frame, text="Запись: ").grid(row=2, column=0, sticky="w", pady=5, padx=5)
        self.entry_content = ctk.CTkTextbox(form_frame, width=400, height=150)
        self.entry_content.grid(row=2, column=1, pady=5, padx=5)

        ctk.CTkButton(form_frame, text="💾 Сохранить запись", command=self.save_log,
                      fg_color="green", hover_color="darkgreen").grid(row=3, column=1, pady=20, sticky="e")

        ctk.CTkButton(form_frame, text="← Отмена",
                      command=self.show_logs if not patient else lambda: self.show_patient_logs(patient),
                      fg_color="gray").grid(row=3, column=0, pady=20)

    def save_log(self):
        """Сохранение записи в журнал"""
        content = self.entry_content.get("1.0", "end").strip()
        doctor = self.entry_doctor.get()

        if hasattr(self, 'log_patient_id') and self.log_patient_id:
            patient_id = self.log_patient_id
        elif hasattr(self, 'log_patient_combo'):
            selected_name = self.log_patient_combo.get()
            patient_id = self.patient_options.get(selected_name)
        else:
            messagebox.showerror("Ошибка", "Выберите пациента!")
            return

        if not content or not doctor:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        if not patient_id:
            messagebox.showerror("Ошибка", "Пациент не выбран!")
            return

        try:
            new_log = PatientLog(
                patient_id=patient_id,
                content=content,
                doctor_name=doctor
            )
            self.db.add(new_log)
            self.db.commit()

            messagebox.showinfo("Успех", "Запись добавлена в журнал!")

            if hasattr(self, 'current_patient_id') and self.current_patient_id == patient_id:
                patient = self.db.query(Patient).filter(Patient.id == patient_id).first()
                if patient:
                    self.show_patient_logs(patient)
                else:
                    self.show_logs()
            else:
                self.show_logs()

        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {str(e)}")

    def delete_log(self, log):
        """Удаление записи из журнала"""
        confirm = messagebox.askyesno("Подтверждение",
                                      f"Вы действительно хотите удалить эту запись?\n\n{log.content[:50]}...")

        if confirm:
            try:
                self.db.delete(log)
                self.db.commit()

                messagebox.showinfo("Успех", "Запись удалена")

                if hasattr(self, 'current_patient_id'):
                    patient = self.db.query(Patient).filter(Patient.id == self.current_patient_id).first()
                    if patient:
                        self.show_patient_logs(patient)
                    else:
                        self.show_logs()
                else:
                    self.show_logs()
            except Exception as e:
                self.db.rollback()
                messagebox.showerror("Ошибка", f"Не удалось удалить: {str(e)}")

    def on_closing(self):
        """Закрытие приложения с очисткой ресурсов"""
        try:
            self.db.close()
        except:
            pass
        self.destroy()


if __name__ == "__main__":
    app = PsychoApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()