
import tkinter as tk
from tkinter import messagebox
import string
import secrets
import sqlite3
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_DIR / "password_history.db"


def create_database():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS password_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                password TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)


def save_password(password):
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute(
            "INSERT INTO password_history (password) VALUES (?)",
            (password,)
        )
        connection.execute("""
            DELETE FROM password_history
            WHERE id NOT IN (
                SELECT id FROM password_history
                ORDER BY id DESC LIMIT 5
            )
        """)


def load_password_history():
    with sqlite3.connect(DATABASE_PATH) as connection:
        rows = connection.execute("""
            SELECT password FROM password_history
            ORDER BY id DESC LIMIT 5
        """).fetchall()
    return [row[0] for row in rows]


def clear_password_history():
    with sqlite3.connect(DATABASE_PATH) as connection:
        connection.execute("DELETE FROM password_history")


create_database()

THEMES = {
    "light": {
        "bg": "#F5F7FA",
        "sidebar": "#172033",
        "card": "#FFFFFF",
        "text": "#172033",
        "secondary": "#6B7280",
        "border": "#D9DEE7",
        "input": "#FFFFFF",
        "button": "#2563EB",
        "hover": "#1D4ED8",
        "success": "#16A34A",
        "warning": "#D97706",
        "danger": "#DC2626",
        "copy": "#EEF2FF"
    },
    "dark": {
        "bg": "#111827",
        "sidebar": "#0B1220",
        "card": "#1F2937",
        "text": "#F9FAFB",
        "secondary": "#9CA3AF",
        "border": "#374151",
        "input": "#111827",
        "button": "#3B82F6",
        "hover": "#2563EB",
        "success": "#22C55E",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "copy": "#26324A"
    }
}

current_theme = "light"
COLORS = THEMES[current_theme]

root = tk.Tk()
root.title("Advanced Random Password Generator")
root.geometry("1000x720")
root.minsize(720, 550)
root.configure(bg=COLORS["bg"])

pages = {}
nav_buttons = {}
history = load_password_history()

length_var = tk.StringVar(value="16")
password_var = tk.StringVar()
strength_var = tk.StringVar(value="—")

uppercase_var = tk.BooleanVar(value=True)
lowercase_var = tk.BooleanVar(value=True)
numbers_var = tk.BooleanVar(value=True)
symbols_var = tk.BooleanVar(value=True)
exclude_var = tk.BooleanVar(value=False)

character_button = None
password_entry = None
copy_button = None
strength_label = None
strength_bar = None
suggestion_label = None


def create_card(parent):
    return tk.Frame(
        parent,
        bg=COLORS["card"],
        highlightbackground=COLORS["border"],
        highlightthickness=1
    )


def styled_button(parent, text, command, width=20):
    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        height=2,
        bg=COLORS["button"],
        fg="white",
        activebackground=COLORS["hover"],
        activeforeground="white",
        relief="flat",
        bd=0,
        font=("Segoe UI", 10, "bold"),
        cursor="hand2"
    )


def create_label(parent, text, size=10, bold=False, **kwargs):
    return tk.Label(
        parent,
        text=text,
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=("Segoe UI", size, "bold" if bold else "normal"),
        **kwargs
    )


def selected_character_types():
    selected = []

    if uppercase_var.get():
        selected.append("uppercase")
    if lowercase_var.get():
        selected.append("lowercase")
    if numbers_var.get():
        selected.append("numbers")
    if symbols_var.get():
        selected.append("symbols")

    return selected


def update_character_button():
    if character_button is None:
        return

    names = {
        "uppercase": "Uppercase",
        "lowercase": "Lowercase",
        "numbers": "Numbers",
        "symbols": "Symbols"
    }

    selected = selected_character_types()

    if len(selected) == 4:
        text = "Upper + Lower + Number + Symbol"
    elif selected:
        text = " + ".join(names[item] for item in selected)
    else:
        text = "Select Character Types"

    character_button.config(text=text)


def choose_character_types():
    popup = tk.Toplevel(root)
    popup.title("Character Types")
    popup.geometry("400x400")
    popup.resizable(False, False)
    popup.configure(bg=COLORS["bg"])
    popup.transient(root)
    popup.grab_set()

    tk.Label(
        popup,
        text="Choose Character Types",
        bg=COLORS["bg"],
        fg=COLORS["text"],
        font=("Segoe UI", 16, "bold")
    ).pack(pady=(25, 8))

    tk.Label(
        popup,
        text="Select at least two types",
        bg=COLORS["bg"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 10)
    ).pack(pady=(0, 20))

    temp_vars = {
        "uppercase": tk.BooleanVar(value=uppercase_var.get()),
        "lowercase": tk.BooleanVar(value=lowercase_var.get()),
        "numbers": tk.BooleanVar(value=numbers_var.get()),
        "symbols": tk.BooleanVar(value=symbols_var.get())
    }

    options = [
        ("Uppercase Letters (A-Z)", "uppercase"),
        ("Lowercase Letters (a-z)", "lowercase"),
        ("Numbers (0-9)", "numbers"),
        ("Symbols (!@#$...)", "symbols")
    ]

    for text, key in options:
        tk.Checkbutton(
            popup,
            text=text,
            variable=temp_vars[key],
            bg=COLORS["bg"],
            fg=COLORS["text"],
            activebackground=COLORS["bg"],
            activeforeground=COLORS["text"],
            selectcolor=COLORS["card"],
            font=("Segoe UI", 11),
            anchor="w"
        ).pack(fill="x", padx=55, pady=5)

    def apply():
        selected = [
            key for key, var in temp_vars.items() if var.get()
        ]

        if len(selected) < 2:
            messagebox.showerror(
                "Invalid Selection",
                "Please select at least two character types.",
                parent=popup
            )
            return

        if not temp_vars["uppercase"].get():
            messagebox.showerror(
                "Uppercase Required",
                "Uppercase letters must be selected.",
                parent=popup
            )
            return

        uppercase_var.set(temp_vars["uppercase"].get())
        lowercase_var.set(temp_vars["lowercase"].get())
        numbers_var.set(temp_vars["numbers"].get())
        symbols_var.set(temp_vars["symbols"].get())

        update_character_button()
        popup.destroy()

    styled_button(popup, "Apply Selection", apply).pack(pady=25)


def create_character_sets():
    sets = {
        "uppercase": string.ascii_uppercase,
        "lowercase": string.ascii_lowercase,
        "numbers": string.digits,
        "symbols": string.punctuation
    }

    if exclude_var.get():
        ambiguous = "O0oIl1"
        sets = {
            key: "".join(c for c in chars if c not in ambiguous)
            for key, chars in sets.items()
        }

    return sets


def generate_password():
    try:
        length = int(length_var.get())
    except ValueError:
        messagebox.showerror(
            "Invalid Length",
            "Enter a valid password length."
        )
        return

    if not 8 <= length <= 64:
        messagebox.showerror(
            "Invalid Length",
            "Password length must be between 8 and 64."
        )
        return

    selected = selected_character_types()

    if len(selected) < 2:
        messagebox.showerror(
            "Character Types",
            "Select at least two character types."
        )
        return

    if "uppercase" not in selected:
        messagebox.showerror(
            "Uppercase Required",
            "Uppercase letters must be selected."
        )
        return

    character_sets = create_character_sets()

    for key in selected:
        if not character_sets[key]:
            messagebox.showerror(
                "Character Error",
                f"No available characters for {key}."
            )
            return

    password_chars = [
        secrets.choice(character_sets[key])
        for key in selected
    ]

    all_characters = "".join(
        character_sets[key] for key in selected
    )

    while len(password_chars) < length:
        password_chars.append(secrets.choice(all_characters))

    for i in range(len(password_chars) - 1, 0, -1):
        j = secrets.randbelow(i + 1)
        password_chars[i], password_chars[j] = (
            password_chars[j],
            password_chars[i]
        )

    password = "".join(password_chars)
    password_var.set(password)

    save_password(password)
    history.clear()
    history.extend(load_password_history())

    update_strength(length, len(selected))
    refresh_history_page()


def copy_to_clipboard(password):
    try:
        root.clipboard_clear()
        root.clipboard_append(password)
        root.update()
    except tk.TclError:
        messagebox.showerror(
            "Clipboard Error",
            "Could not copy the password."
        )


def copy_password():
    password = password_var.get()

    if not password:
        messagebox.showwarning(
            "Copy Password",
            "Generate a password first."
        )
        return

    copy_to_clipboard(password)
    copy_button.config(text="✓ Copied!")

    root.after(
        1200,
        lambda: copy_button.config(text="📋")
        if copy_button.winfo_exists() else None
    )


def update_strength(length, types):
    if length >= 16 and types >= 3:
        strength, color, width = "STRONG", COLORS["success"], 260
    elif length >= 12 and types >= 3:
        strength, color, width = "MEDIUM", COLORS["warning"], 190
    else:
        strength, color, width = "WEAK", COLORS["danger"], 100

    strength_var.set(strength)

    if strength_label and strength_label.winfo_exists():
        strength_label.config(text=strength, fg=color)

    if strength_bar and strength_bar.winfo_exists():
        strength_bar.config(bg=color, width=width)

    if suggestion_label and suggestion_label.winfo_exists():
        if strength == "WEAK":
            suggestion_label.config(
                text=(
                    "💡 Improve your password by using 12-16 or more "
                    "characters and a mix of character types."
                )
            )
        else:
            suggestion_label.config(text="")


def create_generator_page():
    global character_button
    global password_entry
    global copy_button
    global strength_label
    global strength_bar
    global suggestion_label

    frame = pages["generator"]

    tk.Label(
        frame,
        text="Password Generator",
        bg=COLORS["bg"],
        fg=COLORS["text"],
        font=("Segoe UI", 24, "bold")
    ).pack(anchor="w", pady=(5, 3))

    tk.Label(
        frame,
        text="Create a secure random password.",
        bg=COLORS["bg"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(0, 20))

    card = create_card(frame)
    card.pack(fill="x", padx=5)

    inside = tk.Frame(card, bg=COLORS["card"])
    inside.pack(fill="x", padx=25, pady=25)

    create_label(inside, "Password Length", bold=True).pack(anchor="w")

    tk.Spinbox(
        inside,
        from_=8,
        to=64,
        textvariable=length_var,
        width=15,
        bg=COLORS["input"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="solid",
        bd=1,
        font=("Segoe UI", 11)
    ).pack(anchor="w", pady=(6, 16))

    create_label(inside, "Character Types", bold=True).pack(anchor="w")

    character_button = tk.Button(
        inside,
        text="",
        command=choose_character_types,
        width=34,
        height=2,
        bg=COLORS["input"],
        fg=COLORS["text"],
        activebackground=COLORS["copy"],
        activeforeground=COLORS["text"],
        relief="solid",
        bd=1,
        font=("Segoe UI", 10),
        cursor="hand2"
    )
    character_button.pack(anchor="w", pady=(6, 15))
    update_character_button()

    tk.Checkbutton(
        inside,
        text="Exclude ambiguous characters (O, 0, o, I, l, 1)",
        variable=exclude_var,
        bg=COLORS["card"],
        fg=COLORS["text"],
        activebackground=COLORS["card"],
        activeforeground=COLORS["text"],
        selectcolor=COLORS["input"],
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(0, 18))

    create_label(inside, "Generated Password", bold=True).pack(anchor="w")

    password_area = tk.Frame(inside, bg=COLORS["card"])
    password_area.pack(fill="x", pady=(7, 20))

    password_entry = tk.Entry(
        password_area,
        textvariable=password_var,
        bg=COLORS["input"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="solid",
        bd=1,
        font=("Consolas", 12)
    )
    password_entry.pack(side="left", fill="x", expand=True, ipady=9)

    copy_button = tk.Button(
        password_area,
        text="📋",
        command=copy_password,
        width=7,
        height=2,
        bg=COLORS["copy"],
        fg=COLORS["button"],
        activebackground=COLORS["button"],
        activeforeground="white",
        relief="flat",
        bd=0,
        font=("Segoe UI", 11),
        cursor="hand2"
    )
    copy_button.pack(side="right", padx=(8, 0))

    strength_row = tk.Frame(inside, bg=COLORS["card"])
    strength_row.pack(fill="x")

    create_label(
        strength_row, "Password Strength", bold=True
    ).pack(side="left")

    strength_label = tk.Label(
        strength_row,
        text="—",
        bg=COLORS["card"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 10, "bold")
    )
    strength_label.pack(side="right")

    strength_background = tk.Frame(
        inside, bg=COLORS["border"], height=8
    )
    strength_background.pack(fill="x", pady=(8, 20))

    strength_bar = tk.Frame(
        strength_background,
        bg=COLORS["success"],
        width=0,
        height=8
    )
    strength_bar.pack(side="left")

    suggestion_label = tk.Label(
        inside,
        text="",
        bg=COLORS["card"],
        fg=COLORS["warning"],
        font=("Segoe UI", 9),
        wraplength=650,
        justify="left"
    )
    suggestion_label.pack(anchor="w", pady=(0, 10))

    styled_button(
        inside,
        "GENERATE PASSWORD",
        generate_password,
        24
    ).pack(pady=5)


def create_history_page():
    frame = pages["history"]

    tk.Label(
        frame,
        text="Password History",
        bg=COLORS["bg"],
        fg=COLORS["text"],
        font=("Segoe UI", 24, "bold")
    ).pack(anchor="w", pady=(5, 3))

    tk.Label(
        frame,
        text="Your five most recently generated passwords.",
        bg=COLORS["bg"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(0, 20))

    styled_button(
        frame,
        "CLEAR HISTORY",
        delete_all_history,
        18
    ).pack(anchor="e", pady=(0, 12))

    refresh_history_page()


def refresh_history_page():
    if "history" not in pages:
        return

    frame = pages["history"]
    children = frame.winfo_children()

    for widget in children[3:]:
        widget.destroy()

    saved_history = load_password_history()
    history.clear()
    history.extend(saved_history)

    if not saved_history:
        tk.Label(
            frame,
            text="No password history available.",
            bg=COLORS["bg"],
            fg=COLORS["secondary"],
            font=("Segoe UI", 11)
        ).pack(anchor="w", pady=15)
        return

    for password in saved_history:
        card = create_card(frame)
        card.pack(fill="x", pady=5)

        row = tk.Frame(card, bg=COLORS["card"])
        row.pack(fill="x", padx=12, pady=10)

        tk.Label(
            row,
            text=password,
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=("Consolas", 11),
            anchor="w"
        ).pack(side="left", fill="x", expand=True)

        tk.Button(
            row,
            text="Copy",
            command=lambda p=password: copy_to_clipboard(p),
            bg=COLORS["copy"],
            fg=COLORS["button"],
            relief="flat",
            cursor="hand2"
        ).pack(side="right", padx=5)


def delete_all_history():
    if not messagebox.askyesno(
        "Clear History",
        "Delete all saved password history?"
    ):
        return

    clear_password_history()
    history.clear()
    refresh_history_page()


def create_settings_page():
    frame = pages["settings"]

    tk.Label(
        frame,
        text="Settings",
        bg=COLORS["bg"],
        fg=COLORS["text"],
        font=("Segoe UI", 24, "bold")
    ).pack(anchor="w", pady=(5, 3))

    tk.Label(
        frame,
        text="Customize your application.",
        bg=COLORS["bg"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 10)
    ).pack(anchor="w", pady=(0, 20))

    card = create_card(frame)
    card.pack(fill="x", pady=5)

    inside = tk.Frame(card, bg=COLORS["card"])
    inside.pack(fill="x", padx=20, pady=20)

    create_label(
        inside, "Appearance", size=14, bold=True
    ).pack(anchor="w", pady=(0, 10))

    create_label(
        inside, f"Current theme: {current_theme.title()}"
    ).pack(anchor="w", pady=(0, 12))

    styled_button(
        inside,
        "TOGGLE LIGHT / DARK",
        toggle_theme,
        24
    ).pack(anchor="w")

    tk.Label(
        frame,
        text="Password history is stored locally in SQLite.",
        bg=COLORS["bg"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 10),
        wraplength=650,
        justify="left"
    ).pack(anchor="w", pady=20)


def toggle_theme():
    global current_theme, COLORS

    current_theme = "dark" if current_theme == "light" else "light"
    COLORS = THEMES[current_theme]
    root.configure(bg=COLORS["bg"])
    build_interface()


def show_page(page_name):
    for page in pages.values():
        page.pack_forget()

    pages[page_name].pack(
        side="left",
        fill="both",
        expand=True,
        padx=25,
        pady=20
    )

    for name, button in nav_buttons.items():
        button.config(
            bg=COLORS["button"] if name == page_name
            else COLORS["sidebar"]
        )


def build_interface():
    global character_button
    global password_entry
    global copy_button
    global strength_label
    global strength_bar
    global suggestion_label

    for widget in root.winfo_children():
        widget.destroy()

    pages.clear()
    nav_buttons.clear()

    sidebar = tk.Frame(root, bg=COLORS["sidebar"], width=210)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    tk.Label(
        sidebar,
        text="🔐 Password\nGenerator",
        bg=COLORS["sidebar"],
        fg="white",
        font=("Segoe UI", 17, "bold"),
        justify="left"
    ).pack(anchor="w", padx=20, pady=(28, 35))

    main = tk.Frame(root, bg=COLORS["bg"])
    main.pack(side="left", fill="both", expand=True)

    for name, label in [
        ("generator", "🔑  Generator"),
        ("history", "📜  History"),
        ("settings", "⚙️  Settings")
    ]:
        button = tk.Button(
            sidebar,
            text=label,
            command=lambda n=name: show_page(n),
            bg=COLORS["sidebar"],
            fg="white",
            activebackground=COLORS["button"],
            activeforeground="white",
            relief="flat",
            bd=0,
            anchor="w",
            padx=20,
            pady=14,
            font=("Segoe UI", 11),
            cursor="hand2"
        )
        button.pack(fill="x", padx=8, pady=3)
        nav_buttons[name] = button
        pages[name] = tk.Frame(main, bg=COLORS["bg"])

    create_generator_page()
    create_history_page()
    create_settings_page()
    show_page("generator")


build_interface()
root.mainloop()
