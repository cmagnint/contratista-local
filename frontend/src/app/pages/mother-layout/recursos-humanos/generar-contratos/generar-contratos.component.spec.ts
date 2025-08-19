import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GenerarContratosComponent } from './generar-contratos.component';

describe('GenerarContratosComponent', () => {
  let component: GenerarContratosComponent;
  let fixture: ComponentFixture<GenerarContratosComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GenerarContratosComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GenerarContratosComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
