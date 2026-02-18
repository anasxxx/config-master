import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddBankStep3Component } from './add-bank-step3.component';

describe('AddBankStep3Component', () => {
  let component: AddBankStep3Component;
  let fixture: ComponentFixture<AddBankStep3Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddBankStep3Component]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddBankStep3Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
