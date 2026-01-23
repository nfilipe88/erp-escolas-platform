import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TurmaChamada } from './turma-chamada';

describe('TurmaChamada', () => {
  let component: TurmaChamada;
  let fixture: ComponentFixture<TurmaChamada>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TurmaChamada]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TurmaChamada);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
