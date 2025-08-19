import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InformeTransportistaComponent } from './informe-transportista.component';

describe('InformeTransportistaComponent', () => {
  let component: InformeTransportistaComponent;
  let fixture: ComponentFixture<InformeTransportistaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InformeTransportistaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InformeTransportistaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
