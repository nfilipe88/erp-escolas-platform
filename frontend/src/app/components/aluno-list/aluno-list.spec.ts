import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AlunoList } from './aluno-list';

describe('AlunoList', () => {
  let component: AlunoList;
  let fixture: ComponentFixture<AlunoList>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AlunoList]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AlunoList);
    component = fixture.componentInstance;
    await fixture.whenStable();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
