import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MockIntegrationsService } from '../services/mock-integrations.service';
import { SessionService } from '../services/session.service';

@Component({
  selector: 'app-get-started',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './get-started.component.html',
  styleUrl: './get-started.component.scss'
})
export class GetStartedComponent {
  model = {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    smsConsent: false
  };
  statusMessage = '';
  isSaving = false;

  constructor(
    private readonly router: Router,
    private readonly integrations: MockIntegrationsService,
    private readonly session: SessionService
  ) {}

  async submit(): Promise<void> {
    if (!this.model.firstName || !this.model.lastName || !this.model.email || !this.model.phone) {
      this.statusMessage = 'Please complete all required fields.';
      return;
    }

    this.isSaving = true;
    this.session.cache.firstName = this.model.firstName;
    this.session.cache.lastName = this.model.lastName;
    this.session.cache.email = this.model.email;
    this.session.cache.phone = this.integrations.sanitizePhone(this.model.phone);

    if (this.model.smsConsent) {
      this.session.recordConsent('tcpa', new Date().toISOString());
    }

    const hasDuplicate = await this.integrations.queryTransmitForDuplicate(this.model);
    await this.integrations.createSalesforceLead(this.model);
    await this.integrations.startAlloyJourneyIdempotent(this.model);
    await this.integrations.triggerSfmcEvent('lead');

    this.session.persistCache();
    this.isSaving = false;
    this.statusMessage = hasDuplicate
      ? 'Possible duplicate found. Salesforce Lead has been created and flagged.'
      : 'New user created. Proceeding to OTP verification.';

    this.router.navigate(['/otp']);
  }

}
