import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { SupportModalComponent } from '../support-modal/support-modal.component';
import { SessionService } from '../services/session.service';

@Component({
  selector: 'app-header',
  standalone: true,
  imports: [CommonModule, SupportModalComponent],
  templateUrl: './header.component.html',
  styleUrl: './header.component.scss'
})
export class HeaderComponent {
  isSupportOpen = false;

  constructor(
    private readonly router: Router,
    private readonly session: SessionService
  ) {}

  get userName(): string {
    return this.session.firstName;
  }

  logout() {
    this.session.logout();
    this.router.navigate(['/login']);
  }

  openSupport() {
    this.isSupportOpen = true;
  }

  closeSupport(): void {
    this.isSupportOpen = false;
  }
}
