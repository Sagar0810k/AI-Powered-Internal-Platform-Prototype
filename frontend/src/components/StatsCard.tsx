import { useEffect } from 'react';
import { api, type Stats } from '../api';

interface StatsCardProps {
  stats: Stats | null;
  onStatsChange: (stats: Stats | null) => void;
}

export default function StatsCard({ stats, onStatsChange }: StatsCardProps) {
  useEffect(() => {
    let cancelled = false;
    api
      .stats()
      .then((s) => {
        if (!cancelled) onStatsChange(s);
      })
      .catch(() => {
        if (!cancelled) onStatsChange(null);
      });
    return () => {
      cancelled = true;
    };
  }, [onStatsChange]);

  return (
    <section className="card" aria-labelledby="stats-heading">
      <h2 id="stats-heading">Metrics summary</h2>
      {stats ? (
        <p>
          Total requests served: <strong>{stats.total_requests}</strong> &middot; Approved (executed):{' '}
          <strong>{stats.approved_count}</strong>
        </p>
      ) : (
        <p>Loading…</p>
      )}
    </section>
  );
}
