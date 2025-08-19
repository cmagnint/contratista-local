import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PagosEgresosComponent } from './pagos-egresos.component';

describe('PagosEgresosComponent', () => {
  let component: PagosEgresosComponent;
  let fixture: ComponentFixture<PagosEgresosComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PagosEgresosComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PagosEgresosComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
