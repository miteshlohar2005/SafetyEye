import React from 'react';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon, Bell, Search, User } from 'lucide-react';
import { motion } from 'framer-motion';

const Navbar = () => {
  const { theme, toggleTheme } = useTheme();

  return (
    <nav className="h-16 border-b border-[var(--glass-border)] bg-[var(--card-bg)]/80 backdrop-blur-md sticky top-0 z-40 flex items-center justify-between px-6 transition-colors duration-300">
      <div className="flex items-center gap-4 w-1/3">
        <div className="relative w-full max-w-md hidden sm:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-secondary)]" />
          <input 
            type="text" 
            placeholder="Search cameras, zones, alerts..." 
            className="w-full bg-[var(--bg-secondary)] border border-[var(--glass-border)] rounded-full pl-10 pr-4 py-1.5 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--accent-primary)]/50 transition-all text-[var(--text-primary)]"
          />
        </div>
      </div>

      <div className="flex items-center gap-4">
        <motion.button 
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="relative p-2 rounded-full hover:bg-[var(--glass-border)] transition-colors"
        >
          <Bell className="w-5 h-5 text-[var(--text-secondary)]" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-[var(--status-error)] rounded-full border border-[var(--card-bg)]"></span>
        </motion.button>
        
        <motion.button 
          whileHover={{ scale: 1.05, rotate: theme === 'dark' ? 180 : 0 }}
          whileTap={{ scale: 0.95 }}
          onClick={toggleTheme}
          className="p-2 rounded-full hover:bg-[var(--glass-border)] transition-colors"
        >
          {theme === 'dark' ? <Sun className="w-5 h-5 text-yellow-400" /> : <Moon className="w-5 h-5 text-slate-700" />}
        </motion.button>

        <div className="h-8 w-px bg-[var(--glass-border)] mx-2"></div>

        <motion.div 
          whileHover={{ scale: 1.05 }}
          className="flex items-center gap-3 cursor-pointer p-1 pr-3 rounded-full hover:bg-[var(--glass-border)] transition-colors"
        >
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-[var(--accent-primary)] to-[var(--accent-secondary)] flex items-center justify-center text-white font-medium text-sm shadow-md">
            AD
          </div>
          <span className="text-sm font-medium text-[var(--text-primary)] hidden md:block">Admin</span>
        </motion.div>
      </div>
    </nav>
  );
};

export default Navbar;
