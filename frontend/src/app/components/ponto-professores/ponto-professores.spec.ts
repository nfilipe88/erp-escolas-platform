import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PontoProfessores } from './ponto-professores';

describe('PontoProfessores', () => {
  let component: PontoProfessores;
  let fixture: ComponentFixture<PontoProfessores>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PontoProfessores]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PontoProfessores);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
