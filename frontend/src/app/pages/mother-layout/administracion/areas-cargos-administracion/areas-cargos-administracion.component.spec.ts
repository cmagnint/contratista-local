import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AreasCargosAdministracionComponent } from './areas-cargos-administracion.component';

describe('AreasCargosAdministracionComponent', () => {
  let component: AreasCargosAdministracionComponent;
  let fixture: ComponentFixture<AreasCargosAdministracionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AreasCargosAdministracionComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AreasCargosAdministracionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
