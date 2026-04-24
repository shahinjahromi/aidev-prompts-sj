import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { MockIntegrationsService } from '../services/mock-integrations.service';

@Component({
  selector: 'app-otp',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './otp.component.html',
  styleUrl: './otp.component.scss'
})
export class OtpComponent {
  otp = '';
  feedback = '';
  readonly showTestOtp: boolean;
  readonly testOtpCode: string | null;

  constructor(
    private readonly router: Router,
    private readonly integrations: MockIntegrationsService
  ) {
    this.showTestOtp = this.integrations.isTestMode;
    this.testOtpCode = this.integrations.getActiveTestOtpCode();
  }

  async verify(): Promise<void> {
    const status = await this.integrations.verifyTransmitOtp(this.otp);
    await this.integrations.updateAlloyActionNode(status);
    this.feedback = `OTP status: ${status}`;
    if (status === 'Approved') {
      this.router.navigate(['/identity-details']);
    }
  }

}
