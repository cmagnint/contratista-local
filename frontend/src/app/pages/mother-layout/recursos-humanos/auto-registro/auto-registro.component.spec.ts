import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AutoRegistroComponent } from './auto-registro.component';

describe('AutoRegistroComponent', () => {
  let component: AutoRegistroComponent;
  let fixture: ComponentFixture<AutoRegistroComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AutoRegistroComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AutoRegistroComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
