import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MotherLayoutComponent } from './mother-layout.component';

describe('MotherLayoutComponent', () => {
  let component: MotherLayoutComponent;
  let fixture: ComponentFixture<MotherLayoutComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MotherLayoutComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MotherLayoutComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
