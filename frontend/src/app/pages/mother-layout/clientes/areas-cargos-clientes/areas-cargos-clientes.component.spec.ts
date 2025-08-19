import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AreasCargosClientesComponent } from './areas-cargos-clientes.component';

describe('AreasCargosClientesComponent', () => {
  let component: AreasCargosClientesComponent;
  let fixture: ComponentFixture<AreasCargosClientesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AreasCargosClientesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AreasCargosClientesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
