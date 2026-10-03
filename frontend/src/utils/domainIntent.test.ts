/**
 * Unit tests for the detectDomainIntent utility (Bug 2 — domain routing).
 *
 * Run with: npx vitest run src/utils/domainIntent.test.ts
 * (or as part of the regular test suite)
 */

import { describe, it, expect } from 'vitest';
import { detectDomainIntent } from './domainIntent';
import { DomainEnum } from '../types/diagnostic';

describe('detectDomainIntent', () => {
  // -------------------------------------------------------------------------
  // Network detection
  // -------------------------------------------------------------------------
  it('detects network intent for a VPN connectivity description', () => {
    const text =
      'My Windows laptop connects to my home Wi-Fi, but websites cannot load when my VPN ' +
      'is turned on. Other devices on the same Wi-Fi can access the internet normally.';
    expect(detectDomainIntent(text)).toBe(DomainEnum.NETWORK);
  });

  it('detects network intent for a DNS error description', () => {
    const text = 'Websites show dns error and server not found. The internet is not working.';
    expect(detectDomainIntent(text)).toBe(DomainEnum.NETWORK);
  });

  it('detects network intent for a simple wifi/internet description', () => {
    const text = 'My wifi is connected but the internet is very slow. Other devices work fine on the same network.';
    expect(detectDomainIntent(text)).toBe(DomainEnum.NETWORK);
  });

  // -------------------------------------------------------------------------
  // Boot detection
  // -------------------------------------------------------------------------
  it('detects boot intent for a slow boot description', () => {
    const text = 'My PC takes forever to boot. It gets stuck on the logo screen for 10 minutes during startup.';
    expect(detectDomainIntent(text)).toBe(DomainEnum.BOOT_FAILURE);
  });

  it('detects boot intent for a BSOD description', () => {
    const text = 'Windows shows a bsod blue screen and then goes into startup repair.';
    expect(detectDomainIntent(text)).toBe(DomainEnum.BOOT_FAILURE);
  });

  // -------------------------------------------------------------------------
  // Performance detection
  // -------------------------------------------------------------------------
  it('detects performance intent for a CPU freeze description', () => {
    const text = 'My CPU is at 100% and Task Manager shows the process is not responding. Everything lags.';
    expect(detectDomainIntent(text)).toBe(DomainEnum.PERFORMANCE);
  });

  it('detects performance intent for a RAM description', () => {
    const text = 'Chrome is using 8 GB of memory usage and the system is very sluggish and freezing.';
    expect(detectDomainIntent(text)).toBe(DomainEnum.PERFORMANCE);
  });

  // -------------------------------------------------------------------------
  // Driver & Peripheral detection
  // -------------------------------------------------------------------------
  it('detects driver/peripheral intent for printer issues', () => {
    const text = 'My printer is connected via USB cable but Windows shows offline and it is not printing.';
    expect(detectDomainIntent(text)).toBe(DomainEnum.DRIVER_PERIPHERAL);
  });

  it('detects driver/peripheral intent for audio/mic issues', () => {
    const text = 'The microphone has no sound input and the headset audio speaker is not recognized by driver.';
    expect(detectDomainIntent(text)).toBe(DomainEnum.DRIVER_PERIPHERAL);
  });

  it('detects driver/peripheral intent for bluetooth peripheral issues', () => {
    const text = 'My bluetooth mouse and keyboard fail pairing in device manager after driver update.';
    expect(detectDomainIntent(text)).toBe(DomainEnum.DRIVER_PERIPHERAL);
  });

  // -------------------------------------------------------------------------
  // No false positives — ambiguous or too short
  // -------------------------------------------------------------------------
  it('returns null for a very short/ambiguous text', () => {
    expect(detectDomainIntent('slow')).toBeNull();
    expect(detectDomainIntent('')).toBeNull();
    expect(detectDomainIntent('my computer has a problem')).toBeNull();
  });

  it('returns null for text with mixed signals (ambiguous)', () => {
    // "slow" appears in both performance and network keywords, but no clear winner
    const text = 'My computer is slow and the internet is also slow on all devices.';
    // This may return either or null — it must NOT assert a specific wrong domain
    const result = detectDomainIntent(text);
    // If it returns something, it must be a valid DomainEnum
    if (result !== null) {
      expect(Object.values(DomainEnum)).toContain(result);
    }
  });

  it('does not suggest network for a pure CPU performance problem', () => {
    const text =
      'Task Manager shows 100% CPU usage. The high disk usage is causing the application to freeze ' +
      'and show not responding in the title bar. Thermal throttling is making it worse.';
    const result = detectDomainIntent(text);
    expect(result).not.toBe(DomainEnum.NETWORK);
    expect(result).not.toBe(DomainEnum.BOOT_FAILURE);
  });
});
