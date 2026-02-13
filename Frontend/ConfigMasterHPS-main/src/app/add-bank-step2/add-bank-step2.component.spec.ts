import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AddBankStep2Component } from './add-bank-step2.component';

describe('AddBankStep2Component', () => {
  let component: AddBankStep2Component;
  let fixture: ComponentFixture<AddBankStep2Component>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AddBankStep2Component]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AddBankStep2Component);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
