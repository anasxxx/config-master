import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BanksDetailsComponent } from './banks-details.component';

describe('BanksDetailsComponent', () => {
  let component: BanksDetailsComponent;
  let fixture: ComponentFixture<BanksDetailsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BanksDetailsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(BanksDetailsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
