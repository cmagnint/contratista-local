import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FacturasVentaDistribuidasComponent } from './facturas-venta-distribuidas.component';

describe('FacturasVentaDistribuidasComponent', () => {
  let component: FacturasVentaDistribuidasComponent;
  let fixture: ComponentFixture<FacturasVentaDistribuidasComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FacturasVentaDistribuidasComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FacturasVentaDistribuidasComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
