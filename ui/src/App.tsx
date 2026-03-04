import { useState, useRef, useEffect } from 'react';

type LogLevel = 'debug' | 'info' | 'success' | 'warning' | 'error';
type AppStatus = 'idle' | 'running' | 'success' | 'error';
type Theme = 'dark' | 'light';

interface LogEntry {
    timestamp: string;
    text: string;
    level: LogLevel;
}

// SVG Icons as small components
const SunIcon = () => (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="5" />
        <line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" />
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" />
        <line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" />
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" />
    </svg>
);

const MoonIcon = () => (
    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
    </svg>
);

function App() {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [targetPath, setTargetPath] = useState<string>('./my-project');
    const [migrationType, setMigrationType] = useState<string>('react-hooks');
    const [isDryRun, setIsDryRun] = useState<boolean>(true);
    const [status, setStatus] = useState<AppStatus>('idle');
    const [theme, setTheme] = useState<Theme>(() => {
        const saved = localStorage.getItem('cma-theme');
        return (saved === 'light' || saved === 'dark') ? saved : 'dark';
    });

    const [filesScanned, setFilesScanned] = useState<number>(0);
    const [filesMigrated, setFilesMigrated] = useState<number>(0);
    const [issuesFound, setIssuesFound] = useState<number>(0);

    const consoleEndRef = useRef<HTMLDivElement>(null);
    const eventSourceRef = useRef<EventSource | null>(null);

    // Apply theme to DOM
    useEffect(() => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('cma-theme', theme);
    }, [theme]);

    // Auto-scroll
    useEffect(() => {
        if (consoleEndRef.current) {
            consoleEndRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs]);

    const toggleTheme = () => {
        setTheme(prev => prev === 'dark' ? 'light' : 'dark');
    };

    const addLog = (text: string, level: LogLevel = 'info') => {
        const timestamp = new Date().toISOString().substring(11, 19);
        setLogs(prev => [...prev, { timestamp, text, level }]);

        if (text.includes("Found candidate") || text.includes("Scanning")) {
            setFilesScanned(prev => prev + 1);
        }
        if (text.includes("Migrated:")) {
            setFilesMigrated(prev => prev + 1);
        }
        if (level === 'error' || text.includes("Security Error")) {
            setIssuesFound(prev => prev + 1);
        }
    };

    const startAction = (action: 'analyze' | 'run') => {
        if (status === 'running') return;

        setLogs([]);
        setFilesScanned(0);
        setFilesMigrated(0);
        setIssuesFound(0);
        setStatus('running');

        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }

        addLog(`[System] Initiating ${action} sequence for ${migrationType}`, 'debug');

        let url = `/api/${action}?path=${encodeURIComponent(targetPath)}&type=${encodeURIComponent(migrationType)}`;
        if (action === 'run') {
            url += `&dry_run=${isDryRun}`;
        }

        const eventSource = new EventSource(url);
        eventSourceRef.current = eventSource;

        eventSource.onmessage = (event) => {
            const data = event.data;
            if (data === "DONE") {
                eventSource.close();
                setStatus(prev => prev === 'error' ? 'error' : 'success');
                addLog(`=== ${action.toUpperCase()} COMPLETE ===`, 'debug');
            } else if (data.toLowerCase().includes("error") || data.toLowerCase().includes("failed")) {
                addLog(data, 'error');
            } else if (data.includes("Migrated") || data.includes("Found candidate") || data.includes("Complete")) {
                addLog(data, 'success');
            } else if (data.includes("Dry Run")) {
                addLog(data, 'warning');
            } else {
                addLog(data, 'info');
            }
        };

        eventSource.onerror = (err) => {
            console.error("EventSource failed:", err);
            eventSource.close();
            setStatus('error');
            addLog("Connection dropped unexpectedly.", 'error');
        };
    };

    const cancelAction = () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
            setStatus('idle');
            addLog("[System] Sequence terminated by operator.", 'warning');
        }
    };

    const clearLogs = () => setLogs([]);

    const getStatusLabel = () => {
        switch (status) {
            case 'idle': return 'Ready';
            case 'running': return 'Executing';
            case 'success': return 'Completed';
            case 'error': return 'Halted';
        }
    };

    return (
        <div className="app-container">
            {/* Top Navigation */}
            <header className="top-nav">
                <div className="nav-brand">
                    <div className="brand-logo">C</div>
                    <div>
                        <h1 style={{ fontSize: '1rem' }}>Code Migration Assistant</h1>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Enterprise Edition</div>
                    </div>
                </div>

                <div className="nav-right">
                    <div className={`status-pill ${status}`}>
                        <div className="pulse-dot"></div>
                        {getStatusLabel()}
                    </div>
                    <div className="nav-divider"></div>

                    {/* Theme Toggle */}
                    <div className="theme-toggle" onClick={toggleTheme} title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}>
                        <div className="theme-toggle-thumb">
                            {theme === 'dark' ? <MoonIcon /> : <SunIcon />}
                        </div>
                    </div>

                    <div className="nav-divider"></div>
                    <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Operator</span>
                </div>
            </header>

            {/* Main Workspace */}
            <div className="workspace">
                {/* Configuration Sidebar */}
                <aside className="sidebar">
                    <div>
                        <h2 className="section-title">Configuration</h2>
                        <p style={{ marginBottom: '1.5rem' }}>Define migration targets and parameters.</p>

                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label>Target Path</label>
                            <input
                                className="form-control"
                                type="text"
                                value={targetPath}
                                onChange={e => setTargetPath(e.target.value)}
                                placeholder="/var/lib/workspace/my-app"
                            />
                        </div>

                        <div className="form-group" style={{ marginBottom: '1rem' }}>
                            <label>Migration Standard</label>
                            <select
                                className="form-control"
                                value={migrationType}
                                onChange={e => setMigrationType(e.target.value)}
                            >
                                <option value="react-hooks">React: Class → Hooks</option>
                                <option value="vue3">Vue: v2 → v3 Composition</option>
                                <option value="python3">Python: v2.7 → v3.x</option>
                                <option value="typescript" disabled>JS → TypeScript (Beta)</option>
                            </select>
                        </div>

                        <label className="checkbox-wrap" style={{ marginTop: '0.5rem', marginBottom: '2rem' }}>
                            <input
                                type="checkbox"
                                checked={isDryRun}
                                onChange={e => setIsDryRun(e.target.checked)}
                            />
                            <span>Dry Run (Validation Only)</span>
                        </label>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                            {status === 'running' ? (
                                <button className="btn btn-danger" onClick={cancelAction}>
                                    Terminate
                                </button>
                            ) : (
                                <>
                                    <button className="btn btn-secondary" onClick={() => startAction('analyze')}>
                                        Run Analysis
                                    </button>
                                    <button className="btn btn-primary" onClick={() => startAction('run')}>
                                        Execute Migration
                                    </button>
                                </>
                            )}
                        </div>
                    </div>
                </aside>

                {/* Console View */}
                <main className="main-content">
                    <div>
                        <h2 className="section-title">Observability</h2>
                        <div className="metrics-grid">
                            <div className={`metric-card ${status !== 'idle' ? 'active' : ''}`}>
                                <div className="metric-label">Scanned</div>
                                <div className="metric-value">{filesScanned}</div>
                                <div className="metric-subtext">AST nodes parsed</div>
                            </div>
                            <div className={`metric-card ${filesMigrated > 0 ? 'success' : ''}`}>
                                <div className="metric-label">Migrated</div>
                                <div className="metric-value">{filesMigrated}</div>
                                <div className="metric-subtext">Transformed successfully</div>
                            </div>
                            <div className={`metric-card ${issuesFound > 0 ? 'error' : ''}`}>
                                <div className="metric-label">Issues</div>
                                <div className="metric-value" style={{ color: issuesFound > 0 ? 'var(--error-color)' : 'inherit' }}>{issuesFound}</div>
                                <div className="metric-subtext">Errors flagged</div>
                            </div>
                        </div>
                    </div>

                    <div className="console-wrapper">
                        <div className="console-header">
                            <div className="console-tabs">
                                <div className="console-tab active">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
                                    stdout
                                </div>
                                <div className="console-tab">
                                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
                                    stderr
                                </div>
                            </div>
                            <div className="console-actions">
                                <button className="console-button" onClick={clearLogs} title="Clear">
                                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                                </button>
                            </div>
                        </div>
                        <div className="console-body">
                            {logs.length === 0 ? (
                                <div className="empty-state">
                                    <div className="empty-icon">
                                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="4 17 10 11 4 5"></polyline><line x1="12" y1="19" x2="20" y2="19"></line></svg>
                                    </div>
                                    <div>
                                        <div style={{ color: 'var(--text-primary)', fontWeight: 500 }}>Awaiting Instructions</div>
                                        <div style={{ fontSize: '0.85rem' }}>Trigger an analysis or migration to stream output.</div>
                                    </div>
                                </div>
                            ) : (
                                logs.map((log, idx) => (
                                    <div key={idx} className="log-line">
                                        <span className="log-time">{log.timestamp}</span>
                                        <span className={`log-content ${log.level}`}>{log.text}</span>
                                    </div>
                                ))
                            )}
                            <div ref={consoleEndRef} />
                        </div>
                    </div>
                </main>
            </div>
        </div>
    );
}

export default App;
