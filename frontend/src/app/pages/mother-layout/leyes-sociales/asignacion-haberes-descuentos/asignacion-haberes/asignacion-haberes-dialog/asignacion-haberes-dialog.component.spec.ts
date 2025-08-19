import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AsignacionHaberesDialogComponent } from './asignacion-haberes-dialog.component';

describe('AsignacionHaberesDialogComponent', () => {
  let component: AsignacionHaberesDialogComponent;
  let fixture: ComponentFixture<AsignacionHaberesDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsignacionHaberesDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AsignacionHaberesDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
