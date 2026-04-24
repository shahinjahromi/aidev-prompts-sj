import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { FeatureConfigService } from '../services/feature-config.service';
import { SessionService } from '../services/session.service';

@Component({
  selector: 'app-controlling-party',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './controlling-party.component.html',
  styleUrl: './controlling-party.component.scss'
})
export class ControllingPartyComponent {
  role = 'Owner';
  otherRole = '';

  constructor(
    private readonly router: Router,
    private readonly featureFlags: FeatureConfigService,
    private readonly session: SessionService
  ) {}

  get showOtherRole(): boolean {
    return this.featureFlags.flags.enableBOAuthorizedUser;
  }

  async toggleFlag(): Promise<void> {
    this.featureFlags.setFlags({ enableBOAuthorizedUser: !this.featureFlags.flags.enableBOAuthorizedUser });
    await this.featureFlags.loadFromGraphql();
  }

  next(): void {
    this.session.cache.controllingParty = {
      role: this.role,
      otherRole: this.role === 'Other' ? this.otherRole : undefined
    };
    this.session.persistCache();
    this.router.navigate(['/complete-profile']);
  }

}
