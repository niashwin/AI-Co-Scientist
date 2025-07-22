import React from 'react';

export const AgentProgress = ({ currentAgent, iteration, progress, isRunning }) => {
  const getAgentStatus = (agentName) => {
    if (!progress || !progress[agentName]) {
      return 'pending';
    }
    return progress[agentName].status || 'pending';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'running': return '#3b82f6';
      case 'completed': return '#10b981';
      case 'error': return '#ef4444';
      default: return '#9ca3af';
    }
  };

  const getStatusLabel = (status) => {
    switch (status) {
      case 'running': return 'Running';
      case 'completed': return 'Completed';
      case 'error': return 'Error';
      default: return 'Pending';
    }
  };

  const agents = [
    { name: 'generation', label: 'Generation Agent' },
    { name: 'reflection', label: 'Reflection Agent' },
    { name: 'ranking', label: 'Ranking Agent' }
  ];

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '8px',
      padding: '20px',
      border: '1px solid #e5e7eb',
      marginBottom: '24px'
    }}>
      <h3 style={{ 
        fontSize: '16px', 
        fontWeight: '600', 
        color: '#111827', 
        marginBottom: '16px' 
      }}>
        Research Progress - Iteration {iteration}
      </h3>
      
      <div style={{ display: 'flex', gap: '16px' }}>
        {agents.map((agent) => {
          const status = getAgentStatus(agent.name);
          const isActive = currentAgent === agent.name && isRunning;
          
          return (
            <div key={agent.name} style={{
              flex: 1,
              padding: '16px',
              backgroundColor: isActive ? '#f0f9ff' : '#f9fafb',
              borderRadius: '6px',
              border: `2px solid ${isActive ? '#3b82f6' : '#e5e7eb'}`,
              transition: 'all 0.2s ease'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                marginBottom: '8px'
              }}>
                <span style={{
                  fontSize: '14px',
                  fontWeight: '600',
                  color: '#374151'
                }}>
                  {agent.label}
                </span>
                
                <div style={{
                  width: '12px',
                  height: '12px',
                  borderRadius: '50%',
                  backgroundColor: getStatusColor(status)
                }} />
              </div>
              
              <span style={{
                fontSize: '12px',
                color: '#6b7280',
                fontWeight: '500'
              }}>
                {getStatusLabel(status)}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}; 