'use client';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, LineChart, Line, CartesianGrid } from 'recharts';
export function MetricsCharts({ records }: { records:any[] }) {
  const data = records.map(r=>({ name:`I${r.iteration}`, time: Number(r.metric?.elapsed_ms||0), reads: Number(r.metric?.disk_reads||0), cost: Number(r.metric?.plan_cost||0) }));
  return <div className="grid gap-4 lg:grid-cols-2">
    <div className="panel p-4"><h3 className="mb-3 text-sm font-bold">Execution time (ms)</h3><div className="h-64"><ResponsiveContainer><LineChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#1e293b"/><XAxis dataKey="name" stroke="#64748b"/><YAxis stroke="#64748b"/><Tooltip/><Line type="monotone" dataKey="time" strokeWidth={2}/></LineChart></ResponsiveContainer></div></div>
    <div className="panel p-4"><h3 className="mb-3 text-sm font-bold">Disk reads / estimated cost</h3><div className="h-64"><ResponsiveContainer><BarChart data={data}><CartesianGrid strokeDasharray="3 3" stroke="#1e293b"/><XAxis dataKey="name" stroke="#64748b"/><YAxis stroke="#64748b"/><Tooltip/><Bar dataKey="reads"/><Bar dataKey="cost"/></BarChart></ResponsiveContainer></div></div>
  </div>
}
