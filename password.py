```python
import tkinter as tk
from tkinter import messagebox
import string
import secrets
import sqlite3
from pathlib import Path

try:
    import pyperclip
except ImportError:
    pyperclip = None

PROJECT_DIR = Path(__file__).resolve().parent
DATABASE_PATH = PROJECT_DIR / "password_history.db"

def create_database():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            password TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

def save_password(password):
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO password_history (password) VALUES (?)",
        (password,)
    )

    cursor.execute("""
        DELETE FROM password_history
        WHERE id NOT IN (
            SELECT id
            FROM password_history
            ORDER BY id DESC
            LIMIT 5
        )
    """)

    connection.commit()
    connection.close()


def load_password_history():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT password
        FROM password_history
        ORDER BY id DESC
        LIMIT 5
    """)

    records = cursor.fetchall()

    connection.close()

    return [record[0] for record in records]


def clear_password_history():
    connection = sqlite3.connect(DATABASE_PATH)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM password_history")

    connection.commit()
    connection.close()


create_database()


THEMES = {
    "light": {
        "bg": "#F5F7FA",
        "sidebar": "#172033",
        "sidebar_text": "#FFFFFF",
        "card": "#FFFFFF",
        "text": "#172033",
        "secondary": "#6B7280",
        "border": "#D9DEE7",
        "input": "#FFFFFF",
        "button": "#2563EB",
        "button_hover": "#1D4ED8",
        "success": "#16A34A",
        "warning": "#D97706",
        "danger": "#DC2626",
        "copy": "#EEF2FF"
    },
    "dark": {
        "bg": "#111827",
        "sidebar": "#0B1220",
        "sidebar_text": "#FFFFFF",
        "card": "#1F2937",
        "text": "#F9FAFB",
        "secondary": "#9CA3AF",
        "border": "#374151",
        "input": "#111827",
        "button": "#3B82F6",
        "button_hover": "#2563EB",
        "success": "#22C55E",
        "warning": "#F59E0B",
        "danger": "#EF4444",
        "copy": "#26324A"
    }
}


root = tk.Tk()
root.title("Advanced Random Password Generator")
root.geometry("1000x680")
root.minsize(700, 500)

current_theme = "light"
COLORS = THEMES[current_theme]

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
strength_bar = None
strength_label = None
suggestion_frame = None
suggestion_text = None
main_canvas = None
content_frame = None


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()


def create_card(parent):
    return tk.Frame(
        parent,
        bg=COLORS["card"],
        highlightbackground=COLORS["border"],
        highlightthickness=1
    )


def styled_button(parent, text, command, width=18):
    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        height=2,
        bg=COLORS["button"],
        fg="white",
        activebackground=COLORS["button_hover"],
        activeforeground="white",
        relief="flat",
        bd=0,
        font=("Segoe UI", 10, "bold"),
        cursor="hand2"
    )


def selected_character_types():
    selected = []

    if uppercase_var.get():
        selected.append("uppercase")

    if lowercase_var.get():
        selected.append("lowercase")

    if symbols_var.get():
        selected.append("symbols")

    if numbers_var.get():
        selected.append("numbers")

    return selected


def update_character_button():
    selected = selected_character_types()

    names = {
        "uppercase": "Uppercase",
        "lowercase": "Lowercase",
        "symbols": "Symbols",
        "numbers": "Numbers"
    }

    if len(selected) == 4:
        text = "Upper + Lower + Symbol + Number"

    elif selected:
        text = " + ".join(names[item] for item in selected)

    else:
        text = "Select Character Types"

    if character_button:
        character_button.config(text=text)


def choose_character_types():
    popup = tk.Toplevel(root)
    popup.title("Character Types")
    popup.geometry("420x420")
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
    ).pack(pady=(25, 5))

    tk.Label(
        popup,
        text="Select at least 2 types",
        bg=COLORS["bg"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 10)
    ).pack(pady=(0, 20))

    temp_vars = {
        "uppercase": tk.BooleanVar(value=uppercase_var.get()),
        "lowercase": tk.BooleanVar(value=lowercase_var.get()),
        "symbols": tk.BooleanVar(value=symbols_var.get()),
        "numbers": tk.BooleanVar(value=numbers_var.get())
    }

    options = [
        ("Uppercase Letters", "uppercase"),
        ("Lowercase Letters", "lowercase"),
        ("Symbols", "symbols"),
        ("Numbers", "numbers")
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
        ).pack(
            fill="x",
            padx=60,
            pady=5
        )

    def apply():
        selected = [
            key
            for key, variable in temp_vars.items()
            if variable.get()
        ]

        if len(selected) < 2:
            messagebox.showerror(
                "Invalid Character Selection",
                "Please select at least 2 character types.",
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
        symbols_var.set(temp_vars["symbols"].get())
        numbers_var.set(temp_vars["numbers"].get())

        update_character_button()

        popup.destroy()

    styled_button(
        popup,
        "Apply",
        apply,
        18
    ).pack(pady=25)


def generate_block(characters, count):
    result = ""

    for _ in range(count):
        result += secrets.choice(characters)

    return result


def create_character_sets():

    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    symbols = string.punctuation
    numbers = string.digits

    if exclude_var.get():

        ambiguous = "O0oIl1"

        uppercase = "".join(
            c for c in uppercase
            if c not in ambiguous
        )

        lowercase = "".join(
            c for c in lowercase
            if c not in ambiguous
        )

        numbers = "".join(
            c for c in numbers
            if c not in ambiguous
        )

        symbols = "".join(
            c for c in symbols
            if c not in ambiguous
        )

    return {
        "uppercase": uppercase,
        "lowercase": lowercase,
        "symbols": symbols,
        "numbers": numbers
    }


def generate_password():

    try:
        length = int(length_var.get())

    except ValueError:
        messagebox.showerror(
            "Invalid Length",
            "Please enter a valid password length."
        )
        return

    if length < 8 or length > 64:
        messagebox.showerror(
            "Invalid Length",
            "Password length must be between 8 and 64 characters."
        )
        return

    selected = selected_character_types()

    if len(selected) < 2:
        messagebox.showerror(
            "Character Types",
            "Please select at least 2 character types."
        )
        return

    if "uppercase" not in selected:
        messagebox.showerror(
            "Uppercase Required",
            "Uppercase letters must be selected."
        )
        return

    character_sets = create_character_sets()

    for choice in selected:

        if not character_sets[choice]:
            messagebox.showerror(
                "Character Error",
                "No characters are available for the selected type."
            )
            return

    counts = {}

    for choice in selected:
        counts[choice] = 1

    remaining = length - len(selected)

    priority = [
        "uppercase",
        "lowercase",
        "symbols",
        "numbers"
    ]

    for choice in priority:

        if choice not in selected:
            continue

        if remaining <= 0:
            break

        if choice == "uppercase":
            extra = secrets.choice([0, 1, 2])

        elif choice == "lowercase":
            extra = secrets.choice([1, 2, 3, 4])

        elif choice == "symbols":
            extra = secrets.choice([0, 1, 2])

        else:
            extra = remaining

        extra = min(extra, remaining)

        counts[choice] += extra
        remaining -= extra

    if remaining > 0:
        counts[selected[-1]] += remaining

    password = ""

    for choice in priority:

        if choice in selected:
            password += generate_block(
                character_sets[choice],
                counts[choice]
            )

    password_var.set(password)

    copy_to_clipboard(password)

    update_strength(
        length,
        len(selected)
    )

    save_password(password)

    history.clear()
    history.extend(load_password_history())

    refresh_history_page()


def copy_to_clipboard(password):

    try:

        if pyperclip:
            pyperclip.copy(password)

        else:
            root.clipboard_clear()
            root.clipboard_append(password)
            root.update()

    except Exception:

        try:
            root.clipboard_clear()
            root.clipboard_append(password)
            root.update()

        except Exception:
            pass


def copy_password():

    password = password_var.get()

    if not password:

        messagebox.showwarning(
            "Copy Password",
            "Generate a password first."
        )

        return

    copy_to_clipboard(password)

    copy_button.config(text="✓")

    root.after(
        1200,
        lambda: copy_button.config(text="📋")
    )


def update_strength(length, types):

    global strength_bar
    global strength_label

    if length >= 16 and types >= 4:

        strength = "STRONG"
        strength_color = COLORS["success"]
        bar_width = 260

    elif length >= 14 and types >= 3:

        strength = "STRONG"
        strength_color = COLORS["success"]
        bar_width = 260

    elif length >= 12 and types >= 3:

        strength = "MEDIUM"
        strength_color = COLORS["warning"]
        bar_width = 190

    elif length >= 10 and types >= 2:

        strength = "MEDIUM"
        strength_color = COLORS["warning"]
        bar_width = 190

    else:

        strength = "WEAK"
        strength_color = COLORS["danger"]
        bar_width = 100

    strength_var.set(strength)

    if strength_label:

        strength_label.config(
            text=strength,
            fg=strength_color
        )

    if strength_bar:

        strength_bar.config(
            bg=strength_color,
            width=bar_width
        )

    if suggestion_frame:

        if strength == "WEAK":

            suggestion_frame.pack(
                fill="x",
                pady=(20, 0)
            )

            suggestion_text.config(
                text=(
                    "💡  Password is Weak\n\n"
                    "Try making your password stronger:\n"
                    "• Use at least 12 characters\n"
                    "• Add uppercase and lowercase letters\n"
                    "• Add numbers\n"
                    "• Add symbols such as @, #, $, _"
                )
            )

        else:
            suggestion_frame.pack_forget()


def create_generator_page():

    global character_button
    global password_entry
    global copy_button
    global strength_bar
    global strength_label
    global suggestion_frame
    global suggestion_text

    frame = pages["generator"]

    clear_frame(frame)

    tk.Label(
        frame,
        text="Password Generator",
        bg=COLORS["bg"],
        fg=COLORS["text"],
        font=("Segoe UI", 24, "bold")
    ).pack(
        anchor="w",
        pady=(5, 3)
    )

    tk.Label(
        frame,
        text="Create a secure and human-style password.",
        bg=COLORS["bg"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        pady=(0, 20)
    )

    card = create_card(frame)

    card.pack(
        fill="x",
        padx=5,
        pady=5
    )

    inside = tk.Frame(
        card,
        bg=COLORS["card"]
    )

    inside.pack(
        fill="both",
        padx=30,
        pady=28
    )

    tk.Label(
        inside,
        text="Password Length",
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w")

    length_spinbox = tk.Spinbox(
        inside,
        from_=8,
        to=64,
        textvariable=length_var,
        width=18,
        bg=COLORS["input"],
        fg=COLORS["text"],
        buttonbackground=COLORS["input"],
        insertbackground=COLORS["text"],
        relief="solid",
        bd=1,
        font=("Segoe UI", 11)
    )

    length_spinbox.pack(
        anchor="w",
        pady=(6, 18)
    )

    tk.Label(
        inside,
        text="Allowed Length: 8 - 64 characters",
        bg=COLORS["card"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 9)
    ).pack(
        anchor="w",
        pady=(0, 18)
    )

    tk.Label(
        inside,
        text="Character Type",
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w")

    character_button = tk.Button(
        inside,
        text="",
        command=choose_character_types,
        width=32,
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

    character_button.pack(
        anchor="w",
        pady=(6, 18)
    )

    update_character_button()

    tk.Checkbutton(
        inside,
        text="Exclude Ambiguous Characters (O, 0, o, I, l, 1)",
        variable=exclude_var,
        bg=COLORS["card"],
        fg=COLORS["text"],
        activebackground=COLORS["card"],
        activeforeground=COLORS["text"],
        selectcolor=COLORS["input"],
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        pady=(0, 22)
    )

    tk.Label(
        inside,
        text="Password",
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=("Segoe UI", 10, "bold")
    ).pack(anchor="w")

    password_area = tk.Frame(
        inside,
        bg=COLORS["card"]
    )

    password_area.pack(
        fill="x",
        pady=(7, 22)
    )

    password_entry = tk.Entry(
        password_area,
        textvariable=password_var,
        bg=COLORS["input"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="solid",
        bd=1,
        font=("Consolas", 13)
    )

    password_entry.pack(
        side="left",
        fill="x",
        expand=True,
        ipady=9
    )

    copy_button = tk.Button(
        password_area,
        text="📋",
        command=copy_password,
        width=5,
        height=2,
        bg=COLORS["copy"],
        fg=COLORS["button"],
        activebackground=COLORS["button"],
        activeforeground="white",
        relief="flat",
        bd=0,
        font=("Segoe UI", 13),
        cursor="hand2"
    )

    copy_button.pack(
        side="right",
        padx=(8, 0)
    )

    strength_container = tk.Frame(
        inside,
        bg=COLORS["card"]
    )

    strength_container.pack(
        fill="x"
    )

    tk.Label(
        strength_container,
        text="Password Strength",
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=("Segoe UI", 10, "bold")
    ).pack(
        side="left"
    )

    strength_label = tk.Label(
        strength_container,
        text="—",
        bg=COLORS["card"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 10, "bold")
    )

    strength_label.pack(
        side="right"
    )

    strength_bar_background = tk.Frame(
        inside,
        bg=COLORS["border"],
        height=8
    )

    strength_bar_background.pack(
        fill="x",
        pady=(7, 22)
    )

    strength_bar = tk.Frame(
        strength_bar_background,
        bg=COLORS["success"],
        height=8,
        width=0
    )

    strength_bar.pack(
        side="left"
    )

    button_area = tk.Frame(
        inside,
        bg=COLORS["card"]
    )

    button_area.pack(
        pady=5
    )

    styled_button(
        button_area,
        "GENERATE PASSWORD",
        generate_password,
        22
    ).pack(
        side="left",
        padx=5
    )

    suggestion_frame = tk.Frame(
        inside,
        bg="#FEF2F2",
        highlightbackground=COLORS["danger"],
        highlightthickness=1
    )

    suggestion_text = tk.Label(
        suggestion_frame,
        text="",
        bg="#FEF2F2",
        fg="#991B1B",
        justify="left",
        anchor="w",
        font=("Segoe UI", 10),
        wraplength=650
    )

    suggestion_text.pack(
        fill="x",
        padx=15,
        pady=13
    )

    suggestion_frame.pack_forget()


def create_history_page():

    frame = pages["history"]

    clear_frame(frame)

    tk.Label(
        frame,
        text="Password History",
        bg=COLORS["bg"],
        fg=COLORS["text"],
        font=("Segoe UI", 24, "bold")
    ).pack(
        anchor="w",
        pady=(5, 3)
    )

    tk.Label(
        frame,
        text="Last 5 generated passwords saved permanently.",
        bg=COLORS["bg"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        pady=(0, 20)
    )

    tk.Button(
        frame,
        text="CLEAR HISTORY",
        command=delete_all_history,
        bg=COLORS["danger"],
        fg="white",
        activebackground=COLORS["danger"],
        activeforeground="white",
        relief="flat",
        bd=0,
        font=("Segoe UI", 9, "bold"),
        cursor="hand2"
    ).pack(
        anchor="e",
        pady=(0, 10)
    )

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

    if not history:

        tk.Label(
            frame,
            text="No passwords generated yet.",
            bg=COLORS["bg"],
            fg=COLORS["secondary"],
            font=("Segoe UI", 11)
        ).pack(
            pady=50
        )

        return

    for number, password in enumerate(history, 1):

        row = tk.Frame(
            frame,
            bg=COLORS["card"],
            highlightbackground=COLORS["border"],
            highlightthickness=1
        )

        row.pack(
            fill="x",
            pady=5
        )

        tk.Label(
            row,
            text=str(number),
            bg=COLORS["card"],
            fg=COLORS["secondary"],
            font=("Segoe UI", 10, "bold"),
            width=4
        ).pack(
            side="left",
            padx=(10, 0)
        )

        tk.Label(
            row,
            text=password,
            bg=COLORS["card"],
            fg=COLORS["text"],
            font=("Consolas", 11),
            anchor="w"
        ).pack(
            side="left",
            fill="x",
            expand=True,
            padx=10,
            pady=12
        )

        tk.Button(
            row,
            text="📋",
            command=lambda p=password: copy_history_password(p),
            bg=COLORS["copy"],
            fg=COLORS["button"],
            activebackground=COLORS["button"],
            activeforeground="white",
            relief="flat",
            bd=0,
            font=("Segoe UI", 11),
            cursor="hand2"
        ).pack(
            side="right",
            padx=10
        )


def copy_history_password(password):
    copy_to_clipboard(password)


def delete_all_history():

    if not history:

        messagebox.showinfo(
            "History",
            "There is no password history to clear."
        )

        return

    answer = messagebox.askyesno(
        "Clear History",
        "Are you sure you want to delete all saved password history?"
    )

    if not answer:
        return

    clear_password_history()

    history.clear()

    refresh_history_page()


def create_settings_page():

    frame = pages["settings"]

    clear_frame(frame)

    tk.Label(
        frame,
        text="Settings",
        bg=COLORS["bg"],
        fg=COLORS["text"],
        font=("Segoe UI", 24, "bold")
    ).pack(
        anchor="w",
        pady=(5, 3)
    )

    tk.Label(
        frame,
        text="Customize your password generator.",
        bg=COLORS["bg"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        pady=(0, 20)
    )

    appearance_card = create_card(frame)

    appearance_card.pack(
        fill="x",
        pady=5
    )

    tk.Label(
        appearance_card,
        text="Appearance",
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=("Segoe UI", 13, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(20, 12)
    )

    light_var = tk.BooleanVar(
        value=current_theme == "light"
    )

    dark_var = tk.BooleanVar(
        value=current_theme == "dark"
    )

    def select_light():

        light_var.set(True)
        dark_var.set(False)

        if current_theme != "light":
            toggle_theme()

    def select_dark():

        dark_var.set(True)
        light_var.set(False)

        if current_theme != "dark":
            toggle_theme()

    tk.Checkbutton(
        appearance_card,
        text="Light",
        variable=light_var,
        command=select_light,
        bg=COLORS["card"],
        fg=COLORS["text"],
        activebackground=COLORS["card"],
        activeforeground=COLORS["text"],
        selectcolor=COLORS["input"],
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        padx=25,
        pady=5
    )

    tk.Checkbutton(
        appearance_card,
        text="Dark",
        variable=dark_var,
        command=select_dark,
        bg=COLORS["card"],
        fg=COLORS["text"],
        activebackground=COLORS["card"],
        activeforeground=COLORS["text"],
        selectcolor=COLORS["input"],
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        padx=25,
        pady=(5, 20)
    )

    about_card = create_card(frame)

    about_card.pack(
        fill="x",
        pady=12
    )

    tk.Label(
        about_card,
        text="About",
        bg=COLORS["card"],
        fg=COLORS["text"],
        font=("Segoe UI", 13, "bold")
    ).pack(
        anchor="w",
        padx=25,
        pady=(20, 5)
    )

    tk.Label(
        about_card,
        text=(
            "Advanced Random Password Generator\n"
            "Secure password generation using Python secrets.\n"
            "SQLite stores the last 5 generated passwords."
        ),
        bg=COLORS["card"],
        fg=COLORS["secondary"],
        justify="left",
        font=("Segoe UI", 10)
    ).pack(
        anchor="w",
        padx=25,
        pady=(5, 20)
    )

    footer = tk.Frame(
        frame,
        bg=COLORS["bg"]
    )

    footer.pack(
        pady=(25, 20)
    )

    tk.Label(
        footer,
        text="Developed by Arijit Maity",
        bg=COLORS["bg"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 10, "bold")
    ).pack()

    tk.Label(
        footer,
        text="© 2026 Arijit Maity",
        bg=COLORS["bg"],
        fg=COLORS["secondary"],
        font=("Segoe UI", 9)
    ).pack(
        pady=(3, 0)
    )


def show_page(page_name):

    for page in pages.values():
        page.pack_forget()

    pages[page_name].pack(
        fill="both",
        expand=True
    )

    for name, button in nav_buttons.items():

        if name == page_name:

            button.config(
                bg=COLORS["button"],
                fg="white"
            )

        else:

            button.config(
                bg=COLORS["sidebar"],
                fg=COLORS["sidebar_text"]
            )

    if main_canvas:
        main_canvas.yview_moveto(0)


def create_sidebar():

    sidebar = tk.Frame(
        root,
        bg=COLORS["sidebar"],
        width=230
    )

    sidebar.pack(
        side="left",
        fill="y"
    )

    sidebar.pack_propagate(False)

    tk.Label(
        sidebar,
        text="🔐",
        bg=COLORS["sidebar"],
        fg="white",
        font=("Segoe UI Emoji", 30)
    ).pack(
        pady=(30, 5)
    )

    tk.Label(
        sidebar,
        text="Password\nGenerator",
        bg=COLORS["sidebar"],
        fg="white",
        font=("Segoe UI", 15, "bold"),
        justify="center"
    ).pack(
        pady=(0, 35)
    )

    navigation = [
        ("generator", "🔐  Generator"),
        ("history", "🕘  History"),
        ("settings", "⚙  Settings")
    ]

    for page_name, text in navigation:

        button = tk.Button(
            sidebar,
            text=text,
            command=lambda p=page_name: show_page(p),
            bg=COLORS["sidebar"],
            fg=COLORS["sidebar_text"],
            activebackground=COLORS["button"],
            activeforeground="white",
            relief="flat",
            bd=0,
            anchor="w",
            padx=25,
            font=("Segoe UI", 11),
            cursor="hand2"
        )

        button.pack(
            fill="x",
            pady=3,
            ipady=10
        )

        nav_buttons[page_name] = button


def toggle_theme():

    global current_theme
    global COLORS

    if current_theme == "light":
        current_theme = "dark"

    else:
        current_theme = "light"

    COLORS = THEMES[current_theme]

    rebuild_ui()


def rebuild_ui():

    global main_canvas
    global content_frame

    for widget in root.winfo_children():
        widget.destroy()

    pages.clear()
    nav_buttons.clear()

    create_sidebar()

    main_area = tk.Frame(
        root,
        bg=COLORS["bg"]
    )

    main_area.pack(
        side="right",
        fill="both",
        expand=True
    )

    main_canvas = tk.Canvas(
        main_area,
        bg=COLORS["bg"],
        highlightthickness=0
    )

    main_canvas.pack(
        side="left",
        fill="both",
        expand=True
    )

    scrollbar = tk.Scrollbar(
        main_area,
        orient="vertical",
        command=main_canvas.yview
    )

    scrollbar.pack(
        side="right",
        fill="y"
    )

    main_canvas.configure(
        yscrollcommand=scrollbar.set
    )

    content_frame = tk.Frame(
        main_canvas,
        bg=COLORS["bg"]
    )

    canvas_window = main_canvas.create_window(
        (0, 0),
        window=content_frame,
        anchor="nw"
    )

    def update_scroll_region(event=None):

        main_canvas.configure(
            scrollregion=main_canvas.bbox("all")
        )

    content_frame.bind(
        "<Configure>",
        update_scroll_region
    )

    def update_canvas_width(event):

        main_canvas.itemconfig(
            canvas_window,
            width=event.width
        )

    main_canvas.bind(
        "<Configure>",
        update_canvas_width
    )

    def mouse_wheel(event):

        main_canvas.yview_scroll(
            int(-1 * (event.delta / 120)),
            "units"
        )

    main_canvas.bind_all(
        "<MouseWheel>",
        mouse_wheel
    )

    pages["generator"] = tk.Frame(
        content_frame,
        bg=COLORS["bg"]
    )

    pages["history"] = tk.Frame(
        content_frame,
        bg=COLORS["bg"]
    )

    pages["settings"] = tk.Frame(
        content_frame,
        bg=COLORS["bg"]
    )

    create_generator_page()
    create_history_page()
    create_settings_page()

    show_page("generator")


rebuild_ui()

root.mainloop()
```
