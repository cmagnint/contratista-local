import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ReprocesarPagoComponent } from './reprocesar-pago.component';

describe('ReprocesarPagoComponent', () => {
  let component: ReprocesarPagoComponent;
  let fixture: ComponentFixture<ReprocesarPagoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ReprocesarPagoComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ReprocesarPagoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
