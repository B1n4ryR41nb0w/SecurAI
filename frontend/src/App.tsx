import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import ChatPage from "./pages/ChatPage"
import InsightsPage from "./pages/InsightsPage"
import HomePage from "./pages/Homepage"
import ReportPage from "./pages/ReportsPage"
import GitHubPage from "./pages/GithubPage"

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-background text-foreground">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/github-integration" element={<GitHubPage />} />
          <Route path="/report/:analysisId" element={<ReportPage />} />
          <Route path="/chat/:analysisId" element={<ChatPage />} />
          <Route path="/insights/:analysisId" element={<InsightsPage />} />
        </Routes>
      </div>
    </Router>
  )
}

export default App