import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GenerarTxtBancoComponent } from './generar-txt-banco.component';

describe('GenerarTxtBancoComponent', () => {
  let component: GenerarTxtBancoComponent;
  let fixture: ComponentFixture<GenerarTxtBancoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GenerarTxtBancoComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GenerarTxtBancoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
