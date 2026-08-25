import flet as ft
import sqlite3

def init_db():
    conn = sqlite3.connect("debts.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS debts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            amount REAL NOT NULL,
            debt_type TEXT NOT NULL,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()

def main(page: ft.Page):
    page.title = "دفتر الديون - عبدالله المليكي"
    page.theme_mode = ft.ThemeMode.LIGHT
    page.rtl = True
    page.padding = 20
    init_db()

    name_input = ft.TextField(label="اسم الشخص / العميل", expand=True)
    amount_input = ft.TextField(label="المبلغ", keyboard_type=ft.KeyboardType.NUMBER, width=150)
    note_input = ft.TextField(label="ملاحظة / البيان", expand=True)
    type_dropdown = ft.Dropdown(
        label="النوع",
        width=140,
        options=[
            ft.dropdown.Option("له", "له (دَين علي)"),
            ft.dropdown.Option("عليه", "عليه (دَين لي)"),
        ],
        value="عليه"
    )

    records_list = ft.ListView(expand=True, spacing=10)
    summary_text = ft.Text(size=16, weight=ft.FontWeight.BOLD)

    def load_records():
        records_list.controls.clear()
        conn = sqlite3.connect("debts.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, amount, debt_type, note FROM debts ORDER BY id DESC")
        rows = cursor.fetchall()
        
        total_for_me = 0
        total_on_me = 0

        for row in rows:
            r_id, name, amount, d_type, note = row
            if d_type == "عليه":
                total_for_me += amount
                color = "green"
            else:
                total_on_me += amount
                color = "red"

            def delete_record(e, record_id=r_id):
                conn_del = sqlite3.connect("debts.db")
                cur_del = conn_del.cursor()
                cur_del.execute("DELETE FROM debts WHERE id = ?", (record_id,))
                conn_del.commit()
                conn_del.close()
                load_records()

            records_list.controls.append(
                ft.Card(
                    content=ft.Container(
                        padding=12,
                        content=ft.Row([
                            ft.Column([
                                ft.Text(f"{name}", size=18, weight=ft.FontWeight.BOLD),
                                ft.Text(f"النوع: {d_type} | الملاحظة: {note or 'لا يوجد'}", size=12, color="grey"),
                            ], expand=True),
                            ft.Text(f"{amount:,.0f}", size=18, weight=ft.FontWeight.BOLD, color=color),
                            ft.IconButton(ft.icons.DELETE_OUTLINED, icon_color="red", on_click=delete_record)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
                    )
                )
            )

        conn.close()
        summary_text.value = f"إجمالي الديون لك (عليه): {total_for_me:,.0f} | إجمالي الديون عليك (له): {total_on_me:,.0f}"
        page.update()

    def add_record(e):
        if not name_input.value or not amount_input.value:
            return
        try:
            amt = float(amount_input.value)
        except ValueError:
            return

        conn = sqlite3.connect("debts.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO debts (name, amount, debt_type, note) VALUES (?, ?, ?, ?)",
                       (name_input.value, amt, type_dropdown.value, note_input.value))
        conn.commit()
        conn.close()

        name_input.value = ""
        amount_input.value = ""
        note_input.value = ""
        load_records()

    page.add(
        ft.Column([
            ft.Text("دفتر الديون المحاسبي", size=24, weight=ft.FontWeight.BOLD, color="blue"),
            ft.Text("تطوير وتصميم: عبدالله المليكي", size=12, color="grey"),
            ft.Divider(),
            ft.Row([name_input, amount_input]),
            ft.Row([type_dropdown, note_input]),
            ft.ElevatedButton("حفظ العملية", icon=ft.icons.SAVE, on_click=add_record, style=ft.ButtonStyle(bgcolor="blue", color="white")),
            ft.Divider(),
            summary_text,
            ft.Text("سجل العمليات:", size=16, weight=ft.FontWeight.BOLD),
        ]),
        records_list
    )
    load_records()

ft.app(target=main)
