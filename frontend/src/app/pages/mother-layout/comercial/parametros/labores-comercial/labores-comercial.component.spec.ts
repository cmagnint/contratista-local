import { ComponentFixture, TestBed } from '@angular/core/testing';

import { LaboresComercialComponent } from './labores-comercial.component';

describe('LaboresComercialComponent', () => {
  let component: LaboresComercialComponent;
  let fixture: ComponentFixture<LaboresComercialComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LaboresComercialComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(LaboresComercialComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
