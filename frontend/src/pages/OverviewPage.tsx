import React, { useEffect, useState } from 'react';
import { KpiMetrics } from '../types';
import { fetchKpiMetrics, fetchOverviewCharts } from '../services/api';
import { Briefcase, Building2, Code, Layers, ShieldCheck, Clock, Filter } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

export const OverviewPage: React.FC = () => {
  const [kpis, setKpis] = useState<KpiMetrics | null>(null);
  const [charts, setCharts] = useState<any>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedCity, setSelectedCity] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(true);

  const COLORS = ['#d99b00', '#0f3838', '#0d9488', '#d97706', '#6366f1', '#ec4899', '#8b5cf6', '#14b8a6'];

  useEffect(() => {
    loadData();
  }, [selectedCategory, selectedCity]);

  const loadData = async () => {
    setLoading(true);
    try {
      const kpiData = await fetchKpiMetrics();
      const chartData = await fetchOverviewCharts(selectedCategory, selectedCity);
      setKpis(kpiData);
      setCharts(chartData);
    } catch (err) {
      console.error("Error loading overview data:", err);
    } finally {
      setLoading(false);
    }
  };

  const totalCatCount = (charts?.category_distribution || []).reduce((sum: number, item: any) => sum + item.count, 0) || 1;
  const totalExpCount = (charts?.exp_distribution || []).reduce((sum: number, item: any) => sum + item.count, 0) || 1;

  return (
    <div className="space-y-6">
      {/* Filter Toolbar */}
      <div className="custom-card p-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Filter className="w-4 h-4 text-primary" />
          <span className="text-sm font-semibold text-text-primary">Dashboard Filters:</span>
        </div>
        <div className="flex items-center space-x-4">
          <select 
            value={selectedCategory} 
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="input-field text-xs font-medium"
          >
            <option value="">All Job Categories</option>
            <option value="Data Science & Analytics">Data Science & Analytics</option>
            <option value="Software Engineering">Software Engineering</option>
            <option value="Machine Learning & AI">Machine Learning & AI</option>
            <option value="DevOps & Cloud Engineering">DevOps & Cloud Engineering</option>
            <option value="Data Engineering">Data Engineering</option>
            <option value="Cybersecurity">Cybersecurity</option>
          </select>

          <select 
            value={selectedCity} 
            onChange={(e) => setSelectedCity(e.target.value)}
            className="input-field text-xs font-medium"
          >
            <option value="">All Locations</option>
            <option value="San Francisco">San Francisco</option>
            <option value="New York">New York</option>
            <option value="Austin">Austin</option>
            <option value="Seattle">Seattle</option>
            <option value="London">London</option>
            <option value="Bengaluru">Bengaluru</option>
          </select>
          {(selectedCategory || selectedCity) && (
            <button 
              onClick={() => { setSelectedCategory(''); setSelectedCity(''); }}
              className="text-xs text-primary font-semibold hover:underline"
            >
              Reset Filters
            </button>
          )}
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="custom-card p-4 flex items-center space-x-3">
          <div className="p-3 bg-surface-mint rounded-lg text-primary">
            <Briefcase className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-text-secondary font-medium">Job Postings</p>
            <h3 className="text-lg font-bold text-text-primary">{kpis?.total_job_postings || 2000}</h3>
          </div>
        </div>

        <div className="custom-card p-4 flex items-center space-x-3">
          <div className="p-3 bg-surface-mint rounded-lg text-sidebar">
            <Building2 className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-text-secondary font-medium">Companies</p>
            <h3 className="text-lg font-bold text-text-primary">{kpis?.unique_companies || 140}</h3>
          </div>
        </div>

        <div className="custom-card p-4 flex items-center space-x-3">
          <div className="p-3 bg-surface-mint rounded-lg text-amber-600">
            <Code className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-text-secondary font-medium">Mapped Skills</p>
            <h3 className="text-lg font-bold text-text-primary">{kpis?.unique_skills || 52}</h3>
          </div>
        </div>

        <div className="custom-card p-4 flex items-center space-x-3">
          <div className="p-3 bg-surface-mint rounded-lg text-teal-600">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-text-secondary font-medium">Job Categories</p>
            <h3 className="text-lg font-bold text-text-primary">{kpis?.job_categories || 8}</h3>
          </div>
        </div>

        <div className="custom-card p-4 flex items-center space-x-3">
          <div className="p-3 bg-surface-mint rounded-lg text-emerald-600">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-text-secondary font-medium">ETL Quality</p>
            <h3 className="text-lg font-bold text-text-primary">{kpis?.etl_quality_score || 100}%</h3>
          </div>
        </div>

        <div className="custom-card p-4 flex items-center space-x-3">
          <div className="p-3 bg-surface-mint rounded-lg text-indigo-600">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <p className="text-xs text-text-secondary font-medium">Last Refresh</p>
            <h3 className="text-xs font-bold text-text-primary truncate">{kpis?.latest_dataset_refresh?.split(' ')[0] || "2026-10-01"}</h3>
          </div>
        </div>
      </div>

      {/* Visualizations Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Demanded Skills Bar Chart */}
        <div className="custom-card p-5 space-y-3">
          <h3 className="font-bold text-text-primary text-sm">Top Demanded Skills Across Postings</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts?.top_skills || []} layout="vertical" margin={{ left: 20 }}>
                <XAxis type="number" />
                <YAxis dataKey="skill" type="category" tick={{ fontSize: 11 }} width={90} />
                <Tooltip />
                <Bar dataKey="count" fill="#d99b00" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Distribution Donut Chart + All Percentage Badges */}
        <div className="custom-card p-5 space-y-3">
          <h3 className="font-bold text-text-primary text-sm">Job Category Distribution (100% Breakdown)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={charts?.category_distribution || []}
                    dataKey="count"
                    nameKey="category"
                    cx="50%"
                    cy="50%"
                    innerRadius={40}
                    outerRadius={75}
                    paddingAngle={3}
                  >
                    {(charts?.category_distribution || []).map((_: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: any, name: any) => [`${value} postings (${((Number(value) / totalCatCount) * 100).toFixed(1)}%)`, name]} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Legend list showing 100% of all category percentages */}
            <div className="space-y-1.5 text-xs max-h-56 overflow-y-auto pr-1">
              {(charts?.category_distribution || []).map((item: any, index: number) => {
                const pct = ((item.count / totalCatCount) * 100).toFixed(1);
                return (
                  <div key={item.category} className="flex items-center justify-between p-1.5 rounded hover:bg-surface-mint/50 border border-transparent hover:border-border transition">
                    <div className="flex items-center space-x-2 truncate">
                      <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                      <span className="font-medium text-text-primary truncate">{item.category}</span>
                    </div>
                    <div className="flex items-center space-x-2 flex-shrink-0 text-[11px]">
                      <span className="text-text-secondary font-medium">{item.count}</span>
                      <span className="font-extrabold text-sidebar bg-surface-mint border border-border px-1.5 py-0.5 rounded">{pct}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Experience Level Donut + All Percentage Badges */}
        <div className="custom-card p-5 space-y-3">
          <h3 className="font-bold text-text-primary text-sm">Experience Level Breakdown (100% Breakdown)</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 items-center">
            <div className="h-56">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={charts?.exp_distribution || []}
                    dataKey="count"
                    nameKey="level"
                    cx="50%"
                    cy="50%"
                    innerRadius={45}
                    outerRadius={75}
                    paddingAngle={4}
                  >
                    {(charts?.exp_distribution || []).map((_: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[(index + 2) % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: any, name: any) => [`${value} postings (${((Number(value) / totalExpCount) * 100).toFixed(1)}%)`, name]} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            {/* Legend list showing 100% of experience level percentages */}
            <div className="space-y-2 text-xs">
              {(charts?.exp_distribution || []).map((item: any, index: number) => {
                const pct = ((item.count / totalExpCount) * 100).toFixed(1);
                return (
                  <div key={item.level} className="flex items-center justify-between p-2 rounded hover:bg-surface-mint/50 border border-transparent hover:border-border transition">
                    <div className="flex items-center space-x-2 truncate">
                      <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: COLORS[(index + 2) % COLORS.length] }} />
                      <span className="font-medium text-text-primary">{item.level}</span>
                    </div>
                    <div className="flex items-center space-x-2 text-[11px]">
                      <span className="text-text-secondary font-medium">{item.count}</span>
                      <span className="font-extrabold text-sidebar bg-surface-mint border border-border px-2 py-0.5 rounded">{pct}%</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Location Demand Bar Chart */}
        <div className="custom-card p-5 space-y-3">
          <h3 className="font-bold text-text-primary text-sm">Location-wise Job Volume</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={charts?.location_distribution || []}>
                <XAxis dataKey="city" tick={{ fontSize: 11 }} />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#0f3838" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </div>
  );
};
