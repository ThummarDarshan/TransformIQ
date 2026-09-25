import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import {
  Users,
  MessageSquare,
  History,
  ShieldCheck,
  Send,
  CheckCircle2,
  Clock,
  User as UserIcon,
  Sparkles
} from 'lucide-react';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export const CollaborationPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const { user } = useAuth();

  const [activeTab, setActiveTab] = useState<'comments' | 'versions' | 'audit'>('comments');
  const [comments, setComments] = useState<any[]>([]);
  const [versions, setVersions] = useState<any[]>([]);
  const [auditLogs, setAuditLogs] = useState<any[]>([]);
  const [newComment, setNewComment] = useState('');
  const [commentSection, setCommentSection] = useState('architecture');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const fetchCollaborationData = async () => {
    if (!projectId) return;
    try {
      const cRes: any = await api.get(`/collaboration/project/${projectId}/comments`);
      if (cRes.success && cRes.data) setComments(cRes.data);

      const vRes: any = await api.get(`/collaboration/project/${projectId}/versions`);
      if (vRes.success && vRes.data) setVersions(vRes.data);

      const aRes: any = await api.get(`/collaboration/project/${projectId}/audit-logs`);
      if (aRes.success && aRes.data) setAuditLogs(aRes.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchCollaborationData();
  }, [projectId]);

  const handlePostComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newComment.trim() || !projectId) return;
    setIsSubmitting(true);
    try {
      const res: any = await api.post(`/collaboration/project/${projectId}/comments`, {
        section: commentSection,
        content: newComment,
        mentions: ['@LeadArchitect']
      });
      if (res.success && res.data) {
        setComments((prev) => [res.data, ...prev]);
        setNewComment('');
      }
    } catch (e) {
      console.error(e);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-5xl mx-auto">
      {/* HEADER */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-slate-800">
        <div>
          <h1 className="text-2xl font-extrabold text-white">Collaboration, Versioning & Audit Logs</h1>
          <p className="text-xs text-slate-400 mt-1">
            Enterprise team feedback, immutable artifact snapshots, and security audit trails.
          </p>
        </div>

        {/* Tab Controls */}
        <div className="flex flex-wrap items-center gap-1.5 bg-slate-900 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setActiveTab('comments')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
              activeTab === 'comments' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            <MessageSquare className="w-3.5 h-3.5" />
            <span>Comments</span>
          </button>
          <button
            onClick={() => setActiveTab('versions')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
              activeTab === 'versions' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>Version History</span>
          </button>
          <button
            onClick={() => setActiveTab('audit')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1.5 transition ${
              activeTab === 'audit' ? 'bg-blue-600 text-white shadow' : 'text-slate-400 hover:text-white'
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Audit Trail</span>
          </button>
        </div>
      </div>

      {/* TAB CONTENT: COMMENTS */}
      {activeTab === 'comments' && (
        <div className="space-y-6">
          {/* Post Comment Form */}
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 backdrop-blur-md">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 mb-3 flex items-center">
              <MessageSquare className="w-4 h-4 text-blue-400 mr-2" /> Add Reviewer Feedback
            </h3>

            <form onSubmit={handlePostComment} className="space-y-3">
              <div className="flex items-center space-x-3">
                <select
                  value={commentSection}
                  onChange={(e) => setCommentSection(e.target.value)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none"
                >
                  <option value="architecture">Architecture Section</option>
                  <option value="gaps">Gap Analysis</option>
                  <option value="recommendations">AI Recommendations</option>
                  <option value="database">Database Schema</option>
                  <option value="blueprint">Master Blueprint</option>
                </select>
                <span className="text-[11px] text-slate-500">Tagging: @LeadArchitect @ProjectManager</span>
              </div>

              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  required
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Type your technical review note or sign-off comment..."
                  className="flex-1 px-4 py-2.5 bg-slate-950 border border-slate-700 rounded-xl text-xs text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition shadow-lg disabled:opacity-50"
                >
                  Post
                </button>
              </div>
            </form>
          </div>

          {/* Comments List */}
          <div className="space-y-3">
            {comments.map((c) => (
              <div key={c.id} className="p-4 rounded-xl bg-slate-900/60 border border-slate-800 text-xs">
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <span className="font-bold text-white">{c.author_name}</span>
                    <span className="text-[10px] px-2 py-0.5 rounded bg-blue-500/20 text-blue-300 font-mono">
                      {c.section}
                    </span>
                  </div>
                  <span className="text-[10px] text-slate-500">
                    {new Date(c.created_at).toLocaleString()}
                  </span>
                </div>
                <p className="text-slate-300 leading-relaxed">{c.content}</p>
              </div>
            ))}
            {comments.length === 0 && (
              <p className="text-xs text-slate-500 text-center py-8">No comments recorded yet.</p>
            )}
          </div>
        </div>
      )}

      {/* TAB CONTENT: VERSION HISTORY */}
      {activeTab === 'versions' && (
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-4">Immutable Artifact Snapshot History</h3>
          <div className="space-y-3">
            {versions.map((v) => (
              <div key={v.id} className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs flex items-center justify-between">
                <div>
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">
                      v{v.version_number}.0
                    </span>
                    <h4 className="font-bold text-white">{v.artifact_type}</h4>
                  </div>
                  <p className="text-[11px] text-slate-400 mt-1">{v.change_summary}</p>
                  <span className="text-[10px] text-slate-500 mt-1 block">Author: {v.author_name}</span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">
                  {new Date(v.created_at).toLocaleDateString()}
                </span>
              </div>
            ))}
            {versions.length === 0 && (
              <div className="p-4 rounded-xl bg-slate-800/40 border border-slate-700/60 text-xs">
                <div className="flex items-center space-x-2">
                  <span className="font-mono font-bold px-2 py-0.5 rounded bg-purple-500/20 text-purple-300">v1.0</span>
                  <span className="font-bold text-white">Initial Transformation Blueprint</span>
                </div>
                <p className="text-[11px] text-slate-400 mt-1">Generated and approved during Hackathon initialization.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* TAB CONTENT: AUDIT LOGS */}
      {activeTab === 'audit' && (
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
          <h3 className="text-sm font-bold text-white mb-4">Immutable Governance Audit Trail</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-800 text-slate-500 uppercase text-[10px]">
                  <th className="pb-2">Actor</th>
                  <th className="pb-2">Action</th>
                  <th className="pb-2">Details</th>
                  <th className="pb-2 text-right">Timestamp</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {auditLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/30">
                    <td className="py-2.5 font-sans font-semibold text-slate-200">{log.user_name}</td>
                    <td className="py-2.5 text-blue-400">{log.action}</td>
                    <td className="py-2.5 text-slate-400 font-sans text-[11px]">{log.details}</td>
                    <td className="py-2.5 text-right text-slate-500 text-[10px]">
                      {new Date(log.created_at).toLocaleTimeString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
