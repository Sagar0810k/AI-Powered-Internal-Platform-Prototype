import { useCallback, useEffect, useState } from 'react';
import { api, getToken, setToken, type Stats } from './api';
import Login from './components/Login';
import StatsCard from './components/StatsCard';
import AgentConsole from './components/AgentConsole';
import ApprovalQueue from './components/ApprovalQueue';
import AuditTrail from './components/AuditTrail';

export default function App() {
  const [token, setTokenState] = useState<string | null>(getToken());
  const [stats, setStats] = useState<Stats | null>(null);

  const refreshStats = useCallback(async () => {
    try {
      const s = await api.stats();
      setStats(s);
    } catch {
      setStats(null);
    }
  }, []);

  useEffect(() => {
    if (token) {
      void refreshStats();
    }
  }, [token, refreshStats]);

  function handleLogin(nextToken: string) {
    setTokenState(nextToken);
  }

  function handleLogout() {
    setToken(null);
    setTokenState(null);
  }

  if (!token) {
    return (
      <main id="main" className="container">
        <a className="skip-link" href="#main">
          Skip to content
        </a>
        <Login onLogin={handleLogin} />
      </main>
    );
  }

  return (
    <main id="main" className="container">
      <a className="skip-link" href="#main">
        Skip to content
      </a>
      <header className="app-header">
        <div>
          <h1>AI-Powered Internal Platform Prototype</h1>
          <p>Agentic approval workflow demo</p>
        </div>
        <button type="button" className="btn-secondary" onClick={handleLogout}>
          Log out
        </button>
      </header>

      <StatsCard stats={stats} onStatsChange={setStats} />
      <AgentConsole onCreated={() => void refreshStats()} />
      <ApprovalQueue onChanged={() => void refreshStats()} />
      <AuditTrail />

      <footer>
        <p className="hint">Prototype: LLM agent proposals require human approval before execution.</p>
      </footer>
    </main>
  );
}
