'use client';
import { useEffect, useMemo, useState } from 'react';
import { Activity, BrainCircuit, Gauge, Play, Sparkles, Square, Zap } from 'lucide-react';
import ConnectionPanel, { Connection } from './ConnectionPanel';
import QueryEditor from './QueryEditor';
import { DiffEditor } from '@monaco-editor/react';
import { MetricsCharts } from './Charts';
import { apiUrl, post } from '../lib/api';

const demo = `SELECT c.id, c.name, COUNT(o.id) AS order_count\nFROM customers c\nJOIN orders o ON o.customer_id = c.id\nWHERE date(o.created_at) >= date('now', '-90 day')\n  AND c.status = 'active'\nGROUP BY c.id, c.name\nORDER BY order_count DESC;`;

export default function Dashboard() {
  const [conn, setConn] = useState<Connection>({name:'Demo SQLite', db_type:'sqlite', database:'../data/demo.db'});
  const [sql, setSql] = useState(demo);
  const [job, setJob] = useState<any>(null);
  const [running, setRunning] = useState(false);
  const [iterations, setIterations] = useState(4);
  const [repeats, setRepeats] = useState(3);
  const [timeout, setTimeoutMs] = useState(5000);
  const [useLLM, setUseLLM] = useState(false);
  const [schema, setSchema] = useState<any>(null);
  const [schemaMsg, setSchemaMsg] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);

  const loadSchema = async()=>{ setSchemaMsg('Loading…'); try { const r=await post<any>('/api/connections/schema', conn); setSchema(r); setSchemaMsg(`${r.tables?.length||0} tables loaded`); } catch(e) { setSchemaMsg(String(e)); } };

  const start = async()=>{
    setRunning(true); setJob(null);
    try {
      const j = await post<any>('/api/optimize', {connection:conn, sql, iterations, repeats, timeout_ms:timeout, use_llm:useLLM});
      setJob(j);
      setJobId(j.job_id);
      const wsUrl = apiUrl(`/api/jobs/${j.job_id}/ws`).replace(/^http/,'ws');
      const ws = new WebSocket(wsUrl);
      ws.onmessage = e => { const ev=JSON.parse(e.data); if(ev.job) setJob(ev.job); if(ev.record) setJob((old:any)=>({...old, iterations:[...(old?.iterations||[]), ev.record], progress:ev.progress, learning:ev.learning})); if(ev.type==='completed'||ev.type==='final'||ev.type==='error'){ if(ev.job) setJob(ev.job); setRunning(false); ws.close(); } };
      ws.onerror = () => { setRunning(false); };
    } catch(e) { setJob({status:'failed', error:String(e)}); setRunning(false); }
  };

  const stop = async()=>{ if (!jobId) return; try { const cancelled = await post<any>(`/api/jobs/${jobId}/cancel`, {}); setJob(cancelled); } catch(e) { setJob((old:any)=>({...old, error:String(e)})); } };

  const records = useMemo(()=>[job?.baseline, ...(job?.iterations||[])].filter(Boolean), [job]);
  const best = job?.best;
  const improvement = best?.metric?.elapsed_ms && job?.baseline?.metric?.elapsed_ms ? ((1-best.metric.elapsed_ms/job.baseline.metric.elapsed_ms)*100) : 0;

  return <main className="min-h-screen">
    <header className="border-b border-slate-900 bg-slate-950/80 px-6 py-4 backdrop-blur"><div className="mx-auto flex max-w-[1500px] items-center justify-between"><div><div className="flex items-center gap-2"><Sparkles size={18}/><span className="font-black tracking-tight">SQL Optimizer Lab</span></div><p className="mt-1 text-xs text-slate-500">Iterative execution-plan analysis + learning-guided rewrites</p></div><div className="text-xs text-slate-500">Safety: SELECT-only • bounded timeout • rollback test runs</div></div></header>
    <div className="mx-auto grid max-w-[1500px] gap-4 p-4 lg:grid-cols-[310px_1fr]">
      <ConnectionPanel value={conn} onChange={setConn}/>
      <section className="space-y-4">
        <div className="panel p-4"><div className="mb-3 flex items-center justify-between"><div><h1 className="text-lg font-black">Optimization Workbench</h1><p className="text-sm muted">Paste a read-only query, connect a database, then run iterative candidates.</p></div><div><button className="button" onClick={start} disabled={running}><Play className="mr-2 inline" size={15}/>{running?'Optimizing…':'Optimize query'}</button>{running && <button className="ml-2 rounded-lg border border-red-700 px-4 py-2 text-sm font-bold text-red-300 hover:border-red-500" onClick={stop}><Square className="mr-2 inline" size={15}/>Stop</button>}<button className="ml-2 rounded-lg border border-slate-700 px-4 py-2 text-sm font-bold hover:border-cyan-500" onClick={loadSchema}>Load schema</button></div></div><QueryEditor sql={sql} setSql={setSql} dialect={conn.db_type}/></div>
        <div className="grid gap-4 md:grid-cols-4"><div className="panel p-4"><div className="label">Status</div><div className="text-xl font-black">{job?.status||'Idle'}</div><div className="mt-2 h-2 overflow-hidden rounded bg-slate-900"><div className="h-full bg-cyan-500" style={{width:`${job?.progress||0}%`}}/></div></div><div className="panel p-4"><div className="label">Baseline</div><div className="text-xl font-black">{job?.baseline?.metric?.elapsed_ms?.toFixed(1) || '—'} ms</div></div><div className="panel p-4"><div className="label">Best</div><div className="text-xl font-black">{best?.metric?.elapsed_ms?.toFixed(1) || '—'} ms</div></div><div className="panel p-4"><div className="label">Improvement</div><div className="text-xl font-black">{improvement.toFixed(1)}%</div></div></div>
        <div className="panel p-4"><div className="grid gap-3 md:grid-cols-4"><div><label className="label">Iterations</label><input className="input" type="number" min={1} max={5} value={iterations} onChange={e=>setIterations(+e.target.value)}/></div><div><label className="label">Runs / candidate</label><input className="input" type="number" min={1} max={5} value={repeats} onChange={e=>setRepeats(+e.target.value)}/></div><div><label className="label">Timeout ms</label><input className="input" type="number" min={250} max={15000} value={timeout} onChange={e=>setTimeoutMs(+e.target.value)}/></div><label className="flex items-end gap-2 pb-2 text-sm"><input type="checkbox" checked={useLLM} onChange={e=>setUseLLM(e.target.checked)}/> Optional LLM candidates</label></div></div>
        <MetricsCharts records={records}/>
        <div className="grid gap-4 xl:grid-cols-2"><div className="panel p-4"><div className="mb-3 flex items-center gap-2"><BrainCircuit size={17}/><h2 className="font-bold">Learning policy</h2></div><pre className="overflow-auto text-xs text-slate-400">{JSON.stringify(job?.learning||{}, null, 2)}</pre></div><div className="panel p-4"><div className="mb-3 flex items-center gap-2"><Gauge size={17}/><h2 className="font-bold">Index recommendations</h2></div>{(job?.index_recommendations||[]).map((x:string,i:number)=><div key={i} className="mb-2 rounded-lg border border-slate-800 p-3 text-sm text-slate-300">{x}</div>)}{!(job?.index_recommendations||[]).length && <p className="text-sm muted">Recommendations will appear after plan analysis.</p>}</div></div>
        <div className="panel p-4"><div className="mb-3 flex items-center gap-2"><Gauge size={17}/><h2 className="font-bold">Optimization checks</h2></div>{(job?.optimization_advisories||[]).map((x:string,i:number)=><div key={i} className="mb-2 rounded-lg border border-slate-800 p-3 text-sm text-slate-300">{x}</div>)}{!(job?.optimization_advisories||[]).length && <p className="text-sm muted">Query-shape checks will appear after optimization starts.</p>}</div>
        <div className="panel p-4"><div className="mb-3 flex items-center gap-2"><Zap size={17}/><h2 className="font-bold">Performance history</h2></div><div className="overflow-auto"><table className="w-full text-left text-xs"><thead><tr className="border-b border-slate-800 text-slate-500"><th className="p-2">Iteration</th><th>Operator</th><th>Time</th><th>Plan cost</th><th>Reward</th><th>Status</th></tr></thead><tbody>{records.map((r:any)=><tr className="border-b border-slate-900" key={r.candidate_id}><td className="p-2">{r.iteration}</td><td>{r.operator}</td><td>{r.metric?.elapsed_ms?.toFixed(1)||'—'} ms</td><td>{r.metric?.plan_cost??'—'}</td><td>{r.reward?.toFixed(2)||'—'}</td><td>{r.status}</td></tr>)}</tbody></table></div></div>
        {best && best.sql !== sql && <div className="panel p-4"><h2 className="mb-3 font-bold">Original vs. optimized SQL</h2><div className="h-[360px] overflow-hidden rounded-xl border border-slate-800"><DiffEditor theme="vs-dark" language="sql" original={sql} modified={best.sql} options={{readOnly:true,minimap:{enabled:false},automaticLayout:true,fontSize:12}} /></div><p className="mt-3 text-sm muted">{best.explanation}</p></div>}
        {schema && <div className="panel p-4"><h2 className="mb-2 font-bold">Schema snapshot</h2><p className="mb-3 text-xs text-slate-500">{schemaMsg}</p><pre className="max-h-72 overflow-auto text-xs text-slate-400">{JSON.stringify(schema, null, 2)}</pre></div>}
        {job?.error && <div className="panel border-red-900 p-4 text-sm text-red-300"><Activity className="mr-2 inline" size={15}/>{job.error}</div>}
      </section>
    </div>
  </main>
}
