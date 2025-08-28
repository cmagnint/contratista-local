--
-- PostgreSQL database dump
--

-- Dumped from database version 16.9
-- Dumped by pg_dump version 16.9

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: holding; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

SET SESSION AUTHORIZATION DEFAULT;

ALTER TABLE public.holding DISABLE TRIGGER ALL;

INSERT INTO public.holding VALUES (1, 'TESTING', true);
INSERT INTO public.holding VALUES (2, 'TORRES Y CIA', true);


ALTER TABLE public.holding ENABLE TRIGGER ALL;

--
-- Data for Name: afp; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.afp DISABLE TRIGGER ALL;

INSERT INTO public.afp VALUES (1, NULL, 'AFP_1', 10.00, 1);


ALTER TABLE public.afp ENABLE TRIGGER ALL;

--
-- Data for Name: areas_administracion; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.areas_administracion DISABLE TRIGGER ALL;

INSERT INTO public.areas_administracion VALUES (1, 'ADMINISTRACION', 2);
INSERT INTO public.areas_administracion VALUES (3, 'OPERACIONES', 2);
INSERT INTO public.areas_administracion VALUES (4, 'AREA 1', 1);
INSERT INTO public.areas_administracion VALUES (5, 'AREA 2', 1);


ALTER TABLE public.areas_administracion ENABLE TRIGGER ALL;

--
-- Data for Name: banco; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.banco DISABLE TRIGGER ALL;

INSERT INTO public.banco VALUES (1, '001', 'BANCO DE CHILE');
INSERT INTO public.banco VALUES (2, '009', 'BANCO INTERNACIONAL');
INSERT INTO public.banco VALUES (3, '012', 'BANCO DEL ESTADO DE CHILE');
INSERT INTO public.banco VALUES (4, '014', 'SCOTIABANK CHILE');
INSERT INTO public.banco VALUES (5, '016', 'BANCO DE CREDITO E INVERSIONES');
INSERT INTO public.banco VALUES (6, '028', 'BANCO BICE');
INSERT INTO public.banco VALUES (7, '031', 'HSBC BANK (CHILE)');
INSERT INTO public.banco VALUES (8, '037', 'BANCO SANTANDER-CHILE');
INSERT INTO public.banco VALUES (9, '039', 'BANCO ITAÚ CHILE');
INSERT INTO public.banco VALUES (10, '041', 'JP MORGAN CHASE BANK, N. A.');
INSERT INTO public.banco VALUES (11, '049', 'BANCO SECURITY');
INSERT INTO public.banco VALUES (12, '051', 'BANCO FALABELLA');
INSERT INTO public.banco VALUES (13, '053', 'BANCO RIPLEY');
INSERT INTO public.banco VALUES (14, '055', 'BANCO CONSORCIO');
INSERT INTO public.banco VALUES (15, '059', 'BANCO BTG PACTUAL CHILE');
INSERT INTO public.banco VALUES (16, '060', 'CHINA CONSTRUCTION BANK, AGENCIA EN CHILE');
INSERT INTO public.banco VALUES (17, '061', 'BANK OF CHINA, AGENCIA EN CHILE');


ALTER TABLE public.banco ENABLE TRIGGER ALL;

--
-- Data for Name: clientes; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.clientes DISABLE TRIGGER ALL;



ALTER TABLE public.clientes ENABLE TRIGGER ALL;

--
-- Data for Name: campos_clientes; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.campos_clientes DISABLE TRIGGER ALL;



ALTER TABLE public.campos_clientes ENABLE TRIGGER ALL;

--
-- Data for Name: cargos_admnistracion; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.cargos_admnistracion DISABLE TRIGGER ALL;

INSERT INTO public.cargos_admnistracion VALUES (1, 'CARGO 1', 5, 1);
INSERT INTO public.cargos_admnistracion VALUES (2, 'GRTE ADMINISTRACION', 1, 2);
INSERT INTO public.cargos_admnistracion VALUES (3, 'CONTABILIDAD', 1, 2);
INSERT INTO public.cargos_admnistracion VALUES (4, 'RRHH', 1, 2);
INSERT INTO public.cargos_admnistracion VALUES (5, 'GRTE OPERACIONES', 3, 2);
INSERT INTO public.cargos_admnistracion VALUES (6, 'SUPERVISOR', 3, 2);
INSERT INTO public.cargos_admnistracion VALUES (7, 'ANOTADOR', 3, 2);


ALTER TABLE public.cargos_admnistracion ENABLE TRIGGER ALL;

--
-- Data for Name: casas; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.casas DISABLE TRIGGER ALL;



ALTER TABLE public.casas ENABLE TRIGGER ALL;

--
-- Data for Name: ccaf; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.ccaf DISABLE TRIGGER ALL;



ALTER TABLE public.ccaf ENABLE TRIGGER ALL;

--
-- Data for Name: folio_comercial; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.folio_comercial DISABLE TRIGGER ALL;



ALTER TABLE public.folio_comercial ENABLE TRIGGER ALL;

--
-- Data for Name: tramos_transportista; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.tramos_transportista DISABLE TRIGGER ALL;



ALTER TABLE public.tramos_transportista ENABLE TRIGGER ALL;

--
-- Data for Name: folios_transportes; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.folios_transportes DISABLE TRIGGER ALL;



ALTER TABLE public.folios_transportes ENABLE TRIGGER ALL;

--
-- Data for Name: empresas_transporte; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.empresas_transporte DISABLE TRIGGER ALL;



ALTER TABLE public.empresas_transporte ENABLE TRIGGER ALL;

--
-- Data for Name: ips_regimenes; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.ips_regimenes DISABLE TRIGGER ALL;



ALTER TABLE public.ips_regimenes ENABLE TRIGGER ALL;

--
-- Data for Name: mutualidades; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.mutualidades DISABLE TRIGGER ALL;



ALTER TABLE public.mutualidades ENABLE TRIGGER ALL;

--
-- Data for Name: perfiles; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.perfiles DISABLE TRIGGER ALL;

INSERT INTO public.perfiles VALUES (3, 'ADMINISTRADOR PRINCIPAL', 'AMBOS', true, 1);
INSERT INTO public.perfiles VALUES (4, 'ADMINISTRADOR PRINCIPAL', 'AMBOS', true, 2);
INSERT INTO public.perfiles VALUES (5, 'ADMINISTRADOR', 'WEB', true, 2);
INSERT INTO public.perfiles VALUES (6, 'ADMINISTRATIVO', 'WEB', true, 2);
INSERT INTO public.perfiles VALUES (7, 'DIGITADOR RRHH', 'WEB', true, 2);


ALTER TABLE public.perfiles ENABLE TRIGGER ALL;

--
-- Data for Name: salud; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.salud DISABLE TRIGGER ALL;

INSERT INTO public.salud VALUES (1, NULL, 'SALUD_1', 7.00, 1);


ALTER TABLE public.salud ENABLE TRIGGER ALL;

--
-- Data for Name: sociedad; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.sociedad DISABLE TRIGGER ALL;

INSERT INTO public.sociedad VALUES (2, '123456789', 'TESTING SOCIETY', 'TESTER', '182870048', 'RETIRO', 'RETIRO', 'EL LUCERO', true, NULL, 1, NULL);
INSERT INTO public.sociedad VALUES (1, '773819610', 'PRESTACION DE SERVICIOS MILLACHE LTDA', 'JUAN MIGUEL TORRES LILLO', '115664905', 'PARRAL', 'PARRAL', 'DIECIOCHO 640 PISO 3 OFICINA 9', true, NULL, 2, NULL);


ALTER TABLE public.sociedad ENABLE TRIGGER ALL;

--
-- Data for Name: vehiculos_transporte; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.vehiculos_transporte DISABLE TRIGGER ALL;



ALTER TABLE public.vehiculos_transporte ENABLE TRIGGER ALL;

--
-- Data for Name: personal; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.personal DISABLE TRIGGER ALL;

INSERT INTO public.personal VALUES (6, 'CAMILO MAGNIN', NULL, '123456789', NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'carnets/dni.jpg', 'carnets/dni.jpg', '', NULL, NULL, NULL, false, true, 0, false, 0, false, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 1, NULL, NULL, NULL, NULL, NULL);
INSERT INTO public.personal VALUES (7, 'JUAN MIGUEL TORRES LILLO', NULL, '115664905', NULL, NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'carnets/dni.jpg', 'carnets/dni.jpg', '', NULL, NULL, NULL, false, true, 0, false, 0, false, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 2, NULL, NULL, NULL, NULL, NULL);


ALTER TABLE public.personal ENABLE TRIGGER ALL;

--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.usuarios DISABLE TRIGGER ALL;

INSERT INTO public.usuarios VALUES ('pbkdf2_sha256$1000000$XCAx5oDtRbXoQccxG8HHe0$G+MQAD6hZW5+cDvHY4+KsoDjbVj4Rohty5PD5J+tkYE=', NULL, true, 1, '182870048', 'camilo.magnin@gmail.com', NULL, NULL, true, true, false, NULL, NULL, NULL);
INSERT INTO public.usuarios VALUES ('pbkdf2_sha256$1000000$tleUThDhQI9Lk3tNiwdTdl$1wapaSaByvHdszSrBFsPsUFHN4fFzoOcvOLebZyP8oE=', NULL, true, 2, '62548053', 'devt.terrasoft@gmail.com', NULL, NULL, true, true, false, NULL, NULL, NULL);
INSERT INTO public.usuarios VALUES ('pbkdf2_sha256$1000000$VP2c46GALCH44hPK8J9rEK$mCsZEsR6Aa6f7jdmN7m50HhLty9YXgPA0I+4LIZpn7s=', NULL, false, 6, '123456789', 'camilo.d.magnin@gmail.com', NULL, NULL, true, false, true, 1, 3, 6);
INSERT INTO public.usuarios VALUES ('pbkdf2_sha256$1000000$XdwFrs9kGPnY7T1KwYZONJ$gRGPs9kimFwDk+JLFN7smCMNxFYsGv7edzmhAyd1tEY=', NULL, false, 7, '115664905', 'jmtorres@terramas.cl', NULL, NULL, true, false, true, 2, 4, 7);


ALTER TABLE public.usuarios ENABLE TRIGGER ALL;

--
-- Data for Name: apk_links; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.apk_links DISABLE TRIGGER ALL;



ALTER TABLE public.apk_links ENABLE TRIGGER ALL;

--
-- Data for Name: areas; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.areas DISABLE TRIGGER ALL;



ALTER TABLE public.areas ENABLE TRIGGER ALL;

--
-- Data for Name: areas_clientes; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.areas_clientes DISABLE TRIGGER ALL;



ALTER TABLE public.areas_clientes ENABLE TRIGGER ALL;

--
-- Data for Name: asociacion_codigo_qr; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.asociacion_codigo_qr DISABLE TRIGGER ALL;



ALTER TABLE public.asociacion_codigo_qr ENABLE TRIGGER ALL;

--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.auth_group DISABLE TRIGGER ALL;



ALTER TABLE public.auth_group ENABLE TRIGGER ALL;

--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.django_content_type DISABLE TRIGGER ALL;

INSERT INTO public.django_content_type VALUES (1, 'auth', 'permission');
INSERT INTO public.django_content_type VALUES (2, 'auth', 'group');
INSERT INTO public.django_content_type VALUES (3, 'contenttypes', 'contenttype');
INSERT INTO public.django_content_type VALUES (4, 'contratista_test_app', 'areas');
INSERT INTO public.django_content_type VALUES (5, 'contratista_test_app', 'areasadministracion');
INSERT INTO public.django_content_type VALUES (6, 'contratista_test_app', 'areascliente');
INSERT INTO public.django_content_type VALUES (7, 'contratista_test_app', 'banco');
INSERT INTO public.django_content_type VALUES (8, 'contratista_test_app', 'causalfiniquito');
INSERT INTO public.django_content_type VALUES (9, 'contratista_test_app', 'ccaf');
INSERT INTO public.django_content_type VALUES (10, 'contratista_test_app', 'clientes');
INSERT INTO public.django_content_type VALUES (11, 'contratista_test_app', 'developer');
INSERT INTO public.django_content_type VALUES (12, 'contratista_test_app', 'empresastransporte');
INSERT INTO public.django_content_type VALUES (13, 'contratista_test_app', 'holding');
INSERT INTO public.django_content_type VALUES (14, 'contratista_test_app', 'ipsregimen');
INSERT INTO public.django_content_type VALUES (15, 'contratista_test_app', 'mutualidad');
INSERT INTO public.django_content_type VALUES (16, 'contratista_test_app', 'region');
INSERT INTO public.django_content_type VALUES (17, 'contratista_test_app', 'tipodiscapacidad');
INSERT INTO public.django_content_type VALUES (18, 'contratista_test_app', 'tipoimpuestorenta');
INSERT INTO public.django_content_type VALUES (19, 'contratista_test_app', 'tipojornada');
INSERT INTO public.django_content_type VALUES (20, 'contratista_test_app', 'usuarios');
INSERT INTO public.django_content_type VALUES (21, 'contratista_test_app', 'cargoscliente');
INSERT INTO public.django_content_type VALUES (22, 'contratista_test_app', 'camposclientes');
INSERT INTO public.django_content_type VALUES (23, 'contratista_test_app', 'cuentaorigen');
INSERT INTO public.django_content_type VALUES (24, 'contratista_test_app', 'foliocomercial');
INSERT INTO public.django_content_type VALUES (25, 'contratista_test_app', 'foliotransportista');
INSERT INTO public.django_content_type VALUES (26, 'contratista_test_app', 'historialcambiopago');
INSERT INTO public.django_content_type VALUES (27, 'contratista_test_app', 'historialcambiofolio');
INSERT INTO public.django_content_type VALUES (28, 'contratista_test_app', 'haberes');
INSERT INTO public.django_content_type VALUES (29, 'contratista_test_app', 'descuentos');
INSERT INTO public.django_content_type VALUES (30, 'contratista_test_app', 'cuenta');
INSERT INTO public.django_content_type VALUES (31, 'contratista_test_app', 'contratovariables');
INSERT INTO public.django_content_type VALUES (32, 'contratista_test_app', 'contactosclientes');
INSERT INTO public.django_content_type VALUES (33, 'contratista_test_app', 'configuracionsiiautomaticacompra');
INSERT INTO public.django_content_type VALUES (34, 'contratista_test_app', 'casastrabajadores');
INSERT INTO public.django_content_type VALUES (35, 'contratista_test_app', 'cartolamovimiento');
INSERT INTO public.django_content_type VALUES (36, 'contratista_test_app', 'cargosadministracion');
INSERT INTO public.django_content_type VALUES (37, 'contratista_test_app', 'cargos');
INSERT INTO public.django_content_type VALUES (38, 'contratista_test_app', 'apklink');
INSERT INTO public.django_content_type VALUES (39, 'contratista_test_app', 'afptrabajadores');
INSERT INTO public.django_content_type VALUES (40, 'contratista_test_app', 'horarios');
INSERT INTO public.django_content_type VALUES (41, 'contratista_test_app', 'labores');
INSERT INTO public.django_content_type VALUES (42, 'contratista_test_app', 'facturaventasiidistribuida');
INSERT INTO public.django_content_type VALUES (43, 'contratista_test_app', 'facturacomprasiidistribuida');
INSERT INTO public.django_content_type VALUES (44, 'contratista_test_app', 'mescerrado');
INSERT INTO public.django_content_type VALUES (45, 'contratista_test_app', 'modulosmovil');
INSERT INTO public.django_content_type VALUES (46, 'contratista_test_app', 'modulosweb');
INSERT INTO public.django_content_type VALUES (47, 'contratista_test_app', 'pagotransportista');
INSERT INTO public.django_content_type VALUES (48, 'contratista_test_app', 'detallepagotransportista');
INSERT INTO public.django_content_type VALUES (49, 'contratista_test_app', 'perfiles');
INSERT INTO public.django_content_type VALUES (50, 'contratista_test_app', 'enlaceautoregistro');
INSERT INTO public.django_content_type VALUES (51, 'contratista_test_app', 'personaltrabajadores');
INSERT INTO public.django_content_type VALUES (52, 'contratista_test_app', 'licenciamedica');
INSERT INTO public.django_content_type VALUES (53, 'contratista_test_app', 'jefesdecuadrilla');
INSERT INTO public.django_content_type VALUES (54, 'contratista_test_app', 'horaextraordinaria');
INSERT INTO public.django_content_type VALUES (55, 'contratista_test_app', 'diastrabajadosaprobados');
INSERT INTO public.django_content_type VALUES (56, 'contratista_test_app', 'cuadrillas');
INSERT INTO public.django_content_type VALUES (57, 'contratista_test_app', 'codigoqr');
INSERT INTO public.django_content_type VALUES (58, 'contratista_test_app', 'producciontrabajador');
INSERT INTO public.django_content_type VALUES (59, 'contratista_test_app', 'comuna');
INSERT INTO public.django_content_type VALUES (60, 'contratista_test_app', 'registroegreso');
INSERT INTO public.django_content_type VALUES (61, 'contratista_test_app', 'registroingreso');
INSERT INTO public.django_content_type VALUES (62, 'contratista_test_app', 'registropagoefectivo');
INSERT INTO public.django_content_type VALUES (63, 'contratista_test_app', 'registropagotransferencia');
INSERT INTO public.django_content_type VALUES (64, 'contratista_test_app', 'saludtrabajadores');
INSERT INTO public.django_content_type VALUES (65, 'contratista_test_app', 'sociedad');
INSERT INTO public.django_content_type VALUES (66, 'contratista_test_app', 'proformatransportista');
INSERT INTO public.django_content_type VALUES (67, 'contratista_test_app', 'submodulosmovil');
INSERT INTO public.django_content_type VALUES (68, 'contratista_test_app', 'submodulosweb');
INSERT INTO public.django_content_type VALUES (69, 'contratista_test_app', 'supervisores');
INSERT INTO public.django_content_type VALUES (70, 'contratista_test_app', 'contratotrabajador');
INSERT INTO public.django_content_type VALUES (71, 'contratista_test_app', 'trabajadordescuento');
INSERT INTO public.django_content_type VALUES (72, 'contratista_test_app', 'trabajadorhaber');
INSERT INTO public.django_content_type VALUES (73, 'contratista_test_app', 'tramos');
INSERT INTO public.django_content_type VALUES (74, 'contratista_test_app', 'unidadcontrol');
INSERT INTO public.django_content_type VALUES (75, 'contratista_test_app', 'vacaciones');
INSERT INTO public.django_content_type VALUES (76, 'contratista_test_app', 'vehiculostransporte');
INSERT INTO public.django_content_type VALUES (77, 'contratista_test_app', 'choferestransporte');
INSERT INTO public.django_content_type VALUES (78, 'contratista_test_app', 'calibrationsettings');
INSERT INTO public.django_content_type VALUES (79, 'contratista_test_app', 'facturaventasiipordistribuir');
INSERT INTO public.django_content_type VALUES (80, 'contratista_test_app', 'facturacomprasiipordistribuir');
INSERT INTO public.django_content_type VALUES (81, 'contratista_test_app', 'configuracionsiiautomaticaventa');
INSERT INTO public.django_content_type VALUES (82, 'admin', 'logentry');
INSERT INTO public.django_content_type VALUES (83, 'sessions', 'session');
INSERT INTO public.django_content_type VALUES (84, 'oauth2_provider', 'application');
INSERT INTO public.django_content_type VALUES (85, 'oauth2_provider', 'accesstoken');
INSERT INTO public.django_content_type VALUES (86, 'oauth2_provider', 'grant');
INSERT INTO public.django_content_type VALUES (87, 'oauth2_provider', 'refreshtoken');
INSERT INTO public.django_content_type VALUES (88, 'oauth2_provider', 'idtoken');
INSERT INTO public.django_content_type VALUES (89, 'django_celery_beat', 'crontabschedule');
INSERT INTO public.django_content_type VALUES (90, 'django_celery_beat', 'intervalschedule');
INSERT INTO public.django_content_type VALUES (91, 'django_celery_beat', 'periodictask');
INSERT INTO public.django_content_type VALUES (92, 'django_celery_beat', 'periodictasks');
INSERT INTO public.django_content_type VALUES (93, 'django_celery_beat', 'solarschedule');
INSERT INTO public.django_content_type VALUES (94, 'django_celery_beat', 'clockedschedule');


ALTER TABLE public.django_content_type ENABLE TRIGGER ALL;

--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.auth_permission DISABLE TRIGGER ALL;

INSERT INTO public.auth_permission VALUES (1, 'Can add permission', 1, 'add_permission');
INSERT INTO public.auth_permission VALUES (2, 'Can change permission', 1, 'change_permission');
INSERT INTO public.auth_permission VALUES (3, 'Can delete permission', 1, 'delete_permission');
INSERT INTO public.auth_permission VALUES (4, 'Can view permission', 1, 'view_permission');
INSERT INTO public.auth_permission VALUES (5, 'Can add group', 2, 'add_group');
INSERT INTO public.auth_permission VALUES (6, 'Can change group', 2, 'change_group');
INSERT INTO public.auth_permission VALUES (7, 'Can delete group', 2, 'delete_group');
INSERT INTO public.auth_permission VALUES (8, 'Can view group', 2, 'view_group');
INSERT INTO public.auth_permission VALUES (9, 'Can add content type', 3, 'add_contenttype');
INSERT INTO public.auth_permission VALUES (10, 'Can change content type', 3, 'change_contenttype');
INSERT INTO public.auth_permission VALUES (11, 'Can delete content type', 3, 'delete_contenttype');
INSERT INTO public.auth_permission VALUES (12, 'Can view content type', 3, 'view_contenttype');
INSERT INTO public.auth_permission VALUES (13, 'Can add areas', 4, 'add_areas');
INSERT INTO public.auth_permission VALUES (14, 'Can change areas', 4, 'change_areas');
INSERT INTO public.auth_permission VALUES (15, 'Can delete areas', 4, 'delete_areas');
INSERT INTO public.auth_permission VALUES (16, 'Can view areas', 4, 'view_areas');
INSERT INTO public.auth_permission VALUES (17, 'Can add areas administracion', 5, 'add_areasadministracion');
INSERT INTO public.auth_permission VALUES (18, 'Can change areas administracion', 5, 'change_areasadministracion');
INSERT INTO public.auth_permission VALUES (19, 'Can delete areas administracion', 5, 'delete_areasadministracion');
INSERT INTO public.auth_permission VALUES (20, 'Can view areas administracion', 5, 'view_areasadministracion');
INSERT INTO public.auth_permission VALUES (21, 'Can add areas cliente', 6, 'add_areascliente');
INSERT INTO public.auth_permission VALUES (22, 'Can change areas cliente', 6, 'change_areascliente');
INSERT INTO public.auth_permission VALUES (23, 'Can delete areas cliente', 6, 'delete_areascliente');
INSERT INTO public.auth_permission VALUES (24, 'Can view areas cliente', 6, 'view_areascliente');
INSERT INTO public.auth_permission VALUES (25, 'Can add banco', 7, 'add_banco');
INSERT INTO public.auth_permission VALUES (26, 'Can change banco', 7, 'change_banco');
INSERT INTO public.auth_permission VALUES (27, 'Can delete banco', 7, 'delete_banco');
INSERT INTO public.auth_permission VALUES (28, 'Can view banco', 7, 'view_banco');
INSERT INTO public.auth_permission VALUES (29, 'Can add causal finiquito', 8, 'add_causalfiniquito');
INSERT INTO public.auth_permission VALUES (30, 'Can change causal finiquito', 8, 'change_causalfiniquito');
INSERT INTO public.auth_permission VALUES (31, 'Can delete causal finiquito', 8, 'delete_causalfiniquito');
INSERT INTO public.auth_permission VALUES (32, 'Can view causal finiquito', 8, 'view_causalfiniquito');
INSERT INTO public.auth_permission VALUES (33, 'Can add ccaf', 9, 'add_ccaf');
INSERT INTO public.auth_permission VALUES (34, 'Can change ccaf', 9, 'change_ccaf');
INSERT INTO public.auth_permission VALUES (35, 'Can delete ccaf', 9, 'delete_ccaf');
INSERT INTO public.auth_permission VALUES (36, 'Can view ccaf', 9, 'view_ccaf');
INSERT INTO public.auth_permission VALUES (37, 'Can add clientes', 10, 'add_clientes');
INSERT INTO public.auth_permission VALUES (38, 'Can change clientes', 10, 'change_clientes');
INSERT INTO public.auth_permission VALUES (39, 'Can delete clientes', 10, 'delete_clientes');
INSERT INTO public.auth_permission VALUES (40, 'Can view clientes', 10, 'view_clientes');
INSERT INTO public.auth_permission VALUES (41, 'Can add developer', 11, 'add_developer');
INSERT INTO public.auth_permission VALUES (42, 'Can change developer', 11, 'change_developer');
INSERT INTO public.auth_permission VALUES (43, 'Can delete developer', 11, 'delete_developer');
INSERT INTO public.auth_permission VALUES (44, 'Can view developer', 11, 'view_developer');
INSERT INTO public.auth_permission VALUES (45, 'Can add empresas transporte', 12, 'add_empresastransporte');
INSERT INTO public.auth_permission VALUES (46, 'Can change empresas transporte', 12, 'change_empresastransporte');
INSERT INTO public.auth_permission VALUES (47, 'Can delete empresas transporte', 12, 'delete_empresastransporte');
INSERT INTO public.auth_permission VALUES (48, 'Can view empresas transporte', 12, 'view_empresastransporte');
INSERT INTO public.auth_permission VALUES (49, 'Can add holding', 13, 'add_holding');
INSERT INTO public.auth_permission VALUES (50, 'Can change holding', 13, 'change_holding');
INSERT INTO public.auth_permission VALUES (51, 'Can delete holding', 13, 'delete_holding');
INSERT INTO public.auth_permission VALUES (52, 'Can view holding', 13, 'view_holding');
INSERT INTO public.auth_permission VALUES (53, 'Can add ips regimen', 14, 'add_ipsregimen');
INSERT INTO public.auth_permission VALUES (54, 'Can change ips regimen', 14, 'change_ipsregimen');
INSERT INTO public.auth_permission VALUES (55, 'Can delete ips regimen', 14, 'delete_ipsregimen');
INSERT INTO public.auth_permission VALUES (56, 'Can view ips regimen', 14, 'view_ipsregimen');
INSERT INTO public.auth_permission VALUES (57, 'Can add mutualidad', 15, 'add_mutualidad');
INSERT INTO public.auth_permission VALUES (58, 'Can change mutualidad', 15, 'change_mutualidad');
INSERT INTO public.auth_permission VALUES (59, 'Can delete mutualidad', 15, 'delete_mutualidad');
INSERT INTO public.auth_permission VALUES (60, 'Can view mutualidad', 15, 'view_mutualidad');
INSERT INTO public.auth_permission VALUES (61, 'Can add region', 16, 'add_region');
INSERT INTO public.auth_permission VALUES (62, 'Can change region', 16, 'change_region');
INSERT INTO public.auth_permission VALUES (63, 'Can delete region', 16, 'delete_region');
INSERT INTO public.auth_permission VALUES (64, 'Can view region', 16, 'view_region');
INSERT INTO public.auth_permission VALUES (65, 'Can add tipo discapacidad', 17, 'add_tipodiscapacidad');
INSERT INTO public.auth_permission VALUES (66, 'Can change tipo discapacidad', 17, 'change_tipodiscapacidad');
INSERT INTO public.auth_permission VALUES (67, 'Can delete tipo discapacidad', 17, 'delete_tipodiscapacidad');
INSERT INTO public.auth_permission VALUES (68, 'Can view tipo discapacidad', 17, 'view_tipodiscapacidad');
INSERT INTO public.auth_permission VALUES (69, 'Can add tipo impuesto renta', 18, 'add_tipoimpuestorenta');
INSERT INTO public.auth_permission VALUES (70, 'Can change tipo impuesto renta', 18, 'change_tipoimpuestorenta');
INSERT INTO public.auth_permission VALUES (71, 'Can delete tipo impuesto renta', 18, 'delete_tipoimpuestorenta');
INSERT INTO public.auth_permission VALUES (72, 'Can view tipo impuesto renta', 18, 'view_tipoimpuestorenta');
INSERT INTO public.auth_permission VALUES (73, 'Can add tipo jornada', 19, 'add_tipojornada');
INSERT INTO public.auth_permission VALUES (74, 'Can change tipo jornada', 19, 'change_tipojornada');
INSERT INTO public.auth_permission VALUES (75, 'Can delete tipo jornada', 19, 'delete_tipojornada');
INSERT INTO public.auth_permission VALUES (76, 'Can view tipo jornada', 19, 'view_tipojornada');
INSERT INTO public.auth_permission VALUES (77, 'Can add usuarios', 20, 'add_usuarios');
INSERT INTO public.auth_permission VALUES (78, 'Can change usuarios', 20, 'change_usuarios');
INSERT INTO public.auth_permission VALUES (79, 'Can delete usuarios', 20, 'delete_usuarios');
INSERT INTO public.auth_permission VALUES (80, 'Can view usuarios', 20, 'view_usuarios');
INSERT INTO public.auth_permission VALUES (81, 'Can add cargos cliente', 21, 'add_cargoscliente');
INSERT INTO public.auth_permission VALUES (82, 'Can change cargos cliente', 21, 'change_cargoscliente');
INSERT INTO public.auth_permission VALUES (83, 'Can delete cargos cliente', 21, 'delete_cargoscliente');
INSERT INTO public.auth_permission VALUES (84, 'Can view cargos cliente', 21, 'view_cargoscliente');
INSERT INTO public.auth_permission VALUES (85, 'Can add campos clientes', 22, 'add_camposclientes');
INSERT INTO public.auth_permission VALUES (86, 'Can change campos clientes', 22, 'change_camposclientes');
INSERT INTO public.auth_permission VALUES (87, 'Can delete campos clientes', 22, 'delete_camposclientes');
INSERT INTO public.auth_permission VALUES (88, 'Can view campos clientes', 22, 'view_camposclientes');
INSERT INTO public.auth_permission VALUES (89, 'Can add cuenta origen', 23, 'add_cuentaorigen');
INSERT INTO public.auth_permission VALUES (90, 'Can change cuenta origen', 23, 'change_cuentaorigen');
INSERT INTO public.auth_permission VALUES (91, 'Can delete cuenta origen', 23, 'delete_cuentaorigen');
INSERT INTO public.auth_permission VALUES (92, 'Can view cuenta origen', 23, 'view_cuentaorigen');
INSERT INTO public.auth_permission VALUES (93, 'Can add folio comercial', 24, 'add_foliocomercial');
INSERT INTO public.auth_permission VALUES (94, 'Can change folio comercial', 24, 'change_foliocomercial');
INSERT INTO public.auth_permission VALUES (95, 'Can delete folio comercial', 24, 'delete_foliocomercial');
INSERT INTO public.auth_permission VALUES (96, 'Can view folio comercial', 24, 'view_foliocomercial');
INSERT INTO public.auth_permission VALUES (97, 'Can add folio transportista', 25, 'add_foliotransportista');
INSERT INTO public.auth_permission VALUES (98, 'Can change folio transportista', 25, 'change_foliotransportista');
INSERT INTO public.auth_permission VALUES (99, 'Can delete folio transportista', 25, 'delete_foliotransportista');
INSERT INTO public.auth_permission VALUES (100, 'Can view folio transportista', 25, 'view_foliotransportista');
INSERT INTO public.auth_permission VALUES (101, 'Can add historial cambio pago', 26, 'add_historialcambiopago');
INSERT INTO public.auth_permission VALUES (102, 'Can change historial cambio pago', 26, 'change_historialcambiopago');
INSERT INTO public.auth_permission VALUES (103, 'Can delete historial cambio pago', 26, 'delete_historialcambiopago');
INSERT INTO public.auth_permission VALUES (104, 'Can view historial cambio pago', 26, 'view_historialcambiopago');
INSERT INTO public.auth_permission VALUES (105, 'Can add historial cambio folio', 27, 'add_historialcambiofolio');
INSERT INTO public.auth_permission VALUES (106, 'Can change historial cambio folio', 27, 'change_historialcambiofolio');
INSERT INTO public.auth_permission VALUES (107, 'Can delete historial cambio folio', 27, 'delete_historialcambiofolio');
INSERT INTO public.auth_permission VALUES (108, 'Can view historial cambio folio', 27, 'view_historialcambiofolio');
INSERT INTO public.auth_permission VALUES (109, 'Can add haberes', 28, 'add_haberes');
INSERT INTO public.auth_permission VALUES (110, 'Can change haberes', 28, 'change_haberes');
INSERT INTO public.auth_permission VALUES (111, 'Can delete haberes', 28, 'delete_haberes');
INSERT INTO public.auth_permission VALUES (112, 'Can view haberes', 28, 'view_haberes');
INSERT INTO public.auth_permission VALUES (113, 'Can add descuentos', 29, 'add_descuentos');
INSERT INTO public.auth_permission VALUES (114, 'Can change descuentos', 29, 'change_descuentos');
INSERT INTO public.auth_permission VALUES (115, 'Can delete descuentos', 29, 'delete_descuentos');
INSERT INTO public.auth_permission VALUES (116, 'Can view descuentos', 29, 'view_descuentos');
INSERT INTO public.auth_permission VALUES (117, 'Can add cuenta', 30, 'add_cuenta');
INSERT INTO public.auth_permission VALUES (118, 'Can change cuenta', 30, 'change_cuenta');
INSERT INTO public.auth_permission VALUES (119, 'Can delete cuenta', 30, 'delete_cuenta');
INSERT INTO public.auth_permission VALUES (120, 'Can view cuenta', 30, 'view_cuenta');
INSERT INTO public.auth_permission VALUES (121, 'Can add contrato variables', 31, 'add_contratovariables');
INSERT INTO public.auth_permission VALUES (122, 'Can change contrato variables', 31, 'change_contratovariables');
INSERT INTO public.auth_permission VALUES (123, 'Can delete contrato variables', 31, 'delete_contratovariables');
INSERT INTO public.auth_permission VALUES (124, 'Can view contrato variables', 31, 'view_contratovariables');
INSERT INTO public.auth_permission VALUES (125, 'Can add contactos clientes', 32, 'add_contactosclientes');
INSERT INTO public.auth_permission VALUES (126, 'Can change contactos clientes', 32, 'change_contactosclientes');
INSERT INTO public.auth_permission VALUES (127, 'Can delete contactos clientes', 32, 'delete_contactosclientes');
INSERT INTO public.auth_permission VALUES (128, 'Can view contactos clientes', 32, 'view_contactosclientes');
INSERT INTO public.auth_permission VALUES (129, 'Can add configuracion sii automatica compra', 33, 'add_configuracionsiiautomaticacompra');
INSERT INTO public.auth_permission VALUES (130, 'Can change configuracion sii automatica compra', 33, 'change_configuracionsiiautomaticacompra');
INSERT INTO public.auth_permission VALUES (131, 'Can delete configuracion sii automatica compra', 33, 'delete_configuracionsiiautomaticacompra');
INSERT INTO public.auth_permission VALUES (132, 'Can view configuracion sii automatica compra', 33, 'view_configuracionsiiautomaticacompra');
INSERT INTO public.auth_permission VALUES (133, 'Can add casas trabajadores', 34, 'add_casastrabajadores');
INSERT INTO public.auth_permission VALUES (134, 'Can change casas trabajadores', 34, 'change_casastrabajadores');
INSERT INTO public.auth_permission VALUES (135, 'Can delete casas trabajadores', 34, 'delete_casastrabajadores');
INSERT INTO public.auth_permission VALUES (136, 'Can view casas trabajadores', 34, 'view_casastrabajadores');
INSERT INTO public.auth_permission VALUES (137, 'Can add cartola movimiento', 35, 'add_cartolamovimiento');
INSERT INTO public.auth_permission VALUES (138, 'Can change cartola movimiento', 35, 'change_cartolamovimiento');
INSERT INTO public.auth_permission VALUES (139, 'Can delete cartola movimiento', 35, 'delete_cartolamovimiento');
INSERT INTO public.auth_permission VALUES (140, 'Can view cartola movimiento', 35, 'view_cartolamovimiento');
INSERT INTO public.auth_permission VALUES (141, 'Can add cargos administracion', 36, 'add_cargosadministracion');
INSERT INTO public.auth_permission VALUES (142, 'Can change cargos administracion', 36, 'change_cargosadministracion');
INSERT INTO public.auth_permission VALUES (143, 'Can delete cargos administracion', 36, 'delete_cargosadministracion');
INSERT INTO public.auth_permission VALUES (144, 'Can view cargos administracion', 36, 'view_cargosadministracion');
INSERT INTO public.auth_permission VALUES (145, 'Can add cargos', 37, 'add_cargos');
INSERT INTO public.auth_permission VALUES (146, 'Can change cargos', 37, 'change_cargos');
INSERT INTO public.auth_permission VALUES (147, 'Can delete cargos', 37, 'delete_cargos');
INSERT INTO public.auth_permission VALUES (148, 'Can view cargos', 37, 'view_cargos');
INSERT INTO public.auth_permission VALUES (149, 'Can add Enlace APK', 38, 'add_apklink');
INSERT INTO public.auth_permission VALUES (150, 'Can change Enlace APK', 38, 'change_apklink');
INSERT INTO public.auth_permission VALUES (151, 'Can delete Enlace APK', 38, 'delete_apklink');
INSERT INTO public.auth_permission VALUES (152, 'Can view Enlace APK', 38, 'view_apklink');
INSERT INTO public.auth_permission VALUES (153, 'Can add afp trabajadores', 39, 'add_afptrabajadores');
INSERT INTO public.auth_permission VALUES (154, 'Can change afp trabajadores', 39, 'change_afptrabajadores');
INSERT INTO public.auth_permission VALUES (155, 'Can delete afp trabajadores', 39, 'delete_afptrabajadores');
INSERT INTO public.auth_permission VALUES (156, 'Can view afp trabajadores', 39, 'view_afptrabajadores');
INSERT INTO public.auth_permission VALUES (157, 'Can add horarios', 40, 'add_horarios');
INSERT INTO public.auth_permission VALUES (158, 'Can change horarios', 40, 'change_horarios');
INSERT INTO public.auth_permission VALUES (159, 'Can delete horarios', 40, 'delete_horarios');
INSERT INTO public.auth_permission VALUES (160, 'Can view horarios', 40, 'view_horarios');
INSERT INTO public.auth_permission VALUES (161, 'Can add labores', 41, 'add_labores');
INSERT INTO public.auth_permission VALUES (162, 'Can change labores', 41, 'change_labores');
INSERT INTO public.auth_permission VALUES (163, 'Can delete labores', 41, 'delete_labores');
INSERT INTO public.auth_permission VALUES (164, 'Can view labores', 41, 'view_labores');
INSERT INTO public.auth_permission VALUES (165, 'Can add factura venta sii distribuida', 42, 'add_facturaventasiidistribuida');
INSERT INTO public.auth_permission VALUES (166, 'Can change factura venta sii distribuida', 42, 'change_facturaventasiidistribuida');
INSERT INTO public.auth_permission VALUES (167, 'Can delete factura venta sii distribuida', 42, 'delete_facturaventasiidistribuida');
INSERT INTO public.auth_permission VALUES (168, 'Can view factura venta sii distribuida', 42, 'view_facturaventasiidistribuida');
INSERT INTO public.auth_permission VALUES (169, 'Can add factura compra sii distribuida', 43, 'add_facturacomprasiidistribuida');
INSERT INTO public.auth_permission VALUES (170, 'Can change factura compra sii distribuida', 43, 'change_facturacomprasiidistribuida');
INSERT INTO public.auth_permission VALUES (171, 'Can delete factura compra sii distribuida', 43, 'delete_facturacomprasiidistribuida');
INSERT INTO public.auth_permission VALUES (172, 'Can view factura compra sii distribuida', 43, 'view_facturacomprasiidistribuida');
INSERT INTO public.auth_permission VALUES (173, 'Can add mes cerrado', 44, 'add_mescerrado');
INSERT INTO public.auth_permission VALUES (174, 'Can change mes cerrado', 44, 'change_mescerrado');
INSERT INTO public.auth_permission VALUES (175, 'Can delete mes cerrado', 44, 'delete_mescerrado');
INSERT INTO public.auth_permission VALUES (176, 'Can view mes cerrado', 44, 'view_mescerrado');
INSERT INTO public.auth_permission VALUES (177, 'Can add modulos movil', 45, 'add_modulosmovil');
INSERT INTO public.auth_permission VALUES (178, 'Can change modulos movil', 45, 'change_modulosmovil');
INSERT INTO public.auth_permission VALUES (179, 'Can delete modulos movil', 45, 'delete_modulosmovil');
INSERT INTO public.auth_permission VALUES (180, 'Can view modulos movil', 45, 'view_modulosmovil');
INSERT INTO public.auth_permission VALUES (181, 'Can add modulos web', 46, 'add_modulosweb');
INSERT INTO public.auth_permission VALUES (182, 'Can change modulos web', 46, 'change_modulosweb');
INSERT INTO public.auth_permission VALUES (183, 'Can delete modulos web', 46, 'delete_modulosweb');
INSERT INTO public.auth_permission VALUES (184, 'Can view modulos web', 46, 'view_modulosweb');
INSERT INTO public.auth_permission VALUES (185, 'Can add pago transportista', 47, 'add_pagotransportista');
INSERT INTO public.auth_permission VALUES (186, 'Can change pago transportista', 47, 'change_pagotransportista');
INSERT INTO public.auth_permission VALUES (187, 'Can delete pago transportista', 47, 'delete_pagotransportista');
INSERT INTO public.auth_permission VALUES (188, 'Can view pago transportista', 47, 'view_pagotransportista');
INSERT INTO public.auth_permission VALUES (189, 'Can add detalle pago transportista', 48, 'add_detallepagotransportista');
INSERT INTO public.auth_permission VALUES (190, 'Can change detalle pago transportista', 48, 'change_detallepagotransportista');
INSERT INTO public.auth_permission VALUES (191, 'Can delete detalle pago transportista', 48, 'delete_detallepagotransportista');
INSERT INTO public.auth_permission VALUES (192, 'Can view detalle pago transportista', 48, 'view_detallepagotransportista');
INSERT INTO public.auth_permission VALUES (193, 'Can add perfiles', 49, 'add_perfiles');
INSERT INTO public.auth_permission VALUES (194, 'Can change perfiles', 49, 'change_perfiles');
INSERT INTO public.auth_permission VALUES (195, 'Can delete perfiles', 49, 'delete_perfiles');
INSERT INTO public.auth_permission VALUES (196, 'Can view perfiles', 49, 'view_perfiles');
INSERT INTO public.auth_permission VALUES (197, 'Can add enlace auto registro', 50, 'add_enlaceautoregistro');
INSERT INTO public.auth_permission VALUES (198, 'Can change enlace auto registro', 50, 'change_enlaceautoregistro');
INSERT INTO public.auth_permission VALUES (199, 'Can delete enlace auto registro', 50, 'delete_enlaceautoregistro');
INSERT INTO public.auth_permission VALUES (200, 'Can view enlace auto registro', 50, 'view_enlaceautoregistro');
INSERT INTO public.auth_permission VALUES (201, 'Can add personal trabajadores', 51, 'add_personaltrabajadores');
INSERT INTO public.auth_permission VALUES (202, 'Can change personal trabajadores', 51, 'change_personaltrabajadores');
INSERT INTO public.auth_permission VALUES (203, 'Can delete personal trabajadores', 51, 'delete_personaltrabajadores');
INSERT INTO public.auth_permission VALUES (204, 'Can view personal trabajadores', 51, 'view_personaltrabajadores');
INSERT INTO public.auth_permission VALUES (205, 'Can add licencia medica', 52, 'add_licenciamedica');
INSERT INTO public.auth_permission VALUES (206, 'Can change licencia medica', 52, 'change_licenciamedica');
INSERT INTO public.auth_permission VALUES (207, 'Can delete licencia medica', 52, 'delete_licenciamedica');
INSERT INTO public.auth_permission VALUES (208, 'Can view licencia medica', 52, 'view_licenciamedica');
INSERT INTO public.auth_permission VALUES (209, 'Can add jefes de cuadrilla', 53, 'add_jefesdecuadrilla');
INSERT INTO public.auth_permission VALUES (210, 'Can change jefes de cuadrilla', 53, 'change_jefesdecuadrilla');
INSERT INTO public.auth_permission VALUES (211, 'Can delete jefes de cuadrilla', 53, 'delete_jefesdecuadrilla');
INSERT INTO public.auth_permission VALUES (212, 'Can view jefes de cuadrilla', 53, 'view_jefesdecuadrilla');
INSERT INTO public.auth_permission VALUES (213, 'Can add hora extraordinaria', 54, 'add_horaextraordinaria');
INSERT INTO public.auth_permission VALUES (214, 'Can change hora extraordinaria', 54, 'change_horaextraordinaria');
INSERT INTO public.auth_permission VALUES (215, 'Can delete hora extraordinaria', 54, 'delete_horaextraordinaria');
INSERT INTO public.auth_permission VALUES (216, 'Can view hora extraordinaria', 54, 'view_horaextraordinaria');
INSERT INTO public.auth_permission VALUES (217, 'Can add dias trabajados aprobados', 55, 'add_diastrabajadosaprobados');
INSERT INTO public.auth_permission VALUES (218, 'Can change dias trabajados aprobados', 55, 'change_diastrabajadosaprobados');
INSERT INTO public.auth_permission VALUES (219, 'Can delete dias trabajados aprobados', 55, 'delete_diastrabajadosaprobados');
INSERT INTO public.auth_permission VALUES (220, 'Can view dias trabajados aprobados', 55, 'view_diastrabajadosaprobados');
INSERT INTO public.auth_permission VALUES (221, 'Can add cuadrillas', 56, 'add_cuadrillas');
INSERT INTO public.auth_permission VALUES (222, 'Can change cuadrillas', 56, 'change_cuadrillas');
INSERT INTO public.auth_permission VALUES (223, 'Can delete cuadrillas', 56, 'delete_cuadrillas');
INSERT INTO public.auth_permission VALUES (224, 'Can view cuadrillas', 56, 'view_cuadrillas');
INSERT INTO public.auth_permission VALUES (225, 'Can add codigo qr', 57, 'add_codigoqr');
INSERT INTO public.auth_permission VALUES (226, 'Can change codigo qr', 57, 'change_codigoqr');
INSERT INTO public.auth_permission VALUES (227, 'Can delete codigo qr', 57, 'delete_codigoqr');
INSERT INTO public.auth_permission VALUES (228, 'Can view codigo qr', 57, 'view_codigoqr');
INSERT INTO public.auth_permission VALUES (229, 'Can add produccion trabajador', 58, 'add_producciontrabajador');
INSERT INTO public.auth_permission VALUES (230, 'Can change produccion trabajador', 58, 'change_producciontrabajador');
INSERT INTO public.auth_permission VALUES (231, 'Can delete produccion trabajador', 58, 'delete_producciontrabajador');
INSERT INTO public.auth_permission VALUES (232, 'Can view produccion trabajador', 58, 'view_producciontrabajador');
INSERT INTO public.auth_permission VALUES (233, 'Can add comuna', 59, 'add_comuna');
INSERT INTO public.auth_permission VALUES (234, 'Can change comuna', 59, 'change_comuna');
INSERT INTO public.auth_permission VALUES (235, 'Can delete comuna', 59, 'delete_comuna');
INSERT INTO public.auth_permission VALUES (236, 'Can view comuna', 59, 'view_comuna');
INSERT INTO public.auth_permission VALUES (237, 'Can add registro egreso', 60, 'add_registroegreso');
INSERT INTO public.auth_permission VALUES (238, 'Can change registro egreso', 60, 'change_registroegreso');
INSERT INTO public.auth_permission VALUES (239, 'Can delete registro egreso', 60, 'delete_registroegreso');
INSERT INTO public.auth_permission VALUES (240, 'Can view registro egreso', 60, 'view_registroegreso');
INSERT INTO public.auth_permission VALUES (241, 'Can add registro ingreso', 61, 'add_registroingreso');
INSERT INTO public.auth_permission VALUES (242, 'Can change registro ingreso', 61, 'change_registroingreso');
INSERT INTO public.auth_permission VALUES (243, 'Can delete registro ingreso', 61, 'delete_registroingreso');
INSERT INTO public.auth_permission VALUES (244, 'Can view registro ingreso', 61, 'view_registroingreso');
INSERT INTO public.auth_permission VALUES (245, 'Can add registro pago efectivo', 62, 'add_registropagoefectivo');
INSERT INTO public.auth_permission VALUES (246, 'Can change registro pago efectivo', 62, 'change_registropagoefectivo');
INSERT INTO public.auth_permission VALUES (247, 'Can delete registro pago efectivo', 62, 'delete_registropagoefectivo');
INSERT INTO public.auth_permission VALUES (248, 'Can view registro pago efectivo', 62, 'view_registropagoefectivo');
INSERT INTO public.auth_permission VALUES (249, 'Can add registro pago transferencia', 63, 'add_registropagotransferencia');
INSERT INTO public.auth_permission VALUES (250, 'Can change registro pago transferencia', 63, 'change_registropagotransferencia');
INSERT INTO public.auth_permission VALUES (251, 'Can delete registro pago transferencia', 63, 'delete_registropagotransferencia');
INSERT INTO public.auth_permission VALUES (252, 'Can view registro pago transferencia', 63, 'view_registropagotransferencia');
INSERT INTO public.auth_permission VALUES (253, 'Can add salud trabajadores', 64, 'add_saludtrabajadores');
INSERT INTO public.auth_permission VALUES (254, 'Can change salud trabajadores', 64, 'change_saludtrabajadores');
INSERT INTO public.auth_permission VALUES (255, 'Can delete salud trabajadores', 64, 'delete_saludtrabajadores');
INSERT INTO public.auth_permission VALUES (256, 'Can view salud trabajadores', 64, 'view_saludtrabajadores');
INSERT INTO public.auth_permission VALUES (257, 'Can add sociedad', 65, 'add_sociedad');
INSERT INTO public.auth_permission VALUES (258, 'Can change sociedad', 65, 'change_sociedad');
INSERT INTO public.auth_permission VALUES (259, 'Can delete sociedad', 65, 'delete_sociedad');
INSERT INTO public.auth_permission VALUES (260, 'Can view sociedad', 65, 'view_sociedad');
INSERT INTO public.auth_permission VALUES (261, 'Can add proforma transportista', 66, 'add_proformatransportista');
INSERT INTO public.auth_permission VALUES (262, 'Can change proforma transportista', 66, 'change_proformatransportista');
INSERT INTO public.auth_permission VALUES (263, 'Can delete proforma transportista', 66, 'delete_proformatransportista');
INSERT INTO public.auth_permission VALUES (264, 'Can view proforma transportista', 66, 'view_proformatransportista');
INSERT INTO public.auth_permission VALUES (265, 'Can add sub modulos movil', 67, 'add_submodulosmovil');
INSERT INTO public.auth_permission VALUES (266, 'Can change sub modulos movil', 67, 'change_submodulosmovil');
INSERT INTO public.auth_permission VALUES (267, 'Can delete sub modulos movil', 67, 'delete_submodulosmovil');
INSERT INTO public.auth_permission VALUES (268, 'Can view sub modulos movil', 67, 'view_submodulosmovil');
INSERT INTO public.auth_permission VALUES (269, 'Can add sub modulos web', 68, 'add_submodulosweb');
INSERT INTO public.auth_permission VALUES (270, 'Can change sub modulos web', 68, 'change_submodulosweb');
INSERT INTO public.auth_permission VALUES (271, 'Can delete sub modulos web', 68, 'delete_submodulosweb');
INSERT INTO public.auth_permission VALUES (272, 'Can view sub modulos web', 68, 'view_submodulosweb');
INSERT INTO public.auth_permission VALUES (273, 'Can add supervisores', 69, 'add_supervisores');
INSERT INTO public.auth_permission VALUES (274, 'Can change supervisores', 69, 'change_supervisores');
INSERT INTO public.auth_permission VALUES (275, 'Can delete supervisores', 69, 'delete_supervisores');
INSERT INTO public.auth_permission VALUES (276, 'Can view supervisores', 69, 'view_supervisores');
INSERT INTO public.auth_permission VALUES (277, 'Can add contrato trabajador', 70, 'add_contratotrabajador');
INSERT INTO public.auth_permission VALUES (278, 'Can change contrato trabajador', 70, 'change_contratotrabajador');
INSERT INTO public.auth_permission VALUES (279, 'Can delete contrato trabajador', 70, 'delete_contratotrabajador');
INSERT INTO public.auth_permission VALUES (280, 'Can view contrato trabajador', 70, 'view_contratotrabajador');
INSERT INTO public.auth_permission VALUES (281, 'Can add trabajador descuento', 71, 'add_trabajadordescuento');
INSERT INTO public.auth_permission VALUES (282, 'Can change trabajador descuento', 71, 'change_trabajadordescuento');
INSERT INTO public.auth_permission VALUES (283, 'Can delete trabajador descuento', 71, 'delete_trabajadordescuento');
INSERT INTO public.auth_permission VALUES (284, 'Can view trabajador descuento', 71, 'view_trabajadordescuento');
INSERT INTO public.auth_permission VALUES (285, 'Can add trabajador haber', 72, 'add_trabajadorhaber');
INSERT INTO public.auth_permission VALUES (286, 'Can change trabajador haber', 72, 'change_trabajadorhaber');
INSERT INTO public.auth_permission VALUES (287, 'Can delete trabajador haber', 72, 'delete_trabajadorhaber');
INSERT INTO public.auth_permission VALUES (288, 'Can view trabajador haber', 72, 'view_trabajadorhaber');
INSERT INTO public.auth_permission VALUES (289, 'Can add tramos', 73, 'add_tramos');
INSERT INTO public.auth_permission VALUES (290, 'Can change tramos', 73, 'change_tramos');
INSERT INTO public.auth_permission VALUES (291, 'Can delete tramos', 73, 'delete_tramos');
INSERT INTO public.auth_permission VALUES (292, 'Can view tramos', 73, 'view_tramos');
INSERT INTO public.auth_permission VALUES (293, 'Can add unidad control', 74, 'add_unidadcontrol');
INSERT INTO public.auth_permission VALUES (294, 'Can change unidad control', 74, 'change_unidadcontrol');
INSERT INTO public.auth_permission VALUES (295, 'Can delete unidad control', 74, 'delete_unidadcontrol');
INSERT INTO public.auth_permission VALUES (296, 'Can view unidad control', 74, 'view_unidadcontrol');
INSERT INTO public.auth_permission VALUES (297, 'Can add vacaciones', 75, 'add_vacaciones');
INSERT INTO public.auth_permission VALUES (298, 'Can change vacaciones', 75, 'change_vacaciones');
INSERT INTO public.auth_permission VALUES (299, 'Can delete vacaciones', 75, 'delete_vacaciones');
INSERT INTO public.auth_permission VALUES (300, 'Can view vacaciones', 75, 'view_vacaciones');
INSERT INTO public.auth_permission VALUES (301, 'Can add vehiculos transporte', 76, 'add_vehiculostransporte');
INSERT INTO public.auth_permission VALUES (302, 'Can change vehiculos transporte', 76, 'change_vehiculostransporte');
INSERT INTO public.auth_permission VALUES (303, 'Can delete vehiculos transporte', 76, 'delete_vehiculostransporte');
INSERT INTO public.auth_permission VALUES (304, 'Can view vehiculos transporte', 76, 'view_vehiculostransporte');
INSERT INTO public.auth_permission VALUES (305, 'Can add choferes transporte', 77, 'add_choferestransporte');
INSERT INTO public.auth_permission VALUES (306, 'Can change choferes transporte', 77, 'change_choferestransporte');
INSERT INTO public.auth_permission VALUES (307, 'Can delete choferes transporte', 77, 'delete_choferestransporte');
INSERT INTO public.auth_permission VALUES (308, 'Can view choferes transporte', 77, 'view_choferestransporte');
INSERT INTO public.auth_permission VALUES (309, 'Can add calibration settings', 78, 'add_calibrationsettings');
INSERT INTO public.auth_permission VALUES (310, 'Can change calibration settings', 78, 'change_calibrationsettings');
INSERT INTO public.auth_permission VALUES (311, 'Can delete calibration settings', 78, 'delete_calibrationsettings');
INSERT INTO public.auth_permission VALUES (312, 'Can view calibration settings', 78, 'view_calibrationsettings');
INSERT INTO public.auth_permission VALUES (313, 'Can add factura venta sii por distribuir', 79, 'add_facturaventasiipordistribuir');
INSERT INTO public.auth_permission VALUES (314, 'Can change factura venta sii por distribuir', 79, 'change_facturaventasiipordistribuir');
INSERT INTO public.auth_permission VALUES (315, 'Can delete factura venta sii por distribuir', 79, 'delete_facturaventasiipordistribuir');
INSERT INTO public.auth_permission VALUES (316, 'Can view factura venta sii por distribuir', 79, 'view_facturaventasiipordistribuir');
INSERT INTO public.auth_permission VALUES (317, 'Can add factura compra sii por distribuir', 80, 'add_facturacomprasiipordistribuir');
INSERT INTO public.auth_permission VALUES (318, 'Can change factura compra sii por distribuir', 80, 'change_facturacomprasiipordistribuir');
INSERT INTO public.auth_permission VALUES (319, 'Can delete factura compra sii por distribuir', 80, 'delete_facturacomprasiipordistribuir');
INSERT INTO public.auth_permission VALUES (320, 'Can view factura compra sii por distribuir', 80, 'view_facturacomprasiipordistribuir');
INSERT INTO public.auth_permission VALUES (321, 'Can add configuracion sii automatica venta', 81, 'add_configuracionsiiautomaticaventa');
INSERT INTO public.auth_permission VALUES (322, 'Can change configuracion sii automatica venta', 81, 'change_configuracionsiiautomaticaventa');
INSERT INTO public.auth_permission VALUES (323, 'Can delete configuracion sii automatica venta', 81, 'delete_configuracionsiiautomaticaventa');
INSERT INTO public.auth_permission VALUES (324, 'Can view configuracion sii automatica venta', 81, 'view_configuracionsiiautomaticaventa');
INSERT INTO public.auth_permission VALUES (325, 'Can add log entry', 82, 'add_logentry');
INSERT INTO public.auth_permission VALUES (326, 'Can change log entry', 82, 'change_logentry');
INSERT INTO public.auth_permission VALUES (327, 'Can delete log entry', 82, 'delete_logentry');
INSERT INTO public.auth_permission VALUES (328, 'Can view log entry', 82, 'view_logentry');
INSERT INTO public.auth_permission VALUES (329, 'Can add session', 83, 'add_session');
INSERT INTO public.auth_permission VALUES (330, 'Can change session', 83, 'change_session');
INSERT INTO public.auth_permission VALUES (331, 'Can delete session', 83, 'delete_session');
INSERT INTO public.auth_permission VALUES (332, 'Can view session', 83, 'view_session');
INSERT INTO public.auth_permission VALUES (333, 'Can add application', 84, 'add_application');
INSERT INTO public.auth_permission VALUES (334, 'Can change application', 84, 'change_application');
INSERT INTO public.auth_permission VALUES (335, 'Can delete application', 84, 'delete_application');
INSERT INTO public.auth_permission VALUES (336, 'Can view application', 84, 'view_application');
INSERT INTO public.auth_permission VALUES (337, 'Can add access token', 85, 'add_accesstoken');
INSERT INTO public.auth_permission VALUES (338, 'Can change access token', 85, 'change_accesstoken');
INSERT INTO public.auth_permission VALUES (339, 'Can delete access token', 85, 'delete_accesstoken');
INSERT INTO public.auth_permission VALUES (340, 'Can view access token', 85, 'view_accesstoken');
INSERT INTO public.auth_permission VALUES (341, 'Can add grant', 86, 'add_grant');
INSERT INTO public.auth_permission VALUES (342, 'Can change grant', 86, 'change_grant');
INSERT INTO public.auth_permission VALUES (343, 'Can delete grant', 86, 'delete_grant');
INSERT INTO public.auth_permission VALUES (344, 'Can view grant', 86, 'view_grant');
INSERT INTO public.auth_permission VALUES (345, 'Can add refresh token', 87, 'add_refreshtoken');
INSERT INTO public.auth_permission VALUES (346, 'Can change refresh token', 87, 'change_refreshtoken');
INSERT INTO public.auth_permission VALUES (347, 'Can delete refresh token', 87, 'delete_refreshtoken');
INSERT INTO public.auth_permission VALUES (348, 'Can view refresh token', 87, 'view_refreshtoken');
INSERT INTO public.auth_permission VALUES (349, 'Can add id token', 88, 'add_idtoken');
INSERT INTO public.auth_permission VALUES (350, 'Can change id token', 88, 'change_idtoken');
INSERT INTO public.auth_permission VALUES (351, 'Can delete id token', 88, 'delete_idtoken');
INSERT INTO public.auth_permission VALUES (352, 'Can view id token', 88, 'view_idtoken');
INSERT INTO public.auth_permission VALUES (353, 'Can add crontab', 89, 'add_crontabschedule');
INSERT INTO public.auth_permission VALUES (354, 'Can change crontab', 89, 'change_crontabschedule');
INSERT INTO public.auth_permission VALUES (355, 'Can delete crontab', 89, 'delete_crontabschedule');
INSERT INTO public.auth_permission VALUES (356, 'Can view crontab', 89, 'view_crontabschedule');
INSERT INTO public.auth_permission VALUES (357, 'Can add interval', 90, 'add_intervalschedule');
INSERT INTO public.auth_permission VALUES (358, 'Can change interval', 90, 'change_intervalschedule');
INSERT INTO public.auth_permission VALUES (359, 'Can delete interval', 90, 'delete_intervalschedule');
INSERT INTO public.auth_permission VALUES (360, 'Can view interval', 90, 'view_intervalschedule');
INSERT INTO public.auth_permission VALUES (361, 'Can add periodic task', 91, 'add_periodictask');
INSERT INTO public.auth_permission VALUES (362, 'Can change periodic task', 91, 'change_periodictask');
INSERT INTO public.auth_permission VALUES (363, 'Can delete periodic task', 91, 'delete_periodictask');
INSERT INTO public.auth_permission VALUES (364, 'Can view periodic task', 91, 'view_periodictask');
INSERT INTO public.auth_permission VALUES (365, 'Can add periodic task track', 92, 'add_periodictasks');
INSERT INTO public.auth_permission VALUES (366, 'Can change periodic task track', 92, 'change_periodictasks');
INSERT INTO public.auth_permission VALUES (367, 'Can delete periodic task track', 92, 'delete_periodictasks');
INSERT INTO public.auth_permission VALUES (368, 'Can view periodic task track', 92, 'view_periodictasks');
INSERT INTO public.auth_permission VALUES (369, 'Can add solar event', 93, 'add_solarschedule');
INSERT INTO public.auth_permission VALUES (370, 'Can change solar event', 93, 'change_solarschedule');
INSERT INTO public.auth_permission VALUES (371, 'Can delete solar event', 93, 'delete_solarschedule');
INSERT INTO public.auth_permission VALUES (372, 'Can view solar event', 93, 'view_solarschedule');
INSERT INTO public.auth_permission VALUES (373, 'Can add clocked', 94, 'add_clockedschedule');
INSERT INTO public.auth_permission VALUES (374, 'Can change clocked', 94, 'change_clockedschedule');
INSERT INTO public.auth_permission VALUES (375, 'Can delete clocked', 94, 'delete_clockedschedule');
INSERT INTO public.auth_permission VALUES (376, 'Can view clocked', 94, 'view_clockedschedule');


ALTER TABLE public.auth_permission ENABLE TRIGGER ALL;

--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.auth_group_permissions DISABLE TRIGGER ALL;



ALTER TABLE public.auth_group_permissions ENABLE TRIGGER ALL;

--
-- Data for Name: documentos_variables; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.documentos_variables DISABLE TRIGGER ALL;



ALTER TABLE public.documentos_variables ENABLE TRIGGER ALL;

--
-- Data for Name: calibraciones_pdf; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.calibraciones_pdf DISABLE TRIGGER ALL;



ALTER TABLE public.calibraciones_pdf ENABLE TRIGGER ALL;

--
-- Data for Name: cargos; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.cargos DISABLE TRIGGER ALL;



ALTER TABLE public.cargos ENABLE TRIGGER ALL;

--
-- Data for Name: cargos_clientes; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.cargos_clientes DISABLE TRIGGER ALL;



ALTER TABLE public.cargos_clientes ENABLE TRIGGER ALL;

--
-- Data for Name: cuenta_origen; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.cuenta_origen DISABLE TRIGGER ALL;

INSERT INTO public.cuenta_origen VALUES (1, 'CCT', '44700087112', 12, 1);


ALTER TABLE public.cuenta_origen ENABLE TRIGGER ALL;

--
-- Data for Name: cartola_movimiento; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.cartola_movimiento DISABLE TRIGGER ALL;



ALTER TABLE public.cartola_movimiento ENABLE TRIGGER ALL;

--
-- Data for Name: causales_finiquito; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.causales_finiquito DISABLE TRIGGER ALL;



ALTER TABLE public.causales_finiquito ENABLE TRIGGER ALL;

--
-- Data for Name: choferes; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.choferes DISABLE TRIGGER ALL;



ALTER TABLE public.choferes ENABLE TRIGGER ALL;

--
-- Data for Name: regiones; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.regiones DISABLE TRIGGER ALL;



ALTER TABLE public.regiones ENABLE TRIGGER ALL;

--
-- Data for Name: comunas; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.comunas DISABLE TRIGGER ALL;



ALTER TABLE public.comunas ENABLE TRIGGER ALL;

--
-- Data for Name: configuracion_sii_automatica; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.configuracion_sii_automatica DISABLE TRIGGER ALL;



ALTER TABLE public.configuracion_sii_automatica ENABLE TRIGGER ALL;

--
-- Data for Name: configuracion_sii_automatica_venta; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.configuracion_sii_automatica_venta DISABLE TRIGGER ALL;



ALTER TABLE public.configuracion_sii_automatica_venta ENABLE TRIGGER ALL;

--
-- Data for Name: contactos_clientes; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.contactos_clientes DISABLE TRIGGER ALL;



ALTER TABLE public.contactos_clientes ENABLE TRIGGER ALL;

--
-- Data for Name: estados_discapacidad; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.estados_discapacidad DISABLE TRIGGER ALL;



ALTER TABLE public.estados_discapacidad ENABLE TRIGGER ALL;

--
-- Data for Name: unidad_control; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.unidad_control DISABLE TRIGGER ALL;



ALTER TABLE public.unidad_control ENABLE TRIGGER ALL;

--
-- Data for Name: labores; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.labores DISABLE TRIGGER ALL;



ALTER TABLE public.labores ENABLE TRIGGER ALL;

--
-- Data for Name: tipos_impuesto_renta; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.tipos_impuesto_renta DISABLE TRIGGER ALL;



ALTER TABLE public.tipos_impuesto_renta ENABLE TRIGGER ALL;

--
-- Data for Name: tipos_jornada; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.tipos_jornada DISABLE TRIGGER ALL;



ALTER TABLE public.tipos_jornada ENABLE TRIGGER ALL;

--
-- Data for Name: contratos_trabajadores; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.contratos_trabajadores DISABLE TRIGGER ALL;



ALTER TABLE public.contratos_trabajadores ENABLE TRIGGER ALL;

--
-- Data for Name: supervisores; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.supervisores DISABLE TRIGGER ALL;



ALTER TABLE public.supervisores ENABLE TRIGGER ALL;

--
-- Data for Name: jefes_cuadrilla; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.jefes_cuadrilla DISABLE TRIGGER ALL;



ALTER TABLE public.jefes_cuadrilla ENABLE TRIGGER ALL;

--
-- Data for Name: cuadrillas; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.cuadrillas DISABLE TRIGGER ALL;



ALTER TABLE public.cuadrillas ENABLE TRIGGER ALL;

--
-- Data for Name: cuadrillas_trabajadores; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.cuadrillas_trabajadores DISABLE TRIGGER ALL;



ALTER TABLE public.cuadrillas_trabajadores ENABLE TRIGGER ALL;

--
-- Data for Name: cuentas; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.cuentas DISABLE TRIGGER ALL;



ALTER TABLE public.cuentas ENABLE TRIGGER ALL;

--
-- Data for Name: descuentos; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.descuentos DISABLE TRIGGER ALL;



ALTER TABLE public.descuentos ENABLE TRIGGER ALL;

--
-- Data for Name: pagos_transportista; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.pagos_transportista DISABLE TRIGGER ALL;



ALTER TABLE public.pagos_transportista ENABLE TRIGGER ALL;

--
-- Data for Name: detalle_pagos_transportista; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.detalle_pagos_transportista DISABLE TRIGGER ALL;



ALTER TABLE public.detalle_pagos_transportista ENABLE TRIGGER ALL;

--
-- Data for Name: developer; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.developer DISABLE TRIGGER ALL;



ALTER TABLE public.developer ENABLE TRIGGER ALL;

--
-- Data for Name: dias_trabajados_aprobados; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.dias_trabajados_aprobados DISABLE TRIGGER ALL;



ALTER TABLE public.dias_trabajados_aprobados ENABLE TRIGGER ALL;

--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.django_admin_log DISABLE TRIGGER ALL;



ALTER TABLE public.django_admin_log ENABLE TRIGGER ALL;

--
-- Data for Name: django_celery_beat_clockedschedule; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.django_celery_beat_clockedschedule DISABLE TRIGGER ALL;



ALTER TABLE public.django_celery_beat_clockedschedule ENABLE TRIGGER ALL;

--
-- Data for Name: django_celery_beat_crontabschedule; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.django_celery_beat_crontabschedule DISABLE TRIGGER ALL;

INSERT INTO public.django_celery_beat_crontabschedule VALUES (1, '0', '4', '*', '*', '*', 'America/Santiago');
INSERT INTO public.django_celery_beat_crontabschedule VALUES (2, '*', '*', '*', '*', '*', 'America/Santiago');


ALTER TABLE public.django_celery_beat_crontabschedule ENABLE TRIGGER ALL;

--
-- Data for Name: django_celery_beat_intervalschedule; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.django_celery_beat_intervalschedule DISABLE TRIGGER ALL;



ALTER TABLE public.django_celery_beat_intervalschedule ENABLE TRIGGER ALL;

--
-- Data for Name: django_celery_beat_solarschedule; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.django_celery_beat_solarschedule DISABLE TRIGGER ALL;



ALTER TABLE public.django_celery_beat_solarschedule ENABLE TRIGGER ALL;

--
-- Data for Name: django_celery_beat_periodictask; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.django_celery_beat_periodictask DISABLE TRIGGER ALL;

INSERT INTO public.django_celery_beat_periodictask VALUES (1, 'celery.backend_cleanup', 'celery.backend_cleanup', '[]', '{}', NULL, NULL, NULL, NULL, true, '2025-08-18 08:00:00.005623+00', 14, '2025-08-18 08:03:00.027651+00', '', 1, NULL, NULL, false, NULL, NULL, '{}', NULL, 43200);
INSERT INTO public.django_celery_beat_periodictask VALUES (2, 'revisar-configuraciones-automaticas', 'contratista_test_app.tasks.revisar_configuraciones_pendientes', '[]', '{}', 'facturas_automaticas', NULL, NULL, NULL, true, '2025-08-18 16:51:00.005428+00', 19904, '2025-08-18 16:51:45.167242+00', '', 2, NULL, NULL, false, NULL, NULL, '{}', NULL, NULL);


ALTER TABLE public.django_celery_beat_periodictask ENABLE TRIGGER ALL;

--
-- Data for Name: django_celery_beat_periodictasks; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.django_celery_beat_periodictasks DISABLE TRIGGER ALL;

INSERT INTO public.django_celery_beat_periodictasks VALUES (1, '2025-08-04 21:07:34.952508+00');


ALTER TABLE public.django_celery_beat_periodictasks ENABLE TRIGGER ALL;

--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.django_migrations DISABLE TRIGGER ALL;

INSERT INTO public.django_migrations VALUES (1, 'contenttypes', '0001_initial', '2025-08-04 21:06:47.825089+00');
INSERT INTO public.django_migrations VALUES (2, 'contenttypes', '0002_remove_content_type_name', '2025-08-04 21:06:47.839536+00');
INSERT INTO public.django_migrations VALUES (3, 'auth', '0001_initial', '2025-08-04 21:06:47.900731+00');
INSERT INTO public.django_migrations VALUES (4, 'auth', '0002_alter_permission_name_max_length', '2025-08-04 21:06:47.908515+00');
INSERT INTO public.django_migrations VALUES (5, 'auth', '0003_alter_user_email_max_length', '2025-08-04 21:06:47.914998+00');
INSERT INTO public.django_migrations VALUES (6, 'auth', '0004_alter_user_username_opts', '2025-08-04 21:06:47.921433+00');
INSERT INTO public.django_migrations VALUES (7, 'auth', '0005_alter_user_last_login_null', '2025-08-04 21:06:47.930908+00');
INSERT INTO public.django_migrations VALUES (8, 'auth', '0006_require_contenttypes_0002', '2025-08-04 21:06:47.933366+00');
INSERT INTO public.django_migrations VALUES (9, 'auth', '0007_alter_validators_add_error_messages', '2025-08-04 21:06:47.941952+00');
INSERT INTO public.django_migrations VALUES (10, 'auth', '0008_alter_user_username_max_length', '2025-08-04 21:06:47.948543+00');
INSERT INTO public.django_migrations VALUES (11, 'auth', '0009_alter_user_last_name_max_length', '2025-08-04 21:06:47.955119+00');
INSERT INTO public.django_migrations VALUES (12, 'auth', '0010_alter_group_name_max_length', '2025-08-04 21:06:47.966076+00');
INSERT INTO public.django_migrations VALUES (13, 'auth', '0011_update_proxy_permissions', '2025-08-04 21:06:47.97302+00');
INSERT INTO public.django_migrations VALUES (14, 'auth', '0012_alter_user_first_name_max_length', '2025-08-04 21:06:47.97963+00');
INSERT INTO public.django_migrations VALUES (15, 'contratista_test_app', '0001_initial', '2025-08-04 21:06:56.922854+00');
INSERT INTO public.django_migrations VALUES (16, 'admin', '0001_initial', '2025-08-04 21:07:04.110514+00');
INSERT INTO public.django_migrations VALUES (17, 'admin', '0002_logentry_remove_auto_add', '2025-08-04 21:07:04.146779+00');
INSERT INTO public.django_migrations VALUES (18, 'admin', '0003_logentry_add_action_flag_choices', '2025-08-04 21:07:04.26307+00');
INSERT INTO public.django_migrations VALUES (19, 'django_celery_beat', '0001_initial', '2025-08-04 21:07:04.335045+00');
INSERT INTO public.django_migrations VALUES (20, 'django_celery_beat', '0002_auto_20161118_0346', '2025-08-04 21:07:04.370902+00');
INSERT INTO public.django_migrations VALUES (21, 'django_celery_beat', '0003_auto_20161209_0049', '2025-08-04 21:07:04.400349+00');
INSERT INTO public.django_migrations VALUES (22, 'django_celery_beat', '0004_auto_20170221_0000', '2025-08-04 21:07:04.408978+00');
INSERT INTO public.django_migrations VALUES (23, 'django_celery_beat', '0005_add_solarschedule_events_choices', '2025-08-04 21:07:04.417255+00');
INSERT INTO public.django_migrations VALUES (24, 'django_celery_beat', '0006_auto_20180322_0932', '2025-08-04 21:07:04.48097+00');
INSERT INTO public.django_migrations VALUES (25, 'django_celery_beat', '0007_auto_20180521_0826', '2025-08-04 21:07:04.511114+00');
INSERT INTO public.django_migrations VALUES (26, 'django_celery_beat', '0008_auto_20180914_1922', '2025-08-04 21:07:04.566588+00');
INSERT INTO public.django_migrations VALUES (27, 'django_celery_beat', '0006_auto_20180210_1226', '2025-08-04 21:07:04.600687+00');
INSERT INTO public.django_migrations VALUES (28, 'django_celery_beat', '0006_periodictask_priority', '2025-08-04 21:07:04.616174+00');
INSERT INTO public.django_migrations VALUES (29, 'django_celery_beat', '0009_periodictask_headers', '2025-08-04 21:07:04.635102+00');
INSERT INTO public.django_migrations VALUES (30, 'django_celery_beat', '0010_auto_20190429_0326', '2025-08-04 21:07:04.962768+00');
INSERT INTO public.django_migrations VALUES (31, 'django_celery_beat', '0011_auto_20190508_0153', '2025-08-04 21:07:04.994493+00');
INSERT INTO public.django_migrations VALUES (32, 'django_celery_beat', '0012_periodictask_expire_seconds', '2025-08-04 21:07:05.01082+00');
INSERT INTO public.django_migrations VALUES (33, 'django_celery_beat', '0013_auto_20200609_0727', '2025-08-04 21:07:05.03053+00');
INSERT INTO public.django_migrations VALUES (34, 'django_celery_beat', '0014_remove_clockedschedule_enabled', '2025-08-04 21:07:05.040139+00');
INSERT INTO public.django_migrations VALUES (35, 'django_celery_beat', '0015_edit_solarschedule_events_choices', '2025-08-04 21:07:05.049416+00');
INSERT INTO public.django_migrations VALUES (36, 'django_celery_beat', '0016_alter_crontabschedule_timezone', '2025-08-04 21:07:05.064721+00');
INSERT INTO public.django_migrations VALUES (37, 'django_celery_beat', '0017_alter_crontabschedule_month_of_year', '2025-08-04 21:07:05.079107+00');
INSERT INTO public.django_migrations VALUES (38, 'django_celery_beat', '0018_improve_crontab_helptext', '2025-08-04 21:07:05.09513+00');
INSERT INTO public.django_migrations VALUES (39, 'django_celery_beat', '0019_alter_periodictasks_options', '2025-08-04 21:07:05.101702+00');
INSERT INTO public.django_migrations VALUES (40, 'oauth2_provider', '0001_initial', '2025-08-04 21:07:05.824325+00');
INSERT INTO public.django_migrations VALUES (41, 'oauth2_provider', '0002_auto_20190406_1805', '2025-08-04 21:07:05.906817+00');
INSERT INTO public.django_migrations VALUES (42, 'oauth2_provider', '0003_auto_20201211_1314', '2025-08-04 21:07:05.951232+00');
INSERT INTO public.django_migrations VALUES (43, 'oauth2_provider', '0004_auto_20200902_2022', '2025-08-04 21:07:06.500247+00');
INSERT INTO public.django_migrations VALUES (44, 'oauth2_provider', '0005_auto_20211222_2352', '2025-08-04 21:07:07.107885+00');
INSERT INTO public.django_migrations VALUES (45, 'oauth2_provider', '0006_alter_application_client_secret', '2025-08-04 21:07:07.251994+00');
INSERT INTO public.django_migrations VALUES (46, 'oauth2_provider', '0007_application_post_logout_redirect_uris', '2025-08-04 21:07:07.296614+00');
INSERT INTO public.django_migrations VALUES (47, 'oauth2_provider', '0008_alter_accesstoken_token', '2025-08-04 21:07:07.342698+00');
INSERT INTO public.django_migrations VALUES (48, 'oauth2_provider', '0009_add_hash_client_secret', '2025-08-04 21:07:07.397558+00');
INSERT INTO public.django_migrations VALUES (49, 'oauth2_provider', '0010_application_allowed_origins', '2025-08-04 21:07:07.44574+00');
INSERT INTO public.django_migrations VALUES (50, 'oauth2_provider', '0011_refreshtoken_token_family', '2025-08-04 21:07:07.490053+00');
INSERT INTO public.django_migrations VALUES (51, 'oauth2_provider', '0012_add_token_checksum', '2025-08-04 21:07:07.870386+00');
INSERT INTO public.django_migrations VALUES (52, 'sessions', '0001_initial', '2025-08-04 21:07:07.891886+00');


ALTER TABLE public.django_migrations ENABLE TRIGGER ALL;

--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.django_session DISABLE TRIGGER ALL;



ALTER TABLE public.django_session ENABLE TRIGGER ALL;

--
-- Data for Name: enlaces_auto_registro; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.enlaces_auto_registro DISABLE TRIGGER ALL;



ALTER TABLE public.enlaces_auto_registro ENABLE TRIGGER ALL;

--
-- Data for Name: facturas_sii_distribuidas; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.facturas_sii_distribuidas DISABLE TRIGGER ALL;



ALTER TABLE public.facturas_sii_distribuidas ENABLE TRIGGER ALL;

--
-- Data for Name: facturas_sii_por_distribuir; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.facturas_sii_por_distribuir DISABLE TRIGGER ALL;



ALTER TABLE public.facturas_sii_por_distribuir ENABLE TRIGGER ALL;

--
-- Data for Name: facturas_venta_sii_distribuidas; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.facturas_venta_sii_distribuidas DISABLE TRIGGER ALL;



ALTER TABLE public.facturas_venta_sii_distribuidas ENABLE TRIGGER ALL;

--
-- Data for Name: facturas_venta_sii_por_distribuir; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.facturas_venta_sii_por_distribuir DISABLE TRIGGER ALL;



ALTER TABLE public.facturas_venta_sii_por_distribuir ENABLE TRIGGER ALL;

--
-- Data for Name: folio_comercial_fundos; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.folio_comercial_fundos DISABLE TRIGGER ALL;



ALTER TABLE public.folio_comercial_fundos ENABLE TRIGGER ALL;

--
-- Data for Name: folio_comercial_labores; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.folio_comercial_labores DISABLE TRIGGER ALL;



ALTER TABLE public.folio_comercial_labores ENABLE TRIGGER ALL;

--
-- Data for Name: folio_comercial_transportistas; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.folio_comercial_transportistas DISABLE TRIGGER ALL;



ALTER TABLE public.folio_comercial_transportistas ENABLE TRIGGER ALL;

--
-- Data for Name: folio_comercial_vehiculos; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.folio_comercial_vehiculos DISABLE TRIGGER ALL;



ALTER TABLE public.folio_comercial_vehiculos ENABLE TRIGGER ALL;

--
-- Data for Name: haberes; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.haberes DISABLE TRIGGER ALL;



ALTER TABLE public.haberes ENABLE TRIGGER ALL;

--
-- Data for Name: historial_cambios_folio; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.historial_cambios_folio DISABLE TRIGGER ALL;



ALTER TABLE public.historial_cambios_folio ENABLE TRIGGER ALL;

--
-- Data for Name: registro_pagos_efectivo; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.registro_pagos_efectivo DISABLE TRIGGER ALL;



ALTER TABLE public.registro_pagos_efectivo ENABLE TRIGGER ALL;

--
-- Data for Name: registro_pagos_transferencia; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.registro_pagos_transferencia DISABLE TRIGGER ALL;



ALTER TABLE public.registro_pagos_transferencia ENABLE TRIGGER ALL;

--
-- Data for Name: historial_cambios_pago; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.historial_cambios_pago DISABLE TRIGGER ALL;



ALTER TABLE public.historial_cambios_pago ENABLE TRIGGER ALL;

--
-- Data for Name: horarios; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.horarios DISABLE TRIGGER ALL;



ALTER TABLE public.horarios ENABLE TRIGGER ALL;

--
-- Data for Name: horas_extraordinarias; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.horas_extraordinarias DISABLE TRIGGER ALL;



ALTER TABLE public.horas_extraordinarias ENABLE TRIGGER ALL;

--
-- Data for Name: jefes_cuadrilla_trabajadores; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.jefes_cuadrilla_trabajadores DISABLE TRIGGER ALL;



ALTER TABLE public.jefes_cuadrilla_trabajadores ENABLE TRIGGER ALL;

--
-- Data for Name: licencias_medicas; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.licencias_medicas DISABLE TRIGGER ALL;



ALTER TABLE public.licencias_medicas ENABLE TRIGGER ALL;

--
-- Data for Name: meses_cerrados; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.meses_cerrados DISABLE TRIGGER ALL;



ALTER TABLE public.meses_cerrados ENABLE TRIGGER ALL;

--
-- Data for Name: modulos_movil; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.modulos_movil DISABLE TRIGGER ALL;

INSERT INTO public.modulos_movil VALUES (1, 'GESTION TRABAJADORES', 1);
INSERT INTO public.modulos_movil VALUES (2, 'MANO DE OBRA', 1);
INSERT INTO public.modulos_movil VALUES (3, 'COSECHA', 1);


ALTER TABLE public.modulos_movil ENABLE TRIGGER ALL;

--
-- Data for Name: modulos_web; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.modulos_web DISABLE TRIGGER ALL;

INSERT INTO public.modulos_web VALUES (1, 'ADMINISTRACION', 2);
INSERT INTO public.modulos_web VALUES (2, 'RECURSOS HUMANOS', 2);
INSERT INTO public.modulos_web VALUES (3, 'CLIENTES', 2);
INSERT INTO public.modulos_web VALUES (4, 'COMERCIAL', 2);
INSERT INTO public.modulos_web VALUES (5, 'TRANSPORTE', 2);
INSERT INTO public.modulos_web VALUES (6, 'PAGOS', 2);
INSERT INTO public.modulos_web VALUES (7, 'INFORMES', 2);
INSERT INTO public.modulos_web VALUES (8, 'LEYES SOCIALES', 2);
INSERT INTO public.modulos_web VALUES (9, 'COSTOS', 2);
INSERT INTO public.modulos_web VALUES (10, 'TESORERIA', 2);
INSERT INTO public.modulos_web VALUES (11, 'ADMINISTRACION', 1);
INSERT INTO public.modulos_web VALUES (12, 'RECURSOS HUMANOS', 1);
INSERT INTO public.modulos_web VALUES (13, 'CLIENTES', 1);
INSERT INTO public.modulos_web VALUES (14, 'COMERCIAL', 1);
INSERT INTO public.modulos_web VALUES (15, 'TRANSPORTE', 1);
INSERT INTO public.modulos_web VALUES (16, 'PAGOS', 1);
INSERT INTO public.modulos_web VALUES (17, 'INFORMES', 1);
INSERT INTO public.modulos_web VALUES (18, 'LEYES SOCIALES', 1);
INSERT INTO public.modulos_web VALUES (19, 'COSTOS', 1);
INSERT INTO public.modulos_web VALUES (20, 'TESORERIA', 1);


ALTER TABLE public.modulos_web ENABLE TRIGGER ALL;

--
-- Data for Name: oauth2_provider_application; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.oauth2_provider_application DISABLE TRIGGER ALL;



ALTER TABLE public.oauth2_provider_application ENABLE TRIGGER ALL;

--
-- Data for Name: oauth2_provider_idtoken; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.oauth2_provider_idtoken DISABLE TRIGGER ALL;



ALTER TABLE public.oauth2_provider_idtoken ENABLE TRIGGER ALL;

--
-- Data for Name: oauth2_provider_accesstoken; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.oauth2_provider_accesstoken DISABLE TRIGGER ALL;



ALTER TABLE public.oauth2_provider_accesstoken ENABLE TRIGGER ALL;

--
-- Data for Name: oauth2_provider_grant; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.oauth2_provider_grant DISABLE TRIGGER ALL;



ALTER TABLE public.oauth2_provider_grant ENABLE TRIGGER ALL;

--
-- Data for Name: oauth2_provider_refreshtoken; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.oauth2_provider_refreshtoken DISABLE TRIGGER ALL;



ALTER TABLE public.oauth2_provider_refreshtoken ENABLE TRIGGER ALL;

--
-- Data for Name: perfiles_modulos_movil; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.perfiles_modulos_movil DISABLE TRIGGER ALL;



ALTER TABLE public.perfiles_modulos_movil ENABLE TRIGGER ALL;

--
-- Data for Name: perfiles_modulos_web; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.perfiles_modulos_web DISABLE TRIGGER ALL;

INSERT INTO public.perfiles_modulos_web VALUES (1, 4, 1);
INSERT INTO public.perfiles_modulos_web VALUES (2, 4, 2);
INSERT INTO public.perfiles_modulos_web VALUES (3, 4, 3);
INSERT INTO public.perfiles_modulos_web VALUES (4, 4, 4);
INSERT INTO public.perfiles_modulos_web VALUES (5, 4, 5);
INSERT INTO public.perfiles_modulos_web VALUES (6, 4, 6);
INSERT INTO public.perfiles_modulos_web VALUES (7, 4, 7);
INSERT INTO public.perfiles_modulos_web VALUES (8, 4, 8);
INSERT INTO public.perfiles_modulos_web VALUES (9, 4, 9);
INSERT INTO public.perfiles_modulos_web VALUES (10, 4, 10);
INSERT INTO public.perfiles_modulos_web VALUES (11, 3, 11);
INSERT INTO public.perfiles_modulos_web VALUES (12, 3, 12);
INSERT INTO public.perfiles_modulos_web VALUES (13, 3, 13);
INSERT INTO public.perfiles_modulos_web VALUES (14, 3, 14);
INSERT INTO public.perfiles_modulos_web VALUES (15, 3, 15);
INSERT INTO public.perfiles_modulos_web VALUES (16, 3, 16);
INSERT INTO public.perfiles_modulos_web VALUES (17, 3, 17);
INSERT INTO public.perfiles_modulos_web VALUES (18, 3, 18);
INSERT INTO public.perfiles_modulos_web VALUES (19, 3, 19);
INSERT INTO public.perfiles_modulos_web VALUES (20, 3, 20);
INSERT INTO public.perfiles_modulos_web VALUES (21, 5, 1);
INSERT INTO public.perfiles_modulos_web VALUES (22, 5, 2);
INSERT INTO public.perfiles_modulos_web VALUES (23, 5, 3);
INSERT INTO public.perfiles_modulos_web VALUES (24, 5, 4);
INSERT INTO public.perfiles_modulos_web VALUES (25, 5, 5);
INSERT INTO public.perfiles_modulos_web VALUES (26, 5, 6);
INSERT INTO public.perfiles_modulos_web VALUES (27, 5, 7);
INSERT INTO public.perfiles_modulos_web VALUES (28, 5, 8);
INSERT INTO public.perfiles_modulos_web VALUES (29, 5, 9);
INSERT INTO public.perfiles_modulos_web VALUES (30, 5, 10);
INSERT INTO public.perfiles_modulos_web VALUES (31, 6, 1);
INSERT INTO public.perfiles_modulos_web VALUES (32, 6, 2);
INSERT INTO public.perfiles_modulos_web VALUES (33, 6, 5);
INSERT INTO public.perfiles_modulos_web VALUES (34, 6, 6);
INSERT INTO public.perfiles_modulos_web VALUES (35, 6, 7);
INSERT INTO public.perfiles_modulos_web VALUES (36, 6, 8);
INSERT INTO public.perfiles_modulos_web VALUES (37, 6, 9);
INSERT INTO public.perfiles_modulos_web VALUES (38, 6, 10);
INSERT INTO public.perfiles_modulos_web VALUES (39, 7, 2);
INSERT INTO public.perfiles_modulos_web VALUES (40, 7, 7);


ALTER TABLE public.perfiles_modulos_web ENABLE TRIGGER ALL;

--
-- Data for Name: submodulos_movil; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.submodulos_movil DISABLE TRIGGER ALL;

INSERT INTO public.submodulos_movil VALUES (1, 'ENROLLAR TRABAJADOR', 1, 1);
INSERT INTO public.submodulos_movil VALUES (2, 'ASIGNAR QR', 1, 1);
INSERT INTO public.submodulos_movil VALUES (5, 'INGRESAR RENDIMIENTO PERSONA MANO OBRA', 1, 2);
INSERT INTO public.submodulos_movil VALUES (6, 'INFORMES PERSONA MANO OBRA', 1, 2);
INSERT INTO public.submodulos_movil VALUES (7, 'INGRESAR RENDIMIENTO CUADRILLA MANO OBRA', 1, 2);
INSERT INTO public.submodulos_movil VALUES (8, 'INFORMES CUADRILLA MANO OBRA', 1, 2);
INSERT INTO public.submodulos_movil VALUES (9, 'INGRESAR RENDIMIENTO PERSONA COSECHA', 1, 3);
INSERT INTO public.submodulos_movil VALUES (10, 'INFORMES PERSONA COSECHA', 1, 3);
INSERT INTO public.submodulos_movil VALUES (11, 'INGRESAR RENDIMIENTO CUADRILLA COSECHA', 1, 3);
INSERT INTO public.submodulos_movil VALUES (12, 'INFORMES CUADRILLA COSECHA', 1, 3);


ALTER TABLE public.submodulos_movil ENABLE TRIGGER ALL;

--
-- Data for Name: perfiles_submodulos_movil; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.perfiles_submodulos_movil DISABLE TRIGGER ALL;



ALTER TABLE public.perfiles_submodulos_movil ENABLE TRIGGER ALL;

--
-- Data for Name: submodulos_web; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.submodulos_web DISABLE TRIGGER ALL;

INSERT INTO public.submodulos_web VALUES (1, 'PERSONAL', 2, 1);
INSERT INTO public.submodulos_web VALUES (2, 'PERFILES', 2, 1);
INSERT INTO public.submodulos_web VALUES (3, 'USUARIOS', 2, 1);
INSERT INTO public.submodulos_web VALUES (4, 'AREAS/CARGOS ADMINISTRACION', 2, 1);
INSERT INTO public.submodulos_web VALUES (5, 'PARAMETROS ADMINISTRACION', 2, 1);
INSERT INTO public.submodulos_web VALUES (6, 'CONTRATACION PERSONAL', 2, 2);
INSERT INTO public.submodulos_web VALUES (7, 'CREAR CONTRATO', 2, 2);
INSERT INTO public.submodulos_web VALUES (8, 'CONTRATOS FIRMADOS', 2, 2);
INSERT INTO public.submodulos_web VALUES (9, 'PRODUCCION TRABAJADOR', 2, 2);
INSERT INTO public.submodulos_web VALUES (10, 'PARAMETROS RECURSOS HUMANOS', 2, 2);
INSERT INTO public.submodulos_web VALUES (11, 'GENERAR CODIGOS QR', 2, 2);
INSERT INTO public.submodulos_web VALUES (12, 'POSICIONAR VARIABLE CONTRATO', 2, 2);
INSERT INTO public.submodulos_web VALUES (13, 'LIBRO DE REMUNERACIONES ELECTRONICO', 2, 2);
INSERT INTO public.submodulos_web VALUES (14, 'ADMINISTRAR CLIENTES', 2, 3);
INSERT INTO public.submodulos_web VALUES (15, 'AREA/CARGOS CLIENTES', 2, 3);
INSERT INTO public.submodulos_web VALUES (16, 'CONTACTOS', 2, 3);
INSERT INTO public.submodulos_web VALUES (17, 'ACUERDO COMERCIAL', 2, 4);
INSERT INTO public.submodulos_web VALUES (18, 'PARAMETROS COMERCIAL', 2, 4);
INSERT INTO public.submodulos_web VALUES (19, 'TRANSPORTISTAS', 2, 5);
INSERT INTO public.submodulos_web VALUES (20, 'VEHICULOS', 2, 5);
INSERT INTO public.submodulos_web VALUES (21, 'CHOFERES', 2, 5);
INSERT INTO public.submodulos_web VALUES (22, 'TRAMOS', 2, 5);
INSERT INTO public.submodulos_web VALUES (23, 'ACUERDO TRANSPORTES', 2, 5);
INSERT INTO public.submodulos_web VALUES (24, 'PAGO TRANSPORTISTA', 2, 5);
INSERT INTO public.submodulos_web VALUES (25, 'PROFORMA', 2, 5);
INSERT INTO public.submodulos_web VALUES (26, 'TRANSFERENCIA', 2, 6);
INSERT INTO public.submodulos_web VALUES (27, 'EFECTIVO', 2, 6);
INSERT INTO public.submodulos_web VALUES (28, 'PAGOS REALIZADOS', 2, 6);
INSERT INTO public.submodulos_web VALUES (29, 'REPROCESAR PAGO', 2, 6);
INSERT INTO public.submodulos_web VALUES (30, 'INFORME RENDIMIENTO', 2, 7);
INSERT INTO public.submodulos_web VALUES (31, 'INFORME PAGO', 2, 7);
INSERT INTO public.submodulos_web VALUES (32, 'INFORME TRANSPORTISTA', 2, 7);
INSERT INTO public.submodulos_web VALUES (33, 'INFORME DIAS TRABAJADOS', 2, 8);
INSERT INTO public.submodulos_web VALUES (34, 'HABERES DESCUENTOS', 2, 8);
INSERT INTO public.submodulos_web VALUES (35, 'ARCHIVO PREVIRED', 2, 8);
INSERT INTO public.submodulos_web VALUES (36, 'LIQUIDACIONES', 2, 8);
INSERT INTO public.submodulos_web VALUES (37, 'ASIGNACION HABERES', 2, 8);
INSERT INTO public.submodulos_web VALUES (38, 'ASIGNACION DESCUENTOS', 2, 8);
INSERT INTO public.submodulos_web VALUES (39, 'FACTURAS COMPRA AUTOMATICO', 2, 9);
INSERT INTO public.submodulos_web VALUES (40, 'FACTURAS COMPRA DISTRIBUIDAS', 2, 9);
INSERT INTO public.submodulos_web VALUES (41, 'PARAMETROS FACTURA COMPRA', 2, 9);
INSERT INTO public.submodulos_web VALUES (42, 'FACTURAS VENTA AUTOMATICO', 2, 9);
INSERT INTO public.submodulos_web VALUES (43, 'FACTURAS VENTA DISTRIBUIDAS', 2, 9);
INSERT INTO public.submodulos_web VALUES (44, 'PARAMETROS FACTURA VENTA', 2, 9);
INSERT INTO public.submodulos_web VALUES (45, 'CUENTAS', 2, 9);
INSERT INTO public.submodulos_web VALUES (46, 'PAGOS INGRESOS', 2, 10);
INSERT INTO public.submodulos_web VALUES (47, 'PAGOS EGRESOS', 2, 10);
INSERT INTO public.submodulos_web VALUES (48, 'HISTORIAL PAGOS', 2, 10);
INSERT INTO public.submodulos_web VALUES (49, 'PERSONAL', 1, 11);
INSERT INTO public.submodulos_web VALUES (50, 'PERFILES', 1, 11);
INSERT INTO public.submodulos_web VALUES (51, 'USUARIOS', 1, 11);
INSERT INTO public.submodulos_web VALUES (52, 'AREAS/CARGOS ADMINISTRACION', 1, 11);
INSERT INTO public.submodulos_web VALUES (53, 'PARAMETROS ADMINISTRACION', 1, 11);
INSERT INTO public.submodulos_web VALUES (54, 'CONTRATACION PERSONAL', 1, 12);
INSERT INTO public.submodulos_web VALUES (55, 'CREAR CONTRATO', 1, 12);
INSERT INTO public.submodulos_web VALUES (56, 'CONTRATOS FIRMADOS', 1, 12);
INSERT INTO public.submodulos_web VALUES (57, 'PRODUCCION TRABAJADOR', 1, 12);
INSERT INTO public.submodulos_web VALUES (58, 'PARAMETROS RECURSOS HUMANOS', 1, 12);
INSERT INTO public.submodulos_web VALUES (59, 'GENERAR CODIGOS QR', 1, 12);
INSERT INTO public.submodulos_web VALUES (60, 'POSICIONAR VARIABLE CONTRATO', 1, 12);
INSERT INTO public.submodulos_web VALUES (61, 'LIBRO DE REMUNERACIONES ELECTRONICO', 1, 12);
INSERT INTO public.submodulos_web VALUES (62, 'ADMINISTRAR CLIENTES', 1, 13);
INSERT INTO public.submodulos_web VALUES (63, 'AREA/CARGOS CLIENTES', 1, 13);
INSERT INTO public.submodulos_web VALUES (64, 'CONTACTOS', 1, 13);
INSERT INTO public.submodulos_web VALUES (65, 'ACUERDO COMERCIAL', 1, 14);
INSERT INTO public.submodulos_web VALUES (66, 'PARAMETROS COMERCIAL', 1, 14);
INSERT INTO public.submodulos_web VALUES (67, 'TRANSPORTISTAS', 1, 15);
INSERT INTO public.submodulos_web VALUES (68, 'VEHICULOS', 1, 15);
INSERT INTO public.submodulos_web VALUES (69, 'CHOFERES', 1, 15);
INSERT INTO public.submodulos_web VALUES (70, 'TRAMOS', 1, 15);
INSERT INTO public.submodulos_web VALUES (71, 'ACUERDO TRANSPORTES', 1, 15);
INSERT INTO public.submodulos_web VALUES (72, 'PAGO TRANSPORTISTA', 1, 15);
INSERT INTO public.submodulos_web VALUES (73, 'PROFORMA', 1, 15);
INSERT INTO public.submodulos_web VALUES (74, 'TRANSFERENCIA', 1, 16);
INSERT INTO public.submodulos_web VALUES (75, 'EFECTIVO', 1, 16);
INSERT INTO public.submodulos_web VALUES (76, 'PAGOS REALIZADOS', 1, 16);
INSERT INTO public.submodulos_web VALUES (77, 'REPROCESAR PAGO', 1, 16);
INSERT INTO public.submodulos_web VALUES (78, 'INFORME RENDIMIENTO', 1, 17);
INSERT INTO public.submodulos_web VALUES (79, 'INFORME PAGO', 1, 17);
INSERT INTO public.submodulos_web VALUES (80, 'INFORME TRANSPORTISTA', 1, 17);
INSERT INTO public.submodulos_web VALUES (81, 'INFORME DIAS TRABAJADOS', 1, 18);
INSERT INTO public.submodulos_web VALUES (82, 'HABERES DESCUENTOS', 1, 18);
INSERT INTO public.submodulos_web VALUES (83, 'ARCHIVO PREVIRED', 1, 18);
INSERT INTO public.submodulos_web VALUES (84, 'LIQUIDACIONES', 1, 18);
INSERT INTO public.submodulos_web VALUES (85, 'ASIGNACION HABERES', 1, 18);
INSERT INTO public.submodulos_web VALUES (86, 'ASIGNACION DESCUENTOS', 1, 18);
INSERT INTO public.submodulos_web VALUES (87, 'FACTURAS COMPRA AUTOMATICO', 1, 19);
INSERT INTO public.submodulos_web VALUES (88, 'FACTURAS COMPRA DISTRIBUIDAS', 1, 19);
INSERT INTO public.submodulos_web VALUES (89, 'PARAMETROS FACTURA COMPRA', 1, 19);
INSERT INTO public.submodulos_web VALUES (90, 'FACTURAS VENTA AUTOMATICO', 1, 19);
INSERT INTO public.submodulos_web VALUES (91, 'FACTURAS VENTA DISTRIBUIDAS', 1, 19);
INSERT INTO public.submodulos_web VALUES (92, 'PARAMETROS FACTURA VENTA', 1, 19);
INSERT INTO public.submodulos_web VALUES (93, 'CUENTAS', 1, 19);
INSERT INTO public.submodulos_web VALUES (94, 'PAGOS INGRESOS', 1, 20);
INSERT INTO public.submodulos_web VALUES (95, 'PAGOS EGRESOS', 1, 20);
INSERT INTO public.submodulos_web VALUES (96, 'HISTORIAL PAGOS', 1, 20);


ALTER TABLE public.submodulos_web ENABLE TRIGGER ALL;

--
-- Data for Name: perfiles_submodulos_web; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.perfiles_submodulos_web DISABLE TRIGGER ALL;

INSERT INTO public.perfiles_submodulos_web VALUES (1, 4, 1);
INSERT INTO public.perfiles_submodulos_web VALUES (2, 4, 2);
INSERT INTO public.perfiles_submodulos_web VALUES (3, 4, 3);
INSERT INTO public.perfiles_submodulos_web VALUES (4, 4, 4);
INSERT INTO public.perfiles_submodulos_web VALUES (5, 4, 5);
INSERT INTO public.perfiles_submodulos_web VALUES (6, 4, 6);
INSERT INTO public.perfiles_submodulos_web VALUES (7, 4, 7);
INSERT INTO public.perfiles_submodulos_web VALUES (8, 4, 8);
INSERT INTO public.perfiles_submodulos_web VALUES (9, 4, 9);
INSERT INTO public.perfiles_submodulos_web VALUES (10, 4, 10);
INSERT INTO public.perfiles_submodulos_web VALUES (11, 4, 11);
INSERT INTO public.perfiles_submodulos_web VALUES (12, 4, 12);
INSERT INTO public.perfiles_submodulos_web VALUES (13, 4, 13);
INSERT INTO public.perfiles_submodulos_web VALUES (14, 4, 14);
INSERT INTO public.perfiles_submodulos_web VALUES (15, 4, 15);
INSERT INTO public.perfiles_submodulos_web VALUES (16, 4, 16);
INSERT INTO public.perfiles_submodulos_web VALUES (17, 4, 17);
INSERT INTO public.perfiles_submodulos_web VALUES (18, 4, 18);
INSERT INTO public.perfiles_submodulos_web VALUES (19, 4, 19);
INSERT INTO public.perfiles_submodulos_web VALUES (20, 4, 20);
INSERT INTO public.perfiles_submodulos_web VALUES (21, 4, 21);
INSERT INTO public.perfiles_submodulos_web VALUES (22, 4, 22);
INSERT INTO public.perfiles_submodulos_web VALUES (23, 4, 23);
INSERT INTO public.perfiles_submodulos_web VALUES (24, 4, 24);
INSERT INTO public.perfiles_submodulos_web VALUES (25, 4, 25);
INSERT INTO public.perfiles_submodulos_web VALUES (26, 4, 26);
INSERT INTO public.perfiles_submodulos_web VALUES (27, 4, 27);
INSERT INTO public.perfiles_submodulos_web VALUES (28, 4, 28);
INSERT INTO public.perfiles_submodulos_web VALUES (29, 4, 29);
INSERT INTO public.perfiles_submodulos_web VALUES (30, 4, 30);
INSERT INTO public.perfiles_submodulos_web VALUES (31, 4, 31);
INSERT INTO public.perfiles_submodulos_web VALUES (32, 4, 32);
INSERT INTO public.perfiles_submodulos_web VALUES (33, 4, 33);
INSERT INTO public.perfiles_submodulos_web VALUES (34, 4, 34);
INSERT INTO public.perfiles_submodulos_web VALUES (35, 4, 35);
INSERT INTO public.perfiles_submodulos_web VALUES (36, 4, 36);
INSERT INTO public.perfiles_submodulos_web VALUES (37, 4, 37);
INSERT INTO public.perfiles_submodulos_web VALUES (38, 4, 38);
INSERT INTO public.perfiles_submodulos_web VALUES (39, 4, 39);
INSERT INTO public.perfiles_submodulos_web VALUES (40, 4, 40);
INSERT INTO public.perfiles_submodulos_web VALUES (41, 4, 41);
INSERT INTO public.perfiles_submodulos_web VALUES (42, 4, 42);
INSERT INTO public.perfiles_submodulos_web VALUES (43, 4, 43);
INSERT INTO public.perfiles_submodulos_web VALUES (44, 4, 44);
INSERT INTO public.perfiles_submodulos_web VALUES (45, 4, 45);
INSERT INTO public.perfiles_submodulos_web VALUES (46, 4, 46);
INSERT INTO public.perfiles_submodulos_web VALUES (47, 4, 47);
INSERT INTO public.perfiles_submodulos_web VALUES (48, 4, 48);
INSERT INTO public.perfiles_submodulos_web VALUES (49, 3, 49);
INSERT INTO public.perfiles_submodulos_web VALUES (50, 3, 50);
INSERT INTO public.perfiles_submodulos_web VALUES (51, 3, 51);
INSERT INTO public.perfiles_submodulos_web VALUES (52, 3, 52);
INSERT INTO public.perfiles_submodulos_web VALUES (53, 3, 53);
INSERT INTO public.perfiles_submodulos_web VALUES (54, 3, 54);
INSERT INTO public.perfiles_submodulos_web VALUES (55, 3, 55);
INSERT INTO public.perfiles_submodulos_web VALUES (56, 3, 56);
INSERT INTO public.perfiles_submodulos_web VALUES (57, 3, 57);
INSERT INTO public.perfiles_submodulos_web VALUES (58, 3, 58);
INSERT INTO public.perfiles_submodulos_web VALUES (59, 3, 59);
INSERT INTO public.perfiles_submodulos_web VALUES (60, 3, 60);
INSERT INTO public.perfiles_submodulos_web VALUES (61, 3, 61);
INSERT INTO public.perfiles_submodulos_web VALUES (62, 3, 62);
INSERT INTO public.perfiles_submodulos_web VALUES (63, 3, 63);
INSERT INTO public.perfiles_submodulos_web VALUES (64, 3, 64);
INSERT INTO public.perfiles_submodulos_web VALUES (65, 3, 65);
INSERT INTO public.perfiles_submodulos_web VALUES (66, 3, 66);
INSERT INTO public.perfiles_submodulos_web VALUES (67, 3, 67);
INSERT INTO public.perfiles_submodulos_web VALUES (68, 3, 68);
INSERT INTO public.perfiles_submodulos_web VALUES (69, 3, 69);
INSERT INTO public.perfiles_submodulos_web VALUES (70, 3, 70);
INSERT INTO public.perfiles_submodulos_web VALUES (71, 3, 71);
INSERT INTO public.perfiles_submodulos_web VALUES (72, 3, 72);
INSERT INTO public.perfiles_submodulos_web VALUES (73, 3, 73);
INSERT INTO public.perfiles_submodulos_web VALUES (74, 3, 74);
INSERT INTO public.perfiles_submodulos_web VALUES (75, 3, 75);
INSERT INTO public.perfiles_submodulos_web VALUES (76, 3, 76);
INSERT INTO public.perfiles_submodulos_web VALUES (77, 3, 77);
INSERT INTO public.perfiles_submodulos_web VALUES (78, 3, 78);
INSERT INTO public.perfiles_submodulos_web VALUES (79, 3, 79);
INSERT INTO public.perfiles_submodulos_web VALUES (80, 3, 80);
INSERT INTO public.perfiles_submodulos_web VALUES (81, 3, 81);
INSERT INTO public.perfiles_submodulos_web VALUES (82, 3, 82);
INSERT INTO public.perfiles_submodulos_web VALUES (83, 3, 83);
INSERT INTO public.perfiles_submodulos_web VALUES (84, 3, 84);
INSERT INTO public.perfiles_submodulos_web VALUES (85, 3, 85);
INSERT INTO public.perfiles_submodulos_web VALUES (86, 3, 86);
INSERT INTO public.perfiles_submodulos_web VALUES (87, 3, 87);
INSERT INTO public.perfiles_submodulos_web VALUES (88, 3, 88);
INSERT INTO public.perfiles_submodulos_web VALUES (89, 3, 89);
INSERT INTO public.perfiles_submodulos_web VALUES (90, 3, 90);
INSERT INTO public.perfiles_submodulos_web VALUES (91, 3, 91);
INSERT INTO public.perfiles_submodulos_web VALUES (92, 3, 92);
INSERT INTO public.perfiles_submodulos_web VALUES (93, 3, 93);
INSERT INTO public.perfiles_submodulos_web VALUES (94, 3, 94);
INSERT INTO public.perfiles_submodulos_web VALUES (95, 3, 95);
INSERT INTO public.perfiles_submodulos_web VALUES (96, 3, 96);
INSERT INTO public.perfiles_submodulos_web VALUES (97, 5, 1);
INSERT INTO public.perfiles_submodulos_web VALUES (98, 5, 2);
INSERT INTO public.perfiles_submodulos_web VALUES (99, 5, 3);
INSERT INTO public.perfiles_submodulos_web VALUES (100, 5, 4);
INSERT INTO public.perfiles_submodulos_web VALUES (101, 5, 5);
INSERT INTO public.perfiles_submodulos_web VALUES (102, 5, 6);
INSERT INTO public.perfiles_submodulos_web VALUES (103, 5, 7);
INSERT INTO public.perfiles_submodulos_web VALUES (104, 5, 8);
INSERT INTO public.perfiles_submodulos_web VALUES (105, 5, 9);
INSERT INTO public.perfiles_submodulos_web VALUES (106, 5, 10);
INSERT INTO public.perfiles_submodulos_web VALUES (107, 5, 11);
INSERT INTO public.perfiles_submodulos_web VALUES (108, 5, 12);
INSERT INTO public.perfiles_submodulos_web VALUES (109, 5, 13);
INSERT INTO public.perfiles_submodulos_web VALUES (110, 5, 14);
INSERT INTO public.perfiles_submodulos_web VALUES (111, 5, 15);
INSERT INTO public.perfiles_submodulos_web VALUES (112, 5, 16);
INSERT INTO public.perfiles_submodulos_web VALUES (113, 5, 17);
INSERT INTO public.perfiles_submodulos_web VALUES (114, 5, 18);
INSERT INTO public.perfiles_submodulos_web VALUES (115, 5, 19);
INSERT INTO public.perfiles_submodulos_web VALUES (116, 5, 20);
INSERT INTO public.perfiles_submodulos_web VALUES (117, 5, 21);
INSERT INTO public.perfiles_submodulos_web VALUES (118, 5, 22);
INSERT INTO public.perfiles_submodulos_web VALUES (119, 5, 23);
INSERT INTO public.perfiles_submodulos_web VALUES (120, 5, 24);
INSERT INTO public.perfiles_submodulos_web VALUES (121, 5, 25);
INSERT INTO public.perfiles_submodulos_web VALUES (122, 5, 26);
INSERT INTO public.perfiles_submodulos_web VALUES (123, 5, 27);
INSERT INTO public.perfiles_submodulos_web VALUES (124, 5, 28);
INSERT INTO public.perfiles_submodulos_web VALUES (125, 5, 29);
INSERT INTO public.perfiles_submodulos_web VALUES (126, 5, 30);
INSERT INTO public.perfiles_submodulos_web VALUES (127, 5, 31);
INSERT INTO public.perfiles_submodulos_web VALUES (128, 5, 32);
INSERT INTO public.perfiles_submodulos_web VALUES (129, 5, 33);
INSERT INTO public.perfiles_submodulos_web VALUES (130, 5, 34);
INSERT INTO public.perfiles_submodulos_web VALUES (131, 5, 35);
INSERT INTO public.perfiles_submodulos_web VALUES (132, 5, 36);
INSERT INTO public.perfiles_submodulos_web VALUES (133, 5, 37);
INSERT INTO public.perfiles_submodulos_web VALUES (134, 5, 38);
INSERT INTO public.perfiles_submodulos_web VALUES (135, 5, 39);
INSERT INTO public.perfiles_submodulos_web VALUES (136, 5, 40);
INSERT INTO public.perfiles_submodulos_web VALUES (137, 5, 41);
INSERT INTO public.perfiles_submodulos_web VALUES (138, 5, 42);
INSERT INTO public.perfiles_submodulos_web VALUES (139, 5, 43);
INSERT INTO public.perfiles_submodulos_web VALUES (140, 5, 44);
INSERT INTO public.perfiles_submodulos_web VALUES (141, 5, 45);
INSERT INTO public.perfiles_submodulos_web VALUES (142, 5, 46);
INSERT INTO public.perfiles_submodulos_web VALUES (143, 5, 47);
INSERT INTO public.perfiles_submodulos_web VALUES (144, 5, 48);
INSERT INTO public.perfiles_submodulos_web VALUES (145, 6, 3);
INSERT INTO public.perfiles_submodulos_web VALUES (146, 6, 6);
INSERT INTO public.perfiles_submodulos_web VALUES (147, 6, 7);
INSERT INTO public.perfiles_submodulos_web VALUES (148, 6, 8);
INSERT INTO public.perfiles_submodulos_web VALUES (149, 6, 9);
INSERT INTO public.perfiles_submodulos_web VALUES (150, 6, 10);
INSERT INTO public.perfiles_submodulos_web VALUES (151, 6, 11);
INSERT INTO public.perfiles_submodulos_web VALUES (152, 6, 12);
INSERT INTO public.perfiles_submodulos_web VALUES (153, 6, 13);
INSERT INTO public.perfiles_submodulos_web VALUES (154, 6, 20);
INSERT INTO public.perfiles_submodulos_web VALUES (155, 6, 21);
INSERT INTO public.perfiles_submodulos_web VALUES (156, 6, 22);
INSERT INTO public.perfiles_submodulos_web VALUES (157, 6, 23);
INSERT INTO public.perfiles_submodulos_web VALUES (158, 6, 24);
INSERT INTO public.perfiles_submodulos_web VALUES (159, 6, 25);
INSERT INTO public.perfiles_submodulos_web VALUES (160, 6, 26);
INSERT INTO public.perfiles_submodulos_web VALUES (161, 6, 27);
INSERT INTO public.perfiles_submodulos_web VALUES (162, 6, 28);
INSERT INTO public.perfiles_submodulos_web VALUES (163, 6, 29);
INSERT INTO public.perfiles_submodulos_web VALUES (164, 6, 30);
INSERT INTO public.perfiles_submodulos_web VALUES (165, 6, 31);
INSERT INTO public.perfiles_submodulos_web VALUES (166, 6, 32);
INSERT INTO public.perfiles_submodulos_web VALUES (167, 6, 33);
INSERT INTO public.perfiles_submodulos_web VALUES (168, 6, 34);
INSERT INTO public.perfiles_submodulos_web VALUES (169, 6, 35);
INSERT INTO public.perfiles_submodulos_web VALUES (170, 6, 36);
INSERT INTO public.perfiles_submodulos_web VALUES (171, 6, 37);
INSERT INTO public.perfiles_submodulos_web VALUES (172, 6, 38);
INSERT INTO public.perfiles_submodulos_web VALUES (173, 6, 39);
INSERT INTO public.perfiles_submodulos_web VALUES (174, 6, 40);
INSERT INTO public.perfiles_submodulos_web VALUES (175, 6, 41);
INSERT INTO public.perfiles_submodulos_web VALUES (176, 6, 42);
INSERT INTO public.perfiles_submodulos_web VALUES (177, 6, 43);
INSERT INTO public.perfiles_submodulos_web VALUES (178, 6, 44);
INSERT INTO public.perfiles_submodulos_web VALUES (179, 6, 45);
INSERT INTO public.perfiles_submodulos_web VALUES (180, 6, 46);
INSERT INTO public.perfiles_submodulos_web VALUES (181, 6, 47);
INSERT INTO public.perfiles_submodulos_web VALUES (182, 6, 48);
INSERT INTO public.perfiles_submodulos_web VALUES (183, 7, 32);
INSERT INTO public.perfiles_submodulos_web VALUES (184, 7, 6);
INSERT INTO public.perfiles_submodulos_web VALUES (185, 7, 7);
INSERT INTO public.perfiles_submodulos_web VALUES (186, 7, 8);
INSERT INTO public.perfiles_submodulos_web VALUES (187, 7, 9);
INSERT INTO public.perfiles_submodulos_web VALUES (188, 7, 10);
INSERT INTO public.perfiles_submodulos_web VALUES (189, 7, 11);
INSERT INTO public.perfiles_submodulos_web VALUES (190, 7, 12);
INSERT INTO public.perfiles_submodulos_web VALUES (191, 7, 13);
INSERT INTO public.perfiles_submodulos_web VALUES (192, 7, 30);
INSERT INTO public.perfiles_submodulos_web VALUES (193, 7, 31);


ALTER TABLE public.perfiles_submodulos_web ENABLE TRIGGER ALL;

--
-- Data for Name: produccion; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.produccion DISABLE TRIGGER ALL;



ALTER TABLE public.produccion ENABLE TRIGGER ALL;

--
-- Data for Name: proformas_transportista; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.proformas_transportista DISABLE TRIGGER ALL;



ALTER TABLE public.proformas_transportista ENABLE TRIGGER ALL;

--
-- Data for Name: registro_egreso; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.registro_egreso DISABLE TRIGGER ALL;



ALTER TABLE public.registro_egreso ENABLE TRIGGER ALL;

--
-- Data for Name: registro_ingreso; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.registro_ingreso DISABLE TRIGGER ALL;



ALTER TABLE public.registro_ingreso ENABLE TRIGGER ALL;

--
-- Data for Name: registro_pagos_efectivo_historial_cambios; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.registro_pagos_efectivo_historial_cambios DISABLE TRIGGER ALL;



ALTER TABLE public.registro_pagos_efectivo_historial_cambios ENABLE TRIGGER ALL;

--
-- Data for Name: registro_pagos_efectivo_producciones; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.registro_pagos_efectivo_producciones DISABLE TRIGGER ALL;



ALTER TABLE public.registro_pagos_efectivo_producciones ENABLE TRIGGER ALL;

--
-- Data for Name: registro_pagos_transferencia_historial_cambios; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.registro_pagos_transferencia_historial_cambios DISABLE TRIGGER ALL;



ALTER TABLE public.registro_pagos_transferencia_historial_cambios ENABLE TRIGGER ALL;

--
-- Data for Name: registro_pagos_transferencia_producciones; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.registro_pagos_transferencia_producciones DISABLE TRIGGER ALL;



ALTER TABLE public.registro_pagos_transferencia_producciones ENABLE TRIGGER ALL;

--
-- Data for Name: supervisores_trabajadores; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.supervisores_trabajadores DISABLE TRIGGER ALL;



ALTER TABLE public.supervisores_trabajadores ENABLE TRIGGER ALL;

--
-- Data for Name: trabajador_descuento; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.trabajador_descuento DISABLE TRIGGER ALL;



ALTER TABLE public.trabajador_descuento ENABLE TRIGGER ALL;

--
-- Data for Name: trabajador_haber; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.trabajador_haber DISABLE TRIGGER ALL;



ALTER TABLE public.trabajador_haber ENABLE TRIGGER ALL;

--
-- Data for Name: usuarios_empresas_asignadas; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.usuarios_empresas_asignadas DISABLE TRIGGER ALL;



ALTER TABLE public.usuarios_empresas_asignadas ENABLE TRIGGER ALL;

--
-- Data for Name: usuarios_groups; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.usuarios_groups DISABLE TRIGGER ALL;



ALTER TABLE public.usuarios_groups ENABLE TRIGGER ALL;

--
-- Data for Name: usuarios_user_permissions; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.usuarios_user_permissions DISABLE TRIGGER ALL;



ALTER TABLE public.usuarios_user_permissions ENABLE TRIGGER ALL;

--
-- Data for Name: vacaciones; Type: TABLE DATA; Schema: public; Owner: admin_millache
--

ALTER TABLE public.vacaciones DISABLE TRIGGER ALL;



ALTER TABLE public.vacaciones ENABLE TRIGGER ALL;

--
-- Name: afp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.afp_id_seq', 1, true);


--
-- Name: apk_links_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.apk_links_id_seq', 1, false);


--
-- Name: areas_administracion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.areas_administracion_id_seq', 6, true);


--
-- Name: areas_clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.areas_clientes_id_seq', 1, false);


--
-- Name: areas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.areas_id_seq', 1, false);


--
-- Name: asociacion_codigo_qr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.asociacion_codigo_qr_id_seq', 1, false);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 376, true);


--
-- Name: banco_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.banco_id_seq', 1, false);


--
-- Name: calibraciones_pdf_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.calibraciones_pdf_id_seq', 1, false);


--
-- Name: campos_clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.campos_clientes_id_seq', 1, false);


--
-- Name: cargos_admnistracion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.cargos_admnistracion_id_seq', 7, true);


--
-- Name: cargos_clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.cargos_clientes_id_seq', 1, false);


--
-- Name: cargos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.cargos_id_seq', 1, false);


--
-- Name: cartola_movimiento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.cartola_movimiento_id_seq', 1, false);


--
-- Name: casas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.casas_id_seq', 1, false);


--
-- Name: causales_finiquito_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.causales_finiquito_id_seq', 1, false);


--
-- Name: ccaf_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.ccaf_id_seq', 1, false);


--
-- Name: choferes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.choferes_id_seq', 1, false);


--
-- Name: clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.clientes_id_seq', 1, false);


--
-- Name: comunas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.comunas_id_seq', 1, false);


--
-- Name: configuracion_sii_automatica_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.configuracion_sii_automatica_id_seq', 1, false);


--
-- Name: configuracion_sii_automatica_venta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.configuracion_sii_automatica_venta_id_seq', 1, false);


--
-- Name: contactos_clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.contactos_clientes_id_seq', 1, false);


--
-- Name: contratos_trabajadores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.contratos_trabajadores_id_seq', 1, false);


--
-- Name: cuadrillas_trabajadores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.cuadrillas_trabajadores_id_seq', 1, false);


--
-- Name: cuenta_origen_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.cuenta_origen_id_seq', 1, true);


--
-- Name: cuentas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.cuentas_id_seq', 1, false);


--
-- Name: descuentos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.descuentos_id_seq', 1, false);


--
-- Name: detalle_pagos_transportista_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.detalle_pagos_transportista_id_seq', 1, false);


--
-- Name: developer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.developer_id_seq', 1, false);


--
-- Name: dias_trabajados_aprobados_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.dias_trabajados_aprobados_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_celery_beat_clockedschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.django_celery_beat_clockedschedule_id_seq', 1, false);


--
-- Name: django_celery_beat_crontabschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.django_celery_beat_crontabschedule_id_seq', 2, true);


--
-- Name: django_celery_beat_intervalschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.django_celery_beat_intervalschedule_id_seq', 1, false);


--
-- Name: django_celery_beat_periodictask_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.django_celery_beat_periodictask_id_seq', 2, true);


--
-- Name: django_celery_beat_solarschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.django_celery_beat_solarschedule_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 94, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 52, true);


--
-- Name: documentos_variables_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.documentos_variables_id_seq', 1, false);


--
-- Name: empresas_transporte_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.empresas_transporte_id_seq', 1, false);


--
-- Name: enlaces_auto_registro_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.enlaces_auto_registro_id_seq', 1, false);


--
-- Name: estados_discapacidad_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.estados_discapacidad_id_seq', 1, false);


--
-- Name: facturas_sii_distribuidas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.facturas_sii_distribuidas_id_seq', 1, false);


--
-- Name: facturas_sii_por_distribuir_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.facturas_sii_por_distribuir_id_seq', 1, false);


--
-- Name: facturas_venta_sii_distribuidas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.facturas_venta_sii_distribuidas_id_seq', 1, false);


--
-- Name: facturas_venta_sii_por_distribuir_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.facturas_venta_sii_por_distribuir_id_seq', 1, false);


--
-- Name: folio_comercial_fundos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.folio_comercial_fundos_id_seq', 1, false);


--
-- Name: folio_comercial_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.folio_comercial_id_seq', 1, false);


--
-- Name: folio_comercial_labores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.folio_comercial_labores_id_seq', 1, false);


--
-- Name: folio_comercial_transportistas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.folio_comercial_transportistas_id_seq', 1, false);


--
-- Name: folio_comercial_vehiculos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.folio_comercial_vehiculos_id_seq', 1, false);


--
-- Name: folios_transportes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.folios_transportes_id_seq', 1, false);


--
-- Name: haberes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.haberes_id_seq', 1, false);


--
-- Name: historial_cambios_folio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.historial_cambios_folio_id_seq', 1, false);


--
-- Name: historial_cambios_pago_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.historial_cambios_pago_id_seq', 1, false);


--
-- Name: holding_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.holding_id_seq', 2, true);


--
-- Name: horarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.horarios_id_seq', 1, false);


--
-- Name: horas_extraordinarias_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.horas_extraordinarias_id_seq', 1, false);


--
-- Name: ips_regimenes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.ips_regimenes_id_seq', 1, false);


--
-- Name: jefes_cuadrilla_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.jefes_cuadrilla_id_seq', 1, false);


--
-- Name: jefes_cuadrilla_trabajadores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.jefes_cuadrilla_trabajadores_id_seq', 1, false);


--
-- Name: labores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.labores_id_seq', 1, false);


--
-- Name: licencias_medicas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.licencias_medicas_id_seq', 1, false);


--
-- Name: meses_cerrados_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.meses_cerrados_id_seq', 1, false);


--
-- Name: modulos_movil_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.modulos_movil_id_seq', 1, false);


--
-- Name: modulos_web_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.modulos_web_id_seq', 20, true);


--
-- Name: mutualidades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.mutualidades_id_seq', 1, false);


--
-- Name: oauth2_provider_accesstoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.oauth2_provider_accesstoken_id_seq', 1, false);


--
-- Name: oauth2_provider_application_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.oauth2_provider_application_id_seq', 1, false);


--
-- Name: oauth2_provider_grant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.oauth2_provider_grant_id_seq', 1, false);


--
-- Name: oauth2_provider_idtoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.oauth2_provider_idtoken_id_seq', 1, false);


--
-- Name: oauth2_provider_refreshtoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.oauth2_provider_refreshtoken_id_seq', 1, false);


--
-- Name: pagos_transportista_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.pagos_transportista_id_seq', 1, false);


--
-- Name: perfiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.perfiles_id_seq', 7, true);


--
-- Name: perfiles_modulos_movil_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.perfiles_modulos_movil_id_seq', 1, false);


--
-- Name: perfiles_modulos_web_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.perfiles_modulos_web_id_seq', 40, true);


--
-- Name: perfiles_submodulos_movil_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.perfiles_submodulos_movil_id_seq', 1, false);


--
-- Name: perfiles_submodulos_web_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.perfiles_submodulos_web_id_seq', 193, true);


--
-- Name: personal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.personal_id_seq', 7, true);


--
-- Name: produccion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.produccion_id_seq', 1, false);


--
-- Name: proformas_transportista_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.proformas_transportista_id_seq', 1, false);


--
-- Name: regiones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.regiones_id_seq', 1, false);


--
-- Name: registro_egreso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.registro_egreso_id_seq', 1, false);


--
-- Name: registro_ingreso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.registro_ingreso_id_seq', 1, false);


--
-- Name: registro_pagos_efectivo_historial_cambios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.registro_pagos_efectivo_historial_cambios_id_seq', 1, false);


--
-- Name: registro_pagos_efectivo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.registro_pagos_efectivo_id_seq', 1, false);


--
-- Name: registro_pagos_efectivo_producciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.registro_pagos_efectivo_producciones_id_seq', 1, false);


--
-- Name: registro_pagos_transferencia_historial_cambios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.registro_pagos_transferencia_historial_cambios_id_seq', 1, false);


--
-- Name: registro_pagos_transferencia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.registro_pagos_transferencia_id_seq', 1, false);


--
-- Name: registro_pagos_transferencia_producciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.registro_pagos_transferencia_producciones_id_seq', 1, false);


--
-- Name: salud_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.salud_id_seq', 1, true);


--
-- Name: sociedad_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.sociedad_id_seq', 2, true);


--
-- Name: submodulos_movil_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.submodulos_movil_id_seq', 1, false);


--
-- Name: submodulos_web_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.submodulos_web_id_seq', 96, true);


--
-- Name: supervisores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.supervisores_id_seq', 1, false);


--
-- Name: supervisores_trabajadores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.supervisores_trabajadores_id_seq', 1, false);


--
-- Name: tipos_impuesto_renta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.tipos_impuesto_renta_id_seq', 1, false);


--
-- Name: tipos_jornada_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.tipos_jornada_id_seq', 1, false);


--
-- Name: trabajador_descuento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.trabajador_descuento_id_seq', 1, false);


--
-- Name: trabajador_haber_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.trabajador_haber_id_seq', 1, false);


--
-- Name: tramos_transportista_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.tramos_transportista_id_seq', 1, false);


--
-- Name: unidad_control_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.unidad_control_id_seq', 1, false);


--
-- Name: usuarios_empresas_asignadas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.usuarios_empresas_asignadas_id_seq', 1, false);


--
-- Name: usuarios_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.usuarios_groups_id_seq', 1, false);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 7, true);


--
-- Name: usuarios_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.usuarios_user_permissions_id_seq', 1, false);


--
-- Name: vacaciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.vacaciones_id_seq', 1, false);


--
-- Name: vehiculos_transporte_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin_millache
--

SELECT pg_catalog.setval('public.vehiculos_transporte_id_seq', 1, false);


--
-- PostgreSQL database dump complete
--

