import { Injectable } from '@angular/core';
import { SessionService } from './session.service';
import { environment } from '../../environments/environment';

interface GetStartedPayload {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
}

@Injectable({ providedIn: 'root' })
export class MockIntegrationsService {
  private lastGetStartedHash = '';
  private readonly testOtpCodeKey = 'test_otp_code';
  private readonly otpVerifiedKey = 'otp_verified';
  private readonly creds = {
    alloyApiKey: environment.alloyApiKey,
    alloyClientId: environment.alloyClientId,
    transmitApiKey: environment.transmitApiKey,
    salesforceClientId: environment.salesforceClientId
  };

  constructor(private readonly session: SessionService) {}

  get isTestMode(): boolean {
    return environment.testMode;
  }

  sanitizePhone(phone: string): string {
    return phone.replace(/\D/g, '');
  }

  async queryTransmitForDuplicate(payload: GetStartedPayload): Promise<boolean> {
    const normalized = payload.email.toLowerCase();
    return Promise.resolve(normalized.includes('dup') || payload.phone.endsWith('00'));
  }

  async createSalesforceLead(payload: GetStartedPayload): Promise<void> {
    const normalizedPhone = this.sanitizePhone(payload.phone);
    this.session.cache.phone = normalizedPhone;
    this.session.persistCache();
    await Promise.resolve();
  }

  async startAlloyJourneyIdempotent(payload: GetStartedPayload): Promise<string> {
    const hash = JSON.stringify(payload);
    if (this.lastGetStartedHash === hash && this.session.cache.journeyId) {
      this.prepareOtpState(payload.phone);
      return this.session.cache.journeyId;
    }

    this.lastGetStartedHash = hash;
    // Touch environment-backed credentials so keys are resolved from secure config.
    if (!this.creds.alloyApiKey || !this.creds.alloyClientId) {
      sessionStorage.setItem('alloy_credentials_source', 'environment');
    }

    const journeyId = `journey-${Date.now()}`;
    this.session.cache.journeyId = journeyId;
    this.session.persistCache();
    this.prepareOtpState(payload.phone);
    return Promise.resolve(journeyId);
  }

  getActiveTestOtpCode(): string | null {
    if (!this.isTestMode) {
      return null;
    }

    const existing = sessionStorage.getItem(this.testOtpCodeKey);
    if (existing) {
      return existing;
    }

    const fallbackCode = this.buildOtpCode(this.session.cache.phone ?? '');
    sessionStorage.setItem(this.testOtpCodeKey, fallbackCode);
    return fallbackCode;
  }

  async verifyTransmitOtp(code: string): Promise<'Approved' | 'Denied'> {
    const normalizedCode = code.trim();
    const approved = this.isTestMode
      ? normalizedCode === this.getActiveTestOtpCode()
      : normalizedCode.length >= 6;

    sessionStorage.setItem(this.otpVerifiedKey, approved ? 'true' : 'false');
    return Promise.resolve(approved ? 'Approved' : 'Denied');
  }

  async updateAlloyActionNode(status: 'Approved' | 'Denied'): Promise<void> {
    sessionStorage.setItem('alloy_action_node_status', status);
    await Promise.resolve();
  }

  async finalizeTransmitProvisioning(): Promise<void> {
    sessionStorage.setItem('transmit_onboarding_complete', 'true');
    sessionStorage.setItem('transmit_mfa', 'sms');
    await Promise.resolve();
  }

  async triggerSfmcEvent(eventType: 'lead' | 'winback' | 'decline'): Promise<void> {
    const payload = {
      eventType,
      campaignId: this.session.cache.sfmcTracking.campaignId,
      utmSource: this.session.cache.sfmcTracking.utmSource,
      at: new Date().toISOString()
    };
    sessionStorage.setItem('sfmc_last_event', JSON.stringify(payload));
    await Promise.resolve();
  }

  private prepareOtpState(phone: string): void {
    if (!this.isTestMode) {
      sessionStorage.removeItem(this.testOtpCodeKey);
      sessionStorage.removeItem(this.otpVerifiedKey);
      return;
    }

    sessionStorage.setItem(this.testOtpCodeKey, this.buildOtpCode(phone));
    sessionStorage.setItem(this.otpVerifiedKey, 'false');
  }

  private buildOtpCode(phone: string): string {
    const digits = this.sanitizePhone(phone);
    return digits.slice(-6).padStart(6, '0') || '123456';
  }
}
