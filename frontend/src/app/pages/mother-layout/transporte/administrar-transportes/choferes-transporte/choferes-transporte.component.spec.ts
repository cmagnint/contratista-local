import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ChoferesTransporteComponent } from './choferes-transporte.component';

describe('ChoferesTransporteComponent', () => {
  let component: ChoferesTransporteComponent;
  let fixture: ComponentFixture<ChoferesTransporteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ChoferesTransporteComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ChoferesTransporteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
