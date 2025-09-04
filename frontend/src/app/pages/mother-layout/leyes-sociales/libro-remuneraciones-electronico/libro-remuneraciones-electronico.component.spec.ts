import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LibroRemuneracionesElectronicoComponent } from './libro-remuneraciones-electronico.component';

describe('LibroRemuneracionesElectronicoComponent', () => {
  let component: LibroRemuneracionesElectronicoComponent;
  let fixture: ComponentFixture<LibroRemuneracionesElectronicoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LibroRemuneracionesElectronicoComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LibroRemuneracionesElectronicoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
