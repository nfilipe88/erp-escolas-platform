import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProfessorAulas } from './professor-aulas';

describe('ProfessorAulas', () => {
  let component: ProfessorAulas;
  let fixture: ComponentFixture<ProfessorAulas>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProfessorAulas]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProfessorAulas);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
