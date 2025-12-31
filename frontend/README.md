# InfronAI Frontend

AI-powered GCP architecture recommendation platform.

## Tech Stack

- **Next.js 14** (App Router)
- **TypeScript**
- **Tailwind CSS**
- **React 18**

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page
│   │   └── globals.css      # Global styles
│   └── components/
│       ├── Hero.tsx         # Hero section
│       ├── IntentCapture.tsx # Intent input form
│       └── PhaseOverview.tsx # Phase descriptions
├── package.json
├── tsconfig.json
├── tailwind.config.ts
└── next.config.js
```

## Features

- ✅ Single-page layout
- ✅ Hero section with value props
- ✅ Intent capture form with examples
- ✅ Phase overview (2-6)
- ✅ Responsive design
- ✅ Loading states
- ⏳ Backend integration (next step)

## Development

- No backend integration yet
- No state management (yet)
- Clean, minimal UI
- Production-ready structure
