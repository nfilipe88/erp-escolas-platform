import { ApplicationConfig, provideBrowserGlobalErrorListeners } from '@angular/core';
import { provideRouter } from '@angular/router';

import { routes } from './app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './core/interceptors/auth.interceptor';
import { provideAnimations } from '@angular/platform-browser/animations';

// 1. Importações obrigatórias do NgRx
import { provideStore } from '@ngrx/store';
import { provideEffects } from '@ngrx/effects';

// 2. Importações do Estado de Alunos (verifique se os caminhos e nomes de exportação batem certo com os seus ficheiros)
import { alunosReducer } from './store/alunos/alunos.reducer';
import { AlunosEffects } from './store/alunos/aluno.effects';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideRouter(routes),
    // provideHttpClient(withFetch())
    // Configura o HttpClient para usar o nosso interceptor
    provideHttpClient(withInterceptors([authInterceptor])),
    provideAnimations(),

    // 3. Fornecedores do NgRx registados globalmente
    provideStore({ alunos: alunosReducer }),
    provideEffects([AlunosEffects])
  ]
};

