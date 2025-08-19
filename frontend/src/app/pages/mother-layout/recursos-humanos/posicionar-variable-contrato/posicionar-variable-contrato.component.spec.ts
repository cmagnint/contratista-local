import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PosicionarVariableContratoComponent } from './posicionar-variable-contrato.component';

describe('PosicionarVariableContratoComponent', () => {
  let component: PosicionarVariableContratoComponent;
  let fixture: ComponentFixture<PosicionarVariableContratoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PosicionarVariableContratoComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PosicionarVariableContratoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
