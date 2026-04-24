import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { FeatureConfigService } from '../services/feature-config.service';
import { MockIntegrationsService } from '../services/mock-integrations.service';
import { SessionService } from '../services/session.service';

@Component({
  selector: 'app-complete-profile',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './complete-profile.component.html',
  styleUrl: './complete-profile.component.scss'
})
export class CompleteProfileComponent {
  model = {
    website: '',
    annualTransactions: '',
    notes: '',
    authorizedSigners: 0
  };

  message = '';

  constructor(
    private readonly router: Router,
    public readonly featureFlags: FeatureConfigService,
    private readonly integrations: MockIntegrationsService,
    private readonly session: SessionService
  ) {}

  get hasAtLeastOneField(): boolean {
    return !!(this.model.website || this.model.annualTransactions || this.model.notes || this.model.authorizedSigners);
  }

  async submit(): Promise<void> {
    if (!this.hasAtLeastOneField) {
      this.message = 'At least one field is required for submission.';
      return;
    }

    this.session.cache.completeProfile = { ...this.model };
    this.session.persistCache();
    await this.integrations.finalizeTransmitProvisioning();
    await this.integrations.triggerSfmcEvent('winback');
    this.message = 'Profile complete. Proceed to DocuSign consent.';
    this.router.navigate(['/docusign']);
  }

}
