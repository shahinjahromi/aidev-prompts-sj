import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { HeaderComponent } from './header/header.component';
import { FooterComponent } from './footer/footer.component';
import { CspNonceService } from './services/csp-nonce.service';
import { FeatureConfigService } from './services/feature-config.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, HeaderComponent, FooterComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'ado-poc-alloy-angular';

  constructor(
    private readonly cspNonceService: CspNonceService,
    private readonly featureConfigService: FeatureConfigService
  ) {
    this.cspNonceService.applyNonceToDocument();
    this.featureConfigService.loadFromGraphql();
  }
}
