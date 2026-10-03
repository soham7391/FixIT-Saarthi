/**
 * Lightweight deterministic domain-intent detector.
 *
 * Scans a problem description for strong keyword signals and returns the most
 * likely domain. Returns null when the text is ambiguous or too short to decide.
 *
 * Rules:
 * - Only triggers when a domain's scored keywords clearly dominate.
 * - A minimum number of signal words must be present to avoid false positives.
 * - Never forces a switch — callers must present a suggestion, not an override.
 */

import { DomainEnum } from '../types/diagnostic';

interface DomainSignals {
  domain: DomainEnum;
  keywords: string[];
  /** Minimum distinct keyword matches required to surface a suggestion. */
  minMatches: number;
}

const DOMAIN_SIGNALS: DomainSignals[] = [
  {
    domain: DomainEnum.NETWORK,
    minMatches: 2,
    keywords: [
      'wifi', 'wi-fi', 'wireless', 'internet', 'network', 'connected',
      'vpn', 'proxy', 'dns', 'router', 'modem', 'ethernet', 'hotspot',
      'no internet', 'cannot load', "can't load", 'websites', 'website',
      'bandwidth', 'ping', 'latency', 'ip address', 'online', 'offline',
      'connection drops', 'disconnects', 'weak signal', 'server not found',
      'dns error', 'web page', 'webpage', 'url', 'browser not loading',
    ],
  },
  {
    domain: DomainEnum.BOOT_FAILURE,
    minMatches: 2,
    keywords: [
      'boot', 'startup', 'start up', 'bios', 'uefi', 'logo screen',
      'startup repair', 'bsod', 'blue screen', 'reboot loop', 'restart loop',
      "won't start", "won't turn on", 'black screen on start',
      'stuck on logo', 'spinning dots', 'manufacturer logo',
      'slow to start', 'takes forever to start', 'takes minutes to boot',
      'slow startup', 'slow boot', 'loading screen', 'boot error',
    ],
  },
  {
    domain: DomainEnum.PERFORMANCE,
    minMatches: 2,
    keywords: [
      'cpu', 'processor', 'ram', 'memory usage', 'disk usage',
      'freeze', 'freezing', 'froze', 'lag', 'lagging', 'sluggish',
      'task manager', '100% cpu', '100% disk', '100% ram',
      'not responding', 'overheating', 'fan noise', 'thermal',
      'throttling', 'high cpu', 'high ram', 'high disk',
      'chrome using', 'process', 'app hangs', 'application hangs',
    ],
  },
  {
    domain: DomainEnum.DRIVER_PERIPHERAL,
    minMatches: 2,
    keywords: [
      'printer', 'print', 'printing', 'keyboard', 'mouse', 'trackpad',
      'microphone', 'mic', 'speaker', 'audio', 'sound', 'webcam', 'camera',
      'bluetooth', 'headset', 'headphone', 'peripheral', 'usb device',
      'driver', 'device manager', 'unplugged', 'not detected', 'not recognized',
      'device update', 'driver update', 'port', 'dongle',
    ],
  },
];

/**
 * Detects the probable domain of a user's problem description.
 *
 * @param text - The raw problem text entered by the user.
 * @returns The detected DomainEnum, or null if ambiguous / insufficient signal.
 */
export function detectDomainIntent(text: string): DomainEnum | null {
  if (!text || text.trim().length < 15) return null;

  const lower = text.toLowerCase();

  const scores: Array<{ domain: DomainEnum; score: number }> = DOMAIN_SIGNALS.map(
    ({ domain, keywords, minMatches }) => {
      // Count distinct keyword matches
      const matched = keywords.filter((kw) => lower.includes(kw));
      const score = matched.length >= minMatches ? matched.length : 0;
      return { domain, score };
    }
  );

  // Sort descending
  scores.sort((a, b) => b.score - a.score);

  const [first, second] = scores;

  // No signal
  if (!first || first.score === 0) return null;

  // Ambiguous: two domains tied — don't force
  if (second && second.score > 0 && second.score >= first.score) return null;

  return first.domain;
}
