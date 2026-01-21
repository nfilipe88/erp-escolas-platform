import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AlunoFinanceiro } from './aluno-financeiro';

describe('AlunoFinanceiro', () => {
  let component: AlunoFinanceiro;
  let fixture: ComponentFixture<AlunoFinanceiro>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AlunoFinanceiro]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AlunoFinanceiro);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
