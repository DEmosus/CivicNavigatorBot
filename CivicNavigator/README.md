
# CivicNavigator Frontend

A modern, responsive frontend for CivicNavigator, a civic engagement platform where residents can:
- Report incidents (e.g., road maintenance, waste management)
- Chat with a civic bot
- View and manage reported incidents (staff accounts)

---

## 🚀 Tech Stack

- **Framework**: React 19 + Vite
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Linting**: ESLint (`@typescript-eslint`), Prettier
- **State Management**: React Hooks

---

## 📂 Project Structure

```
src/
  components/     # UI components (forms, layout, etc.)
  pages/          # Page-level components (Home, Chat, Incidents)
  utils/          # API and auth helpers
  types/          # Shared TypeScript interfaces
  App.tsx         # Root component
  main.tsx        # Entry point
```

---

## 🔧 Setup

### 1. Install dependencies
```bash
npm install
```

### 2. Configure environment variables
Create `.env` in `frontend/`:
```
VITE_API_BASE_URL=http://127.0.0.1:8000
```

### 3. Start development server
```bash
npm run dev
```

---

## 📝 Key Components

- **IncidentForm.tsx** — Reports new incidents with validation and category dropdown.
- **RegisterForm.tsx** — Creates new user accounts.
- **LoginForm.tsx** — Authenticates users and stores JWT tokens.
- **CivicLayout.tsx** — Global layout with navigation.
- **utils/api.ts** — Axios instance and API helper functions.
- **utils/auth.ts** — Token storage and auth helpers.

---

## ✅ Lint & Format

```bash
npm run lint
npm run format
```

---

---

## tests

```bash
npx vitest run
```

---

## 🔌 API Integration

The frontend communicates with the backend via:
- **POST /api/auth/register** — User registration
- **POST /api/auth/login** — Login
- **POST /api/incidents** — Report incident
- **GET /api/staff/incidents** — Fetch all incidents (staff only)
- **POST /api/chat/message** — Chat with civic bot

---

## 📦 Build for Production

```bash
npm run build
```
The build output will be in `dist/`.

---

## 👥 Roles

- **Resident**: Can chat with bot, report incidents, track their status.
- **Staff**: Can manage incidents, respond to reports.
