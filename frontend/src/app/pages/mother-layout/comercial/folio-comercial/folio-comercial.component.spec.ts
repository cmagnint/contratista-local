import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FolioComercialComponent } from './folio-comercial.component';

describe('FolioComercialComponent', () => {
  let component: FolioComercialComponent;
  let fixture: ComponentFixture<FolioComercialComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FolioComercialComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FolioComercialComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
