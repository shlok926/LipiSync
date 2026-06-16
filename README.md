# LipiSync — Intelligent Braille Workspace & Translation Suite

> A modern, accessible desktop workspace built with PyQt6 for real-time multi-grade Braille translation, OCR image reading, vocal synthesis, speech translation, and interactive education.

---

## ✨ Features

- 🔄 **Text ↔ Braille Translator** — Bi-directional real-time translation supporting Grade 1 Unified English Braille (UEB) and Devanagari Bharati Braille (Hindi & Marathi).
- 📷 **OCR Reader** — Image-to-Braille scanning powered by custom OpenCV contour and grid clustering analysis.
- 🔊 **Vocalizer Studio** — High-fidelity text-to-speech engine with speed/volume controls and MP3 audio export functionality.
- 🎙 **Voice Translation** — Real-time speech-to-text translation engine for hands-free Braille generation.
- 🎓 **Braille Grades** — Support for advanced UEB Braille contractions and syntax mapping.
- ∑ **Math Notation** — Convert mathematical equations into Nemeth Braille code.
- 📄 **Document Reader** — Accessible PDF file reading and conversion.
- 📖 **Learning Center** — Interactive courses and quiz models with performance metrics to learn Braille.
- ⏳ **History & Favorites** — Split-pane double inspection panel with quick bookmarking of past translations.
- ✓ **Accessibility Audit** — Diagnostic panel checking system dependencies, screen-reader status, keyboard accessibility shortcuts, and audio settings.

---

## 🛠️ Tech Stack

| Technology | Role |
|---|---|
| **Python 3.10+** | Core runtime |
| **PyQt6** | High-fidelity dark-themed desktop interface |
| **OpenCV & NumPy** | Optical Character Recognition (OCR) dot grid clustering |
| **Pillow** | Image loading & asset processing |
| **Pyttsx3** | Real-time text-to-speech synthesis |

---

## 🚀 Installation & Usage

### 1. Prerequisites
Ensure you have Python 3.10+ installed.

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/lipisync.git
cd lipisync
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
python main.py
```

---

## 📁 File Structure

```
lipisync/
├── main.py                # App entry point
├── ui.py                  # PyQt6 UI layout & screen components
├── braille_engine.py      # Core translation algorithms
├── braille_maps.py        # Bharati & UEB unicode character maps
├── ocr_module.py          # OpenCV computer vision dot detection
├── settings_manager.py    # Persistent JSON configurations
├── history_favorites.py   # History logging and bookmarks manager
├── statistics_tracker.py  # Workspace stats and data exports
├── requirements.txt       # Project dependencies
└── .gitignore             # Git version control ignore rules
```

---

## ⌨️ Accessibility Shortcuts

| Shortcut | Action |
|---|---|
| **Alt + 1** to **Alt + 9** | Instant navigation between workspace pages |
| **Ctrl + Shift + S** | Vocalize selected translation output |
| **Ctrl + C / Ctrl + V** | Standard clipboard support |

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
