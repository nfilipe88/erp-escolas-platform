import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { HttpFeature, HttpFeatureKind, provideHttpClient, withFetch, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './interceptors/auth.interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    // provideHttpClient(withFetch())
    // Configura o HttpClient para usar o nosso interceptor
    provideHttpClient(withInterceptors([authInterceptor]))
  ]
};
function provovideHttpClient(arg0: HttpFeature<HttpFeatureKind.Fetch>): import("@angular/core").Provider | import("@angular/core").EnvironmentProviders {
  throw new Error('Function not implemented.');
}

