import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Code2,
  Lock,
  ArrowRight,
  RefreshCw,
  Copy,
  Check,
  Send,
  Layers,
  Sparkles
} from 'lucide-react';
import api from '../services/api';
import { ApiCatalogData, ApiEndpoint } from '../types';
import { LoadingScreen } from '../components/common/LoadingScreen';

export const ApisPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const [data, setData] = useState<ApiCatalogData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [selectedEndpoint, setSelectedEndpoint] = useState<ApiEndpoint | null>(null);
  const [copied, setCopied] = useState(false);

  const fetchData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const res: any = await api.get(`/apis/project/${projectId}`);
      if (res.success && res.data) {
        setData(res.data);
        if (res.data.endpoints.length > 0) {
          setSelectedEndpoint(res.data.endpoints[0]);
        }
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
      const res: any = await api.post(`/apis/project/${projectId}/generate`);
      if (res.success && res.data) {
        setData(res.data);
        if (res.data.endpoints.length > 0) {
          setSelectedEndpoint(res.data.endpoints[0]);
        }
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsRegenerating(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

  if (isLoading) {
    return <LoadingScreen message="Generating OpenAPI 3.0 REST endpoint specifications..." />;
  }

  const methodColors: Record<string, string> = {
    GET: 'bg-blue-500/20 text-blue-300 border-blue-500/30',
    POST: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30',
    PUT: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
    DELETE: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300">
              STEP 08
            </span>
            <h1 className="text-2xl font-extrabold text-white">REST API & Integration Designer</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            OpenAPI 3.0 compliant endpoints, payload contracts, authentication, and error handling.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="px-3 py-1.5 sm:px-3.5 sm:py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center space-x-2"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-blue-400 ${isRegenerating ? 'animate-spin' : ''}`} />
            <span>{isRegenerating ? 'Designing...' : 'Regenerate'}</span>
          </button>
          <Link
            to={`/projects/${projectId}/ux`}
            className="px-3.5 py-1.5 sm:px-4 sm:py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-lg"
          >
            <span>Next: UX Wireframes</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* MASTER-DETAIL API CATALOG */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Endpoints List */}
        <div className="space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
            Available Endpoints ({data?.endpoints.length})
          </h3>

          <div className="space-y-2">
            {data?.endpoints.map((ep) => {
              const isSelected = selectedEndpoint?.path === ep.path && selectedEndpoint?.method === ep.method;
              return (
                <div
                  key={`${ep.method}-${ep.path}`}
                  onClick={() => setSelectedEndpoint(ep)}
                  className={`p-3.5 rounded-xl border cursor-pointer transition ${
                    isSelected
                      ? 'bg-slate-800 border-blue-500 text-white shadow-lg'
                      : 'bg-slate-900/60 border-slate-800 text-slate-300 hover:border-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1.5 font-mono">
                    <span
                      className={`text-[10px] font-bold px-2 py-0.5 rounded border ${
                        methodColors[ep.method] || 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {ep.method}
                    </span>
                    <span className="text-[10px] text-slate-400">{ep.category}</span>
                  </div>
                  <h4 className="text-xs font-bold font-mono truncate">{ep.path}</h4>
                  <p className="text-[11px] text-slate-400 mt-1 truncate">{ep.summary}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Selected Endpoint Contract Viewer */}
        <div className="lg:col-span-2 p-4 sm:p-6 rounded-2xl bg-slate-900/80 border border-slate-800 backdrop-blur-md">
          {selectedEndpoint ? (
            <div className="space-y-4 sm:space-y-6">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800 gap-3">
                <div className="min-w-0">
                  <div className="flex flex-wrap items-center gap-2 font-mono mb-1">
                    <span
                      className={`text-xs font-bold px-2.5 py-1 rounded border shrink-0 ${
                        methodColors[selectedEndpoint.method] || 'bg-slate-800 text-slate-300'
                      }`}
                    >
                      {selectedEndpoint.method}
                    </span>
                    <h3 className="text-sm font-bold text-white break-all">{selectedEndpoint.path}</h3>
                  </div>
                  <p className="text-xs text-slate-300">{selectedEndpoint.summary}</p>
                </div>
                {selectedEndpoint.auth_required && (
                  <span className="flex items-center text-xs font-semibold px-2.5 py-1 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 w-fit shrink-0">
                    <Lock className="w-3.5 h-3.5 mr-1" />
                    Bearer JWT
                  </span>
                )}
              </div>

              <p className="text-xs text-slate-400 leading-relaxed">{selectedEndpoint.description}</p>

              {/* Request Payload */}
              {selectedEndpoint.request_body && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Request Body (JSON)
                  </h4>
                  <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-blue-300 overflow-x-auto">
                    {JSON.stringify(selectedEndpoint.request_body, null, 2)}
                  </pre>
                </div>
              )}

              {/* Response Payload */}
              {selectedEndpoint.response_body && (
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Success Response (200 OK)
                  </h4>
                  <pre className="p-4 rounded-xl bg-slate-950 border border-slate-800 text-xs font-mono text-emerald-300 overflow-x-auto">
                    {JSON.stringify(selectedEndpoint.response_body, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-500 text-center py-12">Select an endpoint from the catalog</p>
          )}
        </div>
      </div>
    </div>
  );
};
