import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TraceBatchModalComponent } from './trace-batch-modal.component';

describe('TraceBatchModalComponent', () => {
  let component: TraceBatchModalComponent;
  let fixture: ComponentFixture<TraceBatchModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TraceBatchModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TraceBatchModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
