import { TestBed } from '@angular/core/testing';
import { CanActivateFn } from '@angular/router';

import { contratistaAuthGuard } from './contratista-auth.guard';

describe('contratistaAuthGuard', () => {
  const executeGuard: CanActivateFn = (...guardParameters) => 
      TestBed.runInInjectionContext(() => contratistaAuthGuard(...guardParameters));

  beforeEach(() => {
    TestBed.configureTestingModule({});
  });

  it('should be created', () => {
    expect(executeGuard).toBeTruthy();
  });
});
