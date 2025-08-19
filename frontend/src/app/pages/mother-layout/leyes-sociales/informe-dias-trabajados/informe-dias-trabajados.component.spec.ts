import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InformeDiasTrabajadosComponent } from './informe-dias-trabajados.component';

describe('InformeDiasTrabajadosComponent', () => {
  let component: InformeDiasTrabajadosComponent;
  let fixture: ComponentFixture<InformeDiasTrabajadosComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InformeDiasTrabajadosComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InformeDiasTrabajadosComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
