import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Database,
  Key,
  Code2,
  Copy,
  Check,
  RefreshCw,
  ArrowRight,
  Layers,
  Table as TableIcon
} from 'lucide-react';
import api from '../services/api';
import { DatabaseData } from '../types';
import { LoadingScreen } from '../components/common/LoadingScreen';

export const DatabasePage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const [data, setData] = useState<DatabaseData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [copied, setCopied] = useState(false);

  const fetchData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const res: any = await api.get(`/database/project/${projectId}`);
      if (res.success && res.data) {
        setData(res.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = async () => {
    if (!projectId) return;
    setIsRegenerating(true);
    try {
      const res: any = await api.post(`/database/project/${projectId}/generate`);
      if (res.success && res.data) {
        setData(res.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsRegenerating(false);
    }
  };

  const copyDdl = () => {
    if (data?.sql_ddl) {
      navigator.clipboard.writeText(data.sql_ddl);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

  if (isLoading) {
    return <LoadingScreen message="Designing relational database schema and vector embedding tables..." />;
  }

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300">
              STEP 07
            </span>
            <h1 className="text-2xl font-extrabold text-white">Database & Data Model Designer</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Normalized 3NF schema, primary/foreign key constraints, and SQL DDL code generation.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center space-x-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-cyan-400 ${isRegenerating ? 'animate-spin' : ''}`} />
            <span>{isRegenerating ? 'Designing...' : 'Regenerate'}</span>
          </button>
          <Link
            to={`/projects/${projectId}/apis`}
            className="px-3.5 py-1.5 sm:px-4 sm:py-2 rounded-xl bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-lg"
          >
            <span>Next: REST APIs</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* OVERVIEW BANNER */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs text-slate-300">
        <p>{data?.overview}</p>
      </div>

      {/* ENTITY TABLES GRID */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {data?.entities.map((entity, idx) => (
          <div key={idx} className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center space-x-2">
                <TableIcon className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-bold font-mono text-white">{entity.name}</h3>
              </div>
              <span className="text-[10px] uppercase font-bold text-slate-400 bg-slate-800 px-2 py-0.5 rounded">
                PostgreSQL Table
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-4">{entity.description}</p>

            {/* Field Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-500 uppercase text-[10px]">
                    <th className="pb-2">Field</th>
                    <th className="pb-2">Type</th>
                    <th className="pb-2">Attributes</th>
                    <th className="pb-2">Description</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {entity.fields.map((f, fIdx) => (
                    <tr key={fIdx} className="hover:bg-slate-800/30">
                      <td className="py-2 text-slate-200 flex items-center space-x-1">
                        {f.is_primary && <Key className="w-3 h-3 text-amber-400 inline" />}
                        <span>{f.name}</span>
                      </td>
                      <td className="py-2 text-cyan-400 text-[11px]">{f.type}</td>
                      <td className="py-2">
                        {f.is_primary && (
                          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-amber-500/20 text-amber-300">
                            PK
                          </span>
                        )}
                        {f.is_foreign && (
                          <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-300">
                            FK
                          </span>
                        )}
                      </td>
                      <td className="py-2 text-[10px] text-slate-400 font-sans">{f.description || '-'}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>

      {/* SQL DDL CODE PREVIEW */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-bold text-white flex items-center font-mono">
            <Code2 className="w-4 h-4 text-emerald-400 mr-2" />
            Generated SQL Schema DDL
          </h3>
          <button
            onClick={copyDdl}
            className="px-3 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-semibold flex items-center space-x-1.5 transition"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copied ? 'Copied' : 'Copy DDL'}</span>
          </button>
        </div>

        <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-300 overflow-x-auto">
          {data?.sql_ddl || '-- No SQL DDL available'}
        </pre>
      </div>
    </div>
  );
};
