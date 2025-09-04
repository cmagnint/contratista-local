import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AfpComponent } from './afp.component';

describe('AfpComponent', () => {
  let component: AfpComponent;
  let fixture: ComponentFixture<AfpComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AfpComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AfpComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
