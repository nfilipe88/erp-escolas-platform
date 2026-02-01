import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EscolaList } from './escola-list';

describe('EscolaList', () => {
  let component: EscolaList;
  let fixture: ComponentFixture<EscolaList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EscolaList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EscolaList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
