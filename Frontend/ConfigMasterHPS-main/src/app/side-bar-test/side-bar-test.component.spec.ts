import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SideBarTestComponent } from './side-bar-test.component';

describe('SideBarTestComponent', () => {
  let component: SideBarTestComponent;
  let fixture: ComponentFixture<SideBarTestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SideBarTestComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SideBarTestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
