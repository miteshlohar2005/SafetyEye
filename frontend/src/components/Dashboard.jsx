import React, { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HardHat, ShieldAlert, Activity, Users, AlertTriangle, Play, Square, Camera, Video } from 'lucide-react';

const KPICard = ({ title, value, icon: Icon, colorClass, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
    whileHover={{ y: -5 }}
    className="glass-card rounded-2xl p-6 relative overflow-hidden group"
  >
    <div className={`absolute -right-6 -top-6 w-24 h-24 rounded-full opacity-10 transition-transform group-hover:scale-150 duration-500 ${colorClass}`} />
    
    <div className="flex justify-between items-start mb-4">
      <div>
        <p className="text-[var(--text-secondary)] text-sm font-medium mb-1">{title}</p>
        <h3 className="text-3xl font-bold text-[var(--text-primary)] tracking-tight">{value}</h3>
      </div>
      <div className={`p-3 rounded-xl ${colorClass} bg-opacity-10 dark:bg-opacity-20`}>
        <Icon className={`w-6 h-6 ${colorClass.replace('bg-', 'text-')}`} />
      </div>
    </div>
  </motion.div>
);

const Dashboard = () => {
  const [stats, setStats] = useState({
    is_monitoring: false,
    violation_count: 0,
    total_detections: 0,
    active_violations: 0,
    session_duration_seconds: 0
  });
  const [isLoading, setIsLoading] = useState(false);

  // Fetch stats periodically
  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await fetch('http://localhost:5000/stats');
        if (res.ok) {
          const data = await res.json();
          setStats(data);
        }
      } catch (err) {
        console.error('Failed to fetch stats', err);
      }
    };
    
    fetchStats();
    const interval = setInterval(fetchStats, 2000);
    return () => clearInterval(interval);
  }, []);

  const formatDuration = (totalSeconds) => {
    const h = Math.floor(totalSeconds / 3600);
    const m = Math.floor((totalSeconds % 3600) / 60);
    const s = totalSeconds % 60;
    return `${h.toString().padStart(2, '0')}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const handleStart = async () => {
    setIsLoading(true);
    try {
      await fetch('http://localhost:5000/start_monitoring', { method: 'POST' });
      setStats(prev => ({ ...prev, is_monitoring: true }));
    } catch (e) {
      console.error(e);
    }
    setIsLoading(false);
  };

  const handleStop = async () => {
    setIsLoading(true);
    try {
      await fetch('http://localhost:5000/stop_monitoring', { method: 'POST' });
      setStats(prev => ({ ...prev, is_monitoring: false }));
    } catch (e) {
      console.error(e);
    }
    setIsLoading(false);
  };

  const kpis = [
    { title: 'Session Duration', value: formatDuration(stats.session_duration_seconds), icon: Activity, colorClass: 'bg-blue-500', delay: 0.1 },
    { title: 'Total Detections', value: stats.total_detections, icon: Users, colorClass: 'bg-purple-500', delay: 0.2 },
    { title: 'Active Violations', value: stats.active_violations, icon: ShieldAlert, colorClass: stats.active_violations > 0 ? 'bg-red-500' : 'bg-green-500', delay: 0.3 },
    { title: 'Total Logged Violations', value: stats.violation_count, icon: AlertTriangle, colorClass: 'bg-orange-500', delay: 0.4 },
  ];

  return (
    <div className="space-y-8">
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
        <div>
          <motion.h1 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className="text-3xl font-bold text-[var(--text-primary)] tracking-tight flex items-center gap-3"
          >
            Live Monitoring
            {stats.is_monitoring && (
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
              </span>
            )}
            {!stats.is_monitoring && (
              <span className="relative flex h-3 w-3">
                <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
              </span>
            )}
          </motion.h1>
          <motion.p 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-[var(--text-secondary)] mt-1 font-medium"
          >
            {stats.is_monitoring ? "Monitoring Active" : "Monitoring Stopped"}
          </motion.p>
        </div>

        <motion.div 
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex items-center gap-3"
        >
          <button 
            onClick={handleStart}
            disabled={stats.is_monitoring || isLoading}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium transition-all ${
              stats.is_monitoring 
                ? 'opacity-50 cursor-not-allowed bg-[var(--bg-secondary)] text-[var(--text-secondary)] border border-[var(--glass-border)]' 
                : 'bg-green-500 text-white shadow-lg shadow-green-500/20 hover:bg-green-600 hover:-translate-y-0.5 active:translate-y-0'
            }`}
          >
            <Play className="w-4 h-4" /> Start Monitoring
          </button>

          <button 
            onClick={handleStop}
            disabled={!stats.is_monitoring || isLoading}
            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium transition-all ${
              !stats.is_monitoring 
                ? 'opacity-50 cursor-not-allowed bg-[var(--bg-secondary)] text-[var(--text-secondary)] border border-[var(--glass-border)]' 
                : 'bg-red-500 text-white shadow-lg shadow-red-500/20 hover:bg-red-600 hover:-translate-y-0.5 active:translate-y-0'
            }`}
          >
            <Square className="w-4 h-4" /> Stop Monitoring
          </button>
        </motion.div>
      </header>

      {/* KPI Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {kpis.map((kpi, idx) => (
          <KPICard key={idx} {...kpi} />
        ))}
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Main Live Feed */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          className="xl:col-span-2 glass-card rounded-2xl overflow-hidden flex flex-col relative min-h-[400px]"
        >
          <div className="p-4 border-b border-[var(--glass-border)] flex justify-between items-center bg-[var(--card-bg)]/50 backdrop-blur-md relative z-10">
            <div className="flex items-center gap-3">
              <Camera className={`w-5 h-5 ${stats.is_monitoring ? 'text-green-500' : 'text-red-500'}`} />
              <h2 className="font-semibold text-[var(--text-primary)]">Camera 01: Main Entrance</h2>
            </div>
            <div className="text-xs font-medium px-2 py-1 rounded bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]">
              Model: YOLOv8 Live (NMS Enabled)
            </div>
          </div>
          
          <div className="relative flex-1 bg-black overflow-hidden flex items-center justify-center group">
            {stats.is_monitoring ? (
              <>
                <img 
                  src={`http://localhost:5000/video_feed?t=${Date.now()}`} 
                  alt="Live Video Feed"
                  className="w-full h-full object-cover"
                  onError={(e) => { e.target.style.display = 'none'; document.getElementById('feed-error').style.display = 'flex'; }}
                />
                <div className="absolute inset-0 pointer-events-none opacity-30 mix-blend-overlay">
                  <div className="w-full h-1 bg-cyan-400 animate-scan shadow-[0_0_15px_rgba(34,211,238,0.8)]"></div>
                </div>
                {/* Cyber Corner Accents */}
                <div className="absolute top-4 left-4 w-8 h-8 border-t-2 border-l-2 border-cyan-500 opacity-50 group-hover:opacity-100 transition-opacity"></div>
                <div className="absolute top-4 right-4 w-8 h-8 border-t-2 border-r-2 border-cyan-500 opacity-50 group-hover:opacity-100 transition-opacity"></div>
                <div className="absolute bottom-4 left-4 w-8 h-8 border-b-2 border-l-2 border-cyan-500 opacity-50 group-hover:opacity-100 transition-opacity"></div>
                <div className="absolute bottom-4 right-4 w-8 h-8 border-b-2 border-r-2 border-cyan-500 opacity-50 group-hover:opacity-100 transition-opacity"></div>

                <div id="feed-error" className="absolute inset-0 hidden flex-col items-center justify-center bg-gray-900 text-gray-400">
                  <AlertTriangle className="w-12 h-12 mb-2 text-yellow-500 opacity-50" />
                  <p>Camera Feed Interrupted</p>
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center text-[var(--text-secondary)]">
                <Video className="w-16 h-16 mb-4 opacity-20" />
                <p className="text-lg font-medium">Camera Offline</p>
                <p className="text-sm opacity-60">Click "Start Monitoring" to connect to the feed.</p>
              </div>
            )}
          </div>
        </motion.div>

        {/* Activity Timeline */}
        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.6 }}
          className="glass-card rounded-2xl flex flex-col h-[500px] xl:h-auto"
        >
          <div className="p-5 border-b border-[var(--glass-border)] flex justify-between items-center">
            <h2 className="font-semibold text-[var(--text-primary)]">System Alerts</h2>
            {stats.active_violations > 0 && (
              <span className="text-xs font-bold bg-red-500 text-white px-2 py-1 rounded-full animate-pulse">
                {stats.active_violations} Active
              </span>
            )}
          </div>
          <div className="p-5 flex-1 overflow-y-auto custom-scrollbar">
            {!stats.is_monitoring ? (
              <div className="h-full flex items-center justify-center text-sm text-[var(--text-secondary)] opacity-50">
                System is offline
              </div>
            ) : (
              <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-[var(--glass-border)] before:to-transparent">
                {/* Simulated Real-Time Status Stream */}
                <div className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border border-white bg-slate-300 ${stats.active_violations > 0 ? 'group-[.is-active]:bg-red-500' : 'group-[.is-active]:bg-green-500'} text-slate-500 group-[.is-active]:text-emerald-50 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 transition-colors`}>
                    {stats.active_violations > 0 ? <AlertTriangle className="w-5 h-5 text-white" /> : <HardHat className="w-5 h-5 text-white" />}
                  </div>
                  <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-[var(--glass-border)] bg-[var(--bg-secondary)]/50 shadow-sm">
                    <div className="flex items-center justify-between space-x-2 mb-1">
                      <div className="font-bold text-[var(--text-primary)] text-sm">
                        {stats.active_violations > 0 ? 'Violation Detected' : 'All Clear'}
                      </div>
                      <time className="text-xs font-medium text-[var(--text-secondary)]">Now</time>
                    </div>
                    <div className="text-[var(--text-secondary)] text-xs">Main Entrance Camera</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Dashboard;
