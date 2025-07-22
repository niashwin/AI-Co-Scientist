import React from 'react';
import './index.css';
import { ResearchSession } from './components/ResearchSession';

function App() {
  const [activeTab, setActiveTab] = React.useState('research');
  const [backendHealth, setBackendHealth] = React.useState('connecting');

  React.useEffect(() => {
    checkBackendHealth();
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/system/health');
      if (response.ok) {
        setBackendHealth('healthy');
      } else {
        setBackendHealth('error');
      }
    } catch (error) {
      console.error('Backend health check failed:', error);
      setBackendHealth('error');
    }
  };

  const getHealthIcon = () => {
    switch (backendHealth) {
      case 'healthy': return '✅';
      case 'error': return '❌';
      case 'connecting': return '🔄';
      default: return '❓';
    }
  };

  const getHealthColor = () => {
    switch (backendHealth) {
      case 'healthy': return '#22c55e';
      case 'error': return '#ef4444';
      case 'connecting': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  const testGenerationAgent = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/agents/generation/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          research_goal: 'How can machine learning improve climate change predictions?'
        })
      });
      const result = await response.json();
      alert(response.ok ? 'Generation Agent: SUCCESS!' : `Error: ${result.detail || 'Failed'}`);
    } catch (error) {
      alert(`Generation Agent Error: ${error.message}`);
    }
  };

  const testReflectionAgent = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/agents/reflection/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hypothesis: 'Neural networks can predict weather patterns with 95% accuracy using satellite data and historical climate models'
        })
      });
      const result = await response.json();
      alert(response.ok ? 'Reflection Agent: SUCCESS!' : `Error: ${result.detail || 'Failed'}`);
    } catch (error) {
      alert(`Reflection Agent Error: ${error.message}`);
    }
  };

  const testRankingAgent = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/agents/ranking/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          hypotheses: [
            { content: 'Quantum computing can solve optimization problems exponentially faster', score: 0.8 },
            { content: 'AI can detect cancer from medical images with 99% accuracy', score: 0.7 }
          ]
        })
      });
      const result = await response.json();
      alert(response.ok ? 'Ranking Agent: SUCCESS!' : `Error: ${result.detail || 'Failed'}`);
    } catch (error) {
      alert(`Ranking Agent Error: ${error.message}`);
    }
  };

  return (
    <div style={{ 
      minHeight: '100vh', 
      backgroundColor: '#f8fafc',
      fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif' 
    }}>
      {/* Header */}
      <header style={{
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e5e7eb',
        padding: '16px 0',
        marginBottom: '24px'
      }}>
        <div style={{
          maxWidth: '1200px',
          margin: '0 auto',
          padding: '0 20px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <h1 style={{
              fontSize: '24px',
              fontWeight: '700',
              color: '#111827',
              margin: 0
            }}>
              AI Co-Scientist
            </h1>
            <span style={{
              fontSize: '14px',
              color: '#6b7280',
              fontWeight: '500'
            }}>
              Multi-Agent Scientific Research Platform
            </span>
          </div>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '12px'
          }}>
            <span style={{
              padding: '6px 12px',
              backgroundColor: '#dcfce7',
              color: '#166534',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: '500'
            }}>
              Backend: healthy
            </span>
          </div>
        </div>
      </header>

      {/* Navigation */}
      <nav style={{
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e2e8f0',
        padding: '0 24px'
      }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ display: 'flex', gap: '8px' }}>
            {['research', 'testing'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                style={{
                  padding: '12px 16px',
                  backgroundColor: activeTab === tab ? '#f1f5f9' : 'transparent',
                  color: activeTab === tab ? '#3b82f6' : '#64748b',
                  border: 'none',
                  borderBottom: activeTab === tab ? '2px solid #3b82f6' : '2px solid transparent',
                  fontSize: '14px',
                  fontWeight: '500',
                  cursor: 'pointer',
                  textTransform: 'capitalize'
                }}
              >
                {tab === 'research' ? '🧬 Research Session' : '🧪 Agent Testing'}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main style={{ 
        maxWidth: '1200px', 
        margin: '24px auto',
        padding: '0 24px'
      }}>
        {activeTab === 'research' && (
          <ResearchSession />
        )}
        
        {activeTab === 'testing' && (
          <div>
            {/* API Integration Status */}
            <div style={{
              backgroundColor: '#ffffff',
              borderRadius: '12px',
              padding: '24px',
              border: '1px solid #e2e8f0',
              marginBottom: '24px'
            }}>
              <h2 style={{ 
                fontSize: '20px', 
                fontWeight: '600', 
                color: '#1e293b', 
                marginBottom: '16px' 
              }}>
                🔧 Agent Testing Dashboard
              </h2>
              <p style={{ 
                fontSize: '14px', 
                color: '#64748b', 
                marginBottom: '20px' 
              }}>
                Test individual agents to verify they're working correctly across different scientific domains
              </p>

              <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
                gap: '16px'
              }}>
                <div style={{
                  padding: '20px',
                  backgroundColor: '#f8fafc',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0'
                }}>
                  <h3 style={{ 
                    fontSize: '16px', 
                    fontWeight: '600', 
                    color: '#1e293b', 
                    marginBottom: '8px' 
                  }}>
                    🤖 Generation Agent
                  </h3>
                  <p style={{ 
                    fontSize: '13px', 
                    color: '#64748b', 
                    marginBottom: '12px' 
                  }}>
                    Tests hypothesis generation from research goals across any scientific domain
                  </p>
                  <button 
                    onClick={testGenerationAgent}
                    style={{
                      width: '100%',
                      padding: '10px',
                      backgroundColor: '#3b82f6',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '14px',
                      fontWeight: '500',
                      cursor: 'pointer'
                    }}
                  >
                    Test Generation Agent
                  </button>
                </div>

                <div style={{
                  padding: '20px',
                  backgroundColor: '#f8fafc',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0'
                }}>
                  <h3 style={{ 
                    fontSize: '16px', 
                    fontWeight: '600', 
                    color: '#1e293b', 
                    marginBottom: '8px' 
                  }}>
                    🔍 Reflection Agent
                  </h3>
                  <p style={{ 
                    fontSize: '13px', 
                    color: '#64748b', 
                    marginBottom: '12px' 
                  }}>
                    Tests hypothesis quality assessment and scientific review
                  </p>
                  <button 
                    onClick={testReflectionAgent}
                    style={{
                      width: '100%',
                      padding: '10px',
                      backgroundColor: '#10b981',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '14px',
                      fontWeight: '500',
                      cursor: 'pointer'
                    }}
                  >
                    Test Reflection Agent
                  </button>
                </div>

                <div style={{
                  padding: '20px',
                  backgroundColor: '#f8fafc',
                  borderRadius: '8px',
                  border: '1px solid #e2e8f0'
                }}>
                  <h3 style={{ 
                    fontSize: '16px', 
                    fontWeight: '600', 
                    color: '#1e293b', 
                    marginBottom: '8px' 
                  }}>
                    📊 Ranking Agent
                  </h3>
                  <p style={{ 
                    fontSize: '13px', 
                    color: '#64748b', 
                    marginBottom: '12px' 
                  }}>
                    Tests hypothesis ranking and comparison across research domains
                  </p>
                  <button 
                    onClick={testRankingAgent}
                    style={{
                      width: '100%',
                      padding: '10px',
                      backgroundColor: '#f59e0b',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      fontSize: '14px',
                      fontWeight: '500',
                      cursor: 'pointer'
                    }}
                  >
                    Test Ranking Agent
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App; 