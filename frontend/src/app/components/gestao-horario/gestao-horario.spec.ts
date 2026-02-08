import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GestaoHorario } from './gestao-horario';

describe('GestaoHorario', () => {
  let component: GestaoHorario;
  let fixture: ComponentFixture<GestaoHorario>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GestaoHorario]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GestaoHorario);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
