import React from 'react';
import { Sun, Moon, RefreshCw, HardDrive, ShieldAlert, Wifi } from 'lucide-react';
import { DomainEnum } from '../types/diagnostic';

interface NavbarProps {
  currentDomain: DomainEnum;
  sessionId: string | null;
  onResetSession: () => void;
  theme: 'light' | 'dark';
  onToggleTheme: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentDomain,
  sessionId,
  onResetSession,
  theme,
  onToggleTheme,
}) => {
  return (
    <header className="border-b border-slate-200 dark:border-zinc-800 bg-white/90 dark:bg-zinc-900/90 backdrop-blur-md sticky top-0 z-50 transition-colors">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 h-15 flex items-center justify-between">
        {/* Branding Logo - Clean restrained text without heavy badge or icon */}
        <div className="flex items-center gap-3">
          <div className="flex flex-col">
            <span className="font-semibold tracking-tight text-slate-900 dark:text-zinc-100 text-base">
              FixIT Saarthi
            </span>
            <span className="text-[11px] text-slate-500 dark:text-zinc-400 hidden sm:block">
              Expert Diagnostic System
            </span>
          </div>
        </div>

        {/* Domain Selection Tabs - Clean technical tabs without 'Soon' tags */}
        <div className="hidden md:flex items-center gap-1 p-1 bg-slate-100 dark:bg-zinc-950 rounded-lg border border-slate-200 dark:border-zinc-850">
          <button
            className={`flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium transition-all ${
              currentDomain === DomainEnum.PERFORMANCE
                ? 'bg-white dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 shadow-sm border border-slate-200/80 dark:border-zinc-700'
                : 'text-slate-600 dark:text-zinc-400 hover:text-slate-900 dark:hover:text-zinc-200'
            }`}
          >
            <HardDrive className="w-3.5 h-3.5 text-blue-600 dark:text-blue-400" />
            Performance & Freezing
          </button>

          <button
            disabled
            className="flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium text-slate-400 dark:text-zinc-600 cursor-not-allowed opacity-60"
            title="Boot Failure domain currently unavailable"
          >
            <ShieldAlert className="w-3.5 h-3.5" />
            Boot Failure
          </button>

          <button
            disabled
            className="flex items-center gap-2 px-3 py-1.5 rounded-md text-xs font-medium text-slate-400 dark:text-zinc-600 cursor-not-allowed opacity-60"
            title="Network domain currently unavailable"
          >
            <Wifi className="w-3.5 h-3.5" />
            Network
          </button>
        </div>

        {/* Right Actions: Session & Theme Toggle */}
        <div className="flex items-center gap-2.5">
          {sessionId && (
            <div className="hidden sm:flex flex-col items-end text-xs mr-1">
              <span className="text-slate-400 dark:text-zinc-500 font-mono text-[10px]">Session</span>
              <span className="text-slate-600 dark:text-zinc-300 font-mono text-[11px]" title={sessionId}>
                {sessionId.slice(0, 8)}
              </span>
            </div>
          )}

          {/* Theme Toggle Button */}
          <button
            onClick={onToggleTheme}
            className="p-2 rounded-lg bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 border border-slate-200 dark:border-zinc-700 transition-colors"
            title={`Switch to ${theme === 'dark' ? 'Light' : 'Dark'} mode`}
            aria-label="Toggle Theme"
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4 text-amber-400" />
            ) : (
              <Moon className="w-4 h-4 text-slate-600" />
            )}
          </button>

          {/* Reset Session */}
          <button
            onClick={onResetSession}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-200 text-xs font-medium border border-slate-200 dark:border-zinc-700 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">New Session</span>
          </button>
        </div>
      </div>
    </header>
  );
};
