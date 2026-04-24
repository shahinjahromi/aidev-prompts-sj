import { Injectable } from '@angular/core';

export interface OwnerRecord {
  fullName: string;
  ownershipPercent: number;
  wantsDebitCard: boolean;
}

export interface FlowCache {
  firstName?: string;
  lastName?: string;
  email?: string;
  phone?: string;
  identity?: {
    dob: string;
    ssn: string;
    homeAddress: string;
    residency: string;
  };
  business?: {
    legalName: string;
    entityType: string;
    role: string;
  };
  additionalBusiness?: {
    industry: string;
    naics: string;
    annualRevenue: string;
    businessStory: string;
  };
  owners: OwnerRecord[];
  controllingParty?: {
    role: string;
    otherRole?: string;
  };
  completeProfile?: {
    website?: string;
    annualTransactions?: string;
    notes?: string;
    authorizedSigners?: number;
  };
  consentTimestamps: Record<string, string>;
  sfmcTracking: {
    utmSource: string;
    campaignId: string;
  };
  journeyId?: string;
}

@Injectable({ providedIn: 'root' })
export class SessionService {
  private readonly tokenKey = 'auth_token';
  private readonly cacheKey = 'flow_cache';
  private readonly userKey = 'user_first_name';

  cache: FlowCache = {
    owners: [],
    consentTimestamps: {},
    sfmcTracking: {
      utmSource: 'web-onboarding',
      campaignId: 'lead-default'
    }
  };

  constructor() {
    this.restoreCache();
  }

  get isAuthenticated(): boolean {
    return !!localStorage.getItem(this.tokenKey);
  }

  get firstName(): string {
    return localStorage.getItem(this.userKey) ?? this.cache.firstName ?? 'Customer';
  }

  login(firstName: string): void {
    localStorage.setItem(this.tokenKey, `token-${Date.now()}`);
    localStorage.setItem(this.userKey, firstName);
    this.cache.firstName = firstName;
    this.persistCache();
  }

  logout(): void {
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
    this.cache = {
      owners: [],
      consentTimestamps: {},
      sfmcTracking: {
        utmSource: 'web-onboarding',
        campaignId: 'lead-default'
      }
    };
    this.persistCache();
    sessionStorage.clear();
  }

  recordConsent(key: string, isoTimestamp: string): void {
    this.cache.consentTimestamps[key] = isoTimestamp;
    this.persistCache();
  }

  persistCache(): void {
    localStorage.setItem(this.cacheKey, JSON.stringify(this.cache));
  }

  private restoreCache(): void {
    const raw = localStorage.getItem(this.cacheKey);
    if (!raw) {
      return;
    }

    try {
      const parsed = JSON.parse(raw) as FlowCache;
      const base: FlowCache = {
        owners: [],
        consentTimestamps: {},
        sfmcTracking: {
          utmSource: 'web-onboarding',
          campaignId: 'lead-default'
        }
      };

      this.cache = {
        ...base,
        ...parsed,
        owners: parsed.owners ?? base.owners,
        consentTimestamps: parsed.consentTimestamps ?? base.consentTimestamps,
        sfmcTracking: parsed.sfmcTracking ?? base.sfmcTracking
      };
    } catch {
      this.persistCache();
    }
  }
}
