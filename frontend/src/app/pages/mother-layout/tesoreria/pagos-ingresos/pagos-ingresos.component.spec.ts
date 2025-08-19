import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PagosIngresosComponent } from './pagos-ingresos.component';

describe('PagosIngresosComponent', () => {
  let component: PagosIngresosComponent;
  let fixture: ComponentFixture<PagosIngresosComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PagosIngresosComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PagosIngresosComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
