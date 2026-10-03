[README.md](https://github.com/user-attachments/files/33000717/README.md)
# ComicCraft – AI Comic Story Creator

## Project Overview

**ComicCraft – AI Comic Story Creator** is an AI-powered application that transforms a story idea into a structured five-panel comic with AI-written dialogue, AI-generated illustrations and a final PDF output.

The project documentation is organized according to the TNSDC project phases so that evaluators can easily navigate the complete project journey.

## Objectives

- Let anyone create a comic from a short idea, without drawing or writing skills.
- Combine a text model (Google Gemini) and an image model (Hugging Face) in one simple web workflow.
- Stay reliable: fall back across several models and show clear warnings instead of failing silently.
- Deliver a shareable PDF in a few minutes.

---

## Team Members

| S.No | Team Member |
|---:|---|
| 1 | KAVIYARASAN R |
| 2 | NANDHAKUMAR K |
| 3 | RAJESHKUMAR S |
| 4 | KARUNAKARAN K |
| 5 | TAMILSELVAM S |

---

## Repository Structure

TNSDC documentation is in the eight numbered folders. The runnable application is kept separately in `ComicCraft_App/`.

```text
ComicCraft-TNSDC-Project/
│
├── README.md
├── .gitignore
├── .gitattributes
│
├── 1. Brainstorming & Ideation/
├── 2. Requirement Analysis/
├── 3. Project Design Phase/
├── 4. Project Planning Phase/
├── 5. Project Development Phase/
├── 6. Project Testing/
├── 7. Project Documentation/
├── 8. Project Demonstration/
│   ├── Demo_Video_Link.txt
│   └── project_drivelink.txt
│
└── ComicCraft_App/              <- application source code (separate from documentation)
    ├── app/  templates/  static/  tests/  scripts/diagnostics/
    └── .env.example  requirements*.txt  pytest.ini  README.md
```

Each phase folder has its own `README.md` listing the documents expected there.

---

## TNSDC Documentation by Phase

Original submission documents are PDFs. Where marked, a supplementary `.md` note derived from the source code sits beside them.

### 1. Brainstorming & Ideation – [open folder](1.%20Brainstorming%20%26%20Ideation/README.md)

| Document | Expected File | Status |
|---|---|---|
| Brainstorming & Idea Prioritization | `Brainstorming_and_Idea_Prioritization.pdf` | Add original document |
| Define Problem Statements | `Define_Problem_Statements.pdf` | Add original document |
| Empathy Map | `Empathy_Map.pdf` | Add original document |

### 2. Requirement Analysis – [open folder](2.%20Requirement%20Analysis/README.md)

| Document | Expected File | Status |
|---|---|---|
| Customer Journey Map | `Customer_Journey_Map.pdf` | Add original document |
| Data Flow Diagram | `Data_Flow_Diagram.pdf` | Add original document ([code-derived note](2.%20Requirement%20Analysis/Data_Flow_Diagram.md)) |
| Solution Requirements | `Solution_Requirements.pdf` | Add original document ([code-derived note](2.%20Requirement%20Analysis/Solution_Requirements.md)) |
| Technology Stack | `Technology_Stack.pdf` | Add original document ([code-derived note](2.%20Requirement%20Analysis/Technology_Stack.md)) |

### 3. Project Design Phase – [open folder](3.%20Project%20Design%20Phase/README.md)

| Document | Expected File | Status |
|---|---|---|
| Problem-Solution Fit | `Problem_Solution_Fit.pdf` | Add original document |
| Proposed Solution | `Proposed_Solution.pdf` | Add original document |
| Solution Architecture | `Solution_Architecture.pdf` | Add original document ([code-derived note](3.%20Project%20Design%20Phase/Solution_Architecture.md)) |

### 4. Project Planning Phase – [open folder](4.%20Project%20Planning%20Phase/README.md)

| Document | Expected File | Status |
|---|---|---|
| Project Planning | `Project_Planning.pdf` | Add original document |

### 5. Project Development Phase – [open folder](5.%20Project%20Development%20Phase/README.md)

| Document | Expected File | Status |
|---|---|---|
| Code Layout, Readability and Reusability | `Code_Layout_Readability_and_Reusability.pdf` | Add original document ([code-derived note](5.%20Project%20Development%20Phase/Code_Layout_Readability_and_Reusability.md)) |
| Coding & Solution | `Coding_and_Solution.pdf` | Add original document ([code-derived note](5.%20Project%20Development%20Phase/Coding_and_Solution.md)) |
| Functional Features | `Functional_Features.pdf` | Add original document ([code-derived note](5.%20Project%20Development%20Phase/Functional_Features.md)) |

### 6. Project Testing – [open folder](6.%20Project%20Testing/README.md)

| Document | Expected File | Status |
|---|---|---|
| Performance Testing | `Performance_Testing.pdf` | Add original document |
| Automated tests and diagnostics | – | [Testing_Summary.md](6.%20Project%20Testing/Testing_Summary.md) |

### 7. Project Documentation – [open folder](7.%20Project%20Documentation/README.md)

| Document | Expected File | Status |
|---|---|---|
| ComicCraft Project Report | `ComicCraft_Project_Report.pdf` | Add original document |
| Project Executable Files | `Project_Executable_Files.pdf` | Add original document ([note](7.%20Project%20Documentation/Project_Executable_Files.md): executables are in `ComicCraft_App/`) |
| Sample Project Documentation | `Sample_Project_Documentation.pdf` | Add original document ([code-derived note](7.%20Project%20Documentation/Sample_Project_Documentation.md)) |

### 8. Project Demonstration – [open folder](8.%20Project%20Demonstration/README.md)

| Resource | File | Status |
|---|---|---|
| Demo Video Link | [Demo_Video_Link.txt](8.%20Project%20Demonstration/Demo_Video_Link.txt) | Add demo link |
| Project Drive Link | [project_drivelink.txt](8.%20Project%20Demonstration/project_drivelink.txt) | Add project link |

---

## Project Workflow

```text
Story Idea
    ↓
Story Generation (Gemini: outline, narration, dialogue)
    ↓
Panel / Scene Planning
    ↓
Character & Setting Definition
    ↓
AI Illustration Generation (one image per panel)
    ↓
Comic Panel Assembly
    ↓
PDF Generation
    ↓
Final Comic
```

---

## Key Features

- AI-assisted story creation
- Comic panel generation
- Character and setting customization
- Multiple art-style options
- Tone selection
- Illustration generation with automatic model fallback
- Comic preview
- PDF comic export
- User-friendly web interface
- Error handling and fallback support
- Demo mode that works without API keys

---

## Technology Stack

Python 3.10+, FastAPI and Uvicorn, Jinja2 templates, Pydantic, Google Gemini (`google-genai`), Hugging Face Inference Providers (FLUX.1-schnell, SDXL and others), Pillow, FPDF2, pytest. Details: [Technology_Stack.md](2.%20Requirement%20Analysis/Technology_Stack.md); the original is `2. Requirement Analysis/Technology_Stack.pdf`.

---

## Setup and How to Run

Requirement: Python 3.10 or newer.

```bash
git clone <your-repo-url>
cd ComicCraft-TNSDC-Project/ComicCraft_App
python -m venv .venv
```

Activate the environment: on Windows `.venv\Scripts\Activate.ps1`, on macOS/Linux `source .venv/bin/activate`. Then:

```bash
pip install -r requirements.txt
cp .env.example .env               # Windows: copy .env.example .env
```

Open `.env` and add your own values:

- `GEMINI_API_KEY` from https://aistudio.google.com/apikey
- `HF_TOKEN` from https://huggingface.co/settings/tokens (fine-grained token with "Make calls to Inference Providers")

**Never commit API keys or secrets to GitHub.** No keys yet? Set `DEMO_MODE=true` in `.env` to use placeholder art.

Start the application:

```bash
python -m uvicorn app.main:app --reload
```

Then open http://127.0.0.1:8000 (API docs: http://127.0.0.1:8000/docs, configuration check: http://127.0.0.1:8000/health). Generating five panels takes about 1 to 3 minutes.

Run the automated tests (no keys needed):

```bash
pip install -r requirements-dev.txt
python -m pytest
```

More detail and troubleshooting: [ComicCraft_App/README.md](ComicCraft_App/README.md).

---

## Screenshots and Demo

- Demo video and project Drive link: see [8. Project Demonstration](8.%20Project%20Demonstration/README.md).
- Screenshots: add images to a `screenshots/` folder and link them here (none are stored in the repository yet).

---

## Documentation Rules

- Keep the eight numbered TNSDC folders in the repository.
- Use consistent filenames.
- Keep original documents whenever possible.
- Do not store API keys, passwords, `.env` files, virtual environments, caches, or logs in GitHub.
- Update README links whenever files are moved or renamed.
- Keep application source code separate from TNSDC documentation.
- Do not delete important project documents during restructuring.
- Use PDF for finalized submission documents where appropriate.

---

## Repository Quality Checklist

- [ ] All eight TNSDC phases are present.
- [ ] Every document is placed in the correct phase.
- [ ] Team member names are consistent everywhere.
- [ ] Project title is consistent everywhere.
- [ ] Filenames are professional and consistent.
- [ ] README links are valid.
- [ ] Demo link is available.
- [ ] Project Drive link is available.
- [ ] Final project report is available.
- [ ] No API keys or secrets are committed.
- [ ] No `.venv`, cache, temporary, or unnecessary generated files are committed.
- [ ] Application source code is separated from documentation.
- [ ] Repository is ready for TNSDC evaluation.

---

## Team

**KAVIYARASAN R** · **NANDHAKUMAR K** · **RAJESHKUMAR S** · **KARUNAKARAN K** · **TAMILSELVAM S**

## Project

**ComicCraft – AI Comic Story Creator**

*TNSDC Project Documentation Repository*
