import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { SessionService } from '../services/session.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.scss'
})
export class LoginComponent {
  firstName = '';

  constructor(
    private readonly router: Router,
    private readonly session: SessionService
  ) {}

  login(): void {
    const safeName = this.firstName.trim() || 'Customer';
    this.session.login(safeName);
    this.router.navigate(['/get-started']);
  }

}
