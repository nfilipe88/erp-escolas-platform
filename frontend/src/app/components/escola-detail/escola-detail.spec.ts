import { ComponentFixture, TestBed } from '@angular/core/testing';

import { EscolaDetail } from './escola-detail';

describe('EscolaDetail', () => {
  let component: EscolaDetail;
  let fixture: ComponentFixture<EscolaDetail>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [EscolaDetail]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EscolaDetail);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
