# CampusShield Frontend — Setup Guide

## 📁 Project Structure

```
C:\campusshield\frontend\
├── index.html
├── package.json
├── vite.config.js
├── postcss.config.js
├── tailwind.config.js
└── src/
    ├── main.jsx
    ├── App.jsx
    ├── index.css
    ├── pages/
    │   ├── LandingPage.jsx      ← Hero page with floating 3D cards
    │   ├── AuthPage.jsx         ← Login + Register (glassmorphism)
    │   ├── Dashboard.jsx        ← Main dashboard with scan + results
    │   └── HistoryPage.jsx      ← Expandable scan history
    └── components/
        ├── ui/
        │   ├── Button.jsx       ← Reusable neon glow button
        │   ├── Card.jsx         ← 3D tilt glassmorphism card
        │   └── RiskMeter.jsx    ← Circular + bar risk meter
        └── layout/
            └── Navbar.jsx       ← Fixed top navigation bar
```

## 🚀 Installation Steps

### Step 1: Extract files to your project folder
Copy all files into:
```
C:\campusshield\frontend\
```

### Step 2: Install dependencies
Open terminal in `C:\campusshield\frontend\` and run:
```bash
npm install
```

### Step 3: Start dev server
```bash
npm run dev
```

Open your browser at: **http://localhost:3000**

---

## 🎨 Pages & Routes

| Route        | Page           | Description                          |
|--------------|----------------|--------------------------------------|
| `/`          | Landing Page   | Hero with floating cards, CTAs       |
| `/login`     | Auth Page      | Login/Register glassmorphism form    |
| `/dashboard` | Dashboard      | Stats, AI scan input, risk result    |
| `/history`   | History Page   | Expandable scan history with filters |

---

## 🎨 Design System

### Colors
- **Background**: `#0F172A`
- **Card**: `#1E293B` with glassmorphism
- **Accent Blue**: `#3B82F6`
- **High Risk**: `#EF4444` (red glow)
- **Suspicious**: `#F59E0B` (amber glow)
- **Safe**: `#10B981` (green glow)

### Components
- **Button**: Neon glow on hover, scale animation, loading state
- **Card**: 3D mouse tilt effect, glassmorphism, hover elevation
- **RiskMeter**: Animated circular ring with count-up, dynamic colors
- **RiskBar**: Animated progress bar with glow
- **Navbar**: Fixed, scroll-aware, active route indicator

---

## 📦 Tech Stack
- **React 18** — Functional components + hooks
- **Tailwind CSS 3** — Utility-first with custom extensions
- **Framer Motion 11** — All animations and transitions
- **React Router 6** — Client-side routing
- **Vite 5** — Lightning fast dev server + build
