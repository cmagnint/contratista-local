import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdministrarClientesComponent } from './administrar-clientes.component';

describe('AdministrarClientesComponent', () => {
  let component: AdministrarClientesComponent;
  let fixture: ComponentFixture<AdministrarClientesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AdministrarClientesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AdministrarClientesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
