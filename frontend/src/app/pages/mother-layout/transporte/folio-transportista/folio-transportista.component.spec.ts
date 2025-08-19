import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FolioTransportistaComponent } from './folio-transportista.component';

describe('FolioTransportistaComponent', () => {
  let component: FolioTransportistaComponent;
  let fixture: ComponentFixture<FolioTransportistaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FolioTransportistaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FolioTransportistaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
