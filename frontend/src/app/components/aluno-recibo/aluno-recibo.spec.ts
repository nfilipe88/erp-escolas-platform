import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AlunoRecibo } from './aluno-recibo';

describe('AlunoRecibo', () => {
  let component: AlunoRecibo;
  let fixture: ComponentFixture<AlunoRecibo>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AlunoRecibo]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AlunoRecibo);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
