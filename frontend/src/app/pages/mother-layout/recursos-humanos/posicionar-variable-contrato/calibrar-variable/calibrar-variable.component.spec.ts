import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CalibrarVariableComponent } from './calibrar-variable.component';

describe('CalibrarVariableComponent', () => {
  let component: CalibrarVariableComponent;
  let fixture: ComponentFixture<CalibrarVariableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CalibrarVariableComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CalibrarVariableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
