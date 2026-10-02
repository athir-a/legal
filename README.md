# ⚖️ Legal AI Assistant

An AI-powered legal information assistant that helps users understand legal concepts and find relevant information through a simple, conversational interface.

The system combines **Retrieval-Augmented Generation (RAG)** with a structured backend API to provide clearer, more grounded legal answers while reducing the risk of unsupported AI-generated information.

> **Disclaimer:** This project is intended for legal information and educational purposes only. It does not provide legal advice and should not be treated as a substitute for a qualified legal professional.

---

## 🚀 Features

- 💬 Ask legal questions in natural language
- 🤖 AI-generated explanations in a simple, understandable format
- 📚 Retrieval-Augmented Generation (RAG) for grounded responses
- 🔎 Relevant legal source/section references
- ⚠️ "Not enough information" handling for unsupported questions
- 🧩 Structured responses for easier understanding
- 🌐 Web-based frontend
- 🔌 REST API backend
- 🛡️ Legal disclaimer and defined system scope
- ⚡ Fast interaction through a lightweight API architecture

---

## 🚨 The Problem

Consumers frequently face problems such as:

- Defective products
- Poor or deficient services
- Misleading advertisements
- Unfair trade practices
- Product-related harm
- Online shopping disputes
- Warranty and service issues
- Problems obtaining refunds or replacements
- Difficulty understanding their legal rights

Although consumer-protection laws are publicly available, the information is often difficult for a non-lawyer to navigate.

Users may have to:

1. Identify the relevant legal issue.
2. Find the applicable law.
3. Search through lengthy legal documents.
4. Understand legal terminology.
5. Determine which provision applies to their situation.

This creates a gap between **having access to legal information** and **being able to understand and use that information**.

---

# 💡 Our Solution

Provides a conversational interface through which users can ask questions about consumer protection in everyday language.

For example:

> **"I bought a phone online and it stopped working after a few days. What are my consumer rights?"**

Instead of simply generating an answer from the model's internal knowledge, the system retrieves relevant legal information from its knowledge base and uses that information as context for generating the response.

The system is therefore designed around:

**Question → Retrieval → Legal Context → AI Explanation → Source Reference**

---

# 🎯 Project Objectives

The project aims to:

- Make Indian consumer-protection information easier to understand.
- Reduce the difficulty of navigating legal documents.
- Provide answers grounded in documented legal sources.
- Show relevant source/section references where available.
- Avoid confidently answering when sufficient supporting information cannot be retrieved.
- Present legal information in a structured, accessible format.
- Help users understand possible consumer-protection concepts before seeking professional assistance.

---

# 🧠 Why RAG?

A conventional Large Language Model can generate fluent answers, but relying only on the model's internal knowledge can be problematic for legal applications.

Legal information requires:

- Accurate terminology
- Source grounding
- Traceability
- Awareness of amendments and changes
- Clear separation between supported information and unsupported claims

ConsumerGuard AI therefore uses **Retrieval-Augmented Generation (RAG)**.

### RAG Workflow

```text
                         USER
                           │
                           ▼
                 ┌──────────────────┐
                 │ Consumer Question│
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Query Processing │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Document / Legal │
                 │    Retrieval     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Relevant Legal   │
                 │     Context      │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │  AI Generation   │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Structured Legal │
                 │     Response     │
                 └────────┬─────────┘
                          │
                          ▼
                 ┌──────────────────┐
                 │ Source / Section │
                 │    References    │
                 └──────────────────┘
```

---

# 📚 Consumer Protection Scope

The system is designed around consumer-protection issues in India.

The knowledge base may cover topics including:

- Consumer rights
- Definition of a consumer
- Defective goods
- Deficient services
- Unfair trade practices
- Misleading advertisements
- Product liability
- Consumer complaints
- Consumer dispute redressal
- Consumer Commissions
- Remedies available under consumer-protection law
- E-commerce-related consumer issues
- Relevant rules, regulations, and notifications

The initial legal foundation includes the **Consumer Protection Act, 2019**, which establishes the statutory framework for protecting consumer interests and addressing consumer disputes.

---

# 🏛️ Data Sources & Licensing

The quality of a legal AI system depends heavily on the quality and provenance of its underlying legal information.

Therefore, all sources used to construct the project's knowledge base are documented below.

## Primary Source

| Data Source | Content Used | Source | License / Terms of Use | Usage |
|---|---|---|---|---|
| **India Code — Government of India** | Indian legislation, including the Consumer Protection Act, 2019 | [India Code](https://indiacode.gov.in/home) | Government-hosted legal information; use remains subject to the applicable source terms, notices, and requirements | Primary legal source for the RAG knowledge base and legal references |

India Code describes itself as a digital repository containing content provided by Ministries/Departments of the Government of India and identifies the National Informatics Centre (NIC) as the site's developer.

The **Consumer Protection Act, 2019 (Act No. 35 of 2019)** is available through India Code and is a primary source for the project's consumer-protection knowledge base.

### Data Usage

The legal source material is processed to support the project's retrieval pipeline.

The general process is:

```text
Official Legal Source
        │
        ▼
Document Collection
        │
        ▼
Cleaning / Preprocessing
        │
        ▼
Chunking
        │
        ▼
Knowledge Base
        │
        ▼
Retrieval
        │
        ▼
AI Context
        │
        ▼
Consumer Protection Answer
```

The project:

- Maintains attribution to the original source.
- Uses the source material as the basis for retrieval and contextual answering.
- Provides source/section references where available.
- Does not claim ownership of the underlying government legal texts.
- Encourages users to verify important information against the original official source.

### Licensing Note

The underlying legal material is **not being relicensed by this project**.

The open-source license selected for the project's own software code, if any, is separate from the rights, notices, and terms applicable to third-party or government-provided source material.

We do **not** claim that the underlying India Code material is released under the project's software license.

Before redistributing the underlying source documents independently, users should review the applicable terms and notices associated with the original source.

### Source Attribution

Primary legal source:

**India Code — Digital Repository of Indian Laws**  
Government of India

[https://www.indiacode.nic.in/](https://www.indiacode.nic.in/?utm_source=chatgpt.com)


# ⚠️ Insufficient Information Handling

A major risk in legal AI is presenting an unsupported answer with high confidence.

ConsumerGuard AI therefore includes an **insufficient-information** pathway.

If the system cannot retrieve enough relevant information to support an answer, it should avoid presenting a confident legal conclusion.

Conceptually:

```text
User Question
      │
      ▼
Retrieve Relevant Information
      │
      ├───────────────┐
      │               │
 Sufficient       Insufficient
 Context            Context
      │               │
      ▼               ▼
Generate Answer    State that
with Sources       information
                   is insufficient
```

This helps distinguish between:

- **Supported legal information**
- **Incomplete information**
- **Questions outside the available knowledge base**

---

# 🧩 Answer Structure

Responses are designed to be easier for non-lawyers to understand.

A typical response may contain:

```text
1. Short Answer
2. Explanation
3. Relevant Consumer Protection Concept
4. Applicable Legal Provision
5. Source / Section
6. Important Limitations
7. Disclaimer
```

The objective is to translate complex legal information into understandable language without intentionally changing the meaning of the underlying provision.

---

# 🛡️ Safety & Reliability

This is an informational system rather than a substitute for professional legal advice.

The project incorporates several safeguards.

### 1. Source Grounding

Responses are generated using retrieved legal context whenever available.

### 2. Source References

Relevant legal provisions or source information can be presented alongside the generated answer.

### 3. Insufficient Information Handling

The system can indicate when available information is insufficient rather than fabricating a legal answer.

### 4. Defined Scope

The system focuses specifically on **consumer protection** rather than attempting to answer every area of law.

### 5. Disclaimer

The application clearly communicates that its responses are informational and educational.

---

# 🏗️ System Architecture

```text
┌─────────────────────────────────────────────┐
│                  FRONTEND                   │
│                                             │
│  Question Input → Language → Answer View   │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                BACKEND API                  │
│                                             │
│       Django + Django REST Framework        │
│                                             │
│  • Request Validation                        │
│  • Query Processing                          │
│  • Response Formatting                       │
│  • API Communication                         │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                  RAG LAYER                  │
│                                             │
│  Query → Retrieval → Relevant Context       │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│             CONSUMER LAW KNOWLEDGE          │
│                                             │
│       India Code / Legal Documents          │
└──────────────────────┬──────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────┐
│                 AI MODEL                    │
│                                             │
│  Retrieved Context + User Question          │
│                     ↓                       │
│              Structured Answer              │
└─────────────────────────────────────────────┘
```

---

# 🛠️ Technology Stack

| Component | Technology |
|---|---|
| Frontend | Web-based frontend |
| Backend | Python |
| Backend Framework | Django |
| API Framework | Django REST Framework |
| AI | Large Language Model |
| Knowledge Approach | Retrieval-Augmented Generation |
| Data Source | India Code / official legal sources |
| API Format | REST / JSON |
| Version Control | Git |
| Deployment | Frontend + Python backend hosting |

---

# 🔌 API

## Ask a Consumer Protection Question

### Endpoint

```http
POST /api/ask/
```

### Request

```json
{
  "question": "What is product liability?",
  "language": "en"
}
```

### Example Response

```json
{
  "answer": "Product liability refers to...",
  "sources": [
    {
      "title": "Consumer Protection Act, 2019",
      "section": "Relevant Section"
    }
  ]
}
```

The exact response structure may evolve as the application is developed.

---

# 🧪 Example Questions

Users can ask questions such as:

```text
What is product liability?

What are my rights as a consumer?

I received a defective product. What does consumer law say?

What is an unfair trade practice?

What is a deficient service?

What is a misleading advertisement?

What can a consumer do about a defective product?

What is the Consumer Protection Act, 2019?

What are Consumer Commissions?

Can a consumer make a complaint about an online purchase?
```

The system is designed to accept natural-language questions rather than requiring users to know the exact terminology used in legislation.

---

# ⚙️ Local Development

## 1. Clone the repository

```bash
git clone <repository-url>
cd legal
```

---

## 2. Set up the backend

```bash
cd backend
```

Create a Python virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 3. Configure environment variables

Create a `.env` file according to the project's configuration.

Example:

```env
SECRET_KEY=your_secret_key
DEBUG=True

AI_API_KEY=your_api_key

DATABASE_URL=your_database_url
```

**Never commit API keys, passwords, database credentials, or other secrets to the repository.**

---

## 4. Run migrations

```bash
python manage.py migrate
```

---

## 5. Start the backend

```bash
python manage.py runserver
```

The development server will normally be available at:

```text
http://127.0.0.1:8000/
```

---

## 6. Start the frontend

Open another terminal and navigate to the frontend directory.

Install the required dependencies and start the frontend using the commands defined by the frontend framework.

---

# 🧪 API Testing

The API can be tested locally using `curl`.

Example:

```bash
curl -X POST http://127.0.0.1:8000/api/ask/ \
  -H "Content-Type: application/json" \
  -d "{\"question\":\"What is product liability?\",\"language\":\"en\"}"
```

---

# 🌐 Deployment

The application consists of frontend and backend components that can be deployed independently.

### Frontend

The frontend can be deployed to a web-hosting platform such as Vercel.

### Backend

The Django backend requires a Python-compatible hosting environment.

All production API keys and configuration values should be stored using the deployment platform's environment-variable system rather than hard-coded into the source code.

---

# 👥 Team

- Bhoomika K B
- Irin Maria Varghese
- Ardhra K Manoj
- Athira K Jayan

---

# ⚠️ Disclaimer

This application provides general legal information for educational and informational purposes.

It does **not** constitute legal advice, establish an attorney-client relationship, or replace consultation with a qualified legal professional.

Users should independently verify important legal information and seek professional legal advice for specific legal situations.

---

## ⭐ Project Goal

> **Make legal information easier to access and understand through grounded AI.**

## 📚 Data Sources & Licensing

The Legal AI Assistant uses publicly available legal information as the knowledge base for its retrieval and answer-generation pipeline.

All data sources used by the project are documented below.



### Data Usage

- Only the documented sources listed above are used as part of the project's legal knowledge base.
- Source documents are processed for retrieval and contextual answering.
- Where applicable, the application provides references to the underlying legal source or section.
- The project does not claim ownership of the underlying legal texts unless explicitly stated by the applicable source.
- Users should refer to the original source for the authoritative version of any legal provision.

### Licensing and Terms of Use

Each source is subject to its respective license, copyright notice, and/or terms of use.

Before redistributing the dataset or source documents separately from this application, users should review the terms applicable to each source.

### Data Attribution

Where required by the source's license or terms of use, appropriate attribution is provided to the original publisher/source.

> **Important:** The legal information presented by this application is provided for informational and educational purposes. The application does not provide legal advice. Users should consult the original legal source and/or a qualified legal professional for matters requiring legal advice.
