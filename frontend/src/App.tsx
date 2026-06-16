import { NavLink, Navigate, Route, Routes } from "react-router-dom";

import { AdminPage } from "./pages/AdminPage";
import { AdminInterviewDetailsPage } from "./pages/AdminInterviewDetailsPage";
import { CandidateInterviewPage } from "./pages/CandidateInterviewPage";

function App() {
  return (
    <div className="app-shell">
      <header className="top-nav">
        <div className="top-nav-brand">
          <p className="top-nav-kicker">MVP Demo</p>
          <h1>AI Interviewer Chatbot</h1>
        </div>
        <nav className="top-nav-links">
          <NavLink
            to="/admin"
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            Admin
          </NavLink>
          <NavLink
            to="/admin/interviews"
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
          >
            Interview Details
          </NavLink>
        </nav>
      </header>

      <main className="page-content">
        <Routes>
          <Route path="/" element={<Navigate to="/admin" replace />} />
          <Route path="/admin" element={<AdminPage />} />
          <Route path="/admin/interviews" element={<AdminInterviewDetailsPage />} />
          <Route
            path="/admin/interviews/:id"
            element={<AdminInterviewDetailsPage />}
          />
          <Route path="/interview" element={<CandidateInterviewPage />} />
          <Route path="/interview/:id" element={<CandidateInterviewPage />} />
        </Routes>
      </main>
    </div>
  );
}

export default App;
