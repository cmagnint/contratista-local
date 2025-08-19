import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FacturasCompraAutomatizadaComponent } from './facturas-compra-automatizada.component';

describe('FacturasCompraAutomatizadaComponent', () => {
  let component: FacturasCompraAutomatizadaComponent;
  let fixture: ComponentFixture<FacturasCompraAutomatizadaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FacturasCompraAutomatizadaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FacturasCompraAutomatizadaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
