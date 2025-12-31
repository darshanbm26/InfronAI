# 🚀 InfronAI - Google Cloud Sentinel

> AI-powered GCP infrastructure recommendations with 8-phase intelligent decision flow

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com)

## 📺 Demo Video

**[Watch Demo Video (3 min)](YOUR_YOUTUBE_OR_VIMEO_LINK_HERE)**

## 🌐 Live Demo

**[Try InfronAI Live](YOUR_HOSTED_PROJECT_URL_HERE)**

## 📦 Repository

**[GitHub Repository](https://github.com/YOUR_USERNAME/InfronAI)**

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [License](#license)

---

## 🎯 Overview

InfronAI (Google Cloud Sentinel) is an intelligent infrastructure recommendation system that helps developers and businesses optimize their Google Cloud Platform deployments. Using Google's Gemini AI, it provides personalized infrastructure recommendations through an 8-phase decision-making process.

### The Problem We Solve

- **Cost Optimization**: Prevent over-provisioning and reduce cloud spending by 30-50%
- **Architecture Decisions**: Get expert guidance on GCP service selection
- **Performance Tuning**: Balance cost, performance, and reliability
- **Learning System**: Continuously improves recommendations based on user feedback

### How It Works

1. **Phase 1: Intent Capture** - Tell us what you want to build
2. **Phase 2: Architecture Recommendation** - AI suggests optimal GCP services
3. **Phase 3: Machine Specification** - Detailed compute, storage, and network specs
4. **Phase 4: Pricing Calculation** - Real-time cost estimates
5. **Phase 5: Tradeoff Analysis** - Compare alternatives (cost vs performance)
6. **Phase 6: Presentation** - Clear, visual recommendations
7. **Phase 7: User Decision** - Accept, customize, or reject with reasons
8. **Phase 8: Learning Feedback** - System learns from your choices

---

## ✨ Features

### 🤖 AI-Powered Recommendations
- **Google Gemini Integration** - Leverages Gemini 2.0 Flash for intelligent analysis
- **Context-Aware** - Understands your workload requirements and constraints
- **Multi-Key Support** - Handles rate limits with automatic key rotation (4 API keys)

### 💰 Cost Optimization
- **Real-Time Pricing** - Live GCP pricing data via Cloud Billing API
- **Cost Comparisons** - Compare different configurations side-by-side
- **Budget Awareness** - Respects your cost constraints and suggests alternatives

### 📊 Comprehensive Analysis
- **Trade-off Analysis** - Cost vs Performance vs Reliability matrix
- **Alternative Suggestions** - Multiple viable infrastructure options
- **Risk Assessment** - Identify potential bottlenecks and issues

### 🔄 Continuous Learning
- **Feedback Loop** - Learns from user decisions and customizations
- **Pattern Recognition** - Identifies successful configurations
- **Improving Recommendations** - Gets smarter with every interaction

### 📈 Observability & Monitoring
- **Datadog Integration** - Full telemetry and APM monitoring
- **Custom Metrics** - Track recommendation quality and user satisfaction
- **Business Intelligence** - Dashboards for insights and analytics

### 🛠️ Production-Ready Outputs
- **Infrastructure as Code** - Generate Terraform configurations
- **Docker Support** - Containerized deployment guides
- **CI/CD Templates** - Ready-to-use deployment pipelines

---

## 🛠️ Tech Stack

### Frontend
- **Next.js 14** - React framework with App Router
- **TypeScript** - Type-safe development
- **Tailwind CSS** - Utility-first styling
- **React Components** - Modular, reusable UI for all 8 phases

### Backend
- **Python 3.9+** - Core language
- **FastAPI** - High-performance async API framework
- **Pydantic** - Data validation and settings management
- **Uvicorn** - Lightning-fast ASGI server

### AI & Cloud
- **Google Gemini 2.0 Flash** - AI model for recommendations
- **GCP Cloud Billing API** - Real-time pricing data
- **GCP Services** - Compute Engine, Cloud Run, Cloud Storage, Cloud SQL, etc.

### Monitoring & Observability
- **Datadog** - APM, metrics, logs, and events
- **Custom Telemetry** - Business event tracking across all phases

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (Next.js + TypeScript)           │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Phase 1  │→ │ Phase 2  │→ │ Phase 3  │→ │ Phase 4  │   │
│  │ Intent   │  │ Architect│  │  Specs   │  │ Pricing  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Phase 5  │→ │ Phase 6  │→ │ Phase 7  │→ │ Phase 8  │   │
│  │Tradeoffs │  │Recommend │  │ Decision │  │ Learning │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────┬───────────────────────────────────┘
                          │ REST API (JSON)
┌─────────────────────────▼───────────────────────────────────┐
│                Backend (FastAPI + Python)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Gemini     │  │  GCP Billing │  │   Datadog    │     │
│  │   Client     │  │  API Client  │  │  Telemetry   │     │
│  │ (Multi-Key)  │  │   (Pricing)  │  │   (APM)      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│  ┌──────────────────────────────────────────────────┐      │
│  │           8-Phase Processing Engine              │      │
│  │  Phase1→Phase2→Phase3→Phase4→Phase5→Phase6→      │      │
│  │         Phase7→Phase8→Generate Artifacts         │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ ([Download](https://nodejs.org/))
- **Python** 3.9+ ([Download](https://www.python.org/))
- **Git** ([Download](https://git-scm.com/))
- **GCP Account** with:
  - Gemini API access ([Get API Key](https://makersuite.google.com/app/apikey))
  - Service Account with Billing API access (optional)
- **Datadog Account** (optional for monitoring)

### Installation

#### 1️⃣ Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/InfronAI.git
cd InfronAI
```

#### 2️⃣ Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# Required: GEMINI_API_KEY (at minimum)
# Optional: GCP credentials, Datadog keys
```

**Minimum Required Configuration** (`.env`):
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.0-flash
```

#### 3️⃣ Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Create environment file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

#### 4️⃣ Run the Application

**Terminal 1 - Backend:**
```bash
cd backend
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

🎉 **Access the app at:** `http://localhost:3000`  
📚 **API docs at:** `http://localhost:8000/docs`

---

## 💡 Usage

### Quick Start Example

1. **Enter Your Intent** (Phase 1)
   ```
   "I need a web application for 10,000 daily users with a PostgreSQL database"
   ```

2. **Review AI Recommendations** (Phases 2-6)
   - **Architecture**: Cloud Run + Cloud SQL
   - **Specs**: 2 vCPU, 4GB RAM, 100GB SSD
   - **Estimated Cost**: $45-65/month
   - **Performance**: Medium-High tier

3. **Explore Tradeoffs** (Phase 5)
   - Compare: Cloud Run vs Compute Engine vs GKE
   - Cost/Performance matrix
   - Reliability and scalability impacts

4. **Make Decision** (Phase 7)
   - ✅ **Accept** → Download Terraform + Docker configs
   - ✏️ **Customize** → Adjust specs and regenerate
   - ❌ **Reject** → Provide feedback for better recommendations

5. **Deploy & Learn** (Phase 8)
   - Download generated infrastructure code
   - Follow deployment guide
   - System learns from your decision

---

## 📖 API Documentation

### Core Endpoints

#### `POST /api/phase1/capture-intent`
Capture user's infrastructure requirements

**Request:**
```json
{
  "user_input": "Web app for 10k daily users with database",
  "existing_infrastructure": null
}
```

#### `POST /api/analyze`
Run complete 8-phase analysis

**Request:**
```json
{
  "user_input": "E-commerce platform, 50k daily users",
  "budget_constraint": 500,
  "performance_priority": "balanced"
}
```

**Response:**
```json
{
  "session_id": "sess_abc123",
  "recommendations": [
    {
      "service": "Cloud Run",
      "specs": {"cpu": 4, "memory": "8Gi"},
      "cost_monthly": 120.50
    }
  ],
  "artifacts": {
    "terraform_config": "...",
    "docker_config": "..."
  }
}
```

🔗 **Full Interactive API Documentation:** Visit `http://localhost:8000/docs` when running

---

## 📁 Project Structure

```
InfronAI/
├── frontend/              # Next.js frontend application
│   ├── src/
│   │   ├── app/          # Next.js 14 app directory
│   │   │   ├── page.tsx  # Main page
│   │   │   └── layout.tsx
│   │   ├── components/   # React components
│   │   │   ├── Hero.tsx
│   │   │   ├── IntentCapture.tsx
│   │   │   ├── ResultsDisplay.tsx
│   │   │   └── phases/   # 8-phase UI components
│   │   │       ├── Phase1Intent.tsx
│   │   │       ├── Phase2Architecture.tsx
│   │   │       ├── Phase3Specification.tsx
│   │   │       ├── Phase4Pricing.tsx
│   │   │       ├── Phase5Tradeoffs.tsx
│   │   │       ├── Phase6Presentation.tsx
│   │   │       ├── Phase7Decision.tsx
│   │   │       └── Phase8Learning.tsx
│   │   └── types/        # TypeScript types
│   ├── package.json
│   └── tailwind.config.ts
│
├── backend/              # FastAPI backend
│   ├── src/
│   │   ├── api/         # API routes and models
│   │   │   ├── app.py   # Main FastAPI app
│   │   │   ├── models.py
│   │   │   └── routers/
│   │   │       └── analysis.py
│   │   ├── core/        # Core business logic
│   │   │   ├── gemini_client.py        # Gemini AI integration
│   │   │   ├── gcp_pricing_client.py   # GCP pricing API
│   │   │   └── catalog_manager.py      # Service catalog
│   │   ├── phases/      # 8-phase processors
│   │   │   ├── phase1_intent_capture.py
│   │   │   ├── phase2_architecture_sommelier.py
│   │   │   ├── phase3_machine_specification.py
│   │   │   ├── phase4_pricing_calculation.py
│   │   │   ├── phase5_tradeoff_analysis.py
│   │   │   ├── phase6_recommendation_presentation.py
│   │   │   ├── phase7_user_decision.py
│   │   │   └── phase8_learning_feedback.py
│   │   └── telemetry/   # Datadog integration
│   │       ├── datadog_client.py
│   │       ├── event_schemas.py
│   │       └── metrics_registry.py
│   ├── tests/           # Unit and integration tests
│   ├── requirements.txt # Python dependencies
│   ├── .env.example     # Environment template
│   └── docs/            # Detailed documentation
│
├── datadog-setup/        # Monitoring configuration
├── README.md            # This file
├── SETUP.md             # Detailed setup guide
└── LICENSE              # MIT License
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

This is an open-source project. You are free to use, modify, and distribute this software.

---

## 🙏 Acknowledgments

- **Google** for Gemini API and GCP Platform
- **Datadog** for observability and monitoring tools
- **FastAPI** and **Next.js** communities for excellent frameworks
- All open-source contributors and the developer community

---

## 🔗 Important Links

- 🌐 **Live Demo:** [YOUR_HOSTED_URL_HERE](YOUR_HOSTED_URL_HERE)
- 📺 **Demo Video (3 min):** [YouTube/Vimeo Link](YOUR_VIDEO_LINK_HERE)
- 💻 **GitHub Repository:** [github.com/YOUR_USERNAME/InfronAI](https://github.com/YOUR_USERNAME/InfronAI)
- 📚 **Documentation:** [/backend/docs](backend/docs)
- 📖 **API Docs:** `http://localhost:8000/docs` (when running locally)

---

<div align="center">

**Built for [Hackathon Name] 2026**

**⭐ Star this repo if you find it helpful!**

Made with ❤️ using Google Gemini AI

</div>
