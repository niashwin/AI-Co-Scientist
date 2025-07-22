import React, { useState, useEffect } from 'react';
import { AgentProgress } from './AgentProgress';
import { HypothesisCard } from './HypothesisCard';

export const ResearchSession = () => {
  const [sessionId, setSessionId] = useState(null);
  const [researchGoal, setResearchGoal] = useState('');
  const [hypotheses, setHypotheses] = useState([]);
  const [isStarted, setIsStarted] = useState(false);
  const [error, setError] = useState(null);
  const [sessionStatus, setSessionStatus] = useState('idle');
  
  // NEW: Domain detection state
  const [domainContext, setDomainContext] = useState(null);
  const [domainDetectionLoading, setDomainDetectionLoading] = useState(false);
  
  // Research parameters
  const [maxIterations, setMaxIterations] = useState(3);
  const [hypothesesPerIteration, setHypothesesPerIteration] = useState(1);
  
  // Real WebSocket connection
  const [ws, setWs] = useState(null);
  const [wsConnected, setWsConnected] = useState(false);
  
  // Real agent progress state
  const [currentAgent, setCurrentAgent] = useState('');
  const [iteration, setIteration] = useState(0);
  const [progress, setProgress] = useState({
    generation: 'pending',
    reflection: 'pending',
    ranking: 'pending'
  });
  const [isRunning, setIsRunning] = useState(false);

  // NEW: Domain detection when research goal changes
  useEffect(() => {
    const detectDomain = async () => {
      if (researchGoal.trim().length > 15 && !isStarted) {
        setDomainDetectionLoading(true);
        try {
          const response = await fetch('http://localhost:8000/api/research/detect-domain', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ research_question: researchGoal })
          });
          
          if (response.ok) {
            const domain = await response.json();
            setDomainContext(domain);
          }
        } catch (error) {
          console.log('Domain detection failed, using general context');
          setDomainContext(getDefaultDomainContext());
        } finally {
          setDomainDetectionLoading(false);
        }
      } else if (researchGoal.trim().length <= 15) {
        setDomainContext(null);
      }
    };

    const debounceTimer = setTimeout(detectDomain, 1000);
    return () => clearTimeout(debounceTimer);
  }, [researchGoal, isStarted]);

  // NEW: Get default domain context
  const getDefaultDomainContext = () => ({
    domain: "general",
    expert_role: "scientific researcher",
    research_focus: "scientific research",
    hypothesis_type: "research hypothesis"
  });

  // NEW: Dynamic placeholder text based on detected domain
  const getPlaceholderText = () => {
    if (!domainContext || !domainContext.domain) {
      return "Enter your research question... (e.g., 'How can we solve climate change?')";
    }
    
    const examples = {
      medicine: "Enter your medical research question... (e.g., 'Can aspirin reduce stroke risk?')",
      physics: "Enter your physics research question... (e.g., 'How can we make quantum computers more stable?')",
      computer_science: "Enter your computer science question... (e.g., 'How can AI improve protein folding prediction?')",
      chemistry: "Enter your chemistry question... (e.g., 'What are the best catalysts for carbon capture?')",
      biology: "Enter your biology question... (e.g., 'How do cells repair DNA damage?')",
      psychology: "Enter your psychology question... (e.g., 'What factors influence memory formation?')",
      engineering: "Enter your engineering question... (e.g., 'How can we build more efficient solar panels?')",
      mathematics: "Enter your mathematics question... (e.g., 'What are the applications of topology in data science?')"
    };
    
    return examples[domainContext.domain] || "Enter your scientific research question...";
  };

  // NEW: Dynamic description text based on detected domain
  const getDescriptionText = () => {
    if (!domainContext || !domainContext.domain) {
      return 'Our AI agents will analyze your research goal and generate evidence-based hypotheses.';
    }
    
    const descriptions = {
      'medical_research': 'Specialized for medical research with clinical evidence analysis.',
      'drug_repurposing': 'Optimized for pharmaceutical research and drug discovery.',
      'computer_science': 'Tailored for computational research and algorithm development.',
      'physics': 'Configured for theoretical and experimental physics research.',
      'environmental_science': 'Designed for environmental impact and sustainability research.',
      'climate_science': 'Specialized for climate modeling and atmospheric research.',
      'general_scientific_research': 'Adaptable to diverse scientific research domains.'
    };
    
    return descriptions[domainContext.domain] || 'Our AI agents will analyze your research goal and generate evidence-based hypotheses.';
  };

  // NEW: Get domain icon
  const getDomainIcon = () => {
    if (!domainContext || !domainContext.domain) return '';
    
    const iconMap = {
      'medical_research': 'Medical',
      'drug_repurposing': 'Pharmaceutical', 
      'computer_science': 'Computing',
      'physics': 'Physics',
      'environmental_science': 'Environmental',
      'climate_science': 'Climate',
      'general_scientific_research': 'Research'
    };
    
    return iconMap[domainContext.domain] || 'Research';
  };

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const websocket = new WebSocket('ws://localhost:8000/ws');
        
        websocket.onopen = () => {
          console.log('WebSocket connected');
          setWsConnected(true);
        };
        
        websocket.onmessage = (event) => {
          try {
            const message = JSON.parse(event.data);
            handleWebSocketMessage(message);
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };
        
        websocket.onclose = () => {
          console.log('WebSocket disconnected');
          setWsConnected(false);
          // Attempt to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };
        
        websocket.onerror = (error) => {
          console.error('WebSocket error:', error);
          setWsConnected(false);
        };
        
        setWs(websocket);
        
      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        setWsConnected(false);
        // Retry connection after 5 seconds
        setTimeout(connectWebSocket, 5000);
      }
    };

    connectWebSocket();

    // Cleanup on unmount
    return () => {
      if (ws) {
        ws.close();
      }
    };
  }, []);

  const handleWebSocketMessage = (message) => {
    console.log('Received WebSocket message:', message);
    
    switch(message.type) {
      case 'agent_update':
        handleAgentUpdate(message);
        break;
      case 'session_update':
        handleSessionUpdate(message);
        break;
      default:
        console.log('Unknown message type:', message.type);
    }
  };

  const handleAgentUpdate = (message) => {
    const { agent, status, data } = message;
    
    if (agent && status) {
      setCurrentAgent(agent);
      
      // Update progress for the specific agent
      setProgress(prev => ({
        ...prev,
        [agent.toLowerCase()]: status
      }));
      
      // Set running state based on agent status
      if (status === 'running') {
        setIsRunning(true);
      }
      
      // Handle completed agent updates
      if (status === 'completed') {
        if (agent === 'generation' && data.hypothesis) {
          // Add new hypothesis (but don't show it yet until reflection is complete)
          setHypotheses(prev => {
            const existing = prev.find(h => h.id === data.hypothesis.id);
            if (!existing) {
              return [...prev, { ...data.hypothesis, isProcessing: true }];
            }
            return prev;
          });
        }
        
        if (agent === 'reflection' && data.review) {
          // Update hypothesis with reflection data and mark as complete for display
          setHypotheses(prev => prev.map(h => {
            if (h.iteration === iteration && h.isProcessing) {
              return {
                ...h,
                review: data.review.review || data.review,
                score: data.review.score || h.score,
                isProcessing: false // Now ready to display
              };
            }
            return h;
          }));
        }
        
        if (agent === 'ranking' && data.ranked_hypotheses) {
          // Update hypotheses with ranking
          setHypotheses(data.ranked_hypotheses.map(h => ({ ...h, isProcessing: false })));
        }
      }
    }
  };

  const handleSessionUpdate = (message) => {
    const { event_type, data } = message;
    
    switch(event_type) {
      case 'research_started':
        setSessionStatus('running');
        setIsRunning(true);
        break;
        
      case 'iteration_start':
        if (data.iteration) {
          setIteration(data.iteration);
          // Reset progress for new iteration
          setProgress({
            generation: 'pending',
            reflection: 'pending',
            ranking: 'pending'
          });
        }
        break;
        
      case 'research_completed':
        setSessionStatus('completed');
        setIsStarted(false);
        setIsRunning(false);
        setProgress({
          generation: 'completed',
          reflection: 'completed',
          ranking: 'completed'
        });
        break;
        
      case 'research_error':
        setSessionStatus('error');
        setError(data.error || 'Research session failed');
        setIsStarted(false);
        setIsRunning(false);
        break;
        
      default:
        console.log('Unknown session event:', event_type);
    }
  };

  const startResearch = async () => {
    if (!researchGoal.trim()) {
      setError('Please enter a research goal');
      return;
    }

    if (!wsConnected) {
      setError('WebSocket not connected. Please wait and try again.');
      return;
    }

    try {
      setError(null);
      setIsStarted(true);
      setSessionStatus('running');
      setHypotheses([]); // Clear previous hypotheses
      
      // Generate a session ID
      const newSessionId = `session_${Date.now()}`;
      setSessionId(newSessionId);

      // Start research via API
      const response = await fetch('http://localhost:8000/api/research/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          research_goal: researchGoal,
          session_id: newSessionId,
          max_iterations: maxIterations,
          hypotheses_per_iteration: hypothesesPerIteration
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log('Research started:', result);
      
    } catch (err) {
      console.error('Failed to start research:', err);
      setError(err instanceof Error ? err.message : 'Failed to start research session');
      setIsStarted(false);
      setSessionStatus('error');
    }
  };

  const stopResearch = () => {
    setIsStarted(false);
    setSessionStatus('idle');
    setIsRunning(false);
    setProgress({ generation: 'pending', reflection: 'pending', ranking: 'pending' });
    setCurrentAgent('');
    setIteration(0);
  };

  const resetSession = () => {
    setSessionId(null);
    setResearchGoal('');
    setHypotheses([]);
    setIsStarted(false);
    setError(null);
    setSessionStatus('idle');
    setIsRunning(false);
    setProgress({ generation: 'pending', reflection: 'pending', ranking: 'pending' });
    setCurrentAgent('');
    setIteration(0);
    setDomainContext(null); // NEW: Reset domain context
    setMaxIterations(3);
    setHypothesesPerIteration(1);
  };

  // Filter hypotheses - only show completed ones
  const completedHypotheses = hypotheses.filter(h => !h.isProcessing && h.review && h.score);
  const processingCount = hypotheses.filter(h => h.isProcessing).length;

  return (
    <div>
      {/* Session Setup */}
      <div style={{
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        padding: '24px',
        border: '1px solid #e2e8f0',
        marginBottom: '24px'
      }}>
        <h2 style={{ 
          fontSize: '24px', 
          fontWeight: '600', 
          color: '#1e293b', 
          marginBottom: '16px' 
        }}>
          🧪 Research Session
        </h2>

        {/* Connection Status */}
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          gap: '12px', 
          marginBottom: '16px' 
        }}>
          <div style={{
            padding: '4px 8px',
            backgroundColor: wsConnected ? '#dcfce7' : '#fee2e2',
            color: wsConnected ? '#166534' : '#dc2626',
            borderRadius: '4px',
            fontSize: '12px',
            fontWeight: '500'
          }}>
            WebSocket: {wsConnected ? 'Connected' : 'Disconnected'}
          </div>
          
          {sessionId && (
            <div style={{
              padding: '4px 8px',
              backgroundColor: '#f1f5f9',
              color: '#374151',
              borderRadius: '4px',
              fontSize: '12px',
              fontFamily: 'monospace'
            }}>
              Session: {sessionId.substring(8)}
            </div>
          )}

          {/* NEW: Domain Detection Status */}
          {domainDetectionLoading && (
            <div style={{
              padding: '4px 8px',
              backgroundColor: '#dbeafe',
              color: '#1e40af',
              borderRadius: '4px',
              fontSize: '12px',
              fontWeight: '500'
            }}>
              🔍 Analyzing domain...
            </div>
          )}

          {/* NEW: Show Detected Domain */}
          {domainContext && !domainDetectionLoading && (
            <div style={{
              padding: '4px 8px',
              backgroundColor: '#f3f4f6',
              color: '#374151',
              borderRadius: '4px',
              fontSize: '12px',
              fontWeight: '500'
            }}>
              {getDomainIcon()} {domainContext && domainContext.domain ? domainContext.domain.charAt(0).toUpperCase() + domainContext.domain.slice(1).replace('_', ' ') : 'Scientific'} Research
            </div>
          )}
        </div>

        {/* Research Goal Input */}
        <div style={{ marginBottom: '16px' }}>
          <label style={{
            display: 'block',
            fontSize: '14px',
            fontWeight: '500',
            color: '#374151',
            marginBottom: '8px'
          }}>
            Research Goal
          </label>
          <textarea
            value={researchGoal}
            onChange={(e) => setResearchGoal(e.target.value)}
            placeholder={getPlaceholderText()}
            disabled={isStarted}
            style={{
              width: '100%',
              minHeight: '80px',
              padding: '12px',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '14px',
              fontFamily: 'inherit',
              resize: 'vertical',
              backgroundColor: isStarted ? '#f9fafb' : '#ffffff'
            }}
          />
        </div>

        {/* Research Parameters */}
        <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
          <div style={{ flex: 1 }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Max Iterations (1-10)
            </label>
            <input
              type="number"
              min="1"
              max="10"
              value={maxIterations}
              onChange={(e) => setMaxIterations(parseInt(e.target.value) || 1)}
              disabled={isStarted}
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px',
                backgroundColor: isStarted ? '#f9fafb' : '#ffffff'
              }}
            />
          </div>
          <div style={{ flex: 1 }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: '500',
              color: '#374151',
              marginBottom: '8px'
            }}>
              Hypotheses per Iteration (1-5)
            </label>
            <input
              type="number"
              min="1"
              max="5"
              value={hypothesesPerIteration}
              onChange={(e) => setHypothesesPerIteration(parseInt(e.target.value) || 1)}
              disabled={isStarted}
              style={{
                width: '100%',
                padding: '10px 12px',
                border: '1px solid #d1d5db',
                borderRadius: '6px',
                fontSize: '14px',
                backgroundColor: isStarted ? '#f9fafb' : '#ffffff'
              }}
            />
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div style={{
            padding: '12px',
            backgroundColor: '#fee2e2',
            borderRadius: '6px',
            marginBottom: '16px'
          }}>
            <div style={{ fontSize: '14px', color: '#dc2626' }}>
              ❌ {error}
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {!isStarted ? (
            <button
              onClick={startResearch}
              disabled={!researchGoal.trim() || !wsConnected}
              style={{
                padding: '12px 24px',
                backgroundColor: researchGoal.trim() && wsConnected ? '#3b82f6' : '#9ca3af',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: researchGoal.trim() && wsConnected ? 'pointer' : 'not-allowed',
                transition: 'background-color 0.2s ease'
              }}
            >
              Start Research
            </button>
          ) : (
            <button
              onClick={stopResearch}
              style={{
                padding: '12px 24px',
                backgroundColor: '#ef4444',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                fontSize: '14px',
                fontWeight: '500',
                cursor: 'pointer'
              }}
            >
              Stop Research
            </button>
          )}

          <button
            onClick={resetSession}
            disabled={isStarted}
            style={{
              padding: '12px 24px',
              backgroundColor: isStarted ? '#9ca3af' : '#f3f4f6',
              color: isStarted ? '#ffffff' : '#374151',
              border: '1px solid #d1d5db',
              borderRadius: '6px',
              fontSize: '14px',
              fontWeight: '500',
              cursor: isStarted ? 'not-allowed' : 'pointer'
            }}
          >
            Reset
          </button>
        </div>

        {/* Session Status */}
        <div style={{ marginTop: '16px' }}>
          <div style={{
            padding: '8px 12px',
            backgroundColor: 
              sessionStatus === 'running' ? '#dbeafe' :
              sessionStatus === 'completed' ? '#dcfce7' :
              sessionStatus === 'error' ? '#fee2e2' :
              '#f3f4f6',
            color:
              sessionStatus === 'running' ? '#1e40af' :
              sessionStatus === 'completed' ? '#166534' :
              sessionStatus === 'error' ? '#dc2626' :
              '#6b7280',
            borderRadius: '6px',
            fontSize: '14px',
            fontWeight: '500'
          }}>
            Status: {sessionStatus && typeof sessionStatus === 'string' ? sessionStatus.charAt(0).toUpperCase() + sessionStatus.slice(1) : 'Unknown'}
            {isRunning && ' (Agents active)'}
          </div>
        </div>
      </div>

      {/* Agent Progress */}
      {(isStarted || completedHypotheses.length > 0) && (
        <AgentProgress
          currentAgent={currentAgent}
          iteration={iteration}
          progress={progress}
          isRunning={isRunning}
        />
      )}

      {/* Processing Status */}
      {processingCount > 0 && (
        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          padding: '20px',
          border: '1px solid #e2e8f0',
          marginBottom: '24px'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <div style={{ 
              width: '20px',
              height: '20px',
              border: '2px solid #3b82f6',
              borderTop: '2px solid transparent',
              borderRadius: '50%',
              animation: 'spin 1s linear infinite'
            }}></div>
            <div>
              <div style={{ fontWeight: '600', color: '#1e293b' }}>
                Processing {processingCount} hypothesis{processingCount > 1 ? 'es' : ''}...
              </div>
              <div style={{ fontSize: '14px', color: '#64748b' }}>
                Agents are currently reviewing and analyzing the generated hypotheses
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Completed Hypotheses Section */}
      {completedHypotheses.length > 0 && (
        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          padding: '24px',
          border: '1px solid #e2e8f0',
          marginBottom: '24px'
        }}>
          <h3 style={{ 
            fontSize: '20px', 
            fontWeight: '600', 
            color: '#1e293b', 
            marginBottom: '16px' 
          }}>
            Generated Hypotheses ({completedHypotheses.length})
          </h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {completedHypotheses
              .sort((a, b) => (b.score || 0) - (a.score || 0))
              .map((hypothesis, index) => (
                <HypothesisCard
                  key={hypothesis.id}
                  hypothesis={hypothesis}
                  rank={index + 1}
                />
              ))
            }
          </div>
        </div>
      )}

      {/* Ready to Start Message */}
      {!isStarted && completedHypotheses.length === 0 && sessionStatus === 'idle' && (
        <div style={{
          backgroundColor: '#ffffff',
          borderRadius: '12px',
          padding: '48px 24px',
          border: '1px solid #e2e8f0',
          textAlign: 'center'
        }}>
          <h3 style={{ 
            fontSize: '20px', 
            fontWeight: '600', 
            color: '#1e293b', 
            marginBottom: '8px' 
          }}>
            Ready to Start Research
          </h3>
          <p style={{ fontSize: '14px', color: '#64748b', marginBottom: '24px' }}>
            Enter your research goal above and click "Start Research" to begin the multi-agent workflow.
            <br />
            {getDescriptionText()}
          </p>
          <div style={{ 
            fontSize: '12px', 
            color: '#9ca3af',
            fontStyle: 'italic'
          }}>
            {domainContext && domainContext.domain ? 
              `Detected: ${domainContext.domain.charAt(0).toUpperCase() + domainContext.domain.slice(1).replace('_', ' ')} Research` :
              'The system automatically detects your research domain'
            }
          </div>
        </div>
      )}

      {/* Add CSS for spin animation */}
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}; 