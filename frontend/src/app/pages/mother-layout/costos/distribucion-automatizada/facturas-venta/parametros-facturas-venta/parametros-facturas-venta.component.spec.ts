import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ParametrosFacturasVentaComponent } from './parametros-facturas-venta.component';

describe('ParametrosFacturasVentaComponent', () => {
  let component: ParametrosFacturasVentaComponent;
  let fixture: ComponentFixture<ParametrosFacturasVentaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ParametrosFacturasVentaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ParametrosFacturasVentaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
