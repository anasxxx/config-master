import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddBankStep1Component } from './add-bank-step1.component';

describe('AddBankStep1Component', () => {
  let component: AddBankStep1Component;
  let fixture: ComponentFixture<AddBankStep1Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddBankStep1Component]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddBankStep1Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
