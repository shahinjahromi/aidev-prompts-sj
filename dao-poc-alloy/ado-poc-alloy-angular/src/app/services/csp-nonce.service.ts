import { Injectable } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class CspNonceService {
  private readonly nonce = this.createNonce();

  applyNonceToDocument(): void {
    document.documentElement.setAttribute('data-csp-nonce', this.nonce);

    const scripts = document.querySelectorAll('script');
    scripts.forEach((script) => {
      script.setAttribute('nonce', this.nonce);
    });
  }

  getNonce(): string {
    return this.nonce;
  }

  private createNonce(): string {
    return Math.random().toString(36).slice(2) + Date.now().toString(36);
  }
}
