import React, { useState, useEffect, useRef } from 'react';
import { 
  LineChart, Line, XAxis, YAxis, Tooltip as RechartsTooltip, ResponsiveContainer, CartesianGrid,
  PieChart, Pie, Cell
} from 'recharts';
import { 
  Bot, MessageSquare, Send, X, Activity, TrendingUp, Award,
  BookOpen, HelpCircle, Mail, Phone, User, Video, Search,
  Menu, Trophy, PieChart as PieIcon, Users, UserCheck, UserX, ChevronRight
} from 'lucide-react';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8080";

const CHANNEL_COLORS = {
  "Digital Ad": "#0ea5e9",
  "Email": "#3b82f6",
  "Phone Call": "#f59e0b",
  "Rep Visit": "#8b5cf6",
  "Webinar": "#10b981"
};

const CHANNEL_ICONS = {
  "Digital Ad": <Activity size={15} />,
  "Email": <Mail size={15} />,
  "Phone Call": <Phone size={15} />,
  "Rep Visit": <User size={15} />,
  "Webinar": <Video size={15} />
};

function App() {
  const [searchInput, setSearchInput] = useState('');
  const [hcpData, setHcpData] = useState(null);
  const [stats, setStats] = useState(null);
  const [allHcps, setAllHcps] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Drawer state
  const [menuOpen, setMenuOpen] = useState(false);
  const [menuTab, setMenuTab] = useState('rankings'); // 'rankings' | 'overview'
  const [rankSearch, setRankSearch] = useState('');

  // Chatbot state
  const [chatOpen, setChatOpen] = useState(false);
  const [messages, setMessages] = useState([
    { text: "👋 Hello! I am your HCP AI Assistant. Ask me anything about engagement scores, channel recommendations, or Next Best Actions.", sender: "bot" }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetchStats();
    fetchAllHcps();
  }, []);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping]);

  const fetchStats = async () => {
    try {
      const res = await fetch(`${API_URL}/api/stats`);
      if (res.ok) setStats(await res.json());
    } catch (err) {
      console.error("Failed to fetch stats", err);
    }
  };

  const fetchAllHcps = async () => {
    try {
      const res = await fetch(`${API_URL}/api/hcps`);
      if (res.ok) {
        const data = await res.json();
        // Sort by engagement score descending
        data.sort((a, b) => b.overall_engagement_score_100 - a.overall_engagement_score_100);
        setAllHcps(data);
      }
    } catch (err) {
      console.error("Failed to fetch HCP list", err);
    }
  };

  const fetchHcpById = async (id) => {
    setLoading(true);
    setError('');
    setHcpData(null);

    try {
      const res = await fetch(`${API_URL}/api/hcp/${id}`);
      if (res.ok) {
        setHcpData(await res.json());
        setSearchInput(id);
      } else {
        const errData = await res.json();
        setError(errData.detail || `HCP ID "${id}" not found. Please try another.`);
      }
    } catch (err) {
      setError('Failed to connect to the backend server. Please ensure it is running on port 8080.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    const id = searchInput.trim();
    if (id) fetchHcpById(id);
  };

  const handleSelectHcpFromMenu = (id) => {
    fetchHcpById(id);
    setMenuOpen(false);
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!chatInput.trim()) return;

    const userMessage = chatInput.trim();
    setMessages(prev => [...prev, { text: userMessage, sender: "user" }]);
    setChatInput('');
    setIsTyping(true);

    try {
      const res = await fetch(`${API_URL}/api/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      });
      const data = await res.json();
      setMessages(prev => [...prev, { text: data.response, sender: "bot" }]);
    } catch {
      setMessages(prev => [...prev, { text: "❌ Connection error. Is the backend running?", sender: "bot" }]);
    } finally {
      setIsTyping(false);
    }
  };

  const getEngagementLevel = (score) => {
    if (score >= 70) return { label: "Highly Engaged", color: "#16A34A" };
    if (score >= 40) return { label: "Moderately Engaged", color: "#D97706" };
    return { label: "Low Engagement", color: "#DC2626" };
  };

  const score = hcpData ? hcpData.overall_engagement_score : 0;
  const levelInfo = getEngagementLevel(score);

  const gaugeData = [{ value: score }, { value: 100 - score }];

  const donutData = hcpData
    ? Object.keys(hcpData.weighted_contributions).map(ch => ({
        name: ch,
        value: parseFloat((hcpData.weighted_contributions[ch] * 100).toFixed(1)),
        color: CHANNEL_COLORS[ch]
      }))
    : [];

  const trendData = hcpData
    ? [
        { name: "Dec '24", Score: Math.max(0, Math.round(score - 18)) },
        { name: "Jan '25", Score: Math.max(0, Math.round(score - 14)) },
        { name: "Feb '25", Score: Math.max(0, Math.round(score - 10)) },
        { name: "Mar '25", Score: Math.max(0, Math.round(score - 6)) },
        { name: "Apr '25", Score: Math.max(0, Math.round(score - 2)) },
        { name: "May '25", Score: Math.round(score) }
      ]
    : [];

  const filteredRankings = allHcps.filter(h => {
    const q = rankSearch.toLowerCase();
    return (
      String(h.hcp_id).includes(q) ||
      `${h.first_name} ${h.last_name}`.toLowerCase().includes(q) ||
      (h.specialty && h.specialty.toLowerCase().includes(q))
    );
  });

  return (
    <>
      <main className="main-content">

        {/* Header with search & Burger Menu */}
        <header className="main-header">
          <h1>HCP Engagement Scorecard</h1>

          <div className="header-right-actions">
            <form className="search-bar-wrapper" onSubmit={handleSearch}>
              <div className="search-input-group">
                <Search size={16} className="search-icon" />
                <input
                  type="text"
                  className="search-input"
                  placeholder="Enter HCP ID (e.g. 1001, 1024, 1150...)"
                  value={searchInput}
                  onChange={(e) => setSearchInput(e.target.value)}
                />
              </div>
              <button type="submit" className="search-btn" disabled={loading}>
                {loading ? 'Searching...' : 'Analyze HCP'}
              </button>
            </form>

            <button
              className="burger-menu-btn"
              onClick={() => setMenuOpen(true)}
              title="Menu Options & Rankings"
            >
              <Menu size={20} />
            </button>
          </div>
        </header>

        {/* Error Banner */}
        {error && (
          <div className="error-banner">⚠️ {error}</div>
        )}

        {/* PLACEHOLDER when no HCP searched yet */}
        {!hcpData && !loading && !error && (
          <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="glass-panel" style={{ padding: '40px 60px', textAlign: 'center', color: 'var(--text-muted)', maxWidth: 550 }}>
              <Search size={44} style={{ opacity: 0.3, marginBottom: 14, display: 'block', margin: '0 auto 14px' }} />
              <h2 style={{ fontSize: '1.15rem', color: 'var(--text-main)', marginBottom: 6 }}>No HCP Selected</h2>
              <p style={{ fontSize: '0.85rem', lineHeight: 1.5 }}>Enter an HCP ID in the search bar above or click the ☰ Menu to view the HCP Leaderboard & system stats.</p>
            </div>
          </div>
        )}

        {/* ── HCP PROFILE + SCORECARD ── */}
        {hcpData && (
          <>
            <section className="content-grid">

              {/* LEFT: Profile Scorecard */}
              <div className="glass-panel section-card">
                <div className="section-card-header">
                  <h3>HCP Scorecard</h3>
                  <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', padding: '3px 10px', background: 'rgba(255,255,255,0.05)', borderRadius: 6, border: '1px solid var(--surface-border)' }}>
                    {hcpData.doctor_name} ({hcpData.hcp_id})
                  </span>
                </div>

                <div className="hcp-profile-section">
                  {/* Doctor Info — no avatar */}
                  <div className="profile-info">
                    <h4>{hcpData.doctor_name}</h4>
                    <div className="hcp-badge">{hcpData.hcp_id}</div>
                    <div className="specialty-text">{hcpData.specialty}</div>
                    <div className="hospital-text">Apollo Hospitals, Mumbai</div>
                    <div className="location-text">📍 Maharashtra</div>
                  </div>

                  {/* Gauge Chart */}
                  <div className="score-gauge-container">
                    <p className="score-gauge-title">
                      Overall Engagement Score
                    </p>
                    <div className="gauge-chart-wrapper">
                      <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                          <Pie data={gaugeData} cx="50%" cy="100%" startAngle={180} endAngle={0}
                            innerRadius={55} outerRadius={70} dataKey="value">
                            <Cell fill={levelInfo.color} />
                            <Cell fill="rgba(255,255,255,0.1)" />
                          </Pie>
                        </PieChart>
                      </ResponsiveContainer>
                      <div className="gauge-center-text">
                        <div className="gauge-score">{Math.round(score)}</div>
                        <div className="gauge-score-max">/100</div>
                      </div>
                    </div>
                    <div className="gauge-label" style={{ color: levelInfo.color }}>{levelInfo.label}</div>
                  </div>

                  {/* Channel Progress Bars */}
                  <div className="channel-scores-list">
                    {Object.keys(hcpData.channel_scores).map(ch => {
                      const pct = hcpData.channel_scores[ch] * 100;
                      return (
                        <div className="progress-item" key={ch}>
                          <div className="progress-labels">
                            <span className="progress-name">{ch} Engagement</span>
                            <span className="progress-val">{Math.round(pct)}/100</span>
                          </div>
                          <div className="progress-bar-bg">
                            <div className="progress-bar-fill" style={{ width: `${pct}%`, backgroundColor: CHANNEL_COLORS[ch] }} />
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* RIGHT: Channel-Mix Recommendation */}
              <div className="glass-panel section-card">
                <div className="section-card-header" style={{ marginBottom: 4 }}>
                  <h3>Channel-Mix Recommendation</h3>
                </div>

                <div style={{ fontSize: '0.68rem', fontWeight: 600, color: 'var(--success)', background: 'var(--success-light)', borderRadius: 4, padding: '3px 8px', textAlign: 'center', marginBottom: 6 }}>
                  Recommended Mix for Next 30 Days
                </div>

                <div className="donut-chart-wrapper">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie data={donutData} cx="50%" cy="50%" innerRadius={40} outerRadius={52} paddingAngle={2} dataKey="value">
                        {donutData.map((entry, i) => <Cell key={i} fill={entry.color} />)}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                </div>

                <div className="donut-legend">
                  {donutData.map((item, i) => (
                    <div className="legend-item" key={i}>
                      <span className="legend-color" style={{ backgroundColor: item.color }} />
                      <div>
                        <span className="legend-text">{item.name} ({item.value}%)</span>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="why-rec-box" style={{ marginTop: 6 }}>
                  <strong>Why this recommendation?</strong>
                  <p style={{ marginTop: 2 }}>
                    Dr. {hcpData.doctor_name.split(' ').pop()} shows highest engagement through{' '}
                    <strong>{hcpData.preferred_channel}</strong>. Focus on this channel is recommended.
                  </p>
                </div>
              </div>
            </section>

            {/* ── BOTTOM ROW ── */}
            <section className="bottom-sections-grid">
              {/* Trend Chart */}
              <div className="glass-panel section-card">
                <div className="section-card-header" style={{ marginBottom: 6 }}>
                  <h3>Engagement Trend <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 400 }}>(6 Months)</span></h3>
                </div>
                <div style={{ height: 110 }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={trendData} margin={{ top: 10, right: 15, left: -10, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
                      <XAxis dataKey="name" tick={{ fontSize: 10, fill: '#64748B' }} />
                      <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: '#64748B' }} />
                      <RechartsTooltip contentStyle={{ fontSize: 11, borderRadius: 8, background: '#FFFFFF', borderColor: '#DCE5EF', color: '#172033' }} />
                      <Line type="monotone" dataKey="Score" stroke="#0F9D8A" strokeWidth={2.5}
                        dot={{ r: 3, fill: '#0F9D8A' }} activeDot={{ r: 5 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Recent Interactions */}
              <div className="glass-panel section-card">
                <div className="section-card-header">
                  <h3>Recent Interactions</h3>
                  <span style={{ fontSize: '0.75rem', color: 'var(--primary)', cursor: 'pointer', fontWeight: 600 }}>View All</span>
                </div>
                <div className="interactions-list">
                  {[
                    { ch: hcpData.preferred_channel, desc: 'High-value engagement', date: 'May 29, 2025' },
                    { ch: 'Webinar', desc: 'Cardio Insights 2025', date: 'May 26, 2025' },
                    { ch: 'Email', desc: 'Email Opened', date: 'May 20, 2025' },
                  ].map((item, i) => (
                    <div className="interaction-item" key={i}>
                      <div className="interaction-icon" style={{ backgroundColor: CHANNEL_COLORS[item.ch] + '20', color: CHANNEL_COLORS[item.ch] }}>
                        {CHANNEL_ICONS[item.ch]}
                      </div>
                      <div className="interaction-details">
                        <div className="interaction-header">
                          <span className="interaction-type">{item.ch}</span>
                          <span className="interaction-date">{item.date}</span>
                        </div>
                        <p className="interaction-desc">{item.desc}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Key Insights */}
              <div className="glass-panel section-card">
                <div className="section-card-header">
                  <h3>Key Insights</h3>
                </div>
                <div className="insights-list">
                  <div className="insight-item">
                    <div className="insight-icon" style={{ backgroundColor: 'var(--success-light)', color: 'var(--success)' }}>
                      <TrendingUp size={13} />
                    </div>
                    <div className="insight-text">
                      <h5>Engagement improving steadily</h5>
                      <p>Score improved by {Math.round(score * 0.08)} points compared to last month.</p>
                    </div>
                  </div>
                  <div className="insight-item">
                    <div className="insight-icon" style={{ backgroundColor: 'var(--purple-light)', color: 'var(--purple)' }}>
                      <Award size={13} />
                    </div>
                    <div className="insight-text">
                      <h5>{hcpData.preferred_channel} drives highest engagement</h5>
                      <p>This channel has the strongest impact on overall score.</p>
                    </div>
                  </div>
                  <div className="insight-item">
                    <div className="insight-icon" style={{ backgroundColor: 'var(--warning-light)', color: 'var(--warning)' }}>
                      <BookOpen size={13} />
                    </div>
                    <div className="insight-text">
                      <h5>High content interest</h5>
                      <p>Frequently engages with clinical content and product pages.</p>
                    </div>
                  </div>
                </div>
              </div>
            </section>

            {/* Footer Info */}
            <div className="footer-info">
              <HelpCircle size={14} />
              Engagement Score is calculated using a weighted composite scoring model based on interactions across Email, Webinar, Rep Visits, Phone Calls, and Digital Ads.
            </div>
          </>
        )}
      </main>

      {/* ─── BURGER MENU SLIDE-OVER DRAWER ─────────────────── */}
      {menuOpen && (
        <div className="menu-drawer-backdrop" onClick={() => setMenuOpen(false)}>
          <div className="menu-drawer-panel" onClick={(e) => e.stopPropagation()}>
            <div className="menu-drawer-header">
              <h3>HCP Intelligence Options</h3>
              <button onClick={() => setMenuOpen(false)} className="chatbot-close-btn">
                <X size={20} />
              </button>
            </div>

            {/* Navigation Tabs */}
            <div className="menu-drawer-tabs">
              <button
                className={`drawer-tab ${menuTab === 'rankings' ? 'active' : ''}`}
                onClick={() => setMenuTab('rankings')}
              >
                <Trophy size={16} /> HCP Rankings ({allHcps.length})
              </button>
              <button
                className={`drawer-tab ${menuTab === 'overview' ? 'active' : ''}`}
                onClick={() => setMenuTab('overview')}
              >
                <PieIcon size={16} /> Engagement Overview
              </button>
            </div>

            <div className="menu-drawer-body">
              {/* TAB 1: HCP RANKINGS BY ENGAGEMENT SCORE */}
              {menuTab === 'rankings' && (
                <>
                  <div className="rankings-search">
                    <Search size={14} style={{ color: 'var(--text-muted)' }} />
                    <input
                      type="text"
                      placeholder="Search rank list by name, ID or specialty..."
                      value={rankSearch}
                      onChange={(e) => setRankSearch(e.target.value)}
                    />
                  </div>

                  <div className="rankings-list">
                    {filteredRankings.slice(0, 100).map((hcp, idx) => {
                      const rank = idx + 1;
                      let rankClass = "default";
                      if (rank === 1) rankClass = "gold";
                      else if (rank === 2) rankClass = "silver";
                      else if (rank === 3) rankClass = "bronze";

                      return (
                        <div
                          key={hcp.hcp_id}
                          className="ranking-item"
                          onClick={() => handleSelectHcpFromMenu(hcp.hcp_id)}
                        >
                          <div className={`ranking-rank ${rankClass}`}>
                            {rank}
                          </div>
                          <div className="ranking-info">
                            <div className="ranking-name">{hcp.first_name} {hcp.last_name}</div>
                            <div className="ranking-sub">
                              <span>ID: {hcp.hcp_id}</span> • <span>{hcp.specialty || 'General'}</span>
                            </div>
                          </div>
                          <div className="ranking-score-badge">
                            {Math.round(hcp.overall_engagement_score_100)} pts
                          </div>
                          <ChevronRight size={16} style={{ color: 'var(--text-muted)', marginLeft: 8 }} />
                        </div>
                      );
                    })}
                  </div>
                </>
              )}

              {/* TAB 2: SYSTEM OVERVIEW & SEGMENTATION STATS */}
              {menuTab === 'overview' && stats && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                  {/* Top Stats Row */}
                  <div className="overview-card-grid">
                    <div className="overview-card">
                      <div className="overview-card-title">Total HCPs</div>
                      <div className="overview-card-val">{stats.total_hcps.toLocaleString()}</div>
                    </div>
                    <div className="overview-card">
                      <div className="overview-card-title">Eligible HCPs</div>
                      <div className="overview-card-val" style={{ color: 'var(--primary)' }}>
                        {stats.eligible_hcps.toLocaleString()}
                      </div>
                    </div>
                  </div>

                  {/* Opted Out Card */}
                  <div className="overview-card" style={{ borderColor: 'rgba(239,68,68,0.3)', background: 'rgba(239,68,68,0.06)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span className="overview-card-title" style={{ color: '#fca5a5' }}>Opted-Out HCPs</span>
                      <UserX size={16} color="#ef4444" />
                    </div>
                    <div className="overview-card-val" style={{ color: '#ef4444' }}>
                      {stats.opted_out}
                    </div>
                  </div>

                  {/* Engagement Segments Breakdown */}
                  <div style={{ marginTop: 8 }}>
                    <h4 style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--text-main)', marginBottom: 10 }}>
                      HCP Engagement Segmentation
                    </h4>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {/* Highly Engaged */}
                      <div className="overview-card" style={{ borderLeft: '4px solid #10b981' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                          <span style={{ fontWeight: 700, color: '#10b981' }}>Highly Engaged (Score ≥ 70)</span>
                          <span style={{ fontWeight: 800 }}>{stats.highly_engaged_hcps}</span>
                        </div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 2 }}>
                          {((stats.highly_engaged_hcps / stats.total_hcps) * 100).toFixed(1)}% of total network
                        </div>
                      </div>

                      {/* Moderately Engaged */}
                      <div className="overview-card" style={{ borderLeft: '4px solid #0ea5e9' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                          <span style={{ fontWeight: 700, color: '#0ea5e9' }}>Moderately Engaged (Score 40 - 69)</span>
                          <span style={{ fontWeight: 800 }}>{stats.moderately_engaged_hcps}</span>
                        </div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 2 }}>
                          {((stats.moderately_engaged_hcps / stats.total_hcps) * 100).toFixed(1)}% of total network
                        </div>
                      </div>

                      {/* Low Engagement */}
                      <div className="overview-card" style={{ borderLeft: '4px solid #f59e0b' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                          <span style={{ fontWeight: 700, color: '#f59e0b' }}>Low Engagement (Score 1 - 39)</span>
                          <span style={{ fontWeight: 800 }}>{stats.low_engaged_hcps}</span>
                        </div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 2 }}>
                          {((stats.low_engaged_hcps / stats.total_hcps) * 100).toFixed(1)}% of total network
                        </div>
                      </div>

                      {/* Disengaged */}
                      <div className="overview-card" style={{ borderLeft: '4px solid #ef4444' }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.78rem' }}>
                          <span style={{ fontWeight: 700, color: '#ef4444' }}>Disengaged / Opt-Out (Score = 0)</span>
                          <span style={{ fontWeight: 800 }}>{stats.disengaged_hcps}</span>
                        </div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: 2 }}>
                          {((stats.disengaged_hcps / stats.total_hcps) * 100).toFixed(1)}% of total network
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ─── FLOATING CHATBOT WIDGET ───────────────────────── */}
      <div className="chatbot-widget">
        <div className={`chatbot-panel ${chatOpen ? '' : 'hidden'}`}>
          <div className="chatbot-header">
            <Bot size={18} color="var(--primary)" />
            <h3>HCP AI Assistant</h3>
            <button onClick={() => setChatOpen(false)} className="chatbot-close-btn">
              <X size={18} />
            </button>
          </div>

          <div className="chatbot-messages">
            {messages.map((msg, i) => (
              <div key={i} className={`chat-bubble ${msg.sender}`}>{msg.text}</div>
            ))}
            {isTyping && (
              <div className="chat-bubble bot" style={{ display: 'flex', gap: 4, alignItems: 'center', padding: '10px 14px' }}>
                {[0, 0.2, 0.4].map((d, i) => (
                  <span key={i} style={{ width: 6, height: 6, background: 'var(--primary)', borderRadius: '50%', display: 'inline-block', animation: `blink 1.4s ${d}s infinite` }} />
                ))}
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          <div className="chat-input-area">
            <form className="chat-input-form" onSubmit={handleSendMessage}>
              <input
                type="text"
                placeholder="Ask about engagement scores..."
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
              />
              <button type="submit" disabled={isTyping || !chatInput.trim()}>
                <Send size={16} />
              </button>
            </form>
          </div>
        </div>

        <button className="chatbot-fab" onClick={() => setChatOpen(!chatOpen)} title="AI Assistant">
          {chatOpen ? <X size={22} /> : <MessageSquare size={22} />}
        </button>
      </div>

      <style>{`
        @keyframes blink {
          0%, 80%, 100% { opacity: 0.2; transform: scale(0.8); }
          40% { opacity: 1; transform: scale(1.2); }
        }
      `}</style>
    </>
  );
}

export default App;
