import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProformasTransportistaComponent } from './proformas-transportista.component';

describe('ProformasTransportistaComponent', () => {
  let component: ProformasTransportistaComponent;
  let fixture: ComponentFixture<ProformasTransportistaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProformasTransportistaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProformasTransportistaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
