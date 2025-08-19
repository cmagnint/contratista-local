import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AutoRegistroLinkComponent } from './auto-registro-link.component';

describe('AutoRegistroLinkComponent', () => {
  let component: AutoRegistroLinkComponent;
  let fixture: ComponentFixture<AutoRegistroLinkComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AutoRegistroLinkComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AutoRegistroLinkComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
