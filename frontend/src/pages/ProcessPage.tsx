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
  MarkerType,
  Handle,
  Position
} from 'reactflow';
import 'reactflow/dist/style.css';
import {
  GitMerge,
  Clock,
  TrendingDown,
  Save,
  RefreshCw,
  ArrowRight,
  User,
  Bot,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Sparkles
} from 'lucide-react';
import api from '../services/api';
import { ProcessWorkflowData } from '../types';
import { LoadingScreen } from '../components/common/LoadingScreen';

// Custom Workflow Node for React Flow with connection handles
const CustomWorkflowNode = ({ data }: any) => {
  const typeIcons: Record<string, { border: string; bg: string; text: string; badge: string }> = {
    start: { border: 'border-emerald-500/50', bg: 'bg-emerald-950/80', text: 'text-emerald-300', badge: 'bg-emerald-500/20 text-emerald-300' },
    ai_task: { border: 'border-purple-500/50', bg: 'bg-purple-950/80', text: 'text-purple-300', badge: 'bg-purple-500/20 text-purple-300' },
    decision: { border: 'border-amber-500/50', bg: 'bg-amber-950/80', text: 'text-amber-300', badge: 'bg-amber-500/20 text-amber-300' },
    human_review: { border: 'border-rose-500/50', bg: 'bg-rose-950/80', text: 'text-rose-300', badge: 'bg-rose-500/20 text-rose-300' },
    task: { border: 'border-blue-500/50', bg: 'bg-blue-950/80', text: 'text-blue-300', badge: 'bg-blue-500/20 text-blue-300' },
    end: { border: 'border-slate-500/50', bg: 'bg-slate-900/90', text: 'text-slate-300', badge: 'bg-slate-800 text-slate-300' },
  };

  const styleClass = typeIcons[data.node_type] || { border: 'border-slate-700', bg: 'bg-slate-900', text: 'text-slate-300', badge: 'bg-slate-800 text-slate-300' };

  return (
    <div className={`p-4 rounded-2xl border ${styleClass.border} ${styleClass.bg} shadow-2xl backdrop-blur-md w-64 text-left transition-all hover:scale-105 hover:shadow-purple-500/10`}>
      <Handle type="target" position={Position.Top} className="w-2.5 h-2.5 bg-purple-500 border-2 border-slate-900" />
      <div className="flex items-center justify-between mb-1.5">
        <span className={`text-[9px] font-extrabold uppercase tracking-wider px-2 py-0.5 rounded-full ${styleClass.badge}`}>
          {data.node_type?.replace('_', ' ')}
        </span>
        <span className="text-[10px] font-mono text-slate-400 font-semibold">{data.actor}</span>
      </div>
      <h4 className="text-xs font-bold text-white mb-1 leading-snug">{data.label}</h4>
      <p className="text-[10px] text-slate-300 line-clamp-2 leading-relaxed">{data.description}</p>
      {data.swimlane && (
        <div className="mt-2.5 pt-1.5 border-t border-slate-800 text-[9px] text-slate-400 flex items-center justify-between">
          <span className="font-semibold">Lane: {data.swimlane}</span>
          {data.system && <span className="text-slate-400 font-mono">{data.system}</span>}
        </div>
      )}
      <Handle type="source" position={Position.Bottom} className="w-2.5 h-2.5 bg-purple-500 border-2 border-slate-900" />
    </div>
  );
};

const nodeTypes = {
  customWf: CustomWorkflowNode,
};

export const ProcessPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const [procData, setProcData] = useState<ProcessWorkflowData | null>(null);
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isRegenerating, setIsRegenerating] = useState(false);

  const defaultNodes: Node[] = [
    {
      id: 'wf-1',
      type: 'customWf',
      position: { x: 280, y: 30 },
      data: {
        node_key: 'start',
        node_type: 'start',
        label: 'Complaint Intake & Ingestion',
        actor: 'Customer / Portal',
        system: 'Web / Mobile API',
        swimlane: 'Customer',
        description: 'Customer initiates complaint with multi-channel ticket payload.'
      }
    },
    {
      id: 'wf-2',
      type: 'customWf',
      position: { x: 280, y: 160 },
      data: {
        node_key: 'ai_triage',
        node_type: 'ai_task',
        label: 'AI Real-time Triage & Sentiment',
        actor: 'Azure OpenAI Engine',
        system: 'TransformIQ Intent Core',
        swimlane: 'AI Automation',
        description: 'Classifies issue category, extracts urgency, and detects sentiment score.'
      }
    },
    {
      id: 'wf-3',
      type: 'customWf',
      position: { x: 280, y: 290 },
      data: {
        node_key: 'decision_complexity',
        node_type: 'decision',
        label: 'High Urgency or Complex Escalation?',
        actor: 'Rule Engine',
        system: 'Decision Tree Logic',
        swimlane: 'AI Automation',
        description: 'Determines whether automated resolution is confident or human escalation is required.'
      }
    },
    {
      id: 'wf-4',
      type: 'customWf',
      position: { x: 60, y: 420 },
      data: {
        node_key: 'auto_resolution',
        node_type: 'ai_task',
        label: 'Automated Diagnostic & Resolution',
        actor: 'AI Solution Agent',
        system: 'Self-Service API',
        swimlane: 'AI Automation',
        description: 'Executes automated refund or troubleshooting workflow.'
      }
    },
    {
      id: 'wf-5',
      type: 'customWf',
      position: { x: 480, y: 420 },
      data: {
        node_key: 'human_review',
        node_type: 'human_review',
        label: 'Tier-2 Expert Investigation',
        actor: 'Support Specialist',
        system: 'Support Workspace',
        swimlane: 'Human Operations',
        description: 'Specialist reviews AI recommendation and executes exception override.'
      }
    },
    {
      id: 'wf-6',
      type: 'customWf',
      position: { x: 280, y: 550 },
      data: {
        node_key: 'end',
        node_type: 'end',
        label: 'Resolution Closed & Logged to ERP',
        actor: 'System Integration',
        system: 'PostgreSQL + Kafka',
        swimlane: 'Core Backend',
        description: 'Updates CRM ticket, notifies customer, and logs audit analytics.'
      }
    }
  ];

  const defaultEdges: Edge[] = [
    { id: 'e1-2', source: 'wf-1', target: 'wf-2', animated: true, style: { stroke: '#8b5cf6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' } },
    { id: 'e2-3', source: 'wf-2', target: 'wf-3', animated: true, style: { stroke: '#8b5cf6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' } },
    { id: 'e3-4', source: 'wf-3', target: 'wf-4', label: 'Standard (<$500)', animated: true, style: { stroke: '#10b981', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#10b981' } },
    { id: 'e3-5', source: 'wf-3', target: 'wf-5', label: 'High Urgency / Complex', animated: true, style: { stroke: '#f59e0b', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#f59e0b' } },
    { id: 'e4-6', source: 'wf-4', target: 'wf-6', animated: true, style: { stroke: '#8b5cf6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' } },
    { id: 'e5-6', source: 'wf-5', target: 'wf-6', animated: true, style: { stroke: '#8b5cf6', strokeWidth: 2 }, markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' } },
  ];

  const fetchData = async () => {
    if (!projectId) return;
    setIsLoading(true);
    try {
      const res: any = await api.get(`/processes/project/${projectId}`);
      if (res.success && res.data) {
        setProcData(res.data);
        if (res.data.nodes && res.data.nodes.length > 0) {
          const rfNodes: Node[] = res.data.nodes.map((n: any) => ({
            id: n.id || n.node_key,
            type: 'customWf',
            position: { x: n.position_x || 100, y: n.position_y || 100 },
            data: { ...n },
          }));

          const rfEdges: Edge[] = res.data.edges.map((e: any, idx: number) => ({
            id: e.id || `wf-edge-${idx}`,
            source: e.source,
            target: e.target,
            label: e.label,
            animated: true,
            style: { stroke: '#8b5cf6', strokeWidth: 2 },
            markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' },
          }));

          setNodes(rfNodes);
          setEdges(rfEdges);
        } else {
          setNodes(defaultNodes);
          setEdges(defaultEdges);
        }
      } else {
        setNodes(defaultNodes);
        setEdges(defaultEdges);
      }
    } catch (e) {
      console.error(e);
      setNodes(defaultNodes);
      setEdges(defaultEdges);
    } finally {
      setIsLoading(false);
    }
  };

  const handleRegenerate = async () => {
    if (!projectId) return;
    setIsRegenerating(true);
    try {
      const res: any = await api.post(`/processes/project/${projectId}/generate`);
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

  const handleSaveLayout = async () => {
    if (!projectId) return;
    setIsSaving(true);
    try {
      const layoutPayload = nodes.map((n) => ({
        id: n.id,
        position: n.position,
      }));
      await api.post(`/processes/project/${projectId}/save-layout`, layoutPayload);
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
    return <LoadingScreen message="Designing BPMN workflow, decision trees, and swimlanes..." />;
  }

  const swimlanes = procData?.swimlanes && procData.swimlanes.length > 0
    ? procData.swimlanes
    : ['Customer / End User', 'AI Intent Triage & Classifier', 'Human Resolution Specialist', 'Enterprise Core API & DB'];

  return (
    <div className="space-y-6 animate-fadeIn max-w-7xl mx-auto">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">
              STEP 06
            </span>
            <h1 className="text-2xl font-extrabold text-white">Process Intelligence & BPMN Designer</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Automated workflow orchestration, swimlanes, and human-in-the-loop exception branches.
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
            <RefreshCw className={`w-3.5 h-3.5 text-purple-400 ${isRegenerating ? 'animate-spin' : ''}`} />
            <span>Regenerate</span>
          </button>
          <Link
            to={`/projects/${projectId}/database`}
            className="px-3.5 sm:px-4 py-1.5 sm:py-2 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-500 hover:to-blue-500 text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-lg"
          >
            <span>Next: Database & ER</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* LATENCY REDUCTION BANNER */}
      <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 sm:gap-4">
        <div className="flex items-center space-x-3">
          <div className="p-2.5 rounded-lg bg-purple-500/10 text-purple-400 shrink-0">
            <TrendingDown className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider">Process Efficiency Gain</h4>
            <p className="text-xs text-slate-300">
              Cycle Time reduced from <b className="text-rose-400">{procData?.cycle_time_current || '4.2 Days'}</b> to{' '}
              <b className="text-emerald-400">{procData?.cycle_time_projected || '18 Minutes'}</b>.
            </p>
          </div>
        </div>
        <span className="text-xs font-bold px-3 py-1.5 rounded-lg bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 shrink-0">
          ⚡ {procData?.efficiency_gain || '87.5% Efficiency Gain'}
        </span>
      </div>

      {/* REACT FLOW BPMN CANVAS */}
      <div className="h-[400px] sm:h-[520px] rounded-2xl border border-slate-800 bg-slate-950/90 overflow-hidden relative shadow-2xl">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
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
      </div>

      {/* SWIMLANES SUMMARY */}
      <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-md">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-bold text-white flex items-center space-x-2">
            <Layers className="w-4 h-4 text-purple-400" />
            <span>Orchestrated Swimlane Actors</span>
          </h3>
          <span className="text-[10px] text-slate-400 font-mono">{swimlanes.length} Active Lanes</span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
          {swimlanes.map((lane: string, idx: number) => {
            const icons = ['👤', '🤖', '🛡️', '🗄️'];
            const colors = ['border-blue-500/30 bg-blue-950/30 text-blue-300', 'border-purple-500/30 bg-purple-950/30 text-purple-300', 'border-amber-500/30 bg-amber-950/30 text-amber-300', 'border-emerald-500/30 bg-emerald-950/30 text-emerald-300'];
            return (
              <div
                key={idx}
                className={`p-3.5 rounded-xl border ${colors[idx % colors.length]} text-xs font-semibold flex items-center space-x-2.5 transition hover:scale-[1.02] shadow-sm`}
              >
                <span className="text-base">{icons[idx % icons.length]}</span>
                <span className="truncate">{lane}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
