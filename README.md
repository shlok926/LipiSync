<p align="center">
  <img src="braille_logo.png" width="140" alt="LipiSync Logo">
</p>

<h1 align="center">⠠⠇⠊⠏⠊⠠⠎⠽⠝⠉ LipiSync</h1>

<p align="center">
  <b>Intelligent Braille Workspace & Translation Suite</b>
</p>

<p align="center">
  <i>A premium, fully accessible desktop environment built with PyQt6, providing real-time multi-grade Braille translation, document processing, vocal synthesis, speech translation, and interactive learning.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue?style=flat&logo=python&logoColor=white" alt="Python Version">
  <img src="https://img.shields.io/badge/UI-PyQt6-green?style=flat&logo=qt&logoColor=white" alt="UI Framework">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=flat" alt="License">
  <img src="https://img.shields.io/badge/Status-Production--Ready-brightgreen?style=flat" alt="Production Status">
</p>

<p align="center">
  <a href="#-quick-start">⚡ Quick Start</a> • 
  <a href="#-features">📖 Features</a> • 
  <a href="#-keyboard-shortcuts">⌨️ Keyboard Shortcuts</a> • 
  <a href="#-project-structure">📂 Project Structure</a>
</p>

---

### 🎯 Key Features at a Glance

| ⇄ Translator | 📷 OCR Scan | 🔊 Vocalizer | ✓ Accessibility |
| :---: | :---: | :---: | :---: |
| **UEB & Devanagari** | **Computer Vision** | **TTS & MP3 Export** | **Shortcut Audits** |
| Bi-directional translation for English, Hindi, & Marathi. | OpenCV dot detection & clustering from images. | High-fidelity vocalizer with custom speed controls. | Built-in diagnostic screen-reader feedback tool. |

---

### 📋 Table of Contents

- [💡 Problem Statement](#-problem-statement)
- [✨ Core Capabilities](#-core-capabilities)
- [⚡ Quick Start](#-quick-start)
- [⌨️ Keyboard Shortcuts](#-keyboard-shortcuts)
- [📂 Project Structure](#-project-structure)
- [📄 License](#-license)

---

### 💡 Problem Statement

Visually impaired users, students, and educators face significant barriers when working with tactile writing systems:
* **Complex Standards:** Learning Unified English Braille (UEB) contractions or Devanagari (Bharati Braille) takes substantial time.
* **Lack of Tools:** Sighted teachers struggle to convert math notations and complex worksheets to Braille instantly.
* **Isolated Features:** Digital tools are often split between OCR readers, audio recorders, and translation engines.

**LipiSync** resolves this by providing a unified, dark-mode accessible workspace featuring multi-grade conversion, vocal studio feedback, document reading, and interactive self-evaluation courses.

---

### ✨ Core Capabilities

* **Multi-Grade Braille Translation:** Real-time bi-directional conversion with dynamic visual 6-dot character grids.
* **Document Scanner (OCR):** Drag-and-drop image processing using custom OpenCV contour analysis to detect physical Braille cells.
* **Vocalizer Studio:** High-fidelity TTS feedback that lets creators export Braille translations directly to standalone `.mp3` or `.wav` files.
* **Nemeth Math Translator:** Simple editor translating algebraic formulas and numerals into compliant Braille notations.
* **Learning & Quiz Center:** Gamified progress tracker with quizzes designed for both sighted learners and visually impaired students.
* **Split-Pane History Logs:** Inspection dashboard to review, filter, and bookmark past conversions instantly.

---

### ⚡ Quick Start

#### 1. Clone the repository
```bash
git clone https://github.com/shlok926/LipiSync.git
cd LipiSync
```

#### 2. Install dependencies
```bash
pip install -r requirements.txt
```

#### 3. Launch the application
```bash
python main.py
```

---

### ⌨️ Keyboard Shortcuts

LipiSync is fully keyboard accessible, supporting instant screen-reader focus shortcuts:

| Shortcut | Action |
|---|---|
| **Alt + 1** to **Alt + 9** | Switch active workspace pages |
| **Ctrl + Shift + S** | Speak/vocalize selected braille output |
| **Ctrl + 3** | Copy output text to clipboard |
| **Tab / Shift + Tab** | Focus navigation on UI elements |

---

### 📂 Project Structure

```
LipiSync/
├── main.py                # Application entry point
├── ui.py                  # PyQt6 layout, pages, and dynamic styling
├── braille_engine.py      # Core translation parser and mapping logic
├── braille_maps.py        # Bharati & UEB unicode character maps
├── ocr_module.py          # OpenCV computer vision dot detection algorithms
├── settings_manager.py    # Persistent local configuration manager
├── history_favorites.py   # Translation log & bookmarks manager
├── statistics_tracker.py  # User analytics and CSV/JSON export utils
├── requirements.txt       # Project packages
└── .gitignore             # Git version control rules
```

---

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

*© 2026 LipiSync Team. Designed with accessibility in mind.*
