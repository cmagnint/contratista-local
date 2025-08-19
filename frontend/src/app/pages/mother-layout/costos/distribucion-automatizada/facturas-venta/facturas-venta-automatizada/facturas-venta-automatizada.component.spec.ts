import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FacturasVentaAutomatizadaComponent } from './facturas-venta-automatizada.component';

describe('FacturasVentaAutomatizadaComponent', () => {
  let component: FacturasVentaAutomatizadaComponent;
  let fixture: ComponentFixture<FacturasVentaAutomatizadaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FacturasVentaAutomatizadaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FacturasVentaAutomatizadaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
