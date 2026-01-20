import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TurmaForm } from './turma-form';

describe('TurmaForm', () => {
  let component: TurmaForm;
  let fixture: ComponentFixture<TurmaForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TurmaForm]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TurmaForm);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
