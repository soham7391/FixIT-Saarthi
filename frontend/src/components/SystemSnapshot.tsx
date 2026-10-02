import React from 'react';
import { Cpu, Monitor, HardDrive, Wifi, Laptop, Globe } from 'lucide-react';

export interface MetricItem {
  label: string;
  value: string;
  icon: React.ComponentType<{ className?: string }>;
}

export const useSystemMetrics = () => {
  const getPlatform = (): MetricItem => {
    const nav = navigator as any;
    let val = 'Not available';
    if (nav.userAgentData?.platform) {
      val = nav.userAgentData.platform;
    } else {
      const ua = navigator.userAgent;
      if (ua.includes('Win')) val = 'Windows';
      else if (ua.includes('Mac')) val = 'macOS';
      else if (ua.includes('Linux')) val = 'Linux';
      else if (ua.includes('Android')) val = 'Android';
      else if (ua.includes('iPhone') || ua.includes('iPad')) val = 'iOS';
    }
    return { label: 'OS / Platform', value: val, icon: Laptop };
  };

  const getBrowser = (): MetricItem => {
    const nav = navigator as any;
    let val = 'Not available';
    if (nav.userAgentData?.brands && Array.isArray(nav.userAgentData.brands)) {
      const brandNames = nav.userAgentData.brands
        .map((b: { brand: string }) => b.brand)
        .filter((b: string) => !b.includes('Not A') && !b.includes('Brand'));
      if (brandNames.length > 0) {
        val = brandNames[0];
      }
    }
    if (val === 'Not available') {
      const ua = navigator.userAgent;
      if (ua.includes('Edg/')) val = 'Microsoft Edge';
      else if (ua.includes('Chrome/')) val = 'Google Chrome';
      else if (ua.includes('Firefox/')) val = 'Mozilla Firefox';
      else if (ua.includes('Safari/') && !ua.includes('Chrome/')) val = 'Apple Safari';
    }
    return { label: 'Browser', value: val, icon: Globe };
  };

  const getCpuCores = (): MetricItem => {
    let val = 'Not available';
    if (typeof navigator.hardwareConcurrency === 'number' && navigator.hardwareConcurrency > 0) {
      val = `${navigator.hardwareConcurrency} Cores`;
    }
    return { label: 'CPU Logical Cores', value: val, icon: Cpu };
  };

  const getDeviceMemory = (): MetricItem => {
    const nav = navigator as any;
    let val = 'Not available';
    if (typeof nav.deviceMemory === 'number') {
      val = `${nav.deviceMemory} GB (Approx.)`;
    }
    return { label: 'Device Memory', value: val, icon: HardDrive };
  };

  const getScreenRes = (): MetricItem => {
    let val = 'Not available';
    if (typeof window !== 'undefined' && window.screen) {
      val = `${window.screen.width} × ${window.screen.height}`;
    }
    return { label: 'Display Resolution', value: val, icon: Monitor };
  };

  const getNetworkType = (): MetricItem => {
    const nav = navigator as any;
    const conn = nav.connection || nav.mozConnection || nav.webkitConnection;
    let val = 'Not available';
    if (conn && conn.effectiveType) {
      val = conn.effectiveType.toUpperCase();
    }
    return { label: 'Network Connection', value: val, icon: Wifi };
  };

  const leftMetrics = [getPlatform(), getBrowser(), getCpuCores()];
  const rightMetrics = [getDeviceMemory(), getScreenRes(), getNetworkType()];

  return { leftMetrics, rightMetrics };
};

export const SystemMetricCard: React.FC<{ metrics: MetricItem[]; title?: string }> = ({ metrics, title }) => {
  return (
    <div className="bg-white dark:bg-zinc-900 border border-slate-200/90 dark:border-zinc-800 rounded-xl p-4 shadow-sm transition-colors">
      {title && (
        <div className="text-[10px] font-semibold text-slate-400 dark:text-zinc-500 uppercase tracking-wider mb-3 pb-2 border-b border-slate-100 dark:border-zinc-800 flex items-center justify-between">
          <span>{title}</span>
          <span className="text-[9px] font-mono text-slate-300 dark:text-zinc-600">SNAPSHOT</span>
        </div>
      )}
      <div className="space-y-2">
        {metrics.map((m, idx) => {
          const IconComponent = m.icon;
          const isNotAvailable = m.value === 'Not available';

          return (
            <div
              key={idx}
              className="p-2.5 rounded-lg bg-slate-50 dark:bg-zinc-950/60 border border-slate-200/70 dark:border-zinc-800/80"
            >
              <div className="flex items-center gap-1.5 mb-1">
                <IconComponent className="w-3.5 h-3.5 text-slate-400 dark:text-zinc-500 shrink-0" />
                <span className="text-[10px] font-medium text-slate-500 dark:text-zinc-400 uppercase tracking-tight">
                  {m.label}
                </span>
              </div>
              <span
                className={`font-mono text-xs font-semibold ${
                  isNotAvailable
                    ? 'text-slate-400 dark:text-zinc-600 italic'
                    : 'text-slate-900 dark:text-zinc-100'
                }`}
              >
                {m.value}
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
