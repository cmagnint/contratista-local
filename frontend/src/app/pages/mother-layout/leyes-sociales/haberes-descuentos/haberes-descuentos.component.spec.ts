import { ComponentFixture, TestBed } from '@angular/core/testing';

import { HaberesDescuentosComponent } from './haberes-descuentos.component';

describe('HaberesDescuentosComponent', () => {
  let component: HaberesDescuentosComponent;
  let fixture: ComponentFixture<HaberesDescuentosComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HaberesDescuentosComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(HaberesDescuentosComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
