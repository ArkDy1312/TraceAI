
# 🔍 LLM-Powered Traceability System

A **local-first, privacy-respecting multi-agent system** that links features, commits, and test results for real-time, explainable traceability—powered by LangGraph, Ollama (Gemma), Qdrant, and Gradio.

---

## 🎯 Overview

This project builds a graph-based, intelligent traceability system that enables teams to:
- Automatically **link feature specifications to code commits and tests**
- Ask questions via a **natural language interface** powered by local LLMs
- Ensure **auditable operations with local logs**
- Detect and handle changes efficiently using an **item cache and delta checker**

---

## 🧠 Multi-Agent System

| Agent      | Role            | Responsibility                                                                 |
|------------|------------------|------------------------------------------------------------------------------|
| PM Agent   | Product Manager  | Detects and stores new or changed feature descriptions into PostgreSQL after delta checks |
| Dev Agent  | Developer        | Validates linked features, embeds commit descriptions, and stores them in Qdrant for search |
| QA Agent   | QA Engineer      | Validates feature + commit status, embeds test descriptions, and logs test associations in Qdrant |

---

## 🗂 Example Traceability Graph

Using structured input data (`traceability_sample_data.json`), the system builds graphs like:

```
Feature: "Profile Picture Upload"
 ├── Code: commit_be7099f7 by Jeanette Johnson
 │    ├── Test: test_sea_31 (Failed)
 │    └── Test: test_like_89 (Failed)
```

These links are formed using **semantic similarity + metadata filtering**, not basic keyword matching.

---

## 🧾 Key Features

- 🧠 **LangGraph-based coordination** of PM, Dev, QA agents
- 🛡 **Offline LLMs** with Ollama + Gemma
- 🔍 **Qdrant-powered search** with semantic indexing and filter-based retrieval
- 🧮 **Delta checking** via item caching to avoid redundant processing
- 🧾 **Audit-friendly logs** (SQLite)
- 📊 **Graph UI** (Gradio + pyvis)
- 🧹 **Remove outdated nodes** (delete stale commits/tests)
- 🧠 **Prompt tuning** by user role and workspace
- 📤 **Export traceability results** as Markdown

---

## 🛠 Tools Used

| Tool              | Purpose                                              |
|-------------------|------------------------------------------------------|
| **LangGraph**     | Multi-agent orchestration using directed graphs     |
| **Ollama (Gemma)**| Local LLM inference for natural language reasoning  |
| **Qdrant**        | Vector store for semantic + filtered search         |
| **Gradio**        | UI for dashboard and interactive Q&A                |
| **SQLite**        | Lightweight audit log database                      |
| **PostgreSQL**    | Stores features and commit status metadata          |
| **TQDM, isort, black, flake8** | Dev tools for formatting, linting, and UX     |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Docker & Docker Compose
- [Ollama](https://ollama.com/) with Gemma model installed

### Installation

```bash
git clone https://github.com/your-org/langgraph-trace.git
cd langgraph-trace
docker-compose up --build
```

Access the app at: [http://localhost:8000](http://localhost:8000)

---

## 📊 UI Overview

- 🌐 Interactive graph viewer (via pyvis)
- 💬 Natural language querying
- 🔍 Delta-aware refresh system
- ❌ Manual deletion of obsolete/problematic nodes
- 📄 Export trace views to Markdown

---

## 🧠 Prompt Tuning

Defined in:
- `config/prompt_templates.py`

Scoped by:
- `workspace_id`
- `user_role` (PM, Dev, QA)

---

## 🔒 Privacy & Security

- 🧠 All LLM operations are **offline (via Ollama + Gemma)**
- 🔍 Semantic search with **Qdrant**, filtered by workspace/team
- 🗃 Logs stored locally via **SQLite audit DB**

---

## 🔮 Future Extensions

| Feature            | Description                                         |
|--------------------|-----------------------------------------------------|
| ⏱ Async jobs       | Background task queuing                             |
| 📎 Webhooks         | Auto-update from GitHub, Jira, TestRail             |
| 🔐 Role-based auth | OAuth/JWT login with workspace scoping               |

