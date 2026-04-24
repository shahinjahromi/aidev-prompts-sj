import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { FeatureConfigService } from '../services/feature-config.service';
import { OwnerRecord } from '../services/session.service';
import { SessionService } from '../services/session.service';

@Component({
  selector: 'app-beneficial-owners',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './beneficial-owners.component.html',
  styleUrl: './beneficial-owners.component.scss'
})
export class BeneficialOwnersComponent {
  owner: OwnerRecord = {
    fullName: '',
    ownershipPercent: 0,
    wantsDebitCard: false
  };

  constructor(
    private readonly router: Router,
    private readonly featureFlags: FeatureConfigService,
    public readonly session: SessionService
  ) {}

  get showDebitCardToggle(): boolean {
    return this.featureFlags.flags.enableBODebitCard;
  }

  async toggleFlag(): Promise<void> {
    this.featureFlags.setFlags({ enableBODebitCard: !this.featureFlags.flags.enableBODebitCard });
    await this.featureFlags.loadFromGraphql();
  }

  addOwner(): void {
    if (!this.owner.fullName || this.owner.ownershipPercent <= 0) {
      return;
    }

    if (this.session.cache.owners.length >= 5) {
      return;
    }

    this.session.cache.owners.push({ ...this.owner });
    this.session.persistCache();
    this.owner = {
      fullName: '',
      ownershipPercent: 0,
      wantsDebitCard: false
    };
  }

  next(): void {
    this.router.navigate(['/controlling-party']);
  }

}
