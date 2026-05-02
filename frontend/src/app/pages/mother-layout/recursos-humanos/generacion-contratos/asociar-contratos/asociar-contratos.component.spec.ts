import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AsociarContratosComponent } from './asociar-contratos.component';

describe('AsociarContratosComponent', () => {
  let component: AsociarContratosComponent;
  let fixture: ComponentFixture<AsociarContratosComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsociarContratosComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AsociarContratosComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
