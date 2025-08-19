import { TestBed } from '@angular/core/testing';

import { ContratistaApiService } from './contratista-api.service';

describe('ContratistaApiService', () => {
  let service: ContratistaApiService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(ContratistaApiService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
