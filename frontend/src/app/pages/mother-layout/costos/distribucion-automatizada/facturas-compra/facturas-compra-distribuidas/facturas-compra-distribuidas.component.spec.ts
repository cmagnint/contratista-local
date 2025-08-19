import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FacturasCompraDistribuidasComponent } from './facturas-compra-distribuidas.component';

describe('FacturasCompraDistribuidasComponent', () => {
  let component: FacturasCompraDistribuidasComponent;
  let fixture: ComponentFixture<FacturasCompraDistribuidasComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FacturasCompraDistribuidasComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FacturasCompraDistribuidasComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
