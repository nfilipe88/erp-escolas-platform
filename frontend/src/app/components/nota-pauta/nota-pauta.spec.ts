import { ComponentFixture, TestBed } from '@angular/core/testing';

import { NotaPauta } from './nota-pauta';

describe('NotaPauta', () => {
  let component: NotaPauta;
  let fixture: ComponentFixture<NotaPauta>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [NotaPauta]
    })
    .compileComponents();

    fixture = TestBed.createComponent(NotaPauta);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
