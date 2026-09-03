const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
export const apiUrl = (path: string) => `${API}${path}`;

export async function post<T>(path: string, body: unknown): Promise<T> {
  const r = await fetch(apiUrl(path), { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
  if (!r.ok) throw new Error((await r.json().catch(()=>({detail:r.statusText}))).detail || r.statusText);
  return r.json();
}
