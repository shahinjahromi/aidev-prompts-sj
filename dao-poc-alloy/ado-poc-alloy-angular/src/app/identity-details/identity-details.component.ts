import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { SessionService } from '../services/session.service';

@Component({
  selector: 'app-identity-details',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './identity-details.component.html',
  styleUrl: './identity-details.component.scss'
})
export class IdentityDetailsComponent {
  model = {
    dob: '',
    ssn: '',
    homeAddress: '',
    residency: 'US Citizen'
  };

  residencies = ['US Citizen', 'US National', 'Permanent Resident', 'Other'];

  constructor(
    private readonly router: Router,
    private readonly session: SessionService
  ) {}

  submit(): void {
    this.session.cache.identity = { ...this.model };
    this.session.persistCache();
    this.router.navigate(['/business-details']);
  }

}
