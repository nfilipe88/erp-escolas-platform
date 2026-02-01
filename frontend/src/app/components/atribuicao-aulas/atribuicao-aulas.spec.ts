import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AtribuicaoAulas } from './atribuicao-aulas';

describe('AtribuicaoAulas', () => {
  let component: AtribuicaoAulas;
  let fixture: ComponentFixture<AtribuicaoAulas>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AtribuicaoAulas]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AtribuicaoAulas);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
