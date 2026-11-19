export interface Approval {
  id: number;
  agent_name: string;
  tool_name: string;
  tool_args: Record<string, unknown>;
  status: string;
  created_at: string;
  decided_at: string | null;
  decided_by: string | null;
}

export interface AuditEvent {
  id: number;
  request_id: number;
  action: string;
  actor: string;
  detail: string;
  timestamp: string;
}

export interface Stats {
  total_requests: number;
  approved_count: number;
}

export interface AgentProposal {
  approval_id: number;
  tool_name: string;
  tool_args: Record<string, unknown>;
  rationale: string;
}

const TOKEN_KEY = 'aip_token';

export function getToken(): string | null {
  try {
    return localStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string | null): void {
  try {
    if (token) localStorage.setItem(TOKEN_KEY, token);
    else localStorage.removeItem(TOKEN_KEY);
  } catch {
    /* ignore */
  }
}

interface TokenPayload {
  sub?: string;
  email?: string;
  role?: string;
}

function base64UrlDecode(input: string): string {
  const base64 = input.replace(/-/g, '+').replace(/_/g, '/');
  const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4);
  const json = decodeURIComponent(
    atob(padded)
      .split('')
      .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
      .join(''),
  );
  return json;
}

export function decodeToken(token: string): TokenPayload {
  const parts = token.split('.');
  if (parts.length < 2) return {};
  try {
    return JSON.parse(base64UrlDecode(parts[1])) as TokenPayload;
  } catch {
    return {};
  }
}

export function getUserEmail(): string {
  const payload = decodeToken(getToken() ?? '');
  return payload.sub ?? payload.email ?? '';
}

export function getUserRole(): string {
  const payload = decodeToken(getToken() ?? '');
  return payload.role ?? 'viewer';
}

async function request<T>(
  path: string,
  options: { method?: string; body?: unknown } = {},
): Promise<T> {
  const headers: Record<string, string> = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const res = await fetch(path, {
    method: options.method ?? 'GET',
    headers,
    body: options.body ? JSON.stringify(options.body) : undefined,
  });

  if (!res.ok) {
    const err = (await res.json().catch(() => ({}))) as { detail?: unknown };
    const message = typeof err.detail === 'string' ? err.detail : 'Request failed';
    throw new Error(message);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  login: (email: string, password: string) =>
    request<{ access_token: string }>('/auth/login', {
      method: 'POST',
      body: { email, password },
    }),

  register: (email: string, password: string) =>
    request<{ id: number; email: string; role: string }>('/auth/register', {
      method: 'POST',
      body: { email, password },
    }),

  runAgent: (agentName: string, instruction: string) =>
    request<AgentProposal[]>('/approvals/agent/run', {
      method: 'POST',
      body: { agent_name: agentName, instruction },
    }),

  listApprovals: () => request<Approval[]>('/approvals'),

  approve: (approvalId: number, decidedBy: string) =>
    request<Approval>(`/approvals/${approvalId}/approve`, {
      method: 'POST',
      body: { decided_by: decidedBy },
    }),

  reject: (approvalId: number, decidedBy: string) =>
    request<Approval>(`/approvals/${approvalId}/reject`, {
      method: 'POST',
      body: { decided_by: decidedBy },
    }),

  listAudit: () => request<AuditEvent[]>('/audit'),

  stats: () => request<Stats>('/stats'),
};
