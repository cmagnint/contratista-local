import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TransferenciasRealizadasComponent } from './transferencias-realizadas.component';

describe('TransferenciasRealizadasComponent', () => {
  let component: TransferenciasRealizadasComponent;
  let fixture: ComponentFixture<TransferenciasRealizadasComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TransferenciasRealizadasComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TransferenciasRealizadasComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
