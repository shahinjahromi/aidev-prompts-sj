import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { SessionService } from '../services/session.service';

@Component({
  selector: 'app-additional-business-details',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './additional-business-details.component.html',
  styleUrl: './additional-business-details.component.scss'
})
export class AdditionalBusinessDetailsComponent {
  model = {
    industry: '',
    naics: '',
    annualRevenue: '',
    businessStory: ''
  };

  constructor(
    private readonly router: Router,
    private readonly session: SessionService
  ) {}

  submit(): void {
    this.session.cache.additionalBusiness = { ...this.model };
    this.session.persistCache();
    this.router.navigate(['/beneficial-owners']);
  }

}
