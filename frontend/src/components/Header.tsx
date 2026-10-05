import React from 'react';
import { Database, Clock, RefreshCw, User } from 'lucide-react';

interface HeaderProps {
  pageTitle: string;
  refreshDate?: string;
  qualityScore?: number;
  onRefresh?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ 
  pageTitle, 
  refreshDate = "2026-10-01 12:00", 
  qualityScore = 100.0,
  onRefresh
}) => {
  return (
    <header className="h-16 bg-surface border-b border-border px-6 flex items-center justify-between sticky top-0 z-20 shadow-xs">
      <div>
        <h2 className="text-xl font-bold text-text-primary tracking-tight">{pageTitle}</h2>
      </div>

      <div className="flex items-center space-x-4">
        {/* Dataset Coverage Badge */}
        <div className="flex items-center space-x-2 bg-surface-mint px-3 py-1.5 rounded-lg border border-border text-xs text-text-primary font-medium">
          <Database className="w-3.5 h-3.5 text-primary" />
          <span>Star Schema DW: <b>2,000 Kaggle Jobs</b> | Quality: <b>{qualityScore}%</b></span>
        </div>

        {/* Refresh Timestamp */}
        <div className="flex items-center space-x-1.5 text-xs text-text-secondary">
          <Clock className="w-3.5 h-3.5" />
          <span>Refreshed: {refreshDate}</span>
        </div>

        {/* Refresh Action */}
        {onRefresh && (
          <button 
            onClick={onRefresh}
            className="p-1.5 rounded-lg border border-border hover:bg-surface-secondary text-text-secondary transition"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}

        {/* User Profile */}
        <div className="flex items-center space-x-2 pl-3 border-l border-border">
          <div className="w-8 h-8 rounded-full bg-sidebar flex items-center justify-center text-white font-semibold text-xs shadow-xs">
            <User className="w-4 h-4" />
          </div>
          <div className="text-xs">
            <p className="font-semibold text-text-primary leading-tight">Candidate Profile</p>
            <p className="text-text-secondary text-[11px]">Academic Mode</p>
          </div>
        </div>
      </div>
    </header>
  );
};
