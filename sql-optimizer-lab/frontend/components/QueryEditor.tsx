'use client';
import Editor from '@monaco-editor/react';
export default function QueryEditor({ sql, setSql, dialect }: { sql:string; setSql:(s:string)=>void; dialect:string }) {
  const language = dialect === 'postgresql' ? 'pgsql' : dialect === 'mssql' ? 'sql' : 'sql';
  return <div className="h-[420px] overflow-hidden rounded-xl border border-slate-800"><Editor theme="vs-dark" language={language} value={sql} onChange={v=>setSql(v||'')} options={{ minimap:{enabled:false}, fontSize:13, wordWrap:'on', automaticLayout:true, padding:{top:12} }}/></div>
}
