import React from 'react';
import { ArrowLeft, ArrowRight, Check, X, HelpCircle } from 'lucide-react';
import type { QuestionCardItem } from '../types/diagnostic';
import { DomainEnum } from '../types/diagnostic';

interface QuestionnaireStepProps {
  currentDomain?: DomainEnum;
  answers: Record<string, boolean | undefined>;
  onAnswerChange: (symptomKey: string, value: boolean | undefined) => void;
  onBack: () => void;
  onNext: () => void;
}

const PERFORMANCE_QUESTION_CARDS: QuestionCardItem[] = [
  {
    id: 'q_cpu',
    symptomKey: 'high_cpu_usage',
    questionText: 'Is your CPU usage frequently spiking to 80%-100% in Task Manager?',
    category: 'CPU',
    description: 'High processor workload caused by rogue processes, background scans, or heavy software.',
    type: 'boolean'
  },
  {
    id: 'q_ram',
    symptomKey: 'high_ram_usage',
    questionText: 'Is your RAM / Memory usage above 80% or experiencing memory leaks?',
    category: 'Memory',
    description: 'System memory exhaustion caused by browser tabs (Chrome) or memory leaking background apps.',
    type: 'boolean'
  },
  {
    id: 'q_disk',
    symptomKey: 'high_disk_usage',
    questionText: 'Is your Disk usage stuck at 100% or making continuous read/write sounds?',
    category: 'Disk',
    description: 'Disk saturation, mechanical HDD bottlenecks, or Windows Search indexing spikes.',
    type: 'boolean'
  },
  {
    id: 'q_freeze',
    symptomKey: 'app_freezing',
    questionText: 'Are specific applications freezing or showing "(Not Responding)" in the title bar?',
    category: 'System',
    description: 'Application hangs, thread lockups, or unresponsive software windows.',
    type: 'boolean'
  },
  {
    id: 'q_slowdown',
    symptomKey: 'general_slowdown',
    questionText: 'Is the overall OS experiencing sluggish response, cursor lag, or typing delays?',
    category: 'System',
    description: 'General system-wide latency across all desktop operations.',
    type: 'boolean'
  },
  {
    id: 'q_thermal',
    symptomKey: 'thermal_throttling',
    questionText: 'Is your computer running unusually hot, with loud fan noise or thermal throttling?',
    category: 'Power',
    description: 'CPU clock speed reduction due to thermal overheating or power plan limits.',
    type: 'boolean'
  }
];

const BOOT_QUESTION_CARDS: QuestionCardItem[] = [
  {
    id: 'q_slow_boot',
    symptomKey: 'slow_boot_time',
    questionText: 'Is your computer taking over 2-5 minutes to boot into Windows?',
    category: 'Boot',
    description: 'Extended startup delay before reaching the login screen or desktop.',
    type: 'boolean'
  },
  {
    id: 'q_stuck_logo',
    symptomKey: 'stuck_on_logo',
    questionText: 'Is your system stuck on the manufacturer logo or spinning dots screen?',
    category: 'Boot',
    description: 'Windows logo or UEFI splash screen hangs indefinitely during startup.',
    type: 'boolean'
  },
  {
    id: 'q_boot_error',
    symptomKey: 'boot_error_screen',
    questionText: 'Does Windows display a boot error screen, BSOD, or automatic repair prompt?',
    category: 'System Error',
    description: 'Startup failure error screens, blue screen crash codes, or BCD boot errors.',
    type: 'boolean'
  },
  {
    id: 'q_reboot_loop',
    symptomKey: 'reboot_loop',
    questionText: 'Is your PC repeatedly restarting before reaching the login screen?',
    category: 'Startup',
    description: 'Continuous reboot loops during early system initialization.',
    type: 'boolean'
  },
  {
    id: 'q_recent_update',
    symptomKey: 'recent_windows_update',
    questionText: 'Did this boot issue start immediately after a recent Windows update or driver install?',
    category: 'OS Update',
    description: 'Pending or failed updates interfering with Windows startup configuration.',
    type: 'boolean'
  },
  {
    id: 'q_external_drives',
    symptomKey: 'external_drives_connected',
    questionText: 'Are there any external USB hard drives, flash drives, or cards attached during startup?',
    category: 'Hardware',
    description: 'External USB media conflicting with BIOS/UEFI boot device sequence.',
    type: 'boolean'
  }
];

const NETWORK_QUESTION_CARDS: QuestionCardItem[] = [
  {
    id: 'q_wifi_disabled',
    symptomKey: 'wifi_disabled_airplane',
    questionText: 'Is Wi-Fi disabled or Airplane Mode turned on in your system settings?',
    category: 'Wi-Fi',
    description: 'Wi-Fi adapter switched off in Settings or Airplane Mode blocking all wireless connections.',
    type: 'boolean'
  },
  {
    id: 'q_connected_no_internet',
    symptomKey: 'connected_no_internet',
    questionText: 'Are you connected to Wi-Fi but unable to access websites or online services?',
    category: 'Internet',
    description: 'Device shows Wi-Fi connected but pages fail to load — possible DNS, gateway, or ISP issue.',
    type: 'boolean'
  },
  {
    id: 'q_intermittent',
    symptomKey: 'intermittent_disconnection',
    questionText: 'Does your connection drop frequently or show a weak / unstable Wi-Fi signal?',
    category: 'Signal',
    description: 'Frequent disconnections, signal drops, or Wi-Fi cutting out at intervals.',
    type: 'boolean'
  },
  {
    id: 'q_dns',
    symptomKey: 'dns_lookup_failure',
    questionText: 'Do websites fail with "Server Not Found", "DNS_PROBE_FINISHED", or similar DNS errors?',
    category: 'DNS',
    description: 'DNS resolver failures preventing domain name resolution for websites.',
    type: 'boolean'
  },
  {
    id: 'q_vpn',
    symptomKey: 'vpn_proxy_enabled',
    questionText: 'Is VPN or proxy software currently active on this device?',
    category: 'VPN / Proxy',
    description: 'Active VPN or proxy routing can block, slow, or redirect internet traffic.',
    type: 'boolean'
  },
  {
    id: 'q_other_devices',
    symptomKey: 'other_devices_working',
    questionText: 'Do other devices on the same Wi-Fi network have working internet access?',
    category: 'Network',
    description: 'Helps isolate whether the issue is device-specific or affects the entire network / router.',
    type: 'boolean'
  }
];

const DRIVER_QUESTION_CARDS: QuestionCardItem[] = [
  {
    id: 'q_printer',
    symptomKey: 'printer_not_detected',
    questionText: 'Is your printer showing as Offline, not recognized, or failing to print jobs?',
    category: 'Printer',
    description: 'Printer spooler error, USB cable disconnect, or offline printer status.',
    type: 'boolean'
  },
  {
    id: 'q_keyboard_mouse',
    symptomKey: 'keyboard_mouse_unresponsive',
    questionText: 'Is your keyboard, mouse, or trackpad completely unresponsive to keypresses or clicks?',
    category: 'Input Device',
    description: 'Unresponsive USB/wireless keyboard, mouse freeze, or dead battery.',
    type: 'boolean'
  },
  {
    id: 'q_audio',
    symptomKey: 'audio_device_issue',
    questionText: 'Are your speakers producing no sound or is your microphone failing to record audio?',
    category: 'Audio',
    description: 'Muted audio, wrong default output/input device, or headset mic issue.',
    type: 'boolean'
  },
  {
    id: 'q_webcam',
    symptomKey: 'webcam_unavailable',
    questionText: 'Is your webcam showing a black screen, error code, or "No Camera Found"?',
    category: 'Webcam',
    description: 'Webcam hardware disabled, disconnected, or blocked by privacy toggle.',
    type: 'boolean'
  },
  {
    id: 'q_bluetooth',
    symptomKey: 'bluetooth_connection_failed',
    questionText: 'Is your Bluetooth device failing to connect, pair, or dropping connection?',
    category: 'Bluetooth',
    description: 'Bluetooth radio turned off, stale pairing cache, or signal interference.',
    type: 'boolean'
  },
  {
    id: 'q_driver_update',
    symptomKey: 'device_failed_after_update',
    questionText: 'Did this peripheral stop working immediately after a Windows or driver update?',
    category: 'Driver Update',
    description: 'Incompatible driver version installed during a recent system update.',
    type: 'boolean'
  },
  {
    id: 'q_privacy_blocked',
    symptomKey: 'app_permissions_blocked',
    questionText: 'Are Windows privacy settings blocking applications from accessing camera or microphone?',
    category: 'Privacy Settings',
    description: 'Windows 11/10 privacy toggle preventing software access to media hardware.',
    type: 'boolean'
  }
];

export const QuestionnaireStep: React.FC<QuestionnaireStepProps> = ({
  currentDomain = DomainEnum.PERFORMANCE,
  answers,
  onAnswerChange,
  onBack,
  onNext
}) => {
  const questionCards =
    currentDomain === DomainEnum.BOOT_FAILURE
      ? BOOT_QUESTION_CARDS
      : currentDomain === DomainEnum.NETWORK
      ? NETWORK_QUESTION_CARDS
      : currentDomain === DomainEnum.DRIVER_PERIPHERAL
      ? DRIVER_QUESTION_CARDS
      : PERFORMANCE_QUESTION_CARDS;
  const answeredCount = Object.keys(answers).filter((k) => questionCards.some((c) => c.symptomKey === k) && answers[k] !== undefined).length;

  return (
    <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl p-6 shadow-sm max-w-4xl mx-auto transition-colors">
      {/* Header */}
      <div className="flex items-center justify-between mb-5 pb-4 border-b border-slate-100 dark:border-zinc-800">
        <div>
          <h2 className="text-base font-semibold text-slate-900 dark:text-zinc-100">
            {currentDomain === DomainEnum.BOOT_FAILURE
              ? 'Boot & Startup Question Cards'
              : currentDomain === DomainEnum.NETWORK
              ? 'Network & Connectivity Question Cards'
              : currentDomain === DomainEnum.DRIVER_PERIPHERAL
              ? 'Driver & Peripheral Question Cards'
              : 'Diagnostic Question Cards'}
          </h2>
          <p className="text-xs text-slate-500 dark:text-zinc-400">
            Answer symptom questions to refine cause ranking accuracy.
          </p>
        </div>
        <div className="px-2.5 py-1 rounded bg-slate-100 dark:bg-zinc-800 border border-slate-200 dark:border-zinc-700 text-xs text-slate-700 dark:text-zinc-300 font-mono">
          {answeredCount}/{questionCards.length} Answered
        </div>
      </div>

      {/* Grid of Question Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        {questionCards.map((card) => {
          const currentVal = answers[card.symptomKey];

          return (
            <div
              key={card.id}
              className={`p-4 rounded-lg border transition-all ${
                currentVal === true
                  ? 'bg-blue-50/70 dark:bg-zinc-800/80 border-blue-200 dark:border-zinc-700'
                  : currentVal === false
                  ? 'bg-slate-50 dark:bg-zinc-950/60 border-slate-200 dark:border-zinc-800/80 opacity-80'
                  : 'bg-slate-50/50 dark:bg-zinc-950/40 border-slate-200 dark:border-zinc-800 hover:border-slate-300 dark:hover:border-zinc-700'
              }`}
            >
              <div className="flex items-center justify-between gap-2 mb-2">
                <span className="text-[10px] font-semibold uppercase tracking-wider px-2 py-0.5 rounded bg-slate-100 dark:bg-zinc-800 text-slate-600 dark:text-zinc-400 border border-slate-200 dark:border-zinc-700">
                  {card.category}
                </span>
                <span className="text-[11px] font-mono text-slate-400 dark:text-zinc-500">{card.symptomKey}</span>
              </div>

              <h4 className="text-xs font-semibold text-slate-900 dark:text-zinc-100 mb-1 leading-relaxed">
                {card.questionText}
              </h4>
              <p className="text-[11px] text-slate-500 dark:text-zinc-400 mb-4">{card.description}</p>

              {/* Answer Controls */}
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => onAnswerChange(card.symptomKey, true)}
                  className={`flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-md text-xs font-medium border transition-all active:scale-95 focus:outline-none focus:ring-2 focus:ring-indigo-500/50 ${
                    currentVal === true
                      ? 'bg-indigo-600 text-white border-indigo-600 shadow-sm'
                      : 'bg-white dark:bg-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 border-slate-200 dark:border-zinc-700'
                  }`}
                >
                  <Check className="w-3.5 h-3.5" />
                  Yes
                </button>

                <button
                  type="button"
                  onClick={() => onAnswerChange(card.symptomKey, false)}
                  className={`flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-md text-xs font-medium border transition-all active:scale-95 focus:outline-none focus:ring-2 focus:ring-slate-500/50 ${
                    currentVal === false
                      ? 'bg-slate-800 dark:bg-zinc-700 text-white border-slate-800 dark:border-zinc-700 shadow-sm'
                      : 'bg-white dark:bg-zinc-800 hover:bg-slate-100 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 border-slate-200 dark:border-zinc-700'
                  }`}
                >
                  <X className="w-3.5 h-3.5" />
                  No
                </button>

                <button
                  type="button"
                  onClick={() => onAnswerChange(card.symptomKey, undefined)}
                  className={`flex items-center justify-center gap-1.5 py-1.5 px-2 rounded-md text-xs font-medium border transition-all active:scale-95 focus:outline-none focus:ring-2 focus:ring-slate-400 dark:focus:ring-zinc-500 ${
                    currentVal === undefined
                      ? 'bg-slate-200 dark:bg-zinc-800 text-slate-900 dark:text-zinc-100 border-slate-300 dark:border-zinc-600 font-semibold shadow-xs ring-1 ring-slate-300 dark:ring-zinc-700'
                      : 'bg-white dark:bg-zinc-900 hover:bg-slate-100 dark:hover:bg-zinc-800 text-slate-600 dark:text-zinc-400 border-slate-200 dark:border-zinc-800'
                  }`}
                  title="Skip this question without answering"
                >
                  <HelpCircle className="w-3.5 h-3.5 text-slate-500 dark:text-zinc-400" />
                  Skip
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Navigation */}
      <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-zinc-800">
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-md bg-slate-100 dark:bg-zinc-800 hover:bg-slate-200 dark:hover:bg-zinc-700 text-slate-700 dark:text-zinc-300 text-xs font-medium flex items-center gap-2 transition-all border border-slate-200 dark:border-zinc-700"
        >
          <ArrowLeft className="w-4 h-4" />
          Back: Problem Description
        </button>

        <button
          onClick={onNext}
          className="px-5 py-2 rounded-md bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-medium shadow-sm flex items-center gap-2 transition-all"
        >
          Continue: Screenshot Upload
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
