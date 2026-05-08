import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SupervisoresComponent } from './supervisores.component';

describe('SupervisoresComponent', () => {
  let component: SupervisoresComponent;
  let fixture: ComponentFixture<SupervisoresComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SupervisoresComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(SupervisoresComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
