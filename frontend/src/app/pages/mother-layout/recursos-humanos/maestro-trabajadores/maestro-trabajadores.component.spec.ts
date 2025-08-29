import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MaestroTrabajadoresComponent } from './maestro-trabajadores.component';

describe('MaestroTrabajadoresComponent', () => {
  let component: MaestroTrabajadoresComponent;
  let fixture: ComponentFixture<MaestroTrabajadoresComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MaestroTrabajadoresComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MaestroTrabajadoresComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
