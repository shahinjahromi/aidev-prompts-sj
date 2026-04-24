import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { SessionService } from '../services/session.service';

@Component({
  selector: 'app-docusign',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './docusign.component.html',
  styleUrl: './docusign.component.scss'
})
export class DocusignComponent {
  consent = false;
  message = '';

  constructor(
    private readonly router: Router,
    private readonly session: SessionService
  ) {}

  submit(): void {
    if (!this.consent) {
      this.message = 'E-sign consent is required.';
      return;
    }

    this.session.recordConsent('e_sign', new Date().toISOString());
    this.session.recordConsent('kyc', new Date().toISOString());
    this.message = 'Consent saved. Redirecting to liveness verification.';
    this.router.navigate(['/omb']);
  }

}
