import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TurmaList } from './turma-list';

describe('TurmaList', () => {
  let component: TurmaList;
  let fixture: ComponentFixture<TurmaList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TurmaList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TurmaList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
