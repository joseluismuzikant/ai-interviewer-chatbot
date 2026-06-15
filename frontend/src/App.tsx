import { Link, Navigate, Route, Routes } from "react-router-dom";

import { AdminPage } from "./pages/AdminPage";
import { AdminInterviewDetailsPage } from "./pages/AdminInterviewDetailsPage";
import { CandidateInterviewPage } from "./pages/CandidateInterviewPage";

function App() {
  return (
    <div className="app-shell">
      <header className="top-nav">
        <h1>AI Interviewer Chatbot</h1>
        <nav>
          <Link to="/admin">Admin</Link>
          <Link to="/admin/interviews">Interview Details</Link>
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
