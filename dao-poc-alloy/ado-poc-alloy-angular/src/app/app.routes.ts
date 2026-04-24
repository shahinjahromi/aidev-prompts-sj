import { Routes } from '@angular/router';
import { authGuard } from './auth.guard';

export const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: 'get-started'
  },
  {
    path: 'login',
    loadComponent: () => import('./login/login.component').then((m) => m.LoginComponent)
  },
  {
    path: 'get-started',
    canActivate: [authGuard],
    loadComponent: () => import('./get-started/get-started.component').then((m) => m.GetStartedComponent)
  },
  {
    path: 'otp',
    canActivate: [authGuard],
    loadComponent: () => import('./otp/otp.component').then((m) => m.OtpComponent)
  },
  {
    path: 'identity-details',
    canActivate: [authGuard],
    loadComponent: () => import('./identity-details/identity-details.component').then((m) => m.IdentityDetailsComponent)
  },
  {
    path: 'business-details',
    canActivate: [authGuard],
    loadComponent: () => import('./business-details/business-details.component').then((m) => m.BusinessDetailsComponent)
  },
  {
    path: 'additional-business-details',
    canActivate: [authGuard],
    loadComponent: () =>
      import('./additional-business-details/additional-business-details.component').then((m) => m.AdditionalBusinessDetailsComponent)
  },
  {
    path: 'beneficial-owners',
    canActivate: [authGuard],
    loadComponent: () => import('./beneficial-owners/beneficial-owners.component').then((m) => m.BeneficialOwnersComponent)
  },
  {
    path: 'controlling-party',
    canActivate: [authGuard],
    loadComponent: () => import('./controlling-party/controlling-party.component').then((m) => m.ControllingPartyComponent)
  },
  {
    path: 'complete-profile',
    canActivate: [authGuard],
    loadComponent: () => import('./complete-profile/complete-profile.component').then((m) => m.CompleteProfileComponent)
  },
  {
    path: 'docusign',
    canActivate: [authGuard],
    loadComponent: () => import('./docusign/docusign.component').then((m) => m.DocusignComponent)
  },
  {
    path: 'omb',
    canActivate: [authGuard],
    loadComponent: () => import('./omb-landing/omb-landing.component').then((m) => m.OmbLandingComponent)
  },
  {
    path: 'contactus',
    loadComponent: () => import('./contact-us/contact-us.component').then((m) => m.ContactUsComponent)
  },
  {
    path: 'hardware',
    loadComponent: () => import('./hardware/hardware.component').then((m) => m.HardwareComponent)
  },
  {
    path: 'support',
    redirectTo: 'contactus'
  },
  {
    path: '**',
    redirectTo: 'get-started'
  }
];
