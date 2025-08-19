import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AsignacionDescuentosDialogComponent } from './asignacion-descuentos-dialog.component';

describe('AsignacionDescuentosDialogComponent', () => {
  let component: AsignacionDescuentosDialogComponent;
  let fixture: ComponentFixture<AsignacionDescuentosDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsignacionDescuentosDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AsignacionDescuentosDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
