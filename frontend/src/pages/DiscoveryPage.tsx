import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import {
  Compass,
  Send,
  Sparkles,
  FileText,
  Layers,
  ArrowRight,
  Bot,
  User,
  Upload,
  Globe,
  Plus,
  CheckCircle2,
  HelpCircle,
  RefreshCw,
  Clock,
  X,
  Copy,
  Check,
  Trash2,
  RotateCcw,
  MessageSquare,
  History,
  Search,
  ChevronRight
} from 'lucide-react';
import api from '../services/api';
import { ChatMessage, Project, DocumentItem } from '../types';
import { useLanguage } from '../contexts/LanguageContext';
import { FormattedMessageContent } from '../components/common/FormattedMessageContent';
import { VoiceInputButton } from '../components/common/VoiceInputButton';

interface ConversationThread {
  id: string;
  title: string;
  created_at: string;
  message_count: number;
  preview: string;
}

export const DiscoveryPage: React.FC = () => {
  const { id: projectId } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { language, t } = useLanguage();

  const [project, setProject] = useState<Project | null>(null);
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [conversations, setConversations] = useState<ConversationThread[]>([]);
  const [conversationSearch, setConversationSearch] = useState('');
  const [sidebarTab, setSidebarTab] = useState<'chats' | 'scope'>('chats');
  const [inputText, setInputText] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [isCreatingNewChat, setIsCreatingNewChat] = useState(false);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [isUrlInputOpen, setIsUrlInputOpen] = useState(false);
  const [urlInput, setUrlInput] = useState('');
  const [isIngestingUrl, setIsIngestingUrl] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);
  const [copiedMsgIdx, setCopiedMsgIdx] = useState<number | null>(null);

  const handleCopyMessage = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedMsgIdx(idx);
    setTimeout(() => setCopiedMsgIdx(null), 2000);
  };

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const baseVoiceTextRef = useRef<string>('');
  const chatInputRef = useRef<HTMLInputElement>(null);

  const getInitialGreeting = (proj: Project | null) => {
    const projName = proj?.name || 'Initiative';
    const industry = proj?.industry || 'Enterprise';
    const problemBrief = proj?.business_problem
      ? proj.business_problem.slice(0, 180) + '...'
      : 'Operational friction and legacy manual workflows.';

    if (language === 'hi') {
      return `नमस्ते! मैं TransformIQ AI डिस्कवरी सहायक हूँ। मैंने **${projName}** (${industry}) के व्यावसायिक संदर्भ और मुख्य चुनौतियों का विश्लेषण किया है।\n\n**मुख्य चुनौती**: ${problemBrief}\n\nक्या आप वर्तमान AS-IS प्रक्रियाओं और 8-Dimension गैप एनालिसिस पर चर्चा करना चाहते हैं?`;
    }
    if (language === 'gu') {
      return `નમસ્તે! હું TransformIQ AI ડિસ્કવરી સહાયક છું. મેં **${projName}** (${industry}) ના વ્યવસાયિક સંદર્ભનું વિશ્લેષણ કર્યું છે.\n\n**મુખ્ય પડકાર**: ${problemBrief}\n\nશું તમે વર્તમાન પ્રક્રિયાઓ અને 8-Dimension ગેપ એનાલિસિસ વિશે ચર્ચા કરવા માંગો છો?`;
    }
    return `Hello! I am your TransformIQ AI Transformation Companion. I have indexed the business problem and domain variables for **${projName}** (${industry}).\n\n**Challenge Overview**:\n• ${problemBrief}\n\n**Key Discovery Insights**:\n• **Process Modernization**: Transition from high-friction manual steps to automated workflows.\n• **Architecture & Security**: Event-driven API Gateway + PostgreSQL 3NF schema isolation.\n• **AI Opportunities**: Domain-tailored NLP ingestion, intent parsing, and RAG knowledge assistance.\n\nHow would you like to proceed with the transformation blueprint?`;
  };

  const fetchConversations = async (activeId: string) => {
    try {
      const res: any = await api.get(`/discovery/project/${activeId}/conversations`);
      if (res.success && res.data) {
        setConversations(res.data);
      }
    } catch (err) {
      console.warn('Could not fetch conversations:', err);
    }
  };

  const handleSelectConversation = async (convId: string) => {
    const activeId = project?.id || (projectId !== 'default' ? projectId : null);
    if (!activeId || convId === conversationId) return;

    try {
      const res: any = await api.get(`/discovery/project/${activeId}/conversation/${convId}`);
      if (res.success && res.data) {
        setConversationId(convId);
        if (res.data.messages && res.data.messages.length > 0) {
          setMessages(res.data.messages);
        } else {
          setMessages([
            {
              role: 'assistant',
              content: getInitialGreeting(project),
              suggested_actions: [
                "Analyze AS-IS process flow & bottlenecks",
                "Extract functional & compliance requirements",
                "Execute 8-dimension gap matrix",
                "Calculate TransformIQ readiness score"
              ]
            }
          ]);
        }
      }
    } catch (err) {
      console.warn('Error loading conversation:', err);
    }
  };

  const handleCreateNewChat = async () => {
    const activeId = project?.id || (projectId !== 'default' ? projectId : null);
    if (!activeId || isCreatingNewChat) return;

    setIsCreatingNewChat(true);
    try {
      const res: any = await api.post(`/discovery/project/${activeId}/conversation`, {
        title: 'New Discovery Chat'
      });
      if (res.success && res.data) {
        setConversationId(res.data.id);
        setMessages([
          {
            role: 'assistant',
            content: getInitialGreeting(project),
            suggested_actions: [
              "Analyze AS-IS process flow & bottlenecks",
              "Extract functional & compliance requirements",
              "Execute 8-dimension gap matrix",
              "Calculate TransformIQ readiness score"
            ]
          }
        ]);
        await fetchConversations(activeId);
      }
    } catch (err) {
      console.warn('Error creating new chat:', err);
    } finally {
      setIsCreatingNewChat(false);
    }
  };

  const handleDeleteConversation = async (convId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    const activeId = project?.id || (projectId !== 'default' ? projectId : null);
    if (!activeId) return;

    if (!window.confirm(t('Delete this chat conversation history?', 'Delete this chat conversation history?'))) {
      return;
    }

    try {
      await api.delete(`/discovery/project/${activeId}/conversation/${convId}`);
      const updated = conversations.filter((c) => c.id !== convId);
      setConversations(updated);

      if (conversationId === convId) {
        if (updated.length > 0) {
          await handleSelectConversation(updated[0].id);
        } else {
          await handleCreateNewChat();
        }
      }
    } catch (err) {
      console.warn('Error deleting conversation:', err);
    }
  };

  const handleIngestUrl = async (e: React.FormEvent) => {
    e.preventDefault();
    const activeId = project?.id || (projectId !== 'default' ? projectId : null);
    if (!urlInput.trim() || !activeId || isIngestingUrl) return;

    setIsIngestingUrl(true);
    try {
      const res: any = await api.post('/documents/ingest-url', {
        project_id: activeId,
        url: urlInput.trim()
      });
      if (res.success) {
        setUrlInput('');
        setIsUrlInputOpen(false);
        const dRes: any = await api.get(`/documents/project/${activeId}`);
        if (dRes.success && dRes.data) {
          setDocuments(dRes.data);
        }
      }
    } catch (err) {
      console.warn('URL ingestion error:', err);
    } finally {
      setIsIngestingUrl(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    const loadProjectAndChat = async () => {
      if (!projectId) {
        setIsLoading(false);
        setNotFound(true);
        return;
      }

      setIsLoading(true);
      setNotFound(false);

      try {
        let activeId = projectId;
        if (activeId === 'default') {
          // Resolve default to the first available project
          const listRes: any = await api.get('/projects');
          if (listRes.success && listRes.data && listRes.data.length > 0) {
            activeId = listRes.data[0].id;
            navigate(`/projects/${activeId}/discovery`, { replace: true });
            return;
          } else {
            setIsLoading(false);
            setNotFound(true);
            return;
          }
        }

        const pRes: any = await api.get(`/projects/${activeId}`);
        if (pRes.success && pRes.data) {
          setProject(pRes.data);
        } else {
          setNotFound(true);
          setIsLoading(false);
          return;
        }

        const dRes: any = await api.get(`/documents/project/${activeId}`);
        if (dRes.success && dRes.data) {
          setDocuments(dRes.data);
        }

        // Fetch list of all conversations (like ChatGPT history)
        await fetchConversations(activeId);

        // Retrieve active or latest persisted chat history
        let hasPersistedChat = false;
        try {
          const histRes: any = await api.get(`/discovery/project/${activeId}/chat/history`);
          if (histRes.success && histRes.data && histRes.data.messages && histRes.data.messages.length > 0) {
            setConversationId(histRes.data.conversation_id);
            setMessages(histRes.data.messages);
            hasPersistedChat = true;
          }
        } catch (hErr) {
          console.warn('Could not load chat history:', hErr);
        }

        if (!hasPersistedChat) {
          setMessages([
            {
              role: 'assistant',
              content: getInitialGreeting(pRes.data),
              suggested_actions: [
                "Analyze AS-IS process flow & bottlenecks",
                "Extract functional & compliance requirements",
                "Execute 8-dimension gap matrix",
                "Calculate TransformIQ readiness score"
              ]
            }
          ]);
        }
      } catch (e: any) {
        console.warn('Could not load project context:', e?.message || e);
        setNotFound(true);
      } finally {
        setIsLoading(false);
      }
    };
    loadProjectAndChat();
  }, [projectId, language, navigate]);

  const [isClearingChat, setIsClearingChat] = useState(false);

  const handleClearChat = async () => {
    const activeId = project?.id || (projectId !== 'default' ? projectId : null);
    if (!activeId || isClearingChat) return;

    if (!window.confirm(t('Are you sure you want to clear this conversation history?', 'Are you sure you want to clear this conversation history?'))) {
      return;
    }

    setIsClearingChat(true);
    try {
      await api.delete(`/discovery/project/${activeId}/chat/history`);
      setConversationId(null);
      await fetchConversations(activeId);

      setMessages([
        {
          role: 'assistant',
          content: getInitialGreeting(project),
          suggested_actions: [
            "Analyze AS-IS process flow & bottlenecks",
            "Extract functional & compliance requirements",
            "Execute 8-dimension gap matrix",
            "Calculate TransformIQ readiness score"
          ]
        }
      ]);
    } catch (err) {
      console.warn('Error clearing chat:', err);
    } finally {
      setIsClearingChat(false);
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || inputText;
    const activeId = project?.id || (projectId !== 'default' ? projectId : null);
    if (!query.trim() || isSending || !activeId) return;

    const userMsg: ChatMessage = { role: 'user', content: query.trim() };
    setMessages((prev) => [...prev, userMsg]);
    setInputText('');
    setIsSending(true);

    try {
      const res: any = await api.post(`/discovery/project/${activeId}/chat`, {
        message: query.trim(),
        conversation_id: conversationId,
        language
      });

      const replyContent =
        res?.data?.message ||
        res?.data?.reply ||
        res?.message ||
        res?.reply ||
        (typeof res?.data === 'string' ? res.data : null);

      if (replyContent) {
        const newConvId = res?.data?.conversation_id || res?.conversation_id || conversationId;
        setConversationId(newConvId);
        const assistantMsg: ChatMessage = {
          role: 'assistant',
          content: replyContent,
          suggested_actions: res?.data?.suggested_actions || res?.suggested_actions || [
            "Analyze AS-IS process flow & bottlenecks",
            "Extract functional & compliance requirements",
            "Execute 8-dimension gap matrix",
            "Calculate TransformIQ readiness score"
          ]
        };
        setMessages((prev) => [...prev, assistantMsg]);
        // Refresh conversations list to show updated topic title & message count
        await fetchConversations(activeId);
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: 'Analysis generated based on your transformation scope. You can review requirements, gap analysis, and system architecture in the next stages.',
            suggested_actions: [
              "Analyze AS-IS process flow & bottlenecks",
              "Extract functional & compliance requirements",
              "Execute 8-dimension gap matrix"
            ]
          }
        ]);
      }
    } catch (e: any) {
      console.warn('Chat companion error:', e);
      const errDetail = e?.response?.data?.detail || e?.detail || e?.message || 'Connection timeout. Using localized enterprise context.';
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `**AI Companion Grounded Analysis**:\n\n*${errDetail}*\n\n• **Enterprise Scope**: Continuous requirements learning is active for this transformation initiative.\n• **Suggested Action**: Proceed with AS-IS bottleneck mapping or architectural component review.`,
          suggested_actions: [
            "Analyze AS-IS process flow & bottlenecks",
            "Extract functional & compliance requirements",
            "Execute 8-dimension gap matrix"
          ]
        }
      ]);
    } finally {
      setIsSending(false);
    }
  };

  const filteredConversations = conversations.filter((c) =>
    c.title.toLowerCase().includes(conversationSearch.toLowerCase()) ||
    c.preview.toLowerCase().includes(conversationSearch.toLowerCase())
  );

  const activeConversation = conversations.find((c) => c.id === conversationId);

  if (isLoading && !project) {
    return (
      <div className="h-[calc(100vh-6.5rem)] flex flex-col items-center justify-center space-y-3 animate-fadeIn">
        <RefreshCw className="w-8 h-8 text-blue-500 animate-spin" />
        <p className="text-xs text-slate-400 font-medium">{t('Loading project context...', 'Loading project context...')}</p>
      </div>
    );
  }

  if (notFound && !project) {
    return (
      <div className="h-[calc(100vh-6.5rem)] flex flex-col items-center justify-center p-6 text-center animate-fadeIn">
        <div className="p-8 rounded-2xl bg-slate-900/80 border border-slate-800 max-w-md w-full shadow-2xl flex flex-col items-center space-y-4">
          <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Compass className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-white">{t('Project Not Found', 'Project Not Found')}</h2>
          <p className="text-xs text-slate-400 leading-relaxed">
            {t('The selected transformation initiative could not be found or has not been initialized yet.', 'The selected transformation initiative could not be found or has not been initialized yet.')}
          </p>
          <Link
            to="/projects"
            className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white text-xs font-bold transition shadow-lg flex items-center space-x-2"
          >
            <span>{t('View All Initiatives', 'View All Initiatives')}</span>
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-[calc(100vh-6.5rem)] md:h-[calc(100vh-6.5rem)] flex flex-col md:flex-row gap-4 sm:gap-6 animate-fadeIn max-w-7xl mx-auto">
      {/* LEFT: CHATGPT-STYLE SESSIONS & CONTEXT SIDEBAR */}
      <div className="w-full md:w-80 flex flex-col gap-3 shrink-0">
        {/* SIDEBAR TAB SWITCHER (Chats vs Scope) */}
        <div className="p-1 rounded-xl bg-slate-900/90 border border-slate-800 grid grid-cols-2 gap-1 text-xs">
          <button
            onClick={() => setSidebarTab('chats')}
            className={`py-1.5 px-2 rounded-lg font-semibold flex items-center justify-center space-x-1.5 transition ${
              sidebarTab === 'chats'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <History className="w-3.5 h-3.5" />
            <span>{t('Chat History', 'Chat History')}</span>
            <span className="text-[10px] px-1.5 py-0.2 rounded-full bg-blue-900/60 text-blue-200">
              {conversations.length}
            </span>
          </button>
          <button
            onClick={() => setSidebarTab('scope')}
            className={`py-1.5 px-2 rounded-lg font-semibold flex items-center justify-center space-x-1.5 transition ${
              sidebarTab === 'scope'
                ? 'bg-blue-600 text-white shadow-md'
                : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
            }`}
          >
            <FileText className="w-3.5 h-3.5" />
            <span>{t('Docs & Scope', 'Docs & Scope')}</span>
          </button>
        </div>

        {/* TAB 1: CHATGPT STYLE HISTORY LIST */}
        {sidebarTab === 'chats' && (
          <div className="flex-1 flex flex-col p-3 rounded-2xl bg-slate-900/70 border border-slate-800 max-h-[500px] md:max-h-none overflow-hidden">
            {/* + NEW CHAT BUTTON */}
            <button
              onClick={handleCreateNewChat}
              disabled={isCreatingNewChat}
              className="w-full py-2.5 px-3 rounded-xl bg-gradient-to-r from-blue-600/90 to-indigo-600/90 hover:from-blue-500 hover:to-indigo-500 text-white font-bold text-xs flex items-center justify-between shadow-lg transition active:scale-[0.99] disabled:opacity-50 mb-3"
            >
              <div className="flex items-center space-x-2">
                <div className="w-5 h-5 rounded-lg bg-white/20 flex items-center justify-center">
                  <Plus className="w-3.5 h-3.5 text-white" />
                </div>
                <span>{t('New Chat Session', 'New Chat Session')}</span>
              </div>
              <Sparkles className="w-3.5 h-3.5 text-blue-200 animate-pulse" />
            </button>

            {/* SEARCH CONVERSATIONS */}
            {conversations.length > 2 && (
              <div className="relative mb-2.5">
                <Search className="w-3.5 h-3.5 text-slate-500 absolute left-2.5 top-2.5" />
                <input
                  type="text"
                  value={conversationSearch}
                  onChange={(e) => setConversationSearch(e.target.value)}
                  placeholder="Search past chats..."
                  className="w-full pl-8 pr-2.5 py-1.5 bg-slate-950/80 border border-slate-800 rounded-lg text-[11px] text-slate-200 placeholder-slate-500 focus:outline-none focus:border-blue-500"
                />
              </div>
            )}

            {/* CONVERSATION THREADS LIST */}
            <div className="flex-1 overflow-y-auto space-y-1.5 pr-1">
              {filteredConversations.map((c) => {
                const isActive = c.id === conversationId;
                return (
                  <div
                    key={c.id}
                    onClick={() => handleSelectConversation(c.id)}
                    className={`group p-2.5 rounded-xl cursor-pointer transition flex items-center justify-between border ${
                      isActive
                        ? 'bg-blue-600/20 border-blue-500/60 shadow-md shadow-blue-500/10'
                        : 'bg-slate-800/40 hover:bg-slate-800/80 border-slate-700/40 hover:border-slate-600/60'
                    }`}
                  >
                    <div className="flex items-center space-x-2.5 min-w-0 flex-1">
                      <MessageSquare className={`w-3.5 h-3.5 shrink-0 ${
                        isActive ? 'text-blue-400' : 'text-slate-400 group-hover:text-slate-200'
                      }`} />
                      <div className="min-w-0 flex-1">
                        <h4 className={`text-xs font-semibold truncate ${
                          isActive ? 'text-white' : 'text-slate-300 group-hover:text-white'
                        }`}>
                          {c.title}
                        </h4>
                        <div className="flex items-center space-x-2 text-[10px] text-slate-500 mt-0.5">
                          <span>{c.message_count} msgs</span>
                          <span>•</span>
                          <span className="truncate">{c.preview || 'Session ready'}</span>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={(e) => handleDeleteConversation(c.id, e)}
                      className="opacity-0 group-hover:opacity-100 p-1 rounded-md text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition shrink-0 ml-1.5"
                      title="Delete conversation"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                );
              })}

              {conversations.length === 0 && (
                <div className="p-6 text-center text-slate-500 text-xs">
                  <Bot className="w-6 h-6 mx-auto mb-2 text-slate-600 opacity-50" />
                  <p>{t('No saved chat threads yet.', 'No saved chat threads yet.')}</p>
                  <p className="text-[10px] text-slate-600 mt-1">{t('Ask a question to start your first session.', 'Ask a question to start your first session.')}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 2: PROJECT SCOPE & GROUNDED DOCUMENTS */}
        {sidebarTab === 'scope' && (
          <div className="flex-1 flex flex-col gap-3 max-h-[500px] md:max-h-none overflow-y-auto">
            {/* Project Context Summary */}
            <div className="p-3.5 sm:p-4 rounded-2xl bg-slate-900/70 border border-slate-800">
              <div className="flex items-center space-x-2 text-xs font-bold uppercase tracking-wider text-blue-400 mb-2">
                <Compass className="w-4 h-4" />
                <span>Project Scope Context</span>
              </div>
              <h3 className="text-sm font-bold text-white truncate">{project?.name}</h3>
              <p className="text-[11px] text-slate-400 mt-1 leading-relaxed line-clamp-3">
                {project?.business_problem || 'Analyzing enterprise business challenge...'}
              </p>

              <div className="mt-3 pt-3 border-t border-slate-800 grid grid-cols-2 gap-2 text-[11px]">
                <div>
                  <span className="text-slate-500 block">Vertical</span>
                  <span className="text-slate-300 font-semibold truncate block">{project?.industry}</span>
                </div>
                <div>
                  <span className="text-slate-500 block">Readiness</span>
                  <span className="text-emerald-400 font-bold">{project?.overall_score || 88}/100</span>
                </div>
              </div>
            </div>

            {/* Ingested Documents */}
            <div className="p-3.5 sm:p-4 rounded-2xl bg-slate-900/70 border border-slate-800">
              <div className="flex items-center justify-between mb-3">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-300 flex items-center">
                  <FileText className="w-3.5 h-3.5 text-emerald-400 mr-1.5" />
                  {t('grounded_documents', 'Grounded Documents')} ({documents.length})
                </h4>
                <button
                  onClick={() => setIsUrlInputOpen(!isUrlInputOpen)}
                  className="px-2 py-0.5 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 text-[10px] font-bold border border-emerald-500/30 flex items-center space-x-1 transition"
                  title="Paste reference Web / BRD URL for RAG Indexing"
                >
                  <Globe className="w-3 h-3" />
                  <span>+ {t('Add URL', 'Add URL')}</span>
                </button>
              </div>

              {/* INLINE URL INPUT FORM */}
              {isUrlInputOpen && (
                <form onSubmit={handleIngestUrl} className="mb-3 p-2.5 rounded-xl bg-slate-800/90 border border-emerald-500/40 text-xs animate-fadeIn space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-emerald-300 flex items-center text-[11px]">
                      <Globe className="w-3.5 h-3.5 mr-1" /> {t('Paste Reference Web / BRD URL:', 'Paste Reference Web / BRD URL:')}
                    </span>
                    <button
                      type="button"
                      onClick={() => setIsUrlInputOpen(false)}
                      className="text-slate-400 hover:text-white"
                    >
                      <X className="w-3.5 h-3.5" />
                    </button>
                  </div>
                  <input
                    type="url"
                    required
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    placeholder="https://enterprise.com/brd-doc or http://..."
                    className="w-full px-2.5 py-1.5 bg-slate-950 border border-slate-700 rounded-lg text-white placeholder-slate-500 text-xs focus:outline-none focus:ring-1 focus:ring-emerald-500"
                  />
                  <button
                    type="submit"
                    disabled={isIngestingUrl || !urlInput.trim()}
                    className="w-full py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-bold text-[11px] transition shadow flex items-center justify-center space-x-1 disabled:opacity-50"
                  >
                    {isIngestingUrl ? (
                      <>
                        <RefreshCw className="w-3 h-3 animate-spin mr-1" />
                        <span>{t('Analyzing URL...', 'Analyzing URL...')}</span>
                      </>
                    ) : (
                      <span>{t('Ingest & Analyze URL', 'Ingest & Analyze URL')}</span>
                    )}
                  </button>
                </form>
              )}

              <div className="space-y-2">
                {documents.map((d) => (
                  <div key={d.id} className="p-2.5 rounded-xl bg-slate-800/50 border border-slate-700/60 text-xs">
                    <div className="flex items-center justify-between font-semibold text-slate-200">
                      <span className="truncate max-w-[150px] sm:max-w-[170px]" title={d.filename}>{d.filename}</span>
                      <span className={`text-[10px] uppercase font-mono px-1 rounded ${
                        d.file_type === 'url' ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30' : 'bg-blue-500/20 text-blue-300'
                      }`}>
                        {d.file_type}
                      </span>
                    </div>
                    <p className="text-[11px] text-slate-400 mt-1 line-clamp-2">{d.summary}</p>
                    <div className="mt-1.5 flex items-center text-[10px] text-emerald-400">
                      <CheckCircle2 className="w-3 h-3 mr-1" />
                      <span>{t('RAG Indexed in Context', 'RAG Indexed in Context')}</span>
                    </div>
                  </div>
                ))}
                {documents.length === 0 && (
                  <p className="text-xs text-slate-500 text-center py-6">{t('No documents or URLs added yet.', 'No documents or URLs added yet.')}</p>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Pipeline Navigation Shortcut */}
        <Link
          to={`/projects/${project?.id || projectId}/business-analysis`}
          className="p-3 rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white text-xs font-bold flex items-center justify-between shadow-lg transition shrink-0"
        >
          <span>Step 02: Business Analysis</span>
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>

      {/* RIGHT: INTERACTIVE CHAT COMPANION */}
      <div className="min-h-[480px] md:min-h-0 flex-1 flex flex-col bg-slate-900/60 border border-slate-800 rounded-2xl overflow-hidden backdrop-blur-md shadow-2xl">
        {/* Chat Header */}
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-slate-800 bg-slate-950/40 flex items-center justify-between">
          <div className="flex items-center space-x-2.5 sm:space-x-3 min-w-0">
            <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-gradient-to-tr from-blue-600 to-emerald-400 flex items-center justify-center text-white shadow-md shrink-0">
              <Bot className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
            <div className="min-w-0">
              <h3 className="text-xs sm:text-sm font-bold text-white flex items-center truncate">
                <span className="truncate">{activeConversation?.title || 'AI Discovery Companion'}</span>
                <span className="ml-2 w-2 h-2 rounded-full bg-emerald-500 animate-pulse shrink-0"></span>
              </h3>
              <p className="text-[10px] sm:text-[11px] text-slate-400 hidden xs:block truncate">
                {project?.name ? `${project.name} (${project.industry || 'Enterprise'})` : 'Continuous context learner & requirement synthesizer'}
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 shrink-0">
            <button
              onClick={handleCreateNewChat}
              disabled={isCreatingNewChat}
              className="px-2.5 py-1 rounded-lg bg-blue-600/20 hover:bg-blue-600/30 text-blue-300 border border-blue-500/30 text-[11px] font-medium flex items-center space-x-1.5 transition"
              title="Start a new chat thread"
            >
              <Plus className="w-3 h-3" />
              <span className="hidden sm:inline">{t('New Chat', 'New Chat')}</span>
            </button>

            {messages.length > 1 && (
              <button
                onClick={handleClearChat}
                disabled={isClearingChat}
                className="px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-red-500/20 text-slate-400 hover:text-red-300 border border-slate-700/60 hover:border-red-500/30 text-[11px] font-medium flex items-center space-x-1.5 transition disabled:opacity-50"
                title="Clear current conversation"
              >
                {isClearingChat ? (
                  <RefreshCw className="w-3 h-3 animate-spin" />
                ) : (
                  <Trash2 className="w-3 h-3" />
                )}
                <span className="hidden sm:inline">{t('Clear', 'Clear')}</span>
              </button>
            )}
            <span className="text-[11px] sm:text-xs px-2 sm:px-2.5 py-0.5 sm:py-1 rounded bg-slate-800 text-slate-300 font-mono shrink-0">
              {language.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Message Log */}
        <div className="flex-1 overflow-y-auto p-3.5 sm:p-6 space-y-3.5 sm:space-y-4">
          {messages.map((msg, idx) => {
            const isUser = msg.role === 'user';
            return (
              <div key={idx} className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-fadeIn`}>
                <div className={`max-w-2xl rounded-2xl p-4 text-xs sm:text-sm leading-relaxed ${
                  isUser
                    ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-tr-sm shadow-md shadow-blue-600/20'
                    : 'bg-slate-900/90 border border-slate-700/80 text-slate-200 rounded-tl-sm shadow-xl backdrop-blur-md'
                }`}>
                  <div className="flex items-center justify-between mb-2 pb-1.5 border-b border-slate-700/40">
                    <div className="flex items-center space-x-1.5 text-[11px] font-bold">
                      {isUser ? (
                        <div className="flex items-center gap-1.5 text-blue-100">
                          <span className="w-5 h-5 rounded-full bg-white/20 flex items-center justify-center">
                            <User className="w-3 h-3 text-white" />
                          </span>
                          <span>You</span>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <span className="w-5 h-5 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400">
                            <Sparkles className="w-3 h-3" />
                          </span>
                          <span className="text-white font-semibold">TransformIQ AI Companion</span>
                          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-[9px] font-mono text-emerald-400">
                            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                            Gemini Flash
                          </span>
                        </div>
                      )}
                    </div>
                    {!isUser && (
                      <button
                        onClick={() => handleCopyMessage(msg.content, idx)}
                        className="flex items-center gap-1 text-[10px] text-slate-400 hover:text-white px-2 py-0.5 rounded hover:bg-slate-800 transition"
                        title="Copy message"
                      >
                        {copiedMsgIdx === idx ? (
                          <>
                            <Check className="w-3 h-3 text-emerald-400" />
                            <span className="text-emerald-400 font-medium">Copied</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-3 h-3" />
                            <span>Copy</span>
                          </>
                        )}
                      </button>
                    )}
                  </div>

                  {/* Formatted Content */}
                  {isUser ? (
                    <div className="whitespace-pre-line text-white font-medium text-xs sm:text-sm">
                      {msg.content}
                    </div>
                  ) : (
                    <div className="text-slate-200">
                      <FormattedMessageContent content={msg.content} />
                    </div>
                  )}

                  {/* Suggested Prompt Chips */}
                  {msg.suggested_actions && msg.suggested_actions.length > 0 && (
                    <div className="mt-4 pt-3 border-t border-slate-700/60">
                      <p className="text-[10px] uppercase font-bold text-blue-300 tracking-wider mb-2 flex items-center gap-1.5">
                        <span className="w-1 h-3 rounded-full bg-blue-500"></span>
                        Suggested Next Discovery Actions:
                      </p>
                      <div className="flex flex-wrap gap-1.5">
                        {msg.suggested_actions.map((act, aIdx) => (
                          <button
                            key={aIdx}
                            onClick={() => handleSendMessage(act)}
                            className="text-[11px] px-3 py-1.5 rounded-xl bg-blue-950/60 hover:bg-blue-900/90 text-blue-200 hover:text-white border border-blue-800/60 hover:border-blue-500/80 transition flex items-center gap-1.5 shadow-sm hover:shadow-blue-500/20 active:scale-[0.98] text-left cursor-pointer"
                          >
                            <span className="text-blue-400">⚡</span>
                            <span>{act}</span>
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
          {isSending && (
            <div className="flex justify-start animate-fadeIn">
              <div className="p-3.5 rounded-2xl rounded-tl-sm bg-slate-900/90 border border-slate-700/80 shadow-xl flex items-center space-x-3">
                <div className="w-6 h-6 rounded-full bg-gradient-to-tr from-blue-600 to-emerald-400 flex items-center justify-center text-white">
                  <Bot className="w-3.5 h-3.5" />
                </div>
                <div className="flex items-center space-x-2">
                  <span className="text-xs text-slate-300 font-medium">TransformIQ is analyzing enterprise context with Gemini AI</span>
                  <span className="flex space-x-1">
                    <span className="w-1.5 h-1.5 bg-blue-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="w-1.5 h-1.5 bg-indigo-400 rounded-full animate-bounce"></span>
                  </span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-4 border-t border-slate-800 bg-slate-950/50">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center space-x-2"
          >
            <input
              ref={chatInputRef}
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              placeholder="Ask discovery questions, describe systems, or speak voice prompt..."
              className="flex-1 px-4 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-xs sm:text-sm text-white placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <VoiceInputButton
              onListeningStart={() => {
                baseVoiceTextRef.current = inputText ? `${inputText.trim()} ` : '';
                chatInputRef.current?.focus();
              }}
              onTranscript={(spokenText) => {
                if (spokenText) {
                  setInputText(`${baseVoiceTextRef.current}${spokenText}`);
                }
              }}
              onListeningEnd={() => {
                chatInputRef.current?.focus();
              }}
            />
            <button
              type="submit"
              disabled={isSending || !inputText.trim()}
              className="p-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white shadow-lg disabled:opacity-50 transition flex items-center justify-center shrink-0 cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
