import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UsuarioList } from './usuario-list';

describe('UsuarioList', () => {
  let component: UsuarioList;
  let fixture: ComponentFixture<UsuarioList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UsuarioList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UsuarioList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
