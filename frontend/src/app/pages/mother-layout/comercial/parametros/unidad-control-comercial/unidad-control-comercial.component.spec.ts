import { ComponentFixture, TestBed } from '@angular/core/testing';

import { UnidadControlComercialComponent } from './unidad-control-comercial.component';

describe('UnidadControlComercialComponent', () => {
  let component: UnidadControlComercialComponent;
  let fixture: ComponentFixture<UnidadControlComercialComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [UnidadControlComercialComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(UnidadControlComercialComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
