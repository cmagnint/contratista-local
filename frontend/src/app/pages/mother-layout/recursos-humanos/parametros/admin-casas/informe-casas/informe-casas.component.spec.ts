import { ComponentFixture, TestBed } from '@angular/core/testing';

import { InformeCasasComponent } from './informe-casas.component';

describe('InformeCasasComponent', () => {
  let component: InformeCasasComponent;
  let fixture: ComponentFixture<InformeCasasComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [InformeCasasComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(InformeCasasComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
