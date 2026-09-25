import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  Sliders,
  TrendingUp,
  DollarSign,
  Clock,
  Zap,
  ShieldAlert,
  Sparkles,
  ArrowRight,
  RefreshCw,
  CheckCircle2
} from 'lucide-react';
import api from '../services/api';
import { SimulationResult } from '../types';

export const SimulationPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();

  // Slider inputs
  const [automationLevel, setAutomationLevel] = useState(75);
  const [teamSize, setTeamSize] = useState(6);
  const [budget, setBudget] = useState(150000);
  const [timeline, setTimeline] = useState(4);
  const [aiAdoption, setAiAdoption] = useState('HIGH');

  const [result, setResult] = useState<SimulationResult | null>(null);
  const [isSimulating, setIsSimulating] = useState(false);

  const runSimulation = async (
    auto = automationLevel,
    team = teamSize,
    bud = budget,
    time = timeline,
    ai = aiAdoption
  ) => {
    if (!projectId) return;
    setIsSimulating(true);
    try {
      const res: any = await api.post(`/simulations/project/${projectId}/run`, {
        automation_level: auto,
        team_size: team,
        budget: bud,
        timeline_months: time,
        ai_adoption_level: ai,
      });
      if (res.success && res.data) {
        setResult(res.data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsSimulating(false);
    }
  };

  useEffect(() => {
    runSimulation();
  }, [projectId]);

  // Debounced auto-simulation on slider change
  const handleSliderChange = (type: string, val: any) => {
    let newAuto = automationLevel;
    let newTeam = teamSize;
    let newBud = budget;
    let newTime = timeline;
    let newAi = aiAdoption;

    if (type === 'auto') {
      newAuto = Number(val);
      setAutomationLevel(newAuto);
    } else if (type === 'team') {
      newTeam = Number(val);
      setTeamSize(newTeam);
    } else if (type === 'budget') {
      newBud = Number(val);
      setBudget(newBud);
    } else if (type === 'timeline') {
      newTime = Number(val);
      setTimeline(newTime);
    } else if (type === 'ai') {
      newAi = val;
      setAiAdoption(newAi);
    }

    runSimulation(newAuto, newTeam, newBud, newTime, newAi);
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-7xl mx-auto">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <span className="text-xs font-mono font-bold px-2 py-0.5 rounded bg-amber-500/20 text-amber-300">
              STEP 11
            </span>
            <h1 className="text-2xl font-extrabold text-white">Dynamic What-If Simulator</h1>
          </div>
          <p className="text-xs text-slate-400 mt-1">
            Real-time parameter modeling for automation levels, team staffing, budgets, and projected ROI.
          </p>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            to={`/projects/${projectId}/score`}
            className="px-4 py-2 rounded-xl bg-gradient-to-r from-amber-600 to-blue-600 hover:from-amber-500 hover:to-blue-500 text-white text-xs font-bold transition flex items-center space-x-1.5 shadow-lg"
          >
            <span>Next: TransformIQ Score</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>

      {/* SIMULATOR TWO-COLUMN LAYOUT */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* LEFT COLUMN: INTERACTIVE SLIDERS */}
        <div className="lg:col-span-5 p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md space-y-6">
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-300 flex items-center">
            <Sliders className="w-4 h-4 text-amber-400 mr-2" /> Transformation Levers
          </h3>

          {/* Lever 1: Automation Level */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold text-slate-200">Automation Target Yield</label>
              <span className="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded">
                {automationLevel}% Straight-Through
              </span>
            </div>
            <input
              type="range"
              min="20"
              max="95"
              step="5"
              value={automationLevel}
              onChange={(e) => handleSliderChange('auto', e.target.value)}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>20% (Assisted)</span>
              <span>75% (Target)</span>
              <span>95% (Autonomous)</span>
            </div>
          </div>

          {/* Lever 2: Team Size */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold text-slate-200">Engineering Team Size</label>
              <span className="text-xs font-mono font-bold text-blue-400 bg-blue-500/10 px-2 py-0.5 rounded">
                {teamSize} Specialists
              </span>
            </div>
            <input
              type="range"
              min="2"
              max="15"
              step="1"
              value={teamSize}
              onChange={(e) => handleSliderChange('team', e.target.value)}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>2 Engineers</span>
              <span>6 (Balanced)</span>
              <span>15 (Fast-Track)</span>
            </div>
          </div>

          {/* Lever 3: Target Budget */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="text-xs font-bold text-slate-200">Allocated Budget Envelope</label>
              <span className="text-xs font-mono font-bold text-purple-400 bg-purple-500/10 px-2 py-0.5 rounded">
                ${budget.toLocaleString()}
              </span>
            </div>
            <input
              type="range"
              min="50000"
              max="350000"
              step="10000"
              value={budget}
              onChange={(e) => handleSliderChange('budget', e.target.value)}
              className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-500"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>$50,000</span>
              <span>$150,000</span>
              <span>$350,000</span>
            </div>
          </div>

          {/* Lever 4: AI Adoption Mode */}
          <div>
            <label className="block text-xs font-bold text-slate-200 mb-2">AI Adoption Aggressiveness</label>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
              {['LOW', 'MEDIUM', 'HIGH', 'AGGRESSIVE'].map((lvl) => (
                <button
                  key={lvl}
                  type="button"
                  onClick={() => handleSliderChange('ai', lvl)}
                  className={`py-1.5 rounded-lg text-[10px] font-bold transition ${
                    aiAdoption === lvl
                      ? 'bg-amber-600 text-white shadow'
                      : 'bg-slate-800 text-slate-400 hover:text-white'
                  }`}
                >
                  {lvl}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* RIGHT COLUMN: REAL-TIME SIMULATION TELEMETRY */}
        <div className="lg:col-span-7 space-y-6">
          {/* Projected KPI Cards */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Projected Effort</span>
              <h3 className="text-xl font-black text-white mt-1">{result?.projected_effort_hours || 1120} hrs</h3>
              <span className="text-[10px] text-slate-500">labor hours</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Projected Cost</span>
              <h3 className="text-xl font-black text-emerald-400 mt-1">${result?.projected_cost.toLocaleString() || '138,500'}</h3>
              <span className="text-[10px] text-slate-500">vs ${budget.toLocaleString()} budget</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Timeline</span>
              <h3 className="text-xl font-black text-blue-400 mt-1">{result?.projected_timeline_months || 4} Months</h3>
              <span className="text-[10px] text-slate-500">delivery duration</span>
            </div>

            <div className="p-4 rounded-xl bg-emerald-950/20 border border-emerald-500/30">
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400">Expected ROI</span>
              <h3 className="text-xl font-black text-emerald-400 mt-1">{result?.expected_roi_percentage || 340}%</h3>
              <span className="text-[10px] text-emerald-400/80">12-month net yield</span>
            </div>

            <div className="p-4 rounded-xl bg-purple-950/20 border border-purple-500/30">
              <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400">Efficiency Gain</span>
              <h3 className="text-xl font-black text-purple-400 mt-1">+{result?.efficiency_gain_percentage || 86}%</h3>
              <span className="text-[10px] text-purple-400/80">throughput increase</span>
            </div>

            <div className="p-4 rounded-xl bg-slate-900/60 border border-slate-800">
              <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Delivery Risk</span>
              <h3 className="text-sm font-bold text-amber-400 mt-2 truncate">{result?.risk_level || 'LOW'}</h3>
            </div>
          </div>

          {/* SIMULATION INSIGHTS */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md">
            <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center mb-3">
              <Sparkles className="w-4 h-4 text-amber-400 mr-2" /> AI Scenario Analysis & Insights
            </h4>
            <div className="space-y-2.5 text-xs text-slate-300">
              {result?.simulation_insights?.map((ins, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-slate-800/40 border border-slate-700/60 flex items-start space-x-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                  <span>{ins}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
