import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AsignacionDescuentosComponent } from './asignacion-descuentos.component';

describe('AsignacionDescuentosComponent', () => {
  let component: AsignacionDescuentosComponent;
  let fixture: ComponentFixture<AsignacionDescuentosComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsignacionDescuentosComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AsignacionDescuentosComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
