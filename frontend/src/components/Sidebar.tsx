import React from 'react';
import { 
  LayoutDashboard, TrendingUp, FileText, Target, 
  Briefcase, Cpu, Database, FileDown, Activity, Settings, Sparkles 
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard },
    { id: 'market', label: 'Market Intelligence', icon: TrendingUp },
    { id: 'resume', label: 'Resume Analyzer', icon: FileText },
    { id: 'skill-gap', label: 'Skill Gap Studio', icon: Target },
    { id: 'jobs', label: 'Job Explorer', icon: Briefcase },
    { id: 'mining', label: 'Data Mining Lab', icon: Cpu },
    { id: 'olap', label: 'Warehouse Explorer', icon: Database },
    { id: 'reports', label: 'Reports', icon: FileDown },
    { id: 'pipeline', label: 'Data Pipeline', icon: Activity },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-sidebar text-sidebar-text flex flex-col h-screen fixed left-0 top-0 z-30 shadow-xl border-r border-sidebar-hover">
      {/* Brand Header */}
      <div className="p-5 border-b border-sidebar-hover flex items-center space-x-3">
        <div className="w-9 h-9 rounded-lg bg-primary flex items-center justify-center text-white font-bold shadow">
          <Sparkles className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="font-bold text-lg text-white tracking-wide leading-tight">SkillSphere <span className="text-primary">AI</span></h1>
          <p className="text-xs text-sidebar-muted font-medium">Career & DWM Intelligence</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                isActive 
                  ? 'bg-sidebar-active text-white border-l-4 border-primary shadow-sm font-semibold' 
                  : 'text-sidebar-muted hover:bg-sidebar-hover hover:text-white'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-primary' : 'text-sidebar-muted'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Footer Info */}
      <div className="p-4 border-t border-sidebar-hover text-xs text-sidebar-muted bg-sidebar-hover/30">
        <div className="flex items-center justify-between">
          <span>Star Schema DW</span>
          <span className="bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded text-[10px] font-semibold">Active</span>
        </div>
        <p className="mt-1 text-[11px] opacity-75">DWM Mini-Project Edition</p>
      </div>
    </aside>
  );
};
