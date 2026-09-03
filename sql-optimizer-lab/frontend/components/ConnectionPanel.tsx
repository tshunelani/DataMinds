'use client';
import { useState } from 'react';
import { Database, CheckCircle2 } from 'lucide-react';
import { post } from '../lib/api';

export type Connection = {
  name: string; db_type: 'sqlite'|'postgresql'|'mysql'|'mssql'; host?: string; port?: number; user?: string; password?: string; database: string; ssl_mode?: string;
};

export default function ConnectionPanel({ value, onChange }: { value: Connection; onChange: (v: Connection)=>void }) {
  const [message, setMessage] = useState('');
  const test = async () => { setMessage('Testing…'); try { await post('/api/connections/test', value); setMessage('Connection OK'); } catch(e) { setMessage(String(e)); } };
  const set = (k: keyof Connection, v: any) => onChange({...value, [k]: v});
  return <div className="panel p-4 space-y-3">
    <div className="flex items-center gap-2"><Database size={18}/><h2 className="font-bold">Database Connection</h2></div>
    <div><label className="label">Engine</label><select className="input" value={value.db_type} onChange={e=>set('db_type',e.target.value)}><option value="sqlite">SQLite</option><option value="postgresql">PostgreSQL</option><option value="mysql">MySQL</option><option value="mssql">SQL Server</option></select></div>
    <div><label className="label">Database / path</label><input className="input" value={value.database} onChange={e=>set('database',e.target.value)} /></div>
    {value.db_type !== 'sqlite' && <>
      <div className="grid grid-cols-2 gap-2"><div><label className="label">Host</label><input className="input" value={value.host||''} onChange={e=>set('host',e.target.value)}/></div><div><label className="label">Port</label><input className="input" type="number" value={value.port||''} onChange={e=>set('port',Number(e.target.value))}/></div></div>
      <div className="grid grid-cols-2 gap-2"><div><label className="label">User</label><input className="input" value={value.user||''} onChange={e=>set('user',e.target.value)}/></div><div><label className="label">Password</label><input className="input" type="password" value={value.password||''} onChange={e=>set('password',e.target.value)}/></div></div>
      <div><label className="label">SSL mode</label><input className="input" placeholder="require / verify-full" value={value.ssl_mode||''} onChange={e=>set('ssl_mode',e.target.value)}/></div>
    </>}
    <button className="button w-full" onClick={test}><CheckCircle2 className="mr-2 inline" size={15}/>Test connection</button>
    {message && <p className="text-xs text-slate-400">{message}</p>}
  </div>
}
