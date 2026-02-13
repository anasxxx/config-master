import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BackOfficeActivityComponent } from './back-office-activity.component';

describe('BackOfficeActivityComponent', () => {
  let component: BackOfficeActivityComponent;
  let fixture: ComponentFixture<BackOfficeActivityComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BackOfficeActivityComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BackOfficeActivityComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
