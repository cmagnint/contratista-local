import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AsignacionHaberesComponent } from './asignacion-haberes.component';

describe('AsignacionHaberesComponent', () => {
  let component: AsignacionHaberesComponent;
  let fixture: ComponentFixture<AsignacionHaberesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AsignacionHaberesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AsignacionHaberesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
