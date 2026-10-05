import React, { useState } from 'react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { OverviewPage } from './pages/OverviewPage';
import { MarketIntelligencePage } from './pages/MarketIntelligencePage';
import { ResumeAnalyzerPage } from './pages/ResumeAnalyzerPage';
import { SkillGapStudioPage } from './pages/SkillGapStudioPage';
import { JobExplorerPage } from './pages/JobExplorerPage';
import { DataMiningLabPage } from './pages/DataMiningLabPage';
import { WarehouseExplorerPage } from './pages/WarehouseExplorerPage';
import { ReportsPage } from './pages/ReportsPage';
import { DataPipelinePage } from './pages/DataPipelinePage';
import { SettingsPage } from './pages/SettingsPage';

export function App() {
  const [activeTab, setActiveTab] = useState<string>('overview');

  const pageTitles: Record<string, string> = {
    'overview': 'Overview Analytics Dashboard',
    'market': 'Market Intelligence Exploration',
    'resume': 'Resume Analyzer & Skill Extractor',
    'skill-gap': 'Skill Gap Studio & Candidate Roadmap',
    'jobs': 'Job Explorer & Recommendations',
    'mining': 'Data Mining Lab (Academic DWM Showcase)',
    'olap': 'Warehouse Explorer & Multidimensional OLAP',
    'reports': 'Reports & Export Center',
    'pipeline': 'Data Pipeline & ETL Audit',
    'settings': 'Settings & Platform Status',
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewPage />;
      case 'market':
        return <MarketIntelligencePage />;
      case 'resume':
        return <ResumeAnalyzerPage onProceedToGapStudio={() => setActiveTab('skill-gap')} />;
      case 'skill-gap':
        return <SkillGapStudioPage />;
      case 'jobs':
        return <JobExplorerPage />;
      case 'mining':
        return <DataMiningLabPage />;
      case 'olap':
        return <WarehouseExplorerPage />;
      case 'reports':
        return <ReportsPage />;
      case 'pipeline':
        return <DataPipelinePage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <OverviewPage />;
    }
  };

  return (
    <div className="min-h-screen flex bg-background text-text-primary">
      {/* Sidebar Navigation */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Content Area */}
      <div className="flex-1 ml-64 flex flex-col min-h-screen">
        <Header pageTitle={pageTitles[activeTab] || 'SkillSphere AI'} />

        <main className="flex-1 p-6 max-w-7xl w-full mx-auto">
          {renderActivePage()}
        </main>
      </div>
    </div>
  );
}

export default App;
