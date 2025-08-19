import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PagosTransportistaComponent } from './pagos-transportista.component';

describe('PagosTransportistaComponent', () => {
  let component: PagosTransportistaComponent;
  let fixture: ComponentFixture<PagosTransportistaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PagosTransportistaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PagosTransportistaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
