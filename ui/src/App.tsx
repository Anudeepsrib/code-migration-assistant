import { useState, useRef, useEffect } from 'react';

type LogType = 'info' | 'error' | 'success' | 'warning' | 'default';

interface LogEntryProps {
    text: string;
    type: LogType;
}

function App() {
    const [logs, setLogs] = useState<LogEntryProps[]>([]);
    const [targetPath, setTargetPath] = useState<string>('./my-project');
    const [migrationType, setMigrationType] = useState<string>('react-hooks');
    const [isDryRun, setIsDryRun] = useState<boolean>(true);
    const [status, setStatus] = useState<'idle' | 'running' | 'success' | 'error'>('idle');

    const bottomRef = useRef<HTMLDivElement>(null);
    const eventSourceRef = useRef<EventSource | null>(null);

    useEffect(() => {
        if (bottomRef.current) {
            bottomRef.current.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs]);

    const addLog = (text: string, type: LogType = 'default') => {
        setLogs(prev => [...prev, { text, type }]);
    };

    const startProcess = (action: 'analyze' | 'run') => {
        // Prevent starting if already running
        if (status === 'running') return;

        // Clear previous state
        setLogs([]);
        setStatus('running');

        // Close existing event source if any
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
        }

        addLog(`Initiating ${action} for ${migrationType}...`, 'info');

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
                setStatus('success');
                addLog(`=== ${action.toUpperCase()} COMPLETE ===`, 'success');
            } else if (data.includes("Error:") || data.includes("Failed")) {
                addLog(data, 'error');
                // We do not stop the action immediately on a single file error, unless it's a critical error.
            } else if (data.includes("Migrated") || data.includes("Found candidate")) {
                addLog(data, 'success');
            } else if (data.includes("Dry Run")) {
                addLog(data, 'warning');
            } else {
                addLog(data, 'default');
            }
        };

        eventSource.onerror = (err) => {
            console.error("EventSource failed:", err);
            eventSource.close();
            setStatus('error');
            addLog("Connection to backend lost or an error occurred.", 'error');
        };
    };

    const stopProcess = () => {
        if (eventSourceRef.current) {
            eventSourceRef.current.close();
            eventSourceRef.current = null;
            setStatus('idle');
            addLog("Process forcefully stopped by user.", 'warning');
        }
    };

    return (
        <div className="dashboard-layout">
            {/* Sidebar Controls */}
            <section className="glass-panel controls-section">
                <div>
                    <h2>Code Migration</h2>
                    <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '1.5rem' }}>
                        Transform and modernize your codebase automatically with intelligent confidence scoring.
                    </p>
                </div>

                <div className="form-group">
                    <label>Target Path (File or Directory)</label>
                    <input
                        type="text"
                        value={targetPath}
                        onChange={e => setTargetPath(e.target.value)}
                        placeholder="./src"
                    />
                </div>

                <div className="form-group">
                    <label>Migration Type</label>
                    <select value={migrationType} onChange={e => setMigrationType(e.target.value)}>
                        <option value="react-hooks">React Class immediately - Functional Hooks</option>
                        <option value="vue3">Vue 2 - Vue 3 Composition API</option>
                        <option value="python3">Python 2 - Python 3</option>
                    </select>
                </div>

                <div className="form-group" style={{ marginTop: '0.5rem' }}>
                    <label className="checkbox-group">
                        <input
                            type="checkbox"
                            checked={isDryRun}
                            onChange={e => setIsDryRun(e.target.checked)}
                        />
                        Dry Run (Preview changes only)
                    </label>
                </div>

                <div style={{ flex: 1 }}></div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>Status</span>
                        <span className={`status-badge ${status}`}>
                            {status === 'running' && <span className="loader" style={{ marginRight: '6px', width: '10px', height: '10px', borderWidth: '1px' }}></span>}
                            {status.toUpperCase()}
                        </span>
                    </div>

                    {status === 'running' ? (
                        <button className="action-button" style={{ background: '#ef4444' }} onClick={stopProcess}>
                            Stop Process
                        </button>
                    ) : (
                        <>
                            <button className="action-button" style={{ background: 'rgba(255,255,255,0.1)' }} onClick={() => startProcess('analyze')}>
                                🔍 Analyze Confidence
                            </button>
                            <button className="action-button" onClick={() => startProcess('run')}>
                                🚀 Start Migration
                            </button>
                        </>
                    )}
                </div>
            </section>

            {/* Main Terminal Window */}
            <section className="terminal-window glass-panel" style={{ padding: 0 }}>
                <div className="terminal-header">
                    <div className="window-dots">
                        <div className="dot red"></div>
                        <div className="dot yellow"></div>
                        <div className="dot green"></div>
                    </div>
                    <div className="terminal-title">Migration Output Console</div>
                </div>
                <div className="terminal-content">
                    {logs.length === 0 && (
                        <div style={{ color: '#64748b', fontStyle: 'italic', textAlign: 'center', marginTop: '100px' }}>
                            Awaiting instructions...<br />Select a path and click analyze or start migration.
                        </div>
                    )}
                    {logs.map((log, index) => (
                        <div key={index} className={`log-entry ${log.type}`}>
                            <span style={{ color: '#64748b', marginRight: '10px' }}>{`[${new Date().toLocaleTimeString()}]`}</span>
                            {log.text}
                        </div>
                    ))}
                    <div ref={bottomRef} />
                </div>
            </section>
        </div>
    );
}

export default App;
