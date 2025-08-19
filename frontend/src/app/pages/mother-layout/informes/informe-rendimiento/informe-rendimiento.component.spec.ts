import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InformeRendimientoComponent } from './informe-rendimiento.component';

describe('InformeRendimientoComponent', () => {
  let component: InformeRendimientoComponent;
  let fixture: ComponentFixture<InformeRendimientoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InformeRendimientoComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InformeRendimientoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
