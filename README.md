# 🚗 AI Parking Assistant System

> A multi-stage intelligent parking reservation platform built with LangChain, LangGraph, FastAPI, Streamlit, and RAG — developed progressively across four stages from a simple chatbot to a fully orchestrated multi-agent system.

---

## 📌 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [System Architecture](#system-architecture)
- [Stage 1: RAG Parking Chatbot](#-stage-1-rag-parking-chatbot)
- [Stage 2: Human-In-The-Loop (HITL) Workflow](#-stage-2-human-in-the-loop-hitl-workflow)
- [Stage 3: MCP Server Integration](#-stage-3-mcp-server-integration)
- [Stage 4: LangGraph Orchestration](#-stage-4-langgraph-orchestration)
- [Database](#database)
- [Testing](#testing)
- [Setup & Running the Project](#setup--running-the-project)
- [Example Queries](#example-queries)
- [Security Features](#security-features)
- [Future Improvements](#future-improvements)
- [Author](#author)

---

## Overview

The **AI Parking Assistant System** is a complete end-to-end intelligent parking platform. It enables users to ask natural language questions about parking, make slot reservations, and have those reservations reviewed and approved by an administrator — all orchestrated by a LangGraph multi-agent workflow backed by a FastAPI microservice.

The system was built in four progressive stages, each adding a meaningful layer of intelligence and infrastructure:

| Stage | Focus |
|---|---|
| Stage 1 | RAG Chatbot — answer parking queries using retrieved context |
| Stage 2 | HITL Workflow — admin approval before reservation confirmation |
| Stage 3 | MCP Server — FastAPI microservice to process approved reservations |
| Stage 4 | LangGraph Orchestration — unified multi-agent pipeline |

---

## Tech Stack

| Category | Technology |
|---|---|
| **Language** | Python 3.10 |
| **AI / LLM Orchestration** | LangChain, LangGraph |
| **API Server** | FastAPI, Uvicorn |
| **Frontend UI** | Streamlit |
| **Database** | SQLite |
| **Testing** | Pytest |
| **HTTP Client** | Requests |

---

## Project Structure

```
parking-rag-chatbot/
│
├── app/
│   ├── admin/
│   │   └── admin_agent.py          # Admin HITL agent logic
│   │
│   ├── chatbot/
│   │   ├── chatbot.py              # Core chatbot logic
│   │   └── reservation.py          # Reservation conversation flow
│   │
│   ├── database/
│   │   └── init_db.py              # SQLite schema initialization
│   │
│   ├── guardrails/
│   │   └── filter.py               # Input/output guardrails & PII filtering
│   │
│   ├── mcp/
│   │   ├── mcp_client.py           # MCP client — sends requests to MCP server
│   │   └── mcp_server.py           # FastAPI MCP server — processes reservations
│   │
│   ├── rag/
│   │   └── rag_pipeline.py         # RAG pipeline: embed → retrieve → generate
│   │
│   └── orchestrator.py             # LangGraph orchestrator — ties all agents together
│
├── data/
│   └── parking_info.txt            # Source knowledge base for RAG retrieval
│
├── tests/
│   ├── test_chatbot.py             # Chatbot & RAG tests
│   ├── test_reservation.py         # Reservation workflow tests
│   ├── test_mcp.py                 # MCP server/client tests
│   └── test_orchestrator.py        # End-to-end orchestration tests
│
├── ui.py                           # Streamlit user-facing chatbot UI
├── admin_ui.py                     # Streamlit admin approval dashboard
├── parking.db                      # SQLite database (auto-generated)
├── approved_reservations.txt       # Persistent log of approved reservations
├── requirements.txt
├── pytest.ini
├── README.md
└── .gitignore
```

---

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    Streamlit User UI                     │
│                       (ui.py)                            │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│              LangGraph Orchestrator                      │
│               (app/orchestrator.py)                      │
│                                                          │
│   ┌──────────────┐    ┌──────────────┐                   │
│   │  Intent Node │───►│ Chatbot Node │                   │
│   └──────────────┘    │              │                   │
│                       │ • RAG Q&A    │                   │
│                       │ • Reserv.    │                   │
│                       └──────┬───────┘                   │
│                              │                           │
│                       ┌──────▼───────┐                   │
│                       │  Admin Node  │                   │
│                       │              │                   │
│                       │ • HITL flow  │                   │
│                       │ • Status     │                   │
│                       └──────┬───────┘                   │
└──────────────────────────────┼───────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                │
              ▼                ▼                ▼
   ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐
   │ RAG Pipeline │  │   SQLite DB  │  │  MCP FastAPI     │
   │              │  │  parking.db  │  │  Server          │
   │ HuggingFace  │  │              │  │                  │
   │ Embeddings + │  │  PENDING /   │  │ POST             │
   │ parking_info │  │  APPROVED /  │  │ /process_        │
   │ .txt         │  │  REJECTED    │  │ reservation      │
   └──────────────┘  └──────────────┘  └────────┬─────────┘
                                                │
                                                ▼
                                   approved_reservations.txt

              ┌────────────────────────────────────┐
              │       Streamlit Admin UI            │
              │          (admin_ui.py)              │
              │  • View pending reservations        │
              │  • Approve / Reject actions         │
              └────────────────────────────────────┘
```

---

## 🚀 Stage 1: RAG Parking Chatbot

### Objective

Build an intelligent chatbot capable of answering parking-related questions using Retrieval-Augmented Generation (RAG), grounding every answer in real parking data.

### Features

- LangChain RAG pipeline
- Streamlit chatbot interface
- Guardrails to block restricted/unsafe queries
- Conversational reservation flow (name, car number, date & time)
- Automated tests with Pytest

### How It Works

**RAG Pipeline** (`app/rag/rag_pipeline.py`)

The pipeline follows three steps:

1. **Embed** — The user's query is transformed into a vector using HuggingFace Sentence Transformers.
2. **Retrieve** — The vector is used to fetch the most relevant chunks from `parking_info.txt`.
3. **Generate** — Retrieved chunks are injected into the LLM prompt to produce a grounded response.

The chatbot only answers using the provided context — it never fabricates parking-specific facts.

**Guardrails** (`app/guardrails/filter.py`)

Blocks queries such as:
- Accessing other users' data
- Unauthorized information requests
- Unsafe or prompt-injection instructions

**Reservation Flow** (`app/chatbot/reservation.py`)

Guides users through providing:
- First Name & Surname
- Car Number
- Reservation Date & Time

---

## 👨‍💼 Stage 2: Human-In-The-Loop (HITL) Workflow

### Objective

Introduce mandatory administrator approval before any reservation is confirmed, ensuring human oversight over all bookings.

### Features

- Reservations stored with `PENDING` status awaiting review
- Streamlit admin dashboard for approving or rejecting reservations
- SQLite integration for persistent reservation tracking
- Status query support — users can check their reservation status by name

### Workflow

```
1. User submits a reservation request
       ↓
2. Reservation saved to SQLite with status: PENDING
       ↓
3. Admin reviews in the dashboard (admin_ui.py)
       ↓
4. Admin clicks Approve or Reject
       ↓
5. Status updated in DB → APPROVED or REJECTED
       ↓
6. User queries status: "check status <name>"
```

### Admin Dashboard (`admin_ui.py`)

The Streamlit admin UI provides:
- A live list of all pending reservations
- Reservation details (name, car number, time)
- One-click Approve / Reject buttons

---

## 🌐 Stage 3: MCP Server Integration

### Objective

Implement a FastAPI-based MCP (Model Context Protocol) style server that processes approved reservations and logs them to persistent storage.

### Features

- FastAPI MCP server with a dedicated processing endpoint
- Secure secret-token authentication on all API calls
- MCP client that communicates with the server post-approval
- Approved reservations logged to `approved_reservations.txt`

### MCP Architecture

**Server** (`app/mcp/mcp_server.py`)

```
POST /process_reservation
  ├── Validates secret token
  ├── Processes reservation data
  └── Appends entry to approved_reservations.txt
```

**Client** (`app/mcp/mcp_client.py`)

Called by the admin agent after approval to forward the reservation to the MCP server for final processing.

**Security**

- Secret token in request headers — all unauthenticated requests are rejected
- Restricted API surface (single processing endpoint)

**File Storage Format** (`approved_reservations.txt`)

```
Name | Car Number | Reservation Period | Approval Time
```

Example entry:
```
Sampurna Yanda | OD123456 | 2026-07-01 | 2026-05-12 05:00:22
```

---

## 🔄 Stage 4: LangGraph Orchestration

### Objective

Tie all system components together under a unified LangGraph orchestration layer, enabling intent-based routing across multiple specialized agents.

### Features

- Single LangGraph graph managing the full workflow
- Intent detection to route queries to the correct agent
- Multi-agent coordination across chatbot, admin, and MCP layers
- End-to-end integration testing

### LangGraph Nodes

| Node | Responsibility |
|---|---|
| **Intent Node** | Classifies the user's message — parking query, reservation request, or status check |
| **Chatbot Node** | Handles RAG Q&A and the reservation conversation flow |
| **Admin Node** | Handles reservation status checks and the HITL approval workflow |

### Orchestration Flow

```
User Input (ui.py)
      │
      ▼
LangGraph Orchestrator (orchestrator.py)
      │
      ├──[parking question]──► RAG Chatbot Agent ──► LLM Response
      │
      ├──[book parking]──────► Reservation Agent ──► SQLite (PENDING)
      │                                │
      │                                ▼
      │                         Admin HITL Agent
      │                                │
      │                         ┌──────┴──────┐
      │                      Approve        Reject
      │                         │
      │                         ▼
      │                   MCP FastAPI Server
      │                         │
      │                         ▼
      │               approved_reservations.txt
      │
      └──[check status]──────► Admin Agent ──► Status from SQLite
```

---

## 💾 Database

The system uses **SQLite** (`parking.db`) for reservation persistence.

### Schema

| Field | Type | Description |
|---|---|---|
| `id` | INTEGER | Auto-increment primary key |
| `name` | TEXT | User's first name |
| `surname` | TEXT | User's last name |
| `car_number` | TEXT | Vehicle registration number |
| `reservation_time` | TEXT | Requested reservation date & time |
| `status` | TEXT | `PENDING`, `APPROVED`, or `REJECTED` |

### Status Lifecycle

```
[PENDING] ──► [APPROVED] ──► Sent to MCP Server ──► logged to file
     │
     └──────► [REJECTED]
```

---

## 🧪 Testing

All tests are written with **Pytest** and can be run with a single command.

```bash
pytest -v
```

### Test Coverage

**`test_chatbot.py`**
- RAG response validation (answers grounded in context)
- Guardrail validation (blocked queries return appropriate responses)
- Status query testing

**`test_reservation.py`**
- Full reservation conversation flow
- State transitions (PENDING → APPROVED / REJECTED)
- Reservation confirmation messaging

**`test_mcp.py`**
- MCP server endpoint processing
- API response validation
- Token authentication enforcement

**`test_orchestrator.py`**
- LangGraph intent routing accuracy
- End-to-end pipeline validation
- Multi-agent coordination

---

## Setup & Running the Project

### Prerequisites

- Python 3.10+
- All API keys configured in `.env`

### 1. Clone the Repository

```bash
git clone <repository_url>
cd parking-rag-chatbot
```

### 2. Create a Virtual Environment

```bash
python -m venv venv310
```

Activate it:

```bash
# Linux / macOS
source venv310/bin/activate

# Windows
venv310\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_gemini_api_key
PINECONE_API_KEY=your_pinecone_api_key
MCP_SECRET_TOKEN=your_mcp_secret_token
```

### 5. Run the MCP Server

```bash
uvicorn app.mcp.mcp_server:app --reload
```

### 6. Run the User Chatbot UI

```bash
streamlit run ui.py
```

### 7. Run the Admin Dashboard

```bash
streamlit run admin_ui.py
```

> Run Steps 5, 6, and 7 in **separate terminal windows** simultaneously.

---

## Example Queries

### Parking Information

```
What are the parking prices?
What are the working hours?
```

### Reservation Request

```
book parking
```

### Status Check

```
check status sampurna
```

---

## 🔐 Security Features

| Feature | Description |
|---|---|
| **Guardrails** | Input/output filtering blocks PII leakage and prompt injections |
| **Token Authentication** | MCP server rejects requests without a valid secret token |
| **HITL Approval** | No reservation is confirmed without explicit admin action |
| **Controlled API Surface** | MCP server exposes only the `POST /process_reservation` endpoint |

---

## 📸 Suggested Screenshots for Documentation

To illustrate the system, consider capturing:

- Chatbot interface in action (`ui.py`)
- Reservation booking conversation flow
- Admin approval dashboard (`admin_ui.py`)
- MCP server terminal logs (Uvicorn output)
- Contents of `approved_reservations.txt`
- LangGraph orchestration graph visualization
- Pytest results (`pytest -v` output)

---

## 🔮 Future Improvements

| Enhancement | Description |
|---|---|
| Email Notifications | Notify users when reservations are approved or rejected |
| Docker Deployment | Containerize all services for portable deployment |
| Cloud Database | Replace SQLite with PostgreSQL or a managed cloud DB |
| Kubernetes | Orchestrate multi-container deployment at scale |
| Real-Time Availability | Live parking slot availability tracking |
| OAuth Authentication | Replace token auth with OAuth 2.0 / SSO |
| CI/CD Pipeline | Automate testing and deployment with GitHub Actions |
| Terraform | Infrastructure-as-code for cloud provisioning |

---

## ✅ Final Outcome

This project successfully delivers a complete, production-structured intelligent parking assistant demonstrating:

- A RAG-powered chatbot grounded in real parking data
- A human-in-the-loop reservation approval workflow
- A secure FastAPI MCP microservice for reservation processing
- A unified LangGraph multi-agent orchestration layer
- Persistent data management across SQLite and file storage
- A comprehensive automated test suite across all system layers

---

