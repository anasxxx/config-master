import { TestBed } from '@angular/core/testing';

import { PatchServiceService } from './patch-service.service';

describe('PatchServiceService', () => {
  let service: PatchServiceService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(PatchServiceService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
