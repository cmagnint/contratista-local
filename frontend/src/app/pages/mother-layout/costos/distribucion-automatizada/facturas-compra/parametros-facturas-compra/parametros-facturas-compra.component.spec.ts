import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ParametrosFacturasCompraComponent } from './parametros-facturas-compra.component';

describe('ParametrosFacturasCompraComponent', () => {
  let component: ParametrosFacturasCompraComponent;
  let fixture: ComponentFixture<ParametrosFacturasCompraComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ParametrosFacturasCompraComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ParametrosFacturasCompraComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
