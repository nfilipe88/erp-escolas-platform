// frontend/cypress/e2e/alunos.cy.ts - TESTES DE ALUNOS
describe('Alunos Management', () => {

  beforeEach(() => {
    cy.login('admin@teste.com', 'SenhaSegura123!');
    cy.visit('/alunos');
  });

  it('should display list of alunos', () => {
    cy.get('.aluno-card').should('have.length.gt', 0);
  });

  it('should create new aluno', () => {
    cy.get('.btn-novo-aluno').click();

    // Preencher formulário
    cy.get('input[name="nome"]').type('Maria Teste');
    cy.get('input[name="bi"]').type('123456789BA003');
    cy.get('input[name="data_nascimento"]').type('2010-05-15');

    // Submeter
    cy.get('button[type="submit"]').click();

    // Verificar sucesso
    cy.get('.success-message').should('be.visible');
    cy.get('.aluno-card').should('contain', 'Maria Teste');
  });

  it('should search alunos', () => {
    cy.get('input[placeholder="Buscar aluno"]').type('João');

    // Aguardar debounce
    cy.wait(500);

    // Verificar resultados
    cy.get('.aluno-card').each(($card) => {
      cy.wrap($card).should('contain', 'João');
    });
  });

  it('should edit aluno', () => {
    // Clicar no primeiro aluno
    cy.get('.aluno-card').first().click();
    cy.get('.btn-editar').click();

    // Editar nome
    cy.get('input[name="nome"]').clear().type('Nome Atualizado');
    cy.get('button[type="submit"]').click();

    // Verificar atualização
    cy.get('.success-message').should('be.visible');
    cy.get('.aluno-card').first().should('contain', 'Nome Atualizado');
  });

  it('should delete aluno', () => {
    // Obter número inicial de alunos
    cy.get('.aluno-card').its('length').then((initialCount) => {
      // Clicar em deletar
      cy.get('.aluno-card').first().find('.btn-deletar').click();

      // Confirmar
      cy.get('.confirm-dialog').should('be.visible');
      cy.get('.btn-confirm').click();

      // Verificar que foi deletado
      cy.get('.success-message').should('be.visible');
      cy.get('.aluno-card').should('have.length', initialCount - 1);
    });
  });

  it('should paginate through alunos', () => {
    // Ir para página 2
    cy.get('.pagination .page-2').click();

    // URL deve atualizar
    cy.url().should('include', 'page=2');

    // Deve mostrar alunos diferentes
    cy.get('.aluno-card').should('have.length.gt', 0);
  });
});
