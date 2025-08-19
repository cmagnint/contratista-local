import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InformePagoComponent } from './informe-pago.component';

describe('InformePagoComponent', () => {
  let component: InformePagoComponent;
  let fixture: ComponentFixture<InformePagoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InformePagoComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InformePagoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
