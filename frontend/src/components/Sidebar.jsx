import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { NavLink } from 'react-router-dom';
import { Home, Video, BarChart2, Users, Settings, ShieldAlert, ChevronLeft, ChevronRight } from 'lucide-react';

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);

  const menuItems = [
    { icon: Home, label: 'Dashboard', path: '/' },
    { icon: Video, label: 'Live Monitoring', path: '/monitoring' },
    { icon: ShieldAlert, label: 'Violations', path: '/violations' },
    { icon: BarChart2, label: 'Analytics', path: '/analytics' },
    { icon: Users, label: 'Face Management', path: '/face-management' },
  ];

  return (
    <motion.aside 
      initial={false}
      animate={{ width: collapsed ? 80 : 260 }}
      className="h-screen bg-[var(--sidebar-bg)] border-r border-[var(--glass-border)] flex flex-col transition-colors duration-300 relative z-50 backdrop-blur-md"
    >
      <div className="h-16 flex items-center justify-between px-6 border-b border-[var(--glass-border)]">
        {!collapsed && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            className="font-bold text-lg tracking-tight flex items-center gap-2"
          >
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-secondary)] flex items-center justify-center shadow-lg shadow-[var(--accent-primary)]/20">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)]">SafetyEye</span>
          </motion.div>
        )}
        {collapsed && (
          <div className="w-full flex justify-center">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-secondary)] flex items-center justify-center shadow-lg shadow-[var(--accent-primary)]/20">
              <ShieldAlert className="w-5 h-5 text-white" />
            </div>
          </div>
        )}
      </div>

      <button 
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3.5 top-20 bg-[var(--card-bg)] border border-[var(--glass-border)] rounded-full p-1.5 shadow-md hover:bg-[var(--glass-border)] transition-colors text-[var(--text-secondary)] z-50"
      >
        {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
      </button>

      <div className="flex-1 py-6 px-3 flex flex-col gap-2">
        {menuItems.map((item, index) => (
          <NavLink
            key={index}
            to={item.path}
            className="block focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] rounded-xl"
          >
            {({ isActive }) => (
              <motion.div 
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                className={`
                  relative flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-all duration-200
                  ${isActive 
                    ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] font-medium shadow-sm' 
                    : 'text-[var(--text-secondary)] hover:bg-[var(--glass-border)] hover:text-[var(--text-primary)]'}
                `}
              >
                <item.icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-[var(--accent-primary)]' : ''}`} />
                {!collapsed && (
                  <motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-sm truncate">
                    {item.label}
                  </motion.span>
                )}
                {!collapsed && isActive && (
                  <motion.div layoutId="active-indicator" className="absolute left-0 w-1 h-6 bg-[var(--accent-primary)] rounded-r-full" />
                )}
              </motion.div>
            )}
          </NavLink>
        ))}
      </div>

      <div className="p-4 border-t border-[var(--glass-border)]">
        <NavLink
          to="/settings"
          className="block focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--accent-primary)] rounded-xl"
        >
          {({ isActive }) => (
            <div className={`flex items-center gap-3 px-3 py-2.5 rounded-xl cursor-pointer transition-all ${collapsed ? 'justify-center' : ''} ${isActive ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] font-medium shadow-sm' : 'text-[var(--text-secondary)] hover:bg-[var(--glass-border)] hover:text-[var(--text-primary)]'}`}>
              <Settings className="w-5 h-5" />
              {!collapsed && <span className="text-sm">Settings</span>}
            </div>
          )}
        </NavLink>
      </div>
    </motion.aside>
  );
};

export default Sidebar;
