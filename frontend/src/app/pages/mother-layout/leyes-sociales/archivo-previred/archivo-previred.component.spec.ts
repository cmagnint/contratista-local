import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ArchivoPreviredComponent } from './archivo-previred.component';

describe('ArchivoPreviredComponent', () => {
  let component: ArchivoPreviredComponent;
  let fixture: ComponentFixture<ArchivoPreviredComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ArchivoPreviredComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ArchivoPreviredComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
