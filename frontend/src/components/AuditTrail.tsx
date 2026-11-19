import { useEffect, useState } from 'react';
import type { AuditEvent } from '../api';
import { api } from '../api';

export default function AuditTrail() {
  const [events, setEvents] = useState<AuditEvent[]>([]);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    try {
      const data = await api.listAudit();
      setEvents(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load audit trail');
    }
  }

  useEffect(() => {
    void load();
  }, []);

  return (
    <section className="card" aria-labelledby="audit-heading">
      <h2 id="audit-heading">Audit trail</h2>
      {error ? <p className="error" role="alert">{error}</p> : null}
      {events.length === 0 ? <p>No audit events yet.</p> : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th scope="col">Time</th>
                <th scope="col">Action</th>
                <th scope="col">Request</th>
                <th scope="col">Actor</th>
                <th scope="col">Detail</th>
              </tr>
            </thead>
            <tbody>
              {events.map((e) => (
                <tr key={e.id}>
                  <td className="mono">{e.timestamp}</td>
                  <td>{e.action}</td>
                  <td className="mono">{e.request_id}</td>
                  <td>{e.actor}</td>
                  <td className="mono">{e.detail}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
