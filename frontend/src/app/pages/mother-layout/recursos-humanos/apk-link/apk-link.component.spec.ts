import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ApkLinkComponent } from './apk-link.component';

describe('ApkLinkComponent', () => {
  let component: ApkLinkComponent;
  let fixture: ComponentFixture<ApkLinkComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ApkLinkComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ApkLinkComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
