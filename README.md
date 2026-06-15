# Flashcard Generator Agent ⚡🧠

An advanced, production-grade AI Flashcard Generator application built with **Streamlit**, **LangChain**, and **Python**. It automatically crawls websites, extracts text from multiple PDFs, and performs optical character recognition (OCR) or visual understanding on images to generate highly refined, beautifully styled flashcards ready to import directly into Anki.

## 🚀 Key Features

* **Multisource Extraction**: Support for multiple PDFs (PyMuPDF), URLs (BeautifulSoup), and images (local EasyOCR or cloud-based OpenAI Vision).
* **Smart Content Processing**: Deduplication, whitespace reduction, character repair, and recursive chunking.
* **Agentic Flashcard Design**: Uses LangChain with structured output to discover Basic, Cloze, and Concept cards dynamically aligned to user-configured difficulties (Beginner, Intermediate, Advanced).
* **Automatic Quality Correction**: Self-correcting review agent to fix grammatical slips, normalize cloze deletions, and prune redundant questions.
* **Interactive Editing Grid**: An in-browser editable spreadsheet to search, filter, tweak, delete, or append cards before exporting.
* **Recall Study & Quiz Mode**: Study using interactive 3D HTML cards or test yourself with zero-cost multiple-choice exams.
* **Anki Integration**: Direct exports to standard CSV or pre-formatted `.apkg` files with embedded card styling.

---

## 🛠️ Tech Stack & Requirements

* **Frontend**: Streamlit
* **Backend Agent**: LangChain + OpenAI API (`gpt-4o-mini`, `gpt-4o`)
* **Libraries**: `genanki`, `easyocr`, `pymupdf` (fitz), `beautifulsoup4`, `requests`, `pandas`, `tenacity`
* **Package Manager**: `uv`

---

## 💻 Setup & Installation

### 1. Prerequisite: Install `uv`
If you do not have `uv` installed, get it via:
* **Windows (PowerShell)**:
  ```powershell
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
* **macOS / Linux**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

### 2. Prepare Environment Variables
Create or verify your `.env` file in the root directory:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Install Dependencies
Initialize a virtual environment and sync packages:
```bash
uv venv
uv pip install -r requirements.txt
```

---

## ⚙️ How to Run the App

Launch the application using `uv`:
```bash
uv run streamlit run app.py
```
This opens the browser dashboard at `http://localhost:8501`.

---

## 📂 Project Structure

```
flashcard/
├── app.py                      # Main App & Dashboard
├── requirements.txt            # Package list
├── README.md                   # Setup guide
├── .env                        # Environment credentials (Git-ignored)
├── pages/
│   ├── my_flashcards.py        # 3D Flip Study Arena & MCQ Quizzes
│   ├── history.py              # Loaded/Saved deck log
│   ├── templates.py            # Subject templates customization
│   ├── settings.py             # Active model and chunk configs
│   └── about.py                # Pipeline architecture & import guides
├── agents/
│   ├── flashcard_agent.py      # LangChain card creation agent
│   └── review_agent.py         # Quality editor agent
├── loaders/
│   ├── pdf_loader.py           # PyMuPDF text reader
│   ├── url_loader.py           # BeautifulSoup web crawler
│   └── image_loader.py         # OCR & OpenAI Vision extractor
├── export/
│   ├── csv_exporter.py         # CSV text exporter
│   └── anki_exporter.py        # APKG deck packer
└── utils/
    ├── chunker.py              # Chunking routines
    ├── cleaner.py              # Cleanup routines
    ├── ocr.py                  # EasyOCR singleton
    └── ui_styles.py            # CSS Styling & Session defaults
```
