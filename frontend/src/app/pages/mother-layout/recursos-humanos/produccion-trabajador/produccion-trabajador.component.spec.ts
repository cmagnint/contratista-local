import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProduccionTrabajadorComponent } from './produccion-trabajador.component';

describe('ProduccionTrabajadorComponent', () => {
  let component: ProduccionTrabajadorComponent;
  let fixture: ComponentFixture<ProduccionTrabajadorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProduccionTrabajadorComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProduccionTrabajadorComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
