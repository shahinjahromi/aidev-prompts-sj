import { Injectable } from '@angular/core';

export interface FeatureFlags {
  enableBODebitCard: boolean;
  enableBOAuthorizedUser: boolean;
  enabledAuthorizedUsers: boolean;
}

@Injectable({ providedIn: 'root' })
export class FeatureConfigService {
  flags: FeatureFlags = {
    enableBODebitCard: true,
    enableBOAuthorizedUser: true,
    enabledAuthorizedUsers: true
  };

  async loadFromGraphql(): Promise<FeatureFlags> {
    // Mock GraphQL fetch for this POC app.
    await Promise.resolve();
    return this.flags;
  }

  setFlags(next: Partial<FeatureFlags>): void {
    this.flags = { ...this.flags, ...next };
  }
}
