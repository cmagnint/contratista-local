import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TraspasoTrabajadoresComponent } from './traspaso-trabajadores.component';

describe('TraspasoTrabajadoresComponent', () => {
  let component: TraspasoTrabajadoresComponent;
  let fixture: ComponentFixture<TraspasoTrabajadoresComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TraspasoTrabajadoresComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TraspasoTrabajadoresComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
