import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EscolaForm } from './escola-form';

describe('EscolaForm', () => {
  let component: EscolaForm;
  let fixture: ComponentFixture<EscolaForm>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EscolaForm]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EscolaForm);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
