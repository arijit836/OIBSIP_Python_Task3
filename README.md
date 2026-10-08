# 🔐 Advanced Random Password Generator

A 🔒 desktop password generator built with **Python** and **Tkinter**. It uses Python's `secrets` module and includes configurable character types, password strength feedback, clipboard copying, persistent history, and light and dark themes.

## ✨ Features

- 🔐 Generate secure random passwords
- 📏 Custom password length from 8 to 64 characters
- 🔤 Supports:
  - 🔠 Uppercase letters
  - 🔡 Lowercase letters
  - 🔢 Numbers
  - 🔣 Symbols
- ✅ Requires at least two character types, including uppercase letters
- 🚫 Option to exclude ambiguous characters
- 💪 Password strength indicator and visual feedback
- 📋 Clipboard support through `pyperclip` with a Tkinter fallback
- 💾 Persistent password history using SQLite
- 🕐 Keeps only the five most recently generated passwords
- 📜 History page with copy controls and a clear-history option
- 🌓 Light and dark theme support
- 📜 Scrollable Tkinter interface
- 🗄️ No external database server required

## 🛠️ Technologies Used

- 🐍 **Python 3**
- 🖥️ **Tkinter** — Graphical User Interface
- 🗃️ **SQLite** — Local password history
- 🔐 **`secrets`** — Secure password generation
- 🔤 **`string`** — Character sets
- 📁 **`pathlib`** — Database path management
- 📋 **`pyperclip`** — Preferred clipboard integration

## 📦 Requirements

- 🐍 Python 3
- 🖥️ Tkinter (included with many Python installations; Linux users may need to install it separately)
- 📋 The Python package listed in `requirements.txt`

## 📥 Clone This Project

If you want to clone the repository and set it up with the GitHub remote:

```bash
git clone https://github.com/arijit836/OIBSIP_Python_Task3.git
cd OIBSIP_Python_Task3
```

## 🚀 Setup and Run

Open a terminal in this folder and run:

```bash
python -m pip install -r requirements.txt
python random_pass.py
```

## 📱 Using the Application

1. 📏 Choose a password length between 8 and 64.
2. 🔤 Open **Character Type** and select at least two types, including uppercase letters.
3. 🚫 Optionally enable **Exclude Ambiguous Characters**.
4. ⚡ Select **Generate Password**. The password is copied to the clipboard when clipboard access is available.
5. 📋 Use the copy control beside the password to copy it again.
6. 📜 Open **History** to review or copy one of the five most recent passwords, or clear the history.
7. ⚙️ Open **Settings** to switch between light and dark appearance modes.

## 🔒 Password History and Privacy

The application creates `password_history.db` in this folder and stores the five most recently generated passwords there. This history persists between runs and is displayed in the History page. Use **Clear History** to delete the saved records.

⚠️ The database contains passwords in readable form. Keep it private, do not share it, and store credentials in a trusted password manager. The database is excluded by `.gitignore` to help prevent it from being added to version control.

## 💪 Password Strength

The strength indicator is based on password length and the number of selected character types:

```text
Password condition                              Strength
-----------------------------------------------  --------
16 or more characters and 4 types               Strong 💪
14 or more characters and at least 3 types      Strong 💪
12 or more characters and at least 3 types      Medium 🟡
10 or more characters and at least 2 types      Medium 🟡
Other valid combinations                        Weak 🔴
```

## 📂 Project Files

```text
RANDOM PASSWORD GENERATOR/
├── 📄 .gitignore
├── 📖 README.md
├── 🐍 random_pass.py
└── 📦 requirements.txt
```

`password_history.db` is created automatically when the application runs and is excluded from version control by `.gitignore`.

## 👨‍💻 Developer

Developed by **Arijit Maity**. 🚀
