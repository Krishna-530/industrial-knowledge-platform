# Industrial Knowledge Intelligence Platform

## About the Project

The Industrial Knowledge Intelligence Platform (IKIP) is an AI-powered document management and knowledge discovery system developed during a hackathon.

Many organizations store thousands of technical documents such as manuals, standard operating procedures (SOPs), maintenance reports, research papers, policies, and other industrial documents. Although these documents contain valuable information, finding specific details often requires manually browsing multiple files or relying only on keyword searches.

The goal of this project is to make industrial knowledge easier to organize, process, and search using Artificial Intelligence. Instead of searching only by file names or exact keywords, users can upload documents, process them automatically, and search for information using natural language. The platform also extracts important entities and relationships from documents and represents them as a knowledge graph.

This project combines modern web technologies with AI to build a centralized knowledge management platform that is easy to use and scalable.

---

# Features

## User Authentication

- Secure Login
- JWT Authentication
- Password Hashing
- Role-Based Access Control (RBAC)

---

## Dashboard

The dashboard provides an overview of the platform.

It displays:

- Total Documents
- Processed Documents
- Document Chunks
- Extracted Entities
- Processing Queue Status
- Knowledge Graph Statistics
- Recent Upload Activity

---

## Document Management

Users can

- Upload documents
- View uploaded documents
- Track document processing
- Manage document versions
- View document metadata

Supported file formats include:

- PDF
- DOC
- DOCX
- PPTX
- TXT

---

## AI Processing Pipeline

Whenever a document is uploaded, it follows an automated processing workflow.

```
Document Upload
        │
        ▼
File Validation
        │
        ▼
Text Extraction
        │
        ▼
Chunk Generation
        │
        ▼
Embedding Generation
        │
        ▼
Entity Extraction
        │
        ▼
Relationship Extraction
        │
        ▼
Knowledge Graph Update
        │
        ▼
Search Index Update
        │
        ▼
Processing Complete
```

---

## Semantic Search

The platform supports

- Keyword Search
- AI-based Semantic Search
- Metadata Filtering
- Ranked Search Results

Instead of searching only for exact words, users can search using natural language to retrieve relevant documents.

---

## Knowledge Graph

The application can build a Knowledge Graph from extracted entities and relationships.

This allows users to visualize how different concepts, machines, components, or processes are connected.

If Neo4j is not configured, the application continues to work normally without graph visualization.

---

## User Management

Administrators can

- Create Users
- Edit Users
- Activate or Deactivate Accounts
- Reset Passwords
- Assign Roles
- Manage Permissions

---

## Background Processing

Document processing is performed asynchronously using background workers.

This keeps the application responsive even while large documents are being processed.

---

# Technology Stack

## Frontend

- Next.js 14
- React
- TypeScript
- Tailwind CSS
- TanStack React Query
- Cytoscape.js (Knowledge Graph Visualization)

---

## Backend

- FastAPI
- Python 3.11
- SQLAlchemy
- Alembic
- JWT Authentication
- Bcrypt Password Hashing

---

## Database

- PostgreSQL

---

## AI & Document Processing

- LangChain
- LangGraph
- Groq API
- Embedding Models
- pdfplumber
- PyPDF2
- python-docx
- python-pptx
- pytesseract

---

## Knowledge Graph

- Neo4j (Optional)

---

# Project Structure

```
Industrial-Knowledge-Platform/

├── backend/
│   ├── app/
│   ├── api/
│   ├── core/
│   ├── database/
│   ├── workers/
│   ├── scripts/
│   └── run.py
│
├── frontend/
│
├── docs/
│
├── docker-compose.yml
├── pyproject.toml
├── .env.example
└── README.md
```

---

# Software Requirements

Before running the project, install the following software.

- Python 3.11 or above
- Node.js 18 or above
- PostgreSQL
- Poetry
- Git
- Neo4j (Optional)

---

# Backend Setup

### 1. Clone the repository

```bash
git clone <your-github-repository-url>

cd Industrial-Knowledge-Platform
```

### 2. Install Poetry (if not already installed)

```bash
pip install poetry
```

### 3. Install backend dependencies

```bash
poetry install
```

### 4. Activate the virtual environment

```bash
poetry shell
```

---

# Frontend Setup

Go to the frontend directory.

```bash
cd frontend
```

Install all required packages.

```bash
npm install
```

---

# Environment Configuration

Copy the example environment file.

```bash
cp .env.example .env
```

Update the required values inside the `.env` file.

Important variables include:

- DATABASE_URL
- SECRET_KEY
- SERVER_HOST
- SERVER_PORT
- GROQ_API_KEY
- Neo4j Configuration (Optional)

---

# Database Setup

Create a PostgreSQL database.

Update the connection string inside `.env`.

Run the database migrations.

```bash
alembic upgrade head
```

---

# Running the Backend

From the project root directory, start the backend.

```bash
python run.py
```

The backend will start on

```
http://127.0.0.1:8000
```

Swagger API Documentation

```
http://127.0.0.1:8000/docs
```

ReDoc Documentation

```
http://127.0.0.1:8000/redoc
```

---

# Running the Frontend

Move to the frontend folder.

```bash
cd frontend
```

Start the development server.

```bash
npm run dev
```

The frontend will be available at

```
http://localhost:3000
```

---

# How the System Works

1. The user logs into the platform.
2. A document is uploaded through the interface.
3. The backend validates the uploaded file.
4. The document is stored securely.
5. Background workers extract text from the document.
6. The extracted text is divided into smaller chunks.
7. Embeddings are generated for semantic search.
8. AI extracts entities and relationships.
9. The Knowledge Graph is updated (if enabled).
10. Search indexes are updated.
11. The processed document becomes available for searching.

---

# Future Improvements

Some features planned for future versions include:

- OCR support for scanned documents
- AI Chat with uploaded documents (RAG)
- Multi-language document support
- Real-time processing updates
- Email notifications
- Cloud storage integration
- Advanced analytics dashboard
- Docker deployment for production

---

# Notes

- PostgreSQL is required to store application data.
- Neo4j is optional and is only required for Knowledge Graph visualization.
- A valid Groq API key is required for AI-powered document understanding and semantic search.
- Swagger documentation is automatically available after starting the backend.

---

# License

This project was developed as part of a hackathon for learning and demonstration purposes.

Feel free to use or modify it for educational purposes.