import React, { useState } from 'react';

export const HypothesisCard = ({ 
  hypothesis, 
  isExpanded: initialExpanded = false 
}) => {
  const [isExpanded, setIsExpanded] = useState(initialExpanded);

  const getScoreColor = (score) => {
    if (score >= 0.8) return '#059669'; // Professional green
    if (score >= 0.6) return '#d97706'; // Professional amber
    if (score >= 0.4) return '#dc2626'; // Professional red
    return '#6b7280'; // Gray
  };

  const getScoreLabel = (score) => {
    if (score >= 0.8) return 'High Quality';
    if (score >= 0.6) return 'Good Quality';
    if (score >= 0.4) return 'Moderate Quality';
    return 'Needs Review';
  };

  // Parse hypothesis into structured sections
  const parseHypothesis = (content) => {
    if (!content) return { title: 'Unknown Hypothesis', sections: [] };
    
    // Try to extract a title (first sentence or up to first colon/period)
    const titleMatch = content.match(/^([^:.]{10,100})[:.]/);
    const title = titleMatch ? titleMatch[1].trim() : content.substring(0, 80) + '...';
    
    // Split into sections based on numbered points or clear breaks
    const sections = [];
    const lines = content.split(/\d+\.\s+|\n\n+/);
    
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim();
      if (line.length > 20) {
        // Try to identify section type
        let sectionType = 'Details';
        if (line.toLowerCase().includes('theoretical') || line.toLowerCase().includes('model')) {
          sectionType = 'Theoretical Framework';
        } else if (line.toLowerCase().includes('mechanism') || line.toLowerCase().includes('process')) {
          sectionType = 'Mechanism';
        } else if (line.toLowerCase().includes('rationale') || line.toLowerCase().includes('justification')) {
          sectionType = 'Scientific Rationale';
        } else if (line.toLowerCase().includes('experimental') || line.toLowerCase().includes('validation')) {
          sectionType = 'Experimental Approach';
        }
        
        sections.push({
          type: sectionType,
          content: line
        });
      }
    }
    
    // If no sections found, create a general one
    if (sections.length === 0) {
      sections.push({
        type: 'Hypothesis Description',
        content: content
      });
    }
    
    return { title, sections };
  };

  const parsedHypothesis = parseHypothesis(hypothesis.content);

  return (
    <div style={{
      backgroundColor: '#ffffff',
      borderRadius: '8px',
      border: '1px solid #e5e7eb',
      marginBottom: '16px',
      overflow: 'hidden',
      boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1)',
      transition: 'all 0.2s ease'
    }}>
      {/* Header with Preview */}
      <div 
        style={{
          padding: '20px',
          borderBottom: isExpanded ? '1px solid #f3f4f6' : 'none',
          cursor: 'pointer',
          backgroundColor: isExpanded ? '#f9fafb' : '#ffffff'
        }}
        onClick={() => setIsExpanded(!isExpanded)}
      >
        {/* Metadata Row */}
        <div style={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          marginBottom: '12px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{
              padding: '4px 10px',
              backgroundColor: '#f3f4f6',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: '500',
              color: '#6b7280'
            }}>
              Iteration {hypothesis.iteration}
            </span>
            
            {hypothesis.rank && (
              <span style={{
                padding: '4px 10px',
                backgroundColor: '#eff6ff',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: '500',
                color: '#2563eb'
              }}>
                Rank #{hypothesis.rank}
              </span>
            )}

            <span style={{
              padding: '4px 10px',
              backgroundColor: getScoreColor(hypothesis.score) + '15',
              borderRadius: '20px',
              fontSize: '12px',
              fontWeight: '500',
              color: getScoreColor(hypothesis.score)
            }}>
              {getScoreLabel(hypothesis.score)} ({Math.round(hypothesis.score * 100)}%)
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              width: '60px',
              height: '4px',
              backgroundColor: '#f1f5f9',
              borderRadius: '2px',
              overflow: 'hidden'
            }}>
              <div style={{
                width: `${hypothesis.score * 100}%`,
                height: '100%',
                backgroundColor: getScoreColor(hypothesis.score),
                borderRadius: '2px'
              }} />
            </div>
            <span style={{ 
              fontSize: '16px', 
              color: '#9ca3af',
              transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s ease'
            }}>
              ▼
            </span>
          </div>
        </div>

        {/* Hypothesis Title & Preview */}
        <div>
          <h4 style={{ 
            fontSize: '16px', 
            fontWeight: '600', 
            color: '#111827', 
            marginBottom: '8px',
            lineHeight: '1.4'
          }}>
            {parsedHypothesis.title}
          </h4>
          
          {!isExpanded && (
            <p style={{
              fontSize: '14px',
              color: '#6b7280',
              lineHeight: '1.5',
              margin: 0
            }}>
              {parsedHypothesis.sections[0]?.content.substring(0, 150)}...
            </p>
          )}
        </div>
      </div>

      {/* Expanded Content */}
      <div style={{
        maxHeight: isExpanded ? '2000px' : '0px',
        overflow: 'hidden',
        transition: 'max-height 0.3s ease'
      }}>
        <div style={{ padding: '24px' }}>
          {/* Structured Hypothesis Sections */}
          <div style={{ marginBottom: '24px' }}>
            <h5 style={{ 
              fontSize: '14px', 
              fontWeight: '600', 
              color: '#374151', 
              marginBottom: '16px',
              textTransform: 'uppercase',
              letterSpacing: '0.05em'
            }}>
              Hypothesis Details
            </h5>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {parsedHypothesis.sections.map((section, index) => (
                <div key={index} style={{
                  padding: '16px',
                  backgroundColor: '#f8fafc',
                  borderRadius: '6px',
                  borderLeft: '3px solid #e5e7eb'
                }}>
                  <div style={{
                    fontSize: '12px',
                    fontWeight: '600',
                    color: '#4b5563',
                    marginBottom: '8px',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em'
                  }}>
                    {section.type}
                  </div>
                  <div style={{
                    fontSize: '14px',
                    lineHeight: '1.6',
                    color: '#374151'
                  }}>
                    {section.content}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quality Review */}
          {hypothesis.review && (
            <div style={{ marginBottom: '24px' }}>
              <h5 style={{ 
                fontSize: '14px', 
                fontWeight: '600', 
                color: '#374151', 
                marginBottom: '12px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                Quality Assessment
              </h5>
              <div style={{
                padding: '16px',
                backgroundColor: '#f0f9ff',
                borderRadius: '6px',
                fontSize: '14px',
                lineHeight: '1.6',
                color: '#374151',
                borderLeft: '3px solid #0ea5e9'
              }}>
                {hypothesis.review}
              </div>
            </div>
          )}

          {/* Literature Sources */}
          {hypothesis.literature_sources && hypothesis.literature_sources.length > 0 && (
            <div style={{ marginBottom: '16px' }}>
              <h5 style={{ 
                fontSize: '14px', 
                fontWeight: '600', 
                color: '#374151', 
                marginBottom: '12px',
                textTransform: 'uppercase',
                letterSpacing: '0.05em'
              }}>
                Supporting Literature ({hypothesis.literature_sources.length} sources)
              </h5>
              <div style={{
                maxHeight: '400px',
                overflowY: 'auto',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                backgroundColor: '#ffffff'
              }}>
                {hypothesis.literature_sources.map((source, index) => (
                  <div key={index} style={{
                    padding: '20px',
                    borderBottom: index < hypothesis.literature_sources.length - 1 ? '1px solid #f3f4f6' : 'none'
                  }}>
                    {/* Title */}
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '600',
                      color: '#111827',
                      marginBottom: '8px',
                      lineHeight: '1.4'
                    }}>
                      {source.url ? (
                        <a
                          href={source.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            color: '#2563eb',
                            textDecoration: 'none'
                          }}
                          onMouseEnter={(e) => e.target.style.textDecoration = 'underline'}
                          onMouseLeave={(e) => e.target.style.textDecoration = 'none'}
                        >
                          {source.title || 'Research Paper'}
                        </a>
                      ) : (
                        source.title || 'Research Paper'
                      )}
                    </div>
                    
                    {/* Authors and Journal */}
                    {(source.authors || source.journal || source.year) && (
                      <div style={{
                        fontSize: '13px',
                        color: '#6b7280',
                        marginBottom: '10px',
                        fontStyle: 'italic'
                      }}>
                        {source.authors && source.authors.length > 0 && (
                          <span>{source.authors.slice(0, 3).join(', ')}{source.authors.length > 3 ? ', et al.' : ''}</span>
                        )}
                        {source.journal && (
                          <span>
                            {source.authors && source.authors.length > 0 ? '. ' : ''}
                            <em>{source.journal}</em>
                          </span>
                        )}
                        {source.year && (
                          <span> ({source.year})</span>
                        )}
                      </div>
                    )}
                    
                    {/* Abstract */}
                    {source.abstract && source.abstract !== 'No abstract available' && (
                      <div style={{
                        fontSize: '13px',
                        color: '#4b5563',
                        lineHeight: '1.5',
                        marginBottom: '10px'
                      }}>
                        {source.abstract}
                      </div>
                    )}
                    
                    {/* Metadata */}
                    <div style={{
                      display: 'flex',
                      gap: '12px',
                      fontSize: '11px',
                      color: '#9ca3af'
                    }}>
                      {source.pmid && (
                        <span>PMID: {source.pmid}</span>
                      )}
                      {source.doi && (
                        <span>DOI: {source.doi}</span>
                      )}
                      {source.source && (
                        <span style={{
                          padding: '2px 6px',
                          backgroundColor: '#f3f4f6',
                          borderRadius: '3px',
                          textTransform: 'uppercase',
                          fontSize: '10px',
                          fontWeight: '500'
                        }}>
                          {source.source}
                        </span>
                      )}
                      {source.search_type && (
                        <span style={{
                          padding: '2px 6px',
                          backgroundColor: '#ede9fe',
                          borderRadius: '3px',
                          color: '#7c3aed',
                          fontSize: '10px',
                          fontWeight: '500'
                        }}>
                          {source.search_type}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Technical Metadata */}
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '12px 16px',
            backgroundColor: '#f9fafb',
            borderRadius: '6px',
            fontSize: '11px',
            color: '#6b7280',
            fontFamily: 'monospace'
          }}>
            <span>ID: {hypothesis.id}</span>
            <span>Quality Score: {(hypothesis.score * 100).toFixed(1)}%</span>
          </div>
        </div>
      </div>
    </div>
  );
}; 