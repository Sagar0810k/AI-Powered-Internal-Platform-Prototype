import { useState, type FormEvent } from 'react';
import { api, type AgentProposal } from '../api';

interface AgentConsoleProps {
  onCreated: () => void;
}

export default function AgentConsole({ onCreated }: AgentConsoleProps) {
  const [instruction, setInstruction] = useState('');
  const [proposals, setProposals] = useState<AgentProposal[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function handleRun(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const result = await api.runAgent('mock-agent-v1', instruction);
      setProposals(result);
      onCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Agent run failed');
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card" aria-labelledby="agent-heading">
      <h2 id="agent-heading">Ask the agent</h2>
      <form onSubmit={handleRun}>
        <div>
          <label htmlFor="instruction">Instruction for the agent</label>
          <textarea
            id="instruction"
            value={instruction}
            onChange={(e) => setInstruction(e.target.value)}
            required
            maxLength={500}
          />
        </div>
        <p className="hint">Max 500 characters. The mock agent maps the instruction to tool proposals.</p>
        <button type="submit" disabled={busy || instruction.trim().length === 0}>
          {busy ? 'Running…' : 'Run agent'}
        </button>
      </form>
      {error ? <p className="error" role="alert">{error}</p> : null}
      {proposals ? (
        <div>
          <h3>Proposals</h3>
          <ul>
            {proposals.map((p) => (
              <li key={p.approval_id}>
                <span className="mono">{p.tool_name}</span> — {p.rationale}
              </li>
            ))}
          </ul>
        </div>
      ) : null}
    </section>
  );
}
