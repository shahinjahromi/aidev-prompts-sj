import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { SessionService } from '../services/session.service';

@Component({
  selector: 'app-business-details',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './business-details.component.html',
  styleUrl: './business-details.component.scss'
})
export class BusinessDetailsComponent {
  model = {
    legalName: '',
    entityType: 'LLC - Limited Liability Company',
    role: 'Managing Member'
  };

  readonly entityTypes = [
    'LLC - Limited Liability Company',
    'Corporation - C Corp or S Corp',
    'Sole Proprietorship - single owner business'
  ];

  constructor(
    private readonly router: Router,
    private readonly session: SessionService
  ) {}

  submit(): void {
    this.session.cache.business = { ...this.model };
    this.session.persistCache();
    this.router.navigate(['/additional-business-details']);
  }

}
