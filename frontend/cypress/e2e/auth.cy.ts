// frontend/cypress/e2e/auth.cy.ts - TESTES DE AUTENTICAÇÃO
describe('Authentication', () => {

  beforeEach(() => {
    cy.visit('/login');
  });

  it('should display login form', () => {
    cy.get('input[name="email"]').should('be.visible');
    cy.get('input[name="password"]').should('be.visible');
    cy.get('button[type="submit"]').should('be.visible');
  });

  it('should login successfully with valid credentials', () => {
    cy.get('input[name="email"]').type('admin@teste.com');
    cy.get('input[name="password"]').type('SenhaSegura123!');
    cy.get('button[type="submit"]').click();

    // Deve redirecionar para dashboard
    cy.url().should('include', '/dashboard');
    cy.get('.user-name').should('contain', 'Admin');
  });

  it('should show error with invalid credentials', () => {
    cy.get('input[name="email"]').type('admin@teste.com');
    cy.get('input[name="password"]').type('senhaerrada');
    cy.get('button[type="submit"]').click();

    // Deve mostrar mensagem de erro
    cy.get('.error-message').should('be.visible');
    cy.get('.error-message').should('contain', 'Credenciais inválidas');
  });

  it('should validate required fields', () => {
    cy.get('button[type="submit"]').click();

    cy.get('input[name="email"]').should('have.class', 'ng-invalid');
    cy.get('input[name="password"]').should('have.class', 'ng-invalid');
  });

  it('should logout successfully', () => {
    // Login primeiro
    cy.login('admin@teste.com', 'SenhaSegura123!');

    // Logout
    cy.get('.user-menu').click();
    cy.get('.logout-button').click();

    // Deve redirecionar para login
    cy.url().should('include', '/login');
  });
});
