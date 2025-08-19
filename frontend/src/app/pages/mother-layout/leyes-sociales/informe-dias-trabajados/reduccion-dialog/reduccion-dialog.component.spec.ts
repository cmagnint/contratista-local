import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReduccionDialogComponent } from './reduccion-dialog.component';

describe('ReduccionDialogComponent', () => {
  let component: ReduccionDialogComponent;
  let fixture: ComponentFixture<ReduccionDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReduccionDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ReduccionDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
