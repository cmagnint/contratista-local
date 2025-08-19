import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ContactosClientesComponent } from './contactos-clientes.component';

describe('ContactosClientesComponent', () => {
  let component: ContactosClientesComponent;
  let fixture: ComponentFixture<ContactosClientesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ContactosClientesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ContactosClientesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
