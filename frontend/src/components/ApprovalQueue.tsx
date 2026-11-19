import { useEffect, useState } from 'react';
import type { Approval } from '../api';
import { api, getUserEmail, getUserRole } from '../api';

interface ApprovalQueueProps {
  onChanged: () => void;
}

export default function ApprovalQueue({ onChanged }: ApprovalQueueProps) {
  const [approvals, setApprovals] = useState<Approval[]>([]);
  const [error, setError] = useState<string | null>(null);
  const isAdmin = getUserRole() === 'admin';

  async function load() {
    try {
      const data = await api.listApprovals();
      setApprovals(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load approvals');
    }
  }

  useEffect(() => {
    void load();
  }, []);

  async function handleDecide(approval: Approval, action: 'approve' | 'reject') {
    const decidedBy = getUserEmail();
    try {
      if (action === 'approve') {
        await api.approve(approval.id, decidedBy);
      } else {
        await api.reject(approval.id, decidedBy);
      }
      await load();
      onChanged();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Decision failed');
    }
  }

  return (
    <section className="card" aria-labelledby="approvals-heading">
      <h2 id="approvals-heading">Approval queue</h2>
      {error ? <p className="error" role="alert">{error}</p> : null}
      {approvals.length === 0 ? <p>No approval requests yet. Run the agent to create one.</p> : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th scope="col">ID</th>
                <th scope="col">Status</th>
                <th scope="col">Agent</th>
                <th scope="col">Tool</th>
                <th scope="col">Created</th>
                <th scope="col">Decided</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              {approvals.map((a) => (
                <tr key={a.id}>
                  <td className="mono">{a.id}</td>
                  <td>{a.status}</td>
                  <td>{a.agent_name}</td>
                  <td className="mono">{a.tool_name}</td>
                  <td className="mono">{a.created_at}</td>
                  <td className="mono">{a.decided_at ?? '—'}</td>
                  <td>
                    {isAdmin ? (
                      <span className="row">
                        <button type="button" onClick={() => void handleDecide(a, 'approve')}>Approve</button>
                        <button type="button" className="btn-danger" onClick={() => void handleDecide(a, 'reject')}>Reject</button>
                      </span>
                    ) : (
                      <span className="hint">Read-only (viewer)</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
