import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AlunoBoletim } from './aluno-boletim';

describe('AlunoBoletim', () => {
  let component: AlunoBoletim;
  let fixture: ComponentFixture<AlunoBoletim>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AlunoBoletim]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AlunoBoletim);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
