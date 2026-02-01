import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ConfiguracoesPainel } from './configuracoes-painel';

describe('ConfiguracoesPainel', () => {
  let component: ConfiguracoesPainel;
  let fixture: ComponentFixture<ConfiguracoesPainel>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ConfiguracoesPainel]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ConfiguracoesPainel);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
