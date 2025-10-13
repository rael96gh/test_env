/**
 * Main Dashboard component
 */
import React from 'react';
import Card from '../../components/ui/Card/Card';
import './Dashboard.css';

const Dashboard = ({ onNavigate }) => {
  const tools = [
    {
      id: 'oligo',
      title: 'Oligo Maker',
      description: 'Generate forward and reverse oligos from DNA sequences',
      icon: '🧬',
      color: '#007bff'
    },
    {
      id: 'saturation',
      title: 'Saturation Mutagenesis',
      description: 'Create a library of every possible codon variant',
      icon: '🔬',
      color: '#28a745'
    },
    {
      id: 'custom',
      title: 'Custom Mutagenesis',
      description: 'Generate specific point mutations',
      icon: '✍️',
      color: '#ffc107'
    },
    {
      id: 'scanning',
      title: 'Scanning Mutagenesis',
      description: 'Generate codon scanning mutations',
      icon: '🔍',
      color: '#17a2b8'
    },
    {
      id: 'primers',
      title: 'Primer Generation',
      description: 'Generate primers for PCR and sequencing',
      icon: '🧪',
      color: '#dc3545'
    },
    {
      id: 'recycle',
      title: 'Oligo Recycling',
      description: 'Recycle and optimize existing oligo libraries',
      icon: '♻️',
      color: '#6c757d'
    }
  ];

  return (
    <div className="dashboard">
      <div className="dashboard__header">
        <h1 className="dashboard__title">Variant DNA Library Modules</h1>
        <p className="dashboard__subtitle">
          Select a tool to get started with your DNA analysis and oligo generation workflow.
        </p>
      </div>

      <div className="dashboard__grid">
        {tools.map((tool) => (
          <Card
            key={tool.id}
            hoverable
            onClick={() => onNavigate(tool.id)}
            className="dashboard__card"
          >
            <div className="dashboard__card-content">
              <div
                className="dashboard__card-icon"
                style={{ backgroundColor: `${tool.color}15`, color: tool.color }}
              >
                {tool.icon}
              </div>
              <h3 className="dashboard__card-title">{tool.title}</h3>
              <p className="dashboard__card-description">{tool.description}</p>
            </div>
          </Card>
        ))}
      </div>

      <div className="dashboard__footer">
        <div className="dashboard__stats">
          <div className="dashboard__stat">
            <div className="dashboard__stat-number">10k+</div>
            <div className="dashboard__stat-label">Sequences Processed</div>
          </div>
          <div className="dashboard__stat">
            <div className="dashboard__stat-number">50k+</div>
            <div className="dashboard__stat-label">Oligos Generated</div>
          </div>
          <div className="dashboard__stat">
            <div className="dashboard__stat-number">99.9%</div>
            <div className="dashboard__stat-label">Success Rate</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;