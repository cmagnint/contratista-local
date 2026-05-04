import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ElementosSeguridadComponent } from './elementos-seguridad.component';

describe('ElementosSeguridadComponent', () => {
  let component: ElementosSeguridadComponent;
  let fixture: ComponentFixture<ElementosSeguridadComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ElementosSeguridadComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ElementosSeguridadComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
