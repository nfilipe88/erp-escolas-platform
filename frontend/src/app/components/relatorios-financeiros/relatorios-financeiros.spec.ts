import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RelatoriosFinanceiros } from './relatorios-financeiros';

describe('RelatoriosFinanceiros', () => {
  let component: RelatoriosFinanceiros;
  let fixture: ComponentFixture<RelatoriosFinanceiros>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RelatoriosFinanceiros]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RelatoriosFinanceiros);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
