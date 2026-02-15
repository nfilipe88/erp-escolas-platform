// frontend/cypress/support/commands.ts - COMANDOS CUSTOMIZADOS
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.session([email, password], () => {
    cy.visit('/login');
    cy.get('input[name="email"]').type(email);
    cy.get('input[name="password"]').type(password);
    cy.get('button[type="submit"]').click();
    cy.url().should('include', '/dashboard');
  });
});

Cypress.Commands.add('createAluno', (aluno: any) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/alunos/`,
    headers: {
      Authorization: `Bearer ${window.localStorage.getItem('token')}`
    },
    body: aluno
  });
});

declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>;
      createAluno(aluno: any): Chainable<void>;
    }
  }
}
