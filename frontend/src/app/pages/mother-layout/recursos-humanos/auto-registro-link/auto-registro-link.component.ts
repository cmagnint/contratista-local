import { Component, Inject, OnInit, PLATFORM_ID, ViewChild, ElementRef, AfterViewInit, ChangeDetectorRef } from '@angular/core';
import { isPlatformBrowser, CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatIconModule } from '@angular/material/icon';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSelectModule } from '@angular/material/select';
import { ContratistaApiService } from '../../../../services/contratista-api.service';
import SignaturePad from 'signature_pad';

interface EnlaceData {
  holding: number;
  perfil: number;
  token: string;
  activo: boolean;
  fecha_expiracion: string;
  ruts_permitidos?: string[];
}

interface PersonalData {
  holding: number;
  nombres: string;
  apellidos: string;
  rut: string;
  correo: string;
  estado_civil: string;
  telefono: string;
  nacionalidad: string;
  sexo: string;
  fecha_nacimiento: string;
  direccion: string;
  estado: boolean;
  [key: string]: string | number | boolean;
}

@Component({
  selector: 'app-auto-registro-link',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatCardModule,
    MatSnackBarModule,
    MatIconModule,
    MatProgressSpinnerModule,
    MatSelectModule
  ],
  templateUrl: './auto-registro-link.component.html',
  styleUrls: ['./auto-registro-link.component.css']
})

export class AutoRegistroLinkComponent implements OnInit, AfterViewInit {
  @ViewChild('signaturePad') signaturePadElement!: ElementRef;
  signaturePad!: SignaturePad;
  
  registroForm: FormGroup;
  error: string = '';
  loading: boolean = false;
  token: string = '';
  enlaceId: string = '';
  enlaceValido: boolean = false;
  validacionEnProceso: boolean = true;
  currentStep: number = 1;
  datosEnlace: EnlaceData | null = null;
  public holding: string = '';

  // Propiedades para documentos y previsualizaciones
  carnetFrontal: File | null = null;
  carnetTrasero: File | null = null;
  carnetFrontalPreview: string | null = null;
  carnetTraseroPreview: string | null = null;
  signatureImage: string | null = null;
  isFirmado: boolean = false;

  public todasLasNacionalidades: string[] = [
    'AFGANA', 'ALBANESA', 'ALEMANA', 'ANDORRANA', 'ANGOLEÑA', 'ANTIGUANA', 'ÁRABE', 
    'ARGELINA', 'ARGENTINA', 'ARMENIA', 'AUSTRALIANA', 'AUSTRIACA', 'AZERBAIYANA', 
    'BAHAMEÑA', 'BANGLADESÍ', 'BARBADENSE', 'BAREINÍ', 'BELGA', 'BELICEÑA', 'BENINESA', 
    'BIELORRUSA', 'BIRMANA', 'BOLIVIANA', 'BOSNIA', 'BOTSWANA', 'BRASILEÑA', 'BRUNEANA', 
    'BÚLGARA', 'BURKINESA', 'BURUNDESA', 'BUTANESA', 'CABOVERDIANA', 'CAMBOYANA', 
    'CAMERUNESA', 'CANADIENSE', 'CHADIANA', 'CHILENA', 'CHINA', 'CHIPRIOTA', 'COLOMBIANA', 
    'COMORENSE', 'CONGOLEÑA', 'COSTARRICENSE', 'CROATA', 'CUBANA', 'DANESA', 'DOMINICANA',
    'ECUATORIANA', 'EGIPCIA', 'EMIRATÍ', 'ERITREA', 'ESLOVACA', 'ESLOVENA', 'ESPAÑOLA', 
    'ESTADOUNIDENSE', 'ESTONIA', 'ETÍOPE', 'FILIPINA', 'FINLANDESA', 'FRANCESA', 
    'GABONESA', 'GAMBIANA', 'GEORGIANA', 'GHANESA', 'GRANADINA', 'GRIEGA', 'GUATEMALTECA', 
    'GUINEANA', 'GUYANESA', 'HAITIANA', 'HONDUREÑA', 'HÚNGARA', 'INDIA', 'INDONESIA', 
    'IRANÍ', 'IRAQUÍ', 'IRLANDESA', 'ISLANDESA', 'ISRAELÍ', 'ITALIANA', 'JAMAICANA', 
    'JAPONESA', 'JORDANA', 'KAZAJA', 'KENIANA', 'KIRGUISA', 'KUWAITÍ', 'LAOSIANA', 
    'LESOTENSE', 'LETONA', 'LIBANESA', 'LIBERIANA', 'LIBIA', 'LIECHTENSTEINIANA', 
    'LITUANA', 'LUXEMBURGUESA', 'MACEDONIA', 'MALASIA', 'MALAVÍ', 'MALDIVA', 'MALIENSE', 
    'MALTESA', 'MARROQUÍ', 'MAURICIANA', 'MAURITANA', 'MEXICANA', 'MOLDAVA', 'MONEGASCA', 
    'MONGOLA', 'MONTENEGRINA', 'MOZAMBIQUEÑA', 'NAMIBIA', 'NEPALÍ', 'NICARAGÜENSE', 
    'NIGERINA', 'NIGERIANA', 'NORUEGA', 'NEOZELANDESA', 'OMÁNÍ', 'NEERLANDESA', 
    'PAKISTANÍ', 'PANAMEÑA', 'PAPÚ', 'PARAGUAYA', 'PERUANA', 'POLACA', 'PORTUGUESA', 
    'QATARÍ', 'RUANDESA', 'RUMANA', 'RUSA', 'SAMOANA', 'SALVADOREÑA', 'SANMARINENSE', 
    'SAUDÍ', 'SENEGALESA', 'SERBIA', 'SEYCHELLENSE', 'SIERRALEONESA', 'SINGAPURENSE', 
    'SIRIA', 'SOMALÍ', 'SUAZI', 'SUDAFRICANA', 'SUDANESA', 'SUECA', 'SUIZA', 'SURINAMESA', 
    'TAILANDESA', 'TAIWANESA', 'TANZANA', 'TAYIKA', 'TIMORENSE', 'TOGOLESA', 'TONGANA', 
    'TRINITENSE', 'TUNECINA', 'TURCA', 'TURKMÉNA', 'UCRANIANA', 'UGANDESA', 'URUGUAYA', 
    'UZBEKA', 'VANUATUENSE', 'VATICANA', 'VENEZOLANA', 'VIETNAMITA', 'YEMENÍ', 'YIBUTIANA', 
    'ZAMBIANA', 'ZIMBABUENSE'
  ];
  public nacionalidadesFiltradas: string[] = [];

  estadosCiviles = [
    { value: 'soltero', label: 'Soltero(a)' },
    { value: 'casado', label: 'Casado(a)' },
    { value: 'divorciado', label: 'Divorciado(a)' },
    { value: 'viudo', label: 'Viudo(a)' }
  ];

  sexos = [
    { value: 'M', label: 'Masculino' },
    { value: 'F', label: 'Femenino' }
  ];

  constructor(
    @Inject(PLATFORM_ID) private platformId: Object,
    private route: ActivatedRoute,
    private router: Router,
    private fb: FormBuilder,
    private api: ContratistaApiService,
    private snackBar: MatSnackBar,
    private cdr: ChangeDetectorRef
  ) {
    this.registroForm = this.fb.group({
      nombres: ['', [Validators.required, Validators.minLength(3)]],
      apellidos: ['', [Validators.required, Validators.minLength(3)]],
      rut: ['', [Validators.required, Validators.pattern(/^[0-9]{7,8}[0-9kK]$/)]],
      correo: ['', [Validators.required, Validators.email]],
      estadoCivil: ['', Validators.required],
      telefono: ['', [Validators.required, Validators.pattern(/^(\+?56)?(\s?)(9)(\s?)[9876543]\d{7}$/)]],
      nacionalidad: ['CHILENA', Validators.required],
      sexo: ['', Validators.required],
      fecha_nacimiento: ['', Validators.required],
      direccion: ['', Validators.required]
    });
    this.nacionalidadesFiltradas = [...this.todasLasNacionalidades];
  }

  ngOnInit(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.holding = localStorage.getItem('holding_id') || '';
      this.token = this.route.snapshot.paramMap.get('token') || '';
      this.enlaceId = this.route.snapshot.paramMap.get('id') || '';
      
      if (!this.token || !this.enlaceId) {
        this.validacionEnProceso = false;
        this.error = 'Enlace inválido';
        return;
      }
      
      this.nacionalidadesFiltradas = [...this.todasLasNacionalidades];
      this.validarEnlace();
  
      // Agregar log para verificar el estado inicial
      console.log('Estado inicial:', {
        token: this.token,
        enlaceId: this.enlaceId,
        formValid: this.registroForm?.valid,
        datosEnlace: this.datosEnlace
      });
    }
  }

  ngAfterViewInit() {
    if (this.currentStep === 2) {
      setTimeout(() => {
        this.initializeSignaturePad();
      }, 100);
    }
  }

  initializeSignaturePad() {
    if (this.signaturePadElement && this.signaturePadElement.nativeElement) {
      this.signaturePad = new SignaturePad(this.signaturePadElement.nativeElement, {
        backgroundColor: 'rgb(255, 255, 255)',
        penColor: 'rgb(0, 0, 0)'
      });
      
      // Actualizar estado cuando se termina de firmar
      this.signaturePad.addEventListener("endStroke", () => {
        this.isFirmado = !this.signaturePad.isEmpty();
        this.signatureImage = this.isFirmado ? this.signaturePad.toDataURL() : null;
        this.cdr.detectChanges();
      });
      
      this.resizeCanvas();
      window.addEventListener('resize', this.resizeCanvas.bind(this));
    }
  }

  resizeCanvas() {
    const canvas = this.signaturePadElement?.nativeElement;
    if (canvas) {
      const ratio = Math.max(window.devicePixelRatio || 1, 1);
      canvas.width = canvas.offsetWidth * ratio;
      canvas.height = canvas.offsetHeight * ratio;
      const context = canvas.getContext('2d');
      if (context) {
        context.scale(ratio, ratio);
      }
      if (this.signaturePad) {
        this.signaturePad.clear();
        this.isFirmado = false;
      }
    }
  }

  clearSignature() {
    if (this.signaturePad) {
      this.signaturePad.clear();
      this.signatureImage = null;
      this.isFirmado = false;
    }
  }

  async onFileChange(event: any, type: 'frontal' | 'trasero') {
    const file = event.target.files[0];
    if (file) {
      if (file.type.match(/image.*$/)) {
        if (type === 'frontal') {
          this.carnetFrontal = file;
          this.carnetFrontalPreview = await this.getFilePreview(file);
        } else {
          this.carnetTrasero = file;
          this.carnetTraseroPreview = await this.getFilePreview(file);
        }
        this.cdr.detectChanges();
        console.log(`Imagen ${type} cargada:`, {
          file: file,
          preview: type === 'frontal' ? this.carnetFrontalPreview : this.carnetTraseroPreview
        });
      } else {
        this.mostrarError('Por favor, seleccione un archivo de imagen válido.');
      }
    }
  }

  private getFilePreview(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = reject;
      reader.readAsDataURL(file);
    });
  }

  nextStep() {
    if (this.currentStep === 1 && this.registroForm.valid) {
      this.currentStep = 2;
      this.cdr.detectChanges();
      setTimeout(() => {
        this.initializeSignaturePad();
      }, 100);
    }
  }

  saveSignature() {
    if (this.signaturePad && !this.signaturePad.isEmpty()) {
      this.signatureImage = this.signaturePad.toDataURL();
      this.submitForm();
    } else {
      this.mostrarError('Por favor, dibuje su firma antes de continuar.');
    }
  }

  canSubmit(): boolean {
  console.log('Estado del formulario:', {
    formValid: this.registroForm?.valid,
    carnetFrontal: this.carnetFrontal instanceof File,
    carnetTrasero: this.carnetTrasero instanceof File,
    isFirmado: this.isFirmado,
    signatureImage: !!this.signatureImage,
    loading: !this.loading,
    holding: !!this.holding  // Cambiado para usar this.holding
  });

  return !!(
    this.registroForm?.valid && 
    this.carnetFrontal instanceof File && 
    this.carnetTrasero instanceof File && 
    this.isFirmado && 
    this.signatureImage &&
    !this.loading &&
    this.holding  // Cambiado para usar this.holding
  );
}

submitForm() {
  if (!this.canSubmit()) {
    this.mostrarError('Por favor, complete todos los campos requeridos y asegúrese de firmar.');
    return;
  }

  this.loading = true;
  const formData = new FormData();
  
  // Agregar datos del personal
  formData.append('holding', this.holding);
  formData.append('nombres', this.registroForm.get('nombres')?.value || '');
  formData.append('apellidos', this.registroForm.get('apellidos')?.value || '');
  formData.append('rut', this.registroForm.get('rut')?.value || '');
  formData.append('correo', this.registroForm.get('correo')?.value || '');
  formData.append('estado_civil', this.registroForm.get('estadoCivil')?.value || '');
  formData.append('telefono', this.registroForm.get('telefono')?.value || '');
  formData.append('nacionalidad', this.registroForm.get('nacionalidad')?.value || '');
  formData.append('sexo', this.registroForm.get('sexo')?.value || '');
  formData.append('fecha_nacimiento', this.registroForm.get('fecha_nacimiento')?.value || '');
  formData.append('direccion', this.registroForm.get('direccion')?.value || '');
  
  // Agregar imágenes
  if (this.carnetFrontal instanceof File) {
    formData.append('carnet_front_image', this.carnetFrontal);
  }
  if (this.carnetTrasero instanceof File) {
    formData.append('carnet_back_image', this.carnetTrasero);
  }
  
  // Agregar datos del enlace
  if (this.token) {
    formData.append('token', this.token);
  }
  if (this.enlaceId) {
    formData.append('enlace_id', this.enlaceId);
  }
  
  // Procesar la firma
  if (this.signatureImage) {
    // Convertir la firma a Blob antes de agregarla
    fetch(this.signatureImage)
      .then(res => res.blob())
      .then(blob => {
        formData.append('firma', blob, 'firma.png');
        
        // Realizar la petición HTTP después de agregar la firma
        this.realizarPeticion(formData);
      })
      .catch(error => {
        this.loading = false;
        this.mostrarError('Error al procesar la firma');
      });
  } else {
    this.realizarPeticion(formData);
  }
}

private realizarPeticion(formData: FormData) {
  // Verificar el contenido del FormData antes de enviarlo
  console.log('Contenido del FormData:');
  formData.forEach((value, key) => {
      if (value instanceof File) {
          console.log(key, value.name, value.type, value.size);
      } else {
          console.log(key, value);
      }
  });

  this.api.postFormData('personal-web/', formData).subscribe({
    next: (response: any) => {
      this.mostrarExito('Registro exitoso');
      this.currentStep = 3;
      this.loading = false;
    },
    error: (err) => {
      console.log('Error completo:', err);
      console.log('Error response:', err.error);
      const errorMessage = err.error?.detail || 
                          err.error?.error || 
                          err.error?.message || 
                          'Error al registrar usuario';
      this.mostrarError(errorMessage);
      this.loading = false;
    },
    complete: () => {
      this.loading = false;
    }
  });
}


  validarEnlace() {
    this.api.get(`validar-enlace/${this.token}/${this.enlaceId}/`).subscribe({
      next: (response: EnlaceData) => {
        this.datosEnlace = response;
        this.enlaceValido = true;
        this.validacionEnProceso = false;
      },
      error: (err) => {
        this.enlaceValido = false;
        this.validacionEnProceso = false;
        this.error = err.error?.error || 'El enlace ha expirado o no es válido';
      }
    });
  }

  private mostrarError(mensaje: string) {
    this.error = mensaje;
    this.snackBar.open(mensaje, 'Cerrar', {
      duration: 5000,
      panelClass: ['error-snackbar']
    });
  }

  private mostrarExito(mensaje: string) {
    this.snackBar.open(mensaje, 'Cerrar', {
      duration: 3000,
      panelClass: ['success-snackbar']
    });
  }
}