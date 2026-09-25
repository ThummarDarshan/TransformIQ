import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import ReactFlow, {
  Node,
  Edge,
  Controls,
  Background,
  applyNodeChanges,
  applyEdgeChanges,
  NodeChange,
  EdgeChange,
  Connection,
  addEdge,
  MarkerType,
  Handle,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  Cpu,
  Save,
  RefreshCw,
  ArrowRight,
  ShieldCheck,
  Layers,
  Database,
  Globe,
  Sparkles,
  Info,
  Server,
  Network
} from 'lucide-react';
import api from '../services/api';
import { ArchitectureData } from '../types';
import { LoadingScreen } from '../components/common/LoadingScreen';

// Custom Card Node for React Flow
const CustomArchitectureNode = ({ data }: any) => {
  const layerColors: Record<string, { border: string; bg: string; text: string; badge: string }> = {
    Client: { border: 'border-blue-500/50', bg: 'bg-blue-950/80', text: 'text-blue-300', badge: 'bg-blue-500/20 text-blue-300' },
    API_Gateway: { border: 'border-amber-500/50', bg: 'bg-amber-950/80', text: 'text-amber-300', badge: 'bg-amber-500/20 text-amber-300' },
    Application_Services: { border: 'border-emerald-500/50', bg: 'bg-emerald-950/80', text: 'text-emerald-300', badge: 'bg-emerald-500/20 text-emerald-300' },
    AI_Engine: { border: 'border-purple-500/50', bg: 'bg-purple-950/80', text: 'text-purple-300', badge: 'bg-purple-500/20 text-purple-300' },
    Data_Storage: { border: 'border-cyan-500/50', bg: 'bg-cyan-950/80', text: 'text-cyan-300', badge: 'bg-cyan-500/20 text-cyan-300' },
    External_Integrations: { border: 'border-rose-500/50', bg: 'bg-rose-950/80', text: 'text-rose-300', badge: 'bg-rose-500/20 text-rose-300' },
  };

  const styleClass = layerColors[data.layer] || { border: 'border-slate-700', bg: 'bg-slate-900', text: 'text-slate-300', badge: 'bg-slate-800 text-slate-300' };

  return (
    <div className={`p-4 rounded-2xl border ${styleClass.border} ${styleClass.bg} shadow-2xl backdrop-blur-md w-64 text-left transition-all hover:scale-105 hover:shadow-blue-500/10`}>
      <Handle type="target" position={Position.Top} className="w-2.5 h-2.5 bg-blue-500 border-2 border-slate-900" />
      <div className="flex items-center justify-between mb-1.5">
        <span className={`text-[9px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full ${styleClass.badge}`}>
          {data.layer?.replace('_', ' ')}
        </span>
        <span className="text-[10px] font-mono text-slate-400 font-semibold">{data.tech_stack?.split(',')[0]}</span>
      </div>
      <h4 className="text-xs font-bold text-white mb-1 leading-snug">{data.name}</h4>
      <p className="text-[10px] text-slate-300 line-clamp-2 leading-relaxed mb-2">{data.description}</p>
      {data.responsibilities && (
        <div className="pt-1.5 border-t border-slate-800 text-[9px] text-slate-400">
          • {data.responsibilities[0]}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} className="w-2.5 h-2.5 bg-blue-500 border-2 border-slate-900" />
    </div>
  );
};

const nodeTypes = {
  customArch: CustomArchitectureNode,
};

export const ArchitecturePage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const [archData, setArchData] = useState<ArchitectureData | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);

  const defaultArchNodes: Node[] = [
    {
      id: 'arch-1',
      type: 'customArch',
      position: { x: 280, y: 20 },
      data: {
        id: 'arch-1',
        name: 'Enterprise Client Portal & Mobile Apps',
        layer: 'Client',
        tech_stack: 'React, TypeScript, TailwindCSS, iOS/Android SDK',
        description: 'Customer touchpoints with secure TLS 1.3 channel and JWT session tokens.',
        responsibilities: ['User Authentication', 'Multilingual UI', 'Live Ticket Feedback']
      }
    },
    {
      id: 'arch-2',
      type: 'customArch',
      position: { x: 280, y: 150 },
      data: {
        id: 'arch-2',
        name: 'API Gateway & Rate Limiter',
        layer: 'API_Gateway',
        tech_stack: 'Kong / Envoy, OAuth2, Redis Token Bucket',
        description: 'Centralized edge routing, zero-trust token validation, and rate protection.',
        responsibilities: ['Auth Handshake', 'DDoS Mitigation', 'Telemetry Logging']
      }
    },
    {
      id: 'arch-3',
      type: 'customArch',
      position: { x: 60, y: 300 },
      data: {
        id: 'arch-3',
        name: 'TransformIQ Core Microservices',
        layer: 'Application_Services',
        tech_stack: 'FastAPI, Python 3.12, Celery Asynchronous Workers',
        description: 'Business orchestration, state machine transition, and RBAC authorization.',
        responsibilities: ['Business Workflow', 'Approval Flow', 'Audit Trail Generation']
      }
    },
    {
      id: 'arch-4',
      type: 'customArch',
      position: { x: 500, y: 300 },
      data: {
        id: 'arch-4',
        name: 'AI Agent & Semantic RAG Engine',
        layer: 'AI_Engine',
        tech_stack: 'Azure OpenAI GPT-4o, pgvector, LangChain Core',
        description: 'Natural language analysis, vector similarity lookup, and decision automation.',
        responsibilities: ['Intent Recognition', 'Context Retrieval', 'BPMN Logic Generation']
      }
    },
    {
      id: 'arch-5',
      type: 'customArch',
      position: { x: 280, y: 460 },
      data: {
        id: 'arch-5',
        name: 'PostgreSQL Relational DB & Vector Store',
        layer: 'Data_Storage',
        tech_stack: 'PostgreSQL 16, pgvector, Redis Cache',
        description: 'ACID-compliant enterprise storage with encrypted columns and embeddings.',
        responsibilities: ['Master Records', 'Audit Immutable Log', 'Vector Search Index']
      }
    }
  ];

  const defaultArchEdges: Edge[] = [
    { id: 'ae-1-2', source: 'arch-1', target: 'arch-2', label: 'HTTPS / WSS', animated: true, style: { stroke: '#3b82f6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' } },
    { id: 'ae-2-3', source: 'arch-2', target: 'arch-3', label: 'gRPC Internal', animated: true, style: { stroke: '#3b82f6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' } },
    { id: 'ae-2-4', source: 'arch-2', target: 'arch-4', label: 'Async Queue', animated: true, style: { stroke: '#8b5cf6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' } },
    { id: 'ae-3-5', source: 'arch-3', target: 'arch-5', label: 'SQL / AsyncPG', animated: true, style: { stroke: '#10b981', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' } },
    { id: 'ae-4-5', source: 'arch-4', target: 'arch-5', label: 'Vector KNN', animated: true, style: { stroke: '#06b6d4', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#06b6d4' } },
  ];

  const fetchData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const res: any = await api.get(`/architecture/project/${projectId}`);
      if (res.success && res.data) {
        setArchData(res.data);
        if (res.data.components && res.data.components.length > 0) {
          const rfNodes: Node[] = res.data.components.map((c: any) => ({
            id: c.id,
            type: 'customArch',
            position: { x: c.position_x || 100, y: c.position_y || 100 },
            data: { ...c },
          }));

          const rfEdges: Edge[] = (res.data.connections || []).map((cn: any, idx: number) => ({
            id: cn.id || `edge-${idx}`,
            source: cn.source,
            target: cn.target,
            label: cn.protocol,
            animated: cn.is_async,
            style: { stroke: '#3b82f6', strokeWidth: 2 },
            markerEnd: { type: MarkerType.ArrowClosed, color: '#3b82f6' },
          }));

          setNodes(rfNodes);
          setEdges(rfEdges);
        } else {
          setNodes(defaultArchNodes);
          setEdges(defaultArchEdges);
        }
      } else {
        setNodes(defaultArchNodes);
        setEdges(defaultArchEdges);
      }
    } catch (e) {
      console.error(e);
      setNodes(defaultArchNodes);
      setEdges(defaultArchEdges);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = async () => {
    if (!projectId) return;
    setIsRegenerating(true);
    try {
      const res: any = await api.post(`/architecture/project/${projectId}/generate`);
      if (res.success && res.data) {
        fetchData();
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsRegenerating(false);
    }
  };

  const onNodesChange = useCallback(
    (changes: NodeChange[]) => setNodes((nds) => applyNodeChanges(changes, nds)),
    []
  );
  const onEdgesChange = useCallback(
    (changes: EdgeChange[]) => setEdges((eds) => applyEdgeChanges(changes, eds)),
    []
  );
  const onConnect = useCallback(
    (params: Connection) => setEdges((eds) => addEdge(params, eds)),
    []
  );

  const onNodeClick = (_: any, node: Node) => {
    setSelectedNode(node.data);
  };

  const handleSaveLayout = async () => {
    if (!projectId) return;
    setIsSaving(true);
    try {
      const layoutPayload = nodes.map((n) => ({
        id: n.id,
        position: n.position,
      }));
      await api.post(`/architecture/project/${projectId}/save-layout`, layoutPayload);
    } catch (e) {
      console.error(e);
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [projectId]);

  if (isLoading) {
    return <LoadingScreen message="Synthesizing High-Level Architecture, Microservices, and Security Boundaries..." />;
  }

  const securityBoundaries = archData?.security_boundaries && archData.security_boundaries.length > 0
    ? archData.security_boundaries
    : [
        'TLS 1.3 In-Transit Encryption across all public endpoints',
        'AES-256 Column-Level Encryption for sensitive PII/payment data at rest',
        'Zero-Trust mTLS between Microservices and AI Inference Gateway',
        'Immutable Audit Trail stored with cryptographic hashes in Postgres'
      ];

  return (
    <div className="space-y-6 animate-fadeIn max-w-7xl mx-auto">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-blue-500/20 text-blue-300">
              STEP 05
            </span>
            <h1 className="text-2xl font-extrabold text-white">Solution Architecture (HLD)</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Interactive system topology, component boundaries, microservices, and zero-trust security postures.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleSaveLayout}
            disabled={isSaving}
            className="px-3 sm:px-3.5 py-1.5 sm:py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center space-x-1.5"
          >
            <Save className="w-3.5 h-3.5 text-emerald-400" />
            <span>{isSaving ? 'Saving...' : 'Save Layout'}</span>
          </button>
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="px-3 sm:px-3.5 py-1.5 sm:py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition flex items-center space-x-1.5"
          >
            <RefreshCw className={`w-3.5 h-3.5 text-blue-400 ${isRegenerating ? 'animate-spin' : ''}`} />
            <span>Regenerate</span>
          </button>
          <Link
            to={`/projects/${projectId}/process`}
            className="px-3.5 sm:px-4 py-1.5 sm:py-2 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-lg"
          >
            <span>Next: BPMN Process</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* REACT FLOW CANVAS CONTAINER */}
      <div className="h-[400px] sm:h-[520px] rounded-2xl border border-slate-800 bg-slate-950/90 overflow-hidden relative shadow-2xl">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onNodeClick={onNodeClick}
          nodeTypes={nodeTypes}
          fitView
          fitViewOptions={{ padding: 0.25, minZoom: 0.25, maxZoom: 1.1 }}
          minZoom={0.2}
          maxZoom={1.5}
        >
          <Background color="#1e293b" gap={20} />
          <Controls showInteractive={false} className="hidden xs:block" />
        </ReactFlow>

        <div className="absolute bottom-3 right-3 text-[10px] text-slate-400 bg-slate-900/80 border border-slate-800 px-2 py-1 rounded-lg backdrop-blur-xs pointer-events-none sm:hidden">
          Pinch / Drag to explore
        </div>

        {/* Selected Node Details Drawer */}
        {selectedNode && (
          <div className="absolute inset-x-3 bottom-3 sm:inset-x-auto sm:top-4 sm:right-4 sm:w-80 bg-slate-900/95 border border-slate-700 rounded-2xl p-4 shadow-2xl text-xs z-20 backdrop-blur-md animate-fadeIn max-h-[60%] overflow-y-auto">
            <div className="flex items-center justify-between mb-2">
              <span className="font-bold uppercase tracking-wider text-blue-400">{selectedNode.layer}</span>
              <button
                onClick={() => setSelectedNode(null)}
                className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-800 font-bold"
              >
                ✕
              </button>
            </div>
            <h4 className="text-sm font-bold text-white mb-1">{selectedNode.name}</h4>
            <p className="text-slate-300 mb-3">{selectedNode.description}</p>

            <div className="space-y-2 pt-2 border-t border-slate-800">
              <p><b className="text-slate-400">Tech Stack:</b> <span className="text-slate-200">{selectedNode.tech_stack}</span></p>
              <div>
                <b className="text-slate-400 block mb-1">Responsibilities:</b>
                <ul className="list-disc list-inside text-slate-300 space-y-0.5">
                  {selectedNode.responsibilities?.map((r: string, i: number) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* HLD DETAILS & SECURITY BOUNDARIES */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
          <h3 className="text-sm font-bold text-white flex items-center mb-3">
            <ShieldCheck className="w-4 h-4 text-emerald-400 mr-2" />
            Security Boundaries & Zero-Trust Posture
          </h3>
          <ul className="space-y-2 text-xs text-slate-300">
            {securityBoundaries.map((sb, idx) => (
              <li key={idx} className="flex items-start space-x-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 mt-1.5 shrink-0" />
                <span>{sb}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
          <h3 className="text-sm font-bold text-white flex items-center mb-3">
            <Layers className="w-4 h-4 text-blue-400 mr-2" />
            Data Flow Summary & Communication
          </h3>
          <p className="text-xs text-slate-300 leading-relaxed">
            {archData?.data_flow_summary || 'Event-driven architecture where client API calls are authenticated at the Gateway, routed to core microservices via gRPC, and processed with asynchronous Kafka events and semantic RAG vectors.'}
          </p>
          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-400">
            Deployment Model: <b className="text-slate-200">{archData?.deployment_model || 'Cloud-Native Hybrid (Kubernetes EKS + Azure OpenAI + Neon PostgreSQL)'}</b>
          </div>
        </div>
      </div>
    </div>
  );
};
