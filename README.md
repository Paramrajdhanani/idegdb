# CodeForge IDE - Full-Stack Online Code Compiler & Cloud IDE

> **A high-performance, dark-first cloud IDE and safe multi-language code execution platform built with Django, Django REST Framework, Monaco Editor, and Isolated Sandbox Execution Architecture.**

---

## 🌟 Overview

**CodeForge IDE** is a modern developer tool inspired by the workflow of OnlineGDB, re-engineered from the ground up with a dark-first developer aesthetic, Monaco Editor integration, multi-file project workspace, interactive terminal dock, debugger UI, tokenized sharing, and a secure isolated execution sandbox.

---

## 🚀 Key Features

* **Multi-Language Sandbox**: Execute Python, Node.js/JavaScript, C++, C, Java, SQL (interactive in-memory query engine), Rust, Go, and more with sub-second response times.
* **Monaco Editor Integration**: VS Code-grade editing experience featuring syntax highlighting, multi-cursor, bracket matching, code folding, minimap, formatting (`Ctrl+B`), and customizable themes (*CodeForge Dark*, *Midnight High Contrast*, *VS Dark*, *Light*).
* **Multi-File Project Workspace**: Full directory and file tree hierarchy, active file tabs, in-memory state preservation across tabs, file upload/download, and automatic ZIP bundling.
* **Integrated Terminal Dock**: Dedicated tabs for **Terminal**, **Output** (stdout/stderr separation with exit codes, execution duration in milliseconds, and memory metrics), **Standard Input** (interactive multiline stdin stream), **Errors / Diagnostics**, and **Debug Console**.
* **Debugger UI**: Call stack inspector, variable viewer, watch expression evaluator, and breakpoint manager.
* **Global Command Palette (`Ctrl+P` / `Ctrl+K`)**: Quick-jump to files, switch projects, run commands, and format code instantly.
* **Tokenized Code Sharing**: Generate secure random share tokens for public, read-only, and iframe embeddable sandbox previews without exposing sensitive account data.
* **Cloud Dashboard & Analytics**: Developer activity sparklines, execution success rates, recent runs, and project management (clone, favorite, delete, duplicate).
* **Security & Process Isolation**: Sandboxed temp working directories, CPU/wall-clock execution timeouts (7s default), process limits, output truncation guards against memory overflow attacks, and zero direct execution inside Django web server workers.

---

## 🛠️ Technology Stack

### Backend
* **Language**: Python 3.13+
* **Framework**: Django 5.0+, Django REST Framework (DRF)
* **Database**: PostgreSQL (Production) / SQLite (Zero-setup development)
* **Security**: Non-root subprocess isolation, memory ceiling checks, output flood guards, CSRF & Token authentication, Rate throttling (120/min anon, 600/min user)

### Frontend
* **Core**: Modern JavaScript (ES6+), HTML5 Semantic markup
* **Styling**: Vanilla CSS Design System with CSS Custom Properties, Glassmorphism, 8px grid layout
* **Editor**: Microsoft Monaco Editor
* **Icons**: Lucide Icons
* **Animations**: GSAP (GreenSock Animation Platform)

---

## 📐 Architecture

```
                                  +------------------------------------------------+
                                  |                 CodeForge IDE                  |
                                  |            (Modern Dark-First UI)              |
                                  | Monaco Editor + Lucide + GSAP + WebSocket UI   |
                                  +-----------------------+------------------------+
                                                          |
                                           REST API & WebSockets (JSON)
                                                          |
                                                          v
                                  +------------------------------------------------+
                                  |               Django Backend Core              |
                                  |  Django 5 + Django REST Framework + Channels   |
                                  +-----------------------+------------------------+
                                                          |
                                +-------------------------+-------------------------+
                                |                         |                         |
                                v                         v                         v
                       +-----------------+       +-----------------+       +-----------------+
                       |  Database Layer |       | Execution Engine|       | Sharing & Auth  |
                       | PostgreSQL /    |       | Base Runner +   |       | Tokenized Share |
                       | SQLite (dev)    |       | Safe Sandbox +  |       | Permissions     |
                       | Models & ORM    |       | Judge0/Docker   |       | Session/Token   |
                       +-----------------+       +-----------------+       +-----------------+
```

---

## 📡 REST API Documentation

### Authentication
* `POST /api/auth/register/` - Register a new user account
* `POST /api/auth/login/` - Authenticate and obtain auth token
* `POST /api/auth/logout/` - Invalidate session & auth token
* `GET  /api/auth/me/` - Retrieve current user profile
* `PUT  /api/auth/preferences/` - Update editor theme, font size, and tab size

### Projects & Files
* `GET    /api/projects/` - List user projects (supports `?search=`, `?language=`, `?filter=my|favorite|public`)
* `POST   /api/projects/` - Create project (auto-generates entry point template file)
* `GET    /api/projects/{id}/` - Retrieve full project with all files
* `PATCH  /api/projects/{id}/` - Update project metadata or settings
* `DELETE /api/projects/{id}/` - Delete project
* `POST   /api/projects/{id}/duplicate/` - Clone project into a new copy
* `GET    /api/projects/{id}/download/` - Download project as a clean ZIP archive
* `POST   /api/projects/{id}/files/` - Create a new file in project
* `PATCH  /api/files/{id}/` - Update file content or filename
* `DELETE /api/files/{id}/` - Delete a file

### Code Execution
* `POST /api/executions/` - Execute source code / multi-file project in isolated sandbox
* `GET  /api/executions/history/` - View recent execution history
* `GET  /api/executions/{id}/` - Retrieve execution result, stdout, stderr, and metrics
* `POST /api/executions/{id}/cancel/` - Cancel a running execution

### Sharing
* `POST /api/projects/{id}/share/` - Generate secure share token URL and iframe embed code
* `GET  /api/share/{token}/` - Retrieve shared project payload for sandbox viewing

### Languages & Search
* `GET /api/languages/` - List all active compilers, interpreters, and templates
* `GET /api/search/?q={query}` - Global command palette search across files, projects, and actions

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| <kbd>Ctrl</kbd> + <kbd>Enter</kbd> / <kbd>F9</kbd> | **Run Program** |
| <kbd>F8</kbd> | **Debug Program** |
| <kbd>Ctrl</kbd> + <kbd>S</kbd> | **Save Project** |
| <kbd>Ctrl</kbd> + <kbd>B</kbd> | **Format / Beautify Code** |
| <kbd>Ctrl</kbd> + <kbd>P</kbd> / <kbd>Ctrl</kbd> + <kbd>K</kbd> | **Global Command Palette** |
| <kbd>Ctrl</kbd> + <kbd>M</kbd> | **Create New File** |
| <kbd>Ctrl</kbd> + <kbd>Shift</kbd> + <kbd>S</kbd> | **Editor Settings** |
| <kbd>Esc</kbd> | **Close Active Modals** |

---

## ⚙️ Installation & Development Setup

### 1. Prerequisites
* Python 3.11+ (Python 3.13 recommended)
* Node.js (Optional for local JS execution)

### 2. Setup Environment & Install Dependencies
```bash
# Clone the repository
git clone https://github.com/example/codeforge-ide.git
cd codeforge-ide

# Install required dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

### 4. Run Migrations & Seed Demo Data
```bash
python manage.py makemigrations accounts languages projects executions sharing dashboard
python manage.py migrate
python manage.py seed_data
```

### 5. Launch Development Server
```bash
python manage.py runserver 8000
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🧪 Running Automated Tests

Run the full Django test suite:
```bash
python manage.py test
```

---

## 🔒 Security Architecture

1. **Subprocess Isolation**: Every execution creates an ephemeral temporary directory (`scratch/sandboxes/codeforge_run_*`) destroyed upon process exit.
2. **Timeout Enforcers**: Hard timeout limits (`7s`) kill rogue scripts (e.g. `while True: pass`).
3. **Output Flood Truncation**: Stdout and stderr streams are capped to prevent memory exhaustion attacks.
4. **Non-destructive Environment**: Stripped process environment variables and unbuffered I/O.
5. **No Direct Execution on Web Worker**: Execution is handled by an abstract runner decoupled from web request threads.

---

## 📄 License
MIT License. Built for portfolio demonstration of full-stack engineering excellence.
