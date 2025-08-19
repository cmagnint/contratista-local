import { ComponentFixture, TestBed } from '@angular/core/testing';

import { VehiculosTransporteComponent } from './vehiculos-transporte.component';

describe('VehiculosTransporteComponent', () => {
  let component: VehiculosTransporteComponent;
  let fixture: ComponentFixture<VehiculosTransporteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [VehiculosTransporteComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(VehiculosTransporteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
