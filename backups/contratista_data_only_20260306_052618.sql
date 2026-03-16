--
-- PostgreSQL database dump
--

\restrict G48sY1urY2b5pygeepJFvEcN3ZcFeexkus36bh4k1ztQkMc2nwLDQQ565FI4fD3

-- Dumped from database version 16.10
-- Dumped by pg_dump version 16.10

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
-- Data for Name: holding; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.holding (id, nombre, estado, firma_empleador) VALUES (3, 'TESTING', true, NULL);
INSERT INTO public.holding (id, nombre, estado, firma_empleador) VALUES (4, 'TORRES Y CIA LTDA', true, 'firmas/firma_empleador/firma_empleador.png');


--
-- Data for Name: afp; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (1, 0, 'NO ESTÁ EN AFP', 0.00, 0.00, 0.00, 0.00, 3);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (2, 3, 'CUPRUM', 10.00, 1.44, 0.10, 0.90, 3);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (3, 5, 'HABITAT', 10.00, 1.27, 0.10, 0.90, 3);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (4, 8, 'PROVIDA', 10.00, 1.45, 0.10, 0.90, 3);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (5, 29, 'PLANVITAL', 10.00, 1.16, 0.10, 0.90, 3);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (6, 33, 'CAPITAL', 10.00, 1.44, 0.10, 0.90, 3);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (7, 34, 'MODELO', 10.00, 0.58, 0.10, 0.90, 3);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (8, 35, 'UNO', 10.00, 0.49, 0.10, 0.90, 3);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (9, 0, 'NO ESTÁ EN AFP', 0.00, 0.00, 0.00, 0.00, 4);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (10, 3, 'CUPRUM', 10.00, 1.44, 0.10, 0.90, 4);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (11, 5, 'HABITAT', 10.00, 1.27, 0.10, 0.90, 4);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (12, 8, 'PROVIDA', 10.00, 1.45, 0.10, 0.90, 4);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (13, 29, 'PLANVITAL', 10.00, 1.16, 0.10, 0.90, 4);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (14, 33, 'CAPITAL', 10.00, 1.44, 0.10, 0.90, 4);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (15, 34, 'MODELO', 10.00, 0.58, 0.10, 0.90, 4);
INSERT INTO public.afp (id, codigo, nombre, porcentaje_cotizacion_individual, comision_afp, porcentaje_cargo_empleador, porcentaje_seguro_social, holding_id) VALUES (16, 35, 'UNO', 10.00, 0.49, 0.10, 0.90, 4);


--
-- Data for Name: areas_administracion; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.areas_administracion (id, nombre, holding_id) VALUES (2, 'ADMINISTRACION', 3);
INSERT INTO public.areas_administracion (id, nombre, holding_id) VALUES (3, 'CAMPO', 3);
INSERT INTO public.areas_administracion (id, nombre, holding_id) VALUES (4, 'ADMINISTRACION', 4);
INSERT INTO public.areas_administracion (id, nombre, holding_id) VALUES (6, 'OPERACIONES', 4);


--
-- Data for Name: banco; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (1, '001', 'BANCO DE CHILE');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (2, '009', 'BANCO INTERNACIONAL');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (3, '012', 'BANCO DEL ESTADO DE CHILE');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (4, '014', 'SCOTIABANK CHILE');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (5, '016', 'BANCO DE CREDITO E INVERSIONES');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (6, '028', 'BANCO BICE');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (7, '031', 'HSBC BANK (CHILE)');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (8, '037', 'BANCO SANTANDER-CHILE');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (9, '039', 'BANCO ITAÚ CHILE');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (10, '041', 'JP MORGAN CHASE BANK, N. A.');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (11, '049', 'BANCO SECURITY');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (12, '051', 'BANCO FALABELLA');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (13, '053', 'BANCO RIPLEY');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (14, '055', 'BANCO CONSORCIO');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (15, '059', 'BANCO BTG PACTUAL CHILE');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (16, '060', 'CHINA CONSTRUCTION BANK, AGENCIA EN CHILE');
INSERT INTO public.banco (id, codigo_sbif, nombre) VALUES (17, '061', 'BANK OF CHINA, AGENCIA EN CHILE');


--
-- Data for Name: cargos_admnistracion; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.cargos_admnistracion (id, nombre, area_id, holding_id) VALUES (2, 'ADMINISTRADOR PRINCIPAL', 2, 3);
INSERT INTO public.cargos_admnistracion (id, nombre, area_id, holding_id) VALUES (3, 'SUPERVISOR', 3, 3);
INSERT INTO public.cargos_admnistracion (id, nombre, area_id, holding_id) VALUES (4, 'JEFE DE CUADRILLA', 3, 3);
INSERT INTO public.cargos_admnistracion (id, nombre, area_id, holding_id) VALUES (5, 'ADMINISTRADOR PRINCIPAL', 4, 4);
INSERT INTO public.cargos_admnistracion (id, nombre, area_id, holding_id) VALUES (7, 'GRTE ADMINISTRACION', 4, 4);
INSERT INTO public.cargos_admnistracion (id, nombre, area_id, holding_id) VALUES (8, 'CONTABILIDAD', 4, 4);
INSERT INTO public.cargos_admnistracion (id, nombre, area_id, holding_id) VALUES (9, 'RRHH', 4, 4);
INSERT INTO public.cargos_admnistracion (id, nombre, area_id, holding_id) VALUES (10, 'GRTE OPERACIONES', 6, 4);
INSERT INTO public.cargos_admnistracion (id, nombre, area_id, holding_id) VALUES (11, 'SUPERVISOR', 6, 4);
INSERT INTO public.cargos_admnistracion (id, nombre, area_id, holding_id) VALUES (12, 'JEFE CUADRILLA', 6, 4);
INSERT INTO public.cargos_admnistracion (id, nombre, area_id, holding_id) VALUES (13, 'TEMPORERO', 6, 4);


--
-- Data for Name: ccaf; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: ips_regimenes; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: mutualidades; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: perfiles; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.perfiles (id, nombre_perfil, tipo, estado, holding_id) VALUES (7, 'ADMINISTRADOR PRINCIPAL', 'AMBOS', true, 3);
INSERT INTO public.perfiles (id, nombre_perfil, tipo, estado, holding_id) VALUES (9, 'JEFE DE CUADRILLA', 'AMBOS', true, 3);
INSERT INTO public.perfiles (id, nombre_perfil, tipo, estado, holding_id) VALUES (8, 'SUPERVISOR', 'AMBOS', true, 3);
INSERT INTO public.perfiles (id, nombre_perfil, tipo, estado, holding_id) VALUES (10, 'ADMINISTRADOR PRINCIPAL', 'AMBOS', true, 4);
INSERT INTO public.perfiles (id, nombre_perfil, tipo, estado, holding_id) VALUES (11, 'SUPERVISOR', 'MOVIL', true, 4);
INSERT INTO public.perfiles (id, nombre_perfil, tipo, estado, holding_id) VALUES (12, 'JEFE DE CUADRILLA', 'MOVIL', true, 4);
INSERT INTO public.perfiles (id, nombre_perfil, tipo, estado, holding_id) VALUES (18, 'GRTE AOPERACIONAL', 'AMBOS', true, 4);
INSERT INTO public.perfiles (id, nombre_perfil, tipo, estado, holding_id) VALUES (17, 'RRHH', 'AMBOS', true, 4);


--
-- Data for Name: salud; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (1, 0, 'SIN ISAPRE', 7.00, 3);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (2, 1, 'BANMEDICA', 7.00, 3);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (3, 2, 'CONSALUD', 7.00, 3);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (4, 3, 'VIDATRES', 7.00, 3);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (5, 4, 'COLMENA', 7.00, 3);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (6, 5, 'ISAPRE CRUZ BLANCA S.A.', 7.00, 3);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (7, 7, 'FONASA', 7.00, 3);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (8, 10, 'NUEVA MASVIDA', 7.00, 3);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (9, 11, 'ISAPRE DE CODELCO LTDA.', 7.00, 3);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (10, 12, 'ISAPRE BCO. ESTADO', 7.00, 3);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (11, 25, 'CRUZ DEL NORTE', 7.00, 3);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (12, 0, 'SIN ISAPRE', 7.00, 4);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (13, 1, 'BANMEDICA', 7.00, 4);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (14, 2, 'CONSALUD', 7.00, 4);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (15, 3, 'VIDATRES', 7.00, 4);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (16, 4, 'COLMENA', 7.00, 4);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (17, 5, 'ISAPRE CRUZ BLANCA S.A.', 7.00, 4);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (18, 7, 'FONASA', 7.00, 4);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (19, 10, 'NUEVA MASVIDA', 7.00, 4);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (20, 11, 'ISAPRE DE CODELCO LTDA.', 7.00, 4);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (21, 12, 'ISAPRE BCO. ESTADO', 7.00, 4);
INSERT INTO public.salud (id, codigo, nombre, porcentaje, holding_id) VALUES (22, 25, 'CRUZ DEL NORTE', 7.00, 4);


--
-- Data for Name: sociedad; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.sociedad (id, rol_sociedad, nombre, nombre_representante, rut_representante, comuna, ciudad, calle, estado, ccaf_id, holding_id, mutualidad_id) VALUES (2, '123456789', 'TESTING SOCIETY', 'TESTER', '182870048', 'PARRAL', 'PARRAL', 'BALMACEDA 105', true, NULL, 3, NULL);
INSERT INTO public.sociedad (id, rol_sociedad, nombre, nombre_representante, rut_representante, comuna, ciudad, calle, estado, ccaf_id, holding_id, mutualidad_id) VALUES (3, '773819610', 'PRESTACION DE SERVICIOS MILLACHE LTDA', 'JUAN MIGUEL TORRES LILLO', '115664905', 'PARRAL', 'PARRAL', 'DIECIOCHO 640 PISO 3 OFICINA 9', true, NULL, 4, NULL);


--
-- Data for Name: personal; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (3, 'TESTER', NULL, '205031944', NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'carnets/dni.jpg', 'carnets/dni.jpg', '', NULL, NULL, NULL, false, true, 0, false, 0, false, NULL, NULL, NULL, 2, NULL, 2, 3, NULL, NULL, NULL, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (4, 'GENERAL', 'CARRERA', '97717931', NULL, NULL, 'ENCALADA 2004', '2025-11-10', true, 'Transferencia', 'CUENTA RUT', 9771793, 'CHILENA', 'H', '959898541', 'magnin.camilo.dev@gmail.com', 'carnets/dni.jpg', 'carnets/dni.jpg', '', 'SOLTERO(A)', '1996-04-05', NULL, false, true, 0, false, 0, false, NULL, NULL, 2, 3, 3, 3, 3, NULL, 2, 2, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (14, 'JUAN MIGUEL TORRES LILLO', NULL, '115664905', NULL, NULL, NULL, NULL, true, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 'carnets/dni.jpg', 'carnets/dni.jpg', '', NULL, NULL, NULL, false, true, 0, false, 0, false, NULL, NULL, NULL, 4, NULL, 5, 4, NULL, NULL, NULL, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (18, 'ABIGAIL', 'SILES REQUE', '44561226', '14258269', '44561226-K', 'LAS OBRAS LINARES', '2025-11-18', true, 'Efectivo', '', NULL, 'BOLIVIANA', 'F', '999999', 'correo@gmail.com', 'carnets/carnet_front_1763570299949.png', 'carnets/dni.jpg', 'firmas/firma_14258269.png', 'SOLTERO(A)', '2007-04-09', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 6, NULL, 13, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (19, 'AMELY', 'SILES REQUE', '', '14258259', '44561227-8', 'LAS OBRAS, LINARES', '2025-11-18', true, 'Efectivo', '', NULL, 'BOLIVIANA', 'F', '88888', 'correo@gmail.com', 'carnets/carnet_front_1763573378839.png', 'carnets/carnet_back_1763573378866.png', 'firmas/firma_14258259.png', 'SOLTERO(A)', '2007-04-09', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 6, NULL, 13, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (15, 'MARIA PATRICIA', 'TORRES LILLO', '113354100', '', '', 'PARCELA SANTA LUISA EL LUCERO S/N, RETIRO', '2025-11-01', true, 'Transferencia', 'CUENTA RUT', 11335410, 'CHILENA', 'F', '973691511', 'patricia.torres@terramas.cl', 'carnets/dni.jpg', 'carnets/dni.jpg', '', 'SOLTERO(A)', '1968-12-21', NULL, false, true, 0, false, 0, false, NULL, NULL, 14, 4, 3, 9, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (25, 'MARTIN', 'VEDIA CHAVARRIA', '', '12479079', '44543912-6', 'LAS OBRAS, LINARES', '2025-11-17', true, 'Efectivo', '', NULL, 'BOLIVIANA', 'M', '', 'correo@gmail.com', 'carnets/carnet_front_1763645452477.png', 'carnets/carnet_back_1763645452508.png', 'firmas/firma_12479079.png', 'SOLTERO(A)', '1977-07-27', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 6, NULL, 13, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (17, 'LISETTE SAYONARA', 'VILLALOBOS CO', '198969621', '', '', 'GUADANTUN SN, LINARES', '2025-11-01', true, 'Transferencia', 'CUENTA RUT', 19896962, 'CHILENA', 'F', '972054331', 'jmtorres@terrasoft.cl', 'carnets/dni.jpg', 'carnets/dni.jpg', '', 'SOLTERO(A)', '2000-01-01', NULL, false, true, 0, false, 0, false, NULL, NULL, 10, 6, 3, 11, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (20, 'YAFIRE NATALY', 'VILLALOBOS PALAVECINOS', '202307736', '', '', 'LAS OBRAS', '2025-11-04', true, 'Transferencia', 'CUENTA RUT', 20230773, 'CHILENA', 'F', '99999999', 'correo@gmail.com', 'carnets/dni.jpg', 'carnets/dni.jpg', '', 'SOLTERO(A)', '2000-01-04', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 6, 3, 12, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (26, 'JULIA', 'VELA', '', '8105131', '44543911-8', 'LAS OBRAS, LINARES', '2025-11-17', true, 'Efectivo', '', NULL, 'BOLIVIANA', 'F', '', '', 'carnets/carnet_front_1763645681532.png', 'carnets/carnet_back_1763645681559.png', 'firmas/firma_8105131.png', 'SOLTERO(A)', '1977-03-14', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 6, NULL, 13, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (24, 'VICTOR ALFREDO', 'ABARZUA CASTILLO', '114074721', NULL, NULL, 'PARRAL', '2025-11-01', true, 'Transferencia', 'CUENTA RUT', 11407472, 'CHILENA', 'M', '999795975', 'asesoriasterramas@gmail.com', 'carnets/dni.jpg', 'carnets/dni.jpg', '', 'CASADO(A)', '1969-05-14', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 4, 3, 9, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (27, 'JUDITH MARCELA', 'QUISPE SACA', '', '0743892', '44572183-2', 'LAS OBRAS, LINARES', '2025-11-17', true, 'Efectivo', '', NULL, 'BOLIVIANA', 'F', '', '', 'carnets/carnet_front_1763646025150.png', 'carnets/carnet_back_1763646025175.png', 'firmas/firma_0743892.png', 'SOLTERO(A)', '1998-12-18', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 6, NULL, 13, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (28, 'BEATRIZ', 'COLQUE BERRÍOS', '', '3334413', '44573341-5', 'LAS OBRAS, LINARES', '2025-11-17', true, 'Efectivo', '', NULL, 'BOLIVIA', 'F', '', '', 'carnets/carnet_front_1763646227170.png', 'carnets/carnet_back_1763646227191.png', 'firmas/firma_3334413.png', 'SOLTERO(A)', '1997-01-16', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 6, NULL, 13, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (16, 'JOSE MIGUEL', 'TORRES LILLO', '11288680', '', '', 'EL LUCERO S/N, RETIRO', '2025-11-01', true, 'Transferencia', 'CUENTA CORRIENTE', 32832168, 'CHILENA', 'M', '978452348', 'jose.flacotorres@gmail.com', 'carnets/dni.jpg', 'carnets/dni.jpg', '', 'CASADO(A)', '1968-08-10', NULL, false, true, 0, false, 0, false, NULL, NULL, 11, 6, 5, 10, 4, NULL, 16, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (21, 'LEIDY LAURA', 'CAUMOL ROJAS', '276220624', '', '', 'RETIRO', '2025-11-01', true, 'Efectivo', NULL, NULL, 'BOLIVIANA', 'F', '90311324', 'correo@gmail.com', 'carnets/dni.jpg', 'carnets/dni.jpg', '', 'CASADO(A)', '1985-05-22', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 6, NULL, 12, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (22, 'JOSE MIGUEL', 'MAGÑIN LILLO', '109442933', '', '', 'PARCELA SANTA LUISA EL LUCERO S/N, RETIRO', '2025-11-01', true, 'Transferencia', 'CUENTA RUT', 10944293, 'CHILENA', 'M', '932400361', 'jose.magnin.job@gmail.com', 'carnets/dni.jpg', 'carnets/dni.jpg', '', 'VIUDO(A)', '1971-01-25', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 6, 3, 9, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (31, 'OSCAR LUIS', 'VELIZ CRUZ', '', '.', '44392980-0', 'LAS OBRAS, LINARES', '2025-11-20', true, 'Efectivo', '', NULL, 'BOLIVIANA', 'M', '', '', 'carnets/dni.jpg', 'carnets/dni.jpg', 'firmas/firma_..png', 'SOLTERO(A)', '2000-01-01', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 6, NULL, 13, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (29, 'CINTIA', 'JALDIN VALDIVIA', '', '0054349', '44573339-3', 'LAS OBRAS, LINARES', '2025-11-17', true, 'Efectivo', '', NULL, 'BOLIVIANA', 'F', '', '', 'carnets/carnet_front_1763646697422.png', 'carnets/carnet_back_1763646697437.png', 'firmas/firma_0054349.png', 'SOLTERO(A)', '1999-08-15', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 6, NULL, 13, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (32, 'RAMON', 'CALLO HUMARRA', '', '44562214-1', '', 'LAS OBRAS, LINARES', '2025-11-20', true, 'Efectivo', '', NULL, 'BOLIVIANA', 'M', '', '', 'carnets/dni.jpg', 'carnets/dni.jpg', 'firmas/firma_5.png', 'SOLTERO(A)', '2000-01-01', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 6, NULL, 13, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (30, 'NICOLÁS MATIAS', 'MATAMALA MARTINEZ', '177604933', '', '', 'LAS OBRAS, LINARES', '2025-11-19', true, 'Transferencia', 'CUENTA RUT', 17760493, 'CHILENA', 'M', '', '', 'carnets/carnet_front_1763647010407.png', 'carnets/carnet_back_1763647010427.png', 'firmas/firma_177604933.png', 'SOLTERO(A)', '1991-09-20', NULL, false, true, 0, false, 0, false, NULL, NULL, 12, 6, 3, 13, 4, NULL, 18, 3, NULL);
INSERT INTO public.personal (id, nombres, apellidos, rut, dni, nic, direccion, fecha_ingreso, estado, metodo_pago, tipo_cuenta_bancaria, numero_cuenta, nacionalidad, sexo, telefono, correo, carnet_front_image, carnet_back_image, firma, estado_civil, fecha_nacimiento, sueldo_base, pensionado_vejez, afiliado_afc, cargas_familiares_legales, cargas_familiares_maternales, cargas_familiares_invalidez, subsidio_trabajador_joven, colacion, movilizacion, afp_id, area_id, banco_id, cargo_id, holding_id, ips_regimen_id, salud_id, sociedad_id, huella_digital) VALUES (23, 'FRANCISCA JAVIERA', 'SEPULVEDA INOSTROZA', '198942758', '', '', 'PARRAL', '2025-11-01', true, 'Transferencia', 'CUENTA RUT', 19894275, 'CHILENA', 'F', '941450700', 'terramas.doc@gmail.com', 'carnets/dni.jpg', 'carnets/dni.jpg', '', 'SOLTERO(A)', '1997-12-26', NULL, false, true, 0, false, 0, false, NULL, NULL, 16, 4, 3, 9, 4, NULL, 18, 3, NULL);


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.usuarios (password, last_login, is_superuser, id, rut, email, codigo, codigo_expiracion, estado, is_staff, is_admin, holding_id, perfil_id, persona_id) VALUES ('pbkdf2_sha256$1000000$HMkWLffXLX8MYZYxnUcgUy$tB7JkxodKWW7C0tNpfpB7a5spLK20ORXPlVMiGAxBIE=', NULL, true, 7, '62548053', 'jmiguelt@gmail.com', NULL, NULL, true, true, false, NULL, NULL, NULL);
INSERT INTO public.usuarios (password, last_login, is_superuser, id, rut, email, codigo, codigo_expiracion, estado, is_staff, is_admin, holding_id, perfil_id, persona_id) VALUES ('pbkdf2_sha256$1000000$fh2fPI8Bch5eOrsyxvyOgV$VMVCmT1vu1PnNsz5Lm8BgPQnEmFve6BV18kqEpKHbiU=', NULL, true, 8, '182870048', 'camilo.magnin@gmail.com', NULL, NULL, true, true, false, NULL, NULL, NULL);
INSERT INTO public.usuarios (password, last_login, is_superuser, id, rut, email, codigo, codigo_expiracion, estado, is_staff, is_admin, holding_id, perfil_id, persona_id) VALUES ('pbkdf2_sha256$1000000$wgtUX8xfujRrRjQTGXQ7pB$s9NwMFxtBTH0DYsXCiQHIur6i5ZN6/oFyQovHJxOhKs=', NULL, false, 9, '205031944', 'camilo.d.magnin@gmail.com', NULL, NULL, true, false, true, 3, 7, 3);
INSERT INTO public.usuarios (password, last_login, is_superuser, id, rut, email, codigo, codigo_expiracion, estado, is_staff, is_admin, holding_id, perfil_id, persona_id) VALUES ('pbkdf2_sha256$1000000$oPD9TPVfGmhFc9CMh0BPFX$P85gYBSYh2x1uow0OnIyWiqj/MqweyOUZApVb/Tz0ok=', NULL, false, 10, '97717931', 'magnin.camilo.dev@gmail.com', NULL, NULL, true, false, false, 3, 8, 4);
INSERT INTO public.usuarios (password, last_login, is_superuser, id, rut, email, codigo, codigo_expiracion, estado, is_staff, is_admin, holding_id, perfil_id, persona_id) VALUES ('pbkdf2_sha256$1000000$KcXghiMX5tlX9gkzgDWCMe$c27h5LcXm6HC2TqziVlarvbsHuI9sBq8B1Dnscu8YJ8=', NULL, false, 12, '115664905', 'jmiguelt@hotmail.com', NULL, NULL, true, false, true, 4, 10, 14);
INSERT INTO public.usuarios (password, last_login, is_superuser, id, rut, email, codigo, codigo_expiracion, estado, is_staff, is_admin, holding_id, perfil_id, persona_id) VALUES ('pbkdf2_sha256$1000000$uOtaPb2uGZA3XhJEoF907e$LPmcQdKGQhJVoXyfxLTGsiqy/MK4Bh+BzRmNwb+CeVk=', NULL, false, 15, '198969621', 'jmtorres@terrasoft.cl', NULL, NULL, true, false, false, 4, 11, 17);
INSERT INTO public.usuarios (password, last_login, is_superuser, id, rut, email, codigo, codigo_expiracion, estado, is_staff, is_admin, holding_id, perfil_id, persona_id) VALUES ('pbkdf2_sha256$1000000$wWHjYHphXxLE6qtqOwMY6s$wgjIScvBpq2R1wlQ8joqhhSadiydgBnhfh277earSfk=', NULL, false, 14, '113354100', 'jmtorres@terramas.cl', NULL, NULL, true, false, false, 4, 17, 15);
INSERT INTO public.usuarios (password, last_login, is_superuser, id, rut, email, codigo, codigo_expiracion, estado, is_staff, is_admin, holding_id, perfil_id, persona_id) VALUES ('pbkdf2_sha256$1000000$BIyuNMBsI7DacI5KO1Fq8f$w8svL3YXTwWyCr8d2DTvuqkXHVePLCS1FpCC9NGWhPE=', NULL, false, 13, '11288680K', 'jose.flacotorres@gmail.com', NULL, NULL, true, false, false, 4, 18, 16);
INSERT INTO public.usuarios (password, last_login, is_superuser, id, rut, email, codigo, codigo_expiracion, estado, is_staff, is_admin, holding_id, perfil_id, persona_id) VALUES ('pbkdf2_sha256$1000000$ZQMLmYziSDALgU2U78pQ2M$litd1zbVpOkV1EmxsiFnPkd8Ppo2mDu5GhM5LC5iE9A=', NULL, false, 16, '109442933', 'jose.magnin.job@gmail.com', NULL, NULL, true, false, false, 4, 17, 22);
INSERT INTO public.usuarios (password, last_login, is_superuser, id, rut, email, codigo, codigo_expiracion, estado, is_staff, is_admin, holding_id, perfil_id, persona_id) VALUES ('pbkdf2_sha256$1000000$SrgfVi04obkwdJ8Rv9yuDz$NUMuQIT3FsXbCPlurzlOMogn1MkjLTfNwnYvR5bbLSg=', NULL, false, 17, '198942758', 'terramas.dog@gmail.com', NULL, NULL, true, false, false, 4, 17, 23);
INSERT INTO public.usuarios (password, last_login, is_superuser, id, rut, email, codigo, codigo_expiracion, estado, is_staff, is_admin, holding_id, perfil_id, persona_id) VALUES ('pbkdf2_sha256$1000000$ivy10nkl4d88PEZ6qSmC9U$TXRU81jn5zov27MzgaAl0VMzJFgfT92HvrKlXKIuopY=', NULL, false, 18, '114074721', 'asesoriasterramas@gmail.com', NULL, NULL, true, false, false, 4, 17, 24);


--
-- Data for Name: apk_links; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: areas; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: areas_clientes; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.areas_clientes (id, nombre, holding_id) VALUES (1, 'OPERACIONES', 4);
INSERT INTO public.areas_clientes (id, nombre, holding_id) VALUES (3, 'ADMINIST FUNDO', 4);
INSERT INTO public.areas_clientes (id, nombre, holding_id) VALUES (4, 'ADMINIST CENTRAL', 4);


--
-- Data for Name: asociacion_codigo_qr; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.django_content_type (id, app_label, model) VALUES (1, 'auth', 'permission');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (2, 'auth', 'group');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (3, 'contenttypes', 'contenttype');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (4, 'contratista_test_app', 'areas');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (5, 'contratista_test_app', 'areasadministracion');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (6, 'contratista_test_app', 'areascliente');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (7, 'contratista_test_app', 'banco');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (8, 'contratista_test_app', 'causalfiniquito');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (9, 'contratista_test_app', 'ccaf');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (10, 'contratista_test_app', 'choferestransporte');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (11, 'contratista_test_app', 'clientes');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (12, 'contratista_test_app', 'developer');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (13, 'contratista_test_app', 'empresastransporte');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (14, 'contratista_test_app', 'holding');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (15, 'contratista_test_app', 'ipsregimen');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (16, 'contratista_test_app', 'mutualidad');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (17, 'contratista_test_app', 'region');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (18, 'contratista_test_app', 'tipodiscapacidad');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (19, 'contratista_test_app', 'tipoimpuestorenta');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (20, 'contratista_test_app', 'tipojornada');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (21, 'contratista_test_app', 'usuarios');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (22, 'contratista_test_app', 'cargoscliente');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (23, 'contratista_test_app', 'camposclientes');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (24, 'contratista_test_app', 'cuentaorigen');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (25, 'contratista_test_app', 'documentoschofer');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (26, 'contratista_test_app', 'foliocomercial');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (27, 'contratista_test_app', 'historialcambiopago');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (28, 'contratista_test_app', 'historialcambiofolio');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (29, 'contratista_test_app', 'haberes');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (30, 'contratista_test_app', 'descuentos');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (31, 'contratista_test_app', 'cuenta');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (32, 'contratista_test_app', 'contratovariables');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (33, 'contratista_test_app', 'contactosclientes');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (34, 'contratista_test_app', 'configuracionsiiautomaticacompra');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (35, 'contratista_test_app', 'casastrabajadores');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (36, 'contratista_test_app', 'cartolamovimiento');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (37, 'contratista_test_app', 'cargosadministracion');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (38, 'contratista_test_app', 'cargos');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (39, 'contratista_test_app', 'apklink');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (40, 'contratista_test_app', 'afptrabajadores');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (41, 'contratista_test_app', 'horarios');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (42, 'contratista_test_app', 'labores');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (43, 'contratista_test_app', 'facturaventasiidistribuida');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (44, 'contratista_test_app', 'facturacomprasiidistribuida');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (45, 'contratista_test_app', 'mescerrado');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (46, 'contratista_test_app', 'modulosmovil');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (47, 'contratista_test_app', 'modulosweb');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (48, 'contratista_test_app', 'pagotransportista');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (49, 'contratista_test_app', 'detallepagotransportista');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (50, 'contratista_test_app', 'perfiles');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (51, 'contratista_test_app', 'enlaceautoregistro');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (52, 'contratista_test_app', 'personaltrabajadores');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (53, 'contratista_test_app', 'licenciamedica');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (54, 'contratista_test_app', 'jefesdecuadrilla');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (55, 'contratista_test_app', 'horaextraordinaria');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (56, 'contratista_test_app', 'diastrabajadosaprobados');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (57, 'contratista_test_app', 'cuadrillas');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (58, 'contratista_test_app', 'codigoqr');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (59, 'contratista_test_app', 'producciontrabajador');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (60, 'contratista_test_app', 'comuna');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (61, 'contratista_test_app', 'registroegreso');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (62, 'contratista_test_app', 'registroingreso');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (63, 'contratista_test_app', 'registropagoefectivo');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (64, 'contratista_test_app', 'registropagotransferencia');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (65, 'contratista_test_app', 'saludtrabajadores');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (66, 'contratista_test_app', 'sociedad');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (67, 'contratista_test_app', 'proformatransportista');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (68, 'contratista_test_app', 'submodulosmovil');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (69, 'contratista_test_app', 'submodulosweb');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (70, 'contratista_test_app', 'supervisores');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (71, 'contratista_test_app', 'solicitudtraspaso');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (72, 'contratista_test_app', 'registroasistencia');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (73, 'contratista_test_app', 'contratotrabajador');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (74, 'contratista_test_app', 'trabajadordescuento');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (75, 'contratista_test_app', 'trabajadorhaber');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (76, 'contratista_test_app', 'tramos');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (77, 'contratista_test_app', 'foliotransportista');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (78, 'contratista_test_app', 'unidadcontrol');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (79, 'contratista_test_app', 'registromanoobrapersona');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (80, 'contratista_test_app', 'vacaciones');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (81, 'contratista_test_app', 'vehiculostransporte');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (82, 'contratista_test_app', 'documentosvehiculo');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (83, 'contratista_test_app', 'facturaventasiipordistribuir');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (84, 'contratista_test_app', 'facturacomprasiipordistribuir');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (85, 'contratista_test_app', 'configuracionsiiautomaticaventa');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (86, 'admin', 'logentry');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (87, 'sessions', 'session');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (88, 'oauth2_provider', 'application');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (89, 'oauth2_provider', 'accesstoken');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (90, 'oauth2_provider', 'grant');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (91, 'oauth2_provider', 'refreshtoken');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (92, 'oauth2_provider', 'idtoken');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (93, 'django_celery_beat', 'crontabschedule');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (94, 'django_celery_beat', 'intervalschedule');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (95, 'django_celery_beat', 'periodictask');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (96, 'django_celery_beat', 'periodictasks');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (97, 'django_celery_beat', 'solarschedule');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (98, 'django_celery_beat', 'clockedschedule');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (99, 'contratista_test_app', 'trabajadorempresatransporte');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (100, 'contratista_test_app', 'foliocomerciallabor');
INSERT INTO public.django_content_type (id, app_label, model) VALUES (101, 'contratista_test_app', 'turnohorario');


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (1, 'Can add permission', 1, 'add_permission');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (2, 'Can change permission', 1, 'change_permission');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (3, 'Can delete permission', 1, 'delete_permission');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (4, 'Can view permission', 1, 'view_permission');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (5, 'Can add group', 2, 'add_group');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (6, 'Can change group', 2, 'change_group');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (7, 'Can delete group', 2, 'delete_group');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (8, 'Can view group', 2, 'view_group');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (9, 'Can add content type', 3, 'add_contenttype');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (10, 'Can change content type', 3, 'change_contenttype');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (11, 'Can delete content type', 3, 'delete_contenttype');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (12, 'Can view content type', 3, 'view_contenttype');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (13, 'Can add areas', 4, 'add_areas');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (14, 'Can change areas', 4, 'change_areas');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (15, 'Can delete areas', 4, 'delete_areas');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (16, 'Can view areas', 4, 'view_areas');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (17, 'Can add areas administracion', 5, 'add_areasadministracion');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (18, 'Can change areas administracion', 5, 'change_areasadministracion');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (19, 'Can delete areas administracion', 5, 'delete_areasadministracion');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (20, 'Can view areas administracion', 5, 'view_areasadministracion');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (21, 'Can add areas cliente', 6, 'add_areascliente');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (22, 'Can change areas cliente', 6, 'change_areascliente');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (23, 'Can delete areas cliente', 6, 'delete_areascliente');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (24, 'Can view areas cliente', 6, 'view_areascliente');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (25, 'Can add banco', 7, 'add_banco');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (26, 'Can change banco', 7, 'change_banco');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (27, 'Can delete banco', 7, 'delete_banco');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (28, 'Can view banco', 7, 'view_banco');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (29, 'Can add causal finiquito', 8, 'add_causalfiniquito');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (30, 'Can change causal finiquito', 8, 'change_causalfiniquito');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (31, 'Can delete causal finiquito', 8, 'delete_causalfiniquito');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (32, 'Can view causal finiquito', 8, 'view_causalfiniquito');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (33, 'Can add ccaf', 9, 'add_ccaf');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (34, 'Can change ccaf', 9, 'change_ccaf');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (35, 'Can delete ccaf', 9, 'delete_ccaf');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (36, 'Can view ccaf', 9, 'view_ccaf');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (37, 'Can add choferes transporte', 10, 'add_choferestransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (38, 'Can change choferes transporte', 10, 'change_choferestransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (39, 'Can delete choferes transporte', 10, 'delete_choferestransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (40, 'Can view choferes transporte', 10, 'view_choferestransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (41, 'Can add clientes', 11, 'add_clientes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (42, 'Can change clientes', 11, 'change_clientes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (43, 'Can delete clientes', 11, 'delete_clientes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (44, 'Can view clientes', 11, 'view_clientes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (45, 'Can add developer', 12, 'add_developer');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (46, 'Can change developer', 12, 'change_developer');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (47, 'Can delete developer', 12, 'delete_developer');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (48, 'Can view developer', 12, 'view_developer');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (49, 'Can add empresas transporte', 13, 'add_empresastransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (50, 'Can change empresas transporte', 13, 'change_empresastransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (51, 'Can delete empresas transporte', 13, 'delete_empresastransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (52, 'Can view empresas transporte', 13, 'view_empresastransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (53, 'Can add holding', 14, 'add_holding');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (54, 'Can change holding', 14, 'change_holding');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (55, 'Can delete holding', 14, 'delete_holding');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (56, 'Can view holding', 14, 'view_holding');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (57, 'Can add ips regimen', 15, 'add_ipsregimen');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (58, 'Can change ips regimen', 15, 'change_ipsregimen');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (59, 'Can delete ips regimen', 15, 'delete_ipsregimen');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (60, 'Can view ips regimen', 15, 'view_ipsregimen');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (61, 'Can add mutualidad', 16, 'add_mutualidad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (62, 'Can change mutualidad', 16, 'change_mutualidad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (63, 'Can delete mutualidad', 16, 'delete_mutualidad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (64, 'Can view mutualidad', 16, 'view_mutualidad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (65, 'Can add region', 17, 'add_region');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (66, 'Can change region', 17, 'change_region');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (67, 'Can delete region', 17, 'delete_region');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (68, 'Can view region', 17, 'view_region');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (69, 'Can add tipo discapacidad', 18, 'add_tipodiscapacidad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (70, 'Can change tipo discapacidad', 18, 'change_tipodiscapacidad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (71, 'Can delete tipo discapacidad', 18, 'delete_tipodiscapacidad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (72, 'Can view tipo discapacidad', 18, 'view_tipodiscapacidad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (73, 'Can add tipo impuesto renta', 19, 'add_tipoimpuestorenta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (74, 'Can change tipo impuesto renta', 19, 'change_tipoimpuestorenta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (75, 'Can delete tipo impuesto renta', 19, 'delete_tipoimpuestorenta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (76, 'Can view tipo impuesto renta', 19, 'view_tipoimpuestorenta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (77, 'Can add tipo jornada', 20, 'add_tipojornada');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (78, 'Can change tipo jornada', 20, 'change_tipojornada');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (79, 'Can delete tipo jornada', 20, 'delete_tipojornada');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (80, 'Can view tipo jornada', 20, 'view_tipojornada');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (81, 'Can add usuarios', 21, 'add_usuarios');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (82, 'Can change usuarios', 21, 'change_usuarios');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (83, 'Can delete usuarios', 21, 'delete_usuarios');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (84, 'Can view usuarios', 21, 'view_usuarios');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (85, 'Can add cargos cliente', 22, 'add_cargoscliente');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (86, 'Can change cargos cliente', 22, 'change_cargoscliente');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (87, 'Can delete cargos cliente', 22, 'delete_cargoscliente');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (88, 'Can view cargos cliente', 22, 'view_cargoscliente');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (89, 'Can add campos clientes', 23, 'add_camposclientes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (90, 'Can change campos clientes', 23, 'change_camposclientes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (91, 'Can delete campos clientes', 23, 'delete_camposclientes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (92, 'Can view campos clientes', 23, 'view_camposclientes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (93, 'Can add cuenta origen', 24, 'add_cuentaorigen');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (94, 'Can change cuenta origen', 24, 'change_cuentaorigen');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (95, 'Can delete cuenta origen', 24, 'delete_cuentaorigen');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (96, 'Can view cuenta origen', 24, 'view_cuentaorigen');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (97, 'Can add documentos chofer', 25, 'add_documentoschofer');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (98, 'Can change documentos chofer', 25, 'change_documentoschofer');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (99, 'Can delete documentos chofer', 25, 'delete_documentoschofer');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (100, 'Can view documentos chofer', 25, 'view_documentoschofer');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (101, 'Can add folio comercial', 26, 'add_foliocomercial');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (102, 'Can change folio comercial', 26, 'change_foliocomercial');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (103, 'Can delete folio comercial', 26, 'delete_foliocomercial');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (104, 'Can view folio comercial', 26, 'view_foliocomercial');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (105, 'Can add historial cambio pago', 27, 'add_historialcambiopago');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (106, 'Can change historial cambio pago', 27, 'change_historialcambiopago');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (107, 'Can delete historial cambio pago', 27, 'delete_historialcambiopago');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (108, 'Can view historial cambio pago', 27, 'view_historialcambiopago');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (109, 'Can add historial cambio folio', 28, 'add_historialcambiofolio');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (110, 'Can change historial cambio folio', 28, 'change_historialcambiofolio');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (111, 'Can delete historial cambio folio', 28, 'delete_historialcambiofolio');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (112, 'Can view historial cambio folio', 28, 'view_historialcambiofolio');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (113, 'Can add haberes', 29, 'add_haberes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (114, 'Can change haberes', 29, 'change_haberes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (115, 'Can delete haberes', 29, 'delete_haberes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (116, 'Can view haberes', 29, 'view_haberes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (117, 'Can add descuentos', 30, 'add_descuentos');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (118, 'Can change descuentos', 30, 'change_descuentos');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (119, 'Can delete descuentos', 30, 'delete_descuentos');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (120, 'Can view descuentos', 30, 'view_descuentos');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (121, 'Can add cuenta', 31, 'add_cuenta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (122, 'Can change cuenta', 31, 'change_cuenta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (123, 'Can delete cuenta', 31, 'delete_cuenta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (124, 'Can view cuenta', 31, 'view_cuenta');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (125, 'Can add contrato variables', 32, 'add_contratovariables');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (126, 'Can change contrato variables', 32, 'change_contratovariables');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (127, 'Can delete contrato variables', 32, 'delete_contratovariables');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (128, 'Can view contrato variables', 32, 'view_contratovariables');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (129, 'Can add contactos clientes', 33, 'add_contactosclientes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (130, 'Can change contactos clientes', 33, 'change_contactosclientes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (131, 'Can delete contactos clientes', 33, 'delete_contactosclientes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (132, 'Can view contactos clientes', 33, 'view_contactosclientes');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (133, 'Can add configuracion sii automatica compra', 34, 'add_configuracionsiiautomaticacompra');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (134, 'Can change configuracion sii automatica compra', 34, 'change_configuracionsiiautomaticacompra');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (135, 'Can delete configuracion sii automatica compra', 34, 'delete_configuracionsiiautomaticacompra');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (136, 'Can view configuracion sii automatica compra', 34, 'view_configuracionsiiautomaticacompra');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (137, 'Can add casas trabajadores', 35, 'add_casastrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (138, 'Can change casas trabajadores', 35, 'change_casastrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (139, 'Can delete casas trabajadores', 35, 'delete_casastrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (140, 'Can view casas trabajadores', 35, 'view_casastrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (141, 'Can add cartola movimiento', 36, 'add_cartolamovimiento');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (142, 'Can change cartola movimiento', 36, 'change_cartolamovimiento');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (143, 'Can delete cartola movimiento', 36, 'delete_cartolamovimiento');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (144, 'Can view cartola movimiento', 36, 'view_cartolamovimiento');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (145, 'Can add cargos administracion', 37, 'add_cargosadministracion');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (146, 'Can change cargos administracion', 37, 'change_cargosadministracion');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (147, 'Can delete cargos administracion', 37, 'delete_cargosadministracion');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (148, 'Can view cargos administracion', 37, 'view_cargosadministracion');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (149, 'Can add cargos', 38, 'add_cargos');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (150, 'Can change cargos', 38, 'change_cargos');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (151, 'Can delete cargos', 38, 'delete_cargos');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (152, 'Can view cargos', 38, 'view_cargos');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (153, 'Can add Enlace APK', 39, 'add_apklink');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (154, 'Can change Enlace APK', 39, 'change_apklink');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (155, 'Can delete Enlace APK', 39, 'delete_apklink');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (156, 'Can view Enlace APK', 39, 'view_apklink');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (157, 'Can add afp trabajadores', 40, 'add_afptrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (158, 'Can change afp trabajadores', 40, 'change_afptrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (159, 'Can delete afp trabajadores', 40, 'delete_afptrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (160, 'Can view afp trabajadores', 40, 'view_afptrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (161, 'Can add horarios', 41, 'add_horarios');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (162, 'Can change horarios', 41, 'change_horarios');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (163, 'Can delete horarios', 41, 'delete_horarios');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (164, 'Can view horarios', 41, 'view_horarios');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (165, 'Can add labores', 42, 'add_labores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (166, 'Can change labores', 42, 'change_labores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (167, 'Can delete labores', 42, 'delete_labores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (168, 'Can view labores', 42, 'view_labores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (169, 'Can add factura venta sii distribuida', 43, 'add_facturaventasiidistribuida');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (170, 'Can change factura venta sii distribuida', 43, 'change_facturaventasiidistribuida');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (171, 'Can delete factura venta sii distribuida', 43, 'delete_facturaventasiidistribuida');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (172, 'Can view factura venta sii distribuida', 43, 'view_facturaventasiidistribuida');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (173, 'Can add factura compra sii distribuida', 44, 'add_facturacomprasiidistribuida');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (174, 'Can change factura compra sii distribuida', 44, 'change_facturacomprasiidistribuida');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (175, 'Can delete factura compra sii distribuida', 44, 'delete_facturacomprasiidistribuida');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (176, 'Can view factura compra sii distribuida', 44, 'view_facturacomprasiidistribuida');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (177, 'Can add mes cerrado', 45, 'add_mescerrado');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (178, 'Can change mes cerrado', 45, 'change_mescerrado');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (179, 'Can delete mes cerrado', 45, 'delete_mescerrado');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (180, 'Can view mes cerrado', 45, 'view_mescerrado');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (181, 'Can add modulos movil', 46, 'add_modulosmovil');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (182, 'Can change modulos movil', 46, 'change_modulosmovil');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (183, 'Can delete modulos movil', 46, 'delete_modulosmovil');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (184, 'Can view modulos movil', 46, 'view_modulosmovil');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (185, 'Can add modulos web', 47, 'add_modulosweb');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (186, 'Can change modulos web', 47, 'change_modulosweb');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (187, 'Can delete modulos web', 47, 'delete_modulosweb');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (188, 'Can view modulos web', 47, 'view_modulosweb');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (189, 'Can add pago transportista', 48, 'add_pagotransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (190, 'Can change pago transportista', 48, 'change_pagotransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (191, 'Can delete pago transportista', 48, 'delete_pagotransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (192, 'Can view pago transportista', 48, 'view_pagotransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (193, 'Can add detalle pago transportista', 49, 'add_detallepagotransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (194, 'Can change detalle pago transportista', 49, 'change_detallepagotransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (195, 'Can delete detalle pago transportista', 49, 'delete_detallepagotransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (196, 'Can view detalle pago transportista', 49, 'view_detallepagotransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (197, 'Can add perfiles', 50, 'add_perfiles');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (198, 'Can change perfiles', 50, 'change_perfiles');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (199, 'Can delete perfiles', 50, 'delete_perfiles');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (200, 'Can view perfiles', 50, 'view_perfiles');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (201, 'Can add enlace auto registro', 51, 'add_enlaceautoregistro');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (202, 'Can change enlace auto registro', 51, 'change_enlaceautoregistro');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (203, 'Can delete enlace auto registro', 51, 'delete_enlaceautoregistro');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (204, 'Can view enlace auto registro', 51, 'view_enlaceautoregistro');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (205, 'Can add personal trabajadores', 52, 'add_personaltrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (206, 'Can change personal trabajadores', 52, 'change_personaltrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (207, 'Can delete personal trabajadores', 52, 'delete_personaltrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (208, 'Can view personal trabajadores', 52, 'view_personaltrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (209, 'Can add licencia medica', 53, 'add_licenciamedica');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (210, 'Can change licencia medica', 53, 'change_licenciamedica');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (211, 'Can delete licencia medica', 53, 'delete_licenciamedica');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (212, 'Can view licencia medica', 53, 'view_licenciamedica');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (213, 'Can add jefes de cuadrilla', 54, 'add_jefesdecuadrilla');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (214, 'Can change jefes de cuadrilla', 54, 'change_jefesdecuadrilla');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (215, 'Can delete jefes de cuadrilla', 54, 'delete_jefesdecuadrilla');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (216, 'Can view jefes de cuadrilla', 54, 'view_jefesdecuadrilla');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (217, 'Can add hora extraordinaria', 55, 'add_horaextraordinaria');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (218, 'Can change hora extraordinaria', 55, 'change_horaextraordinaria');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (219, 'Can delete hora extraordinaria', 55, 'delete_horaextraordinaria');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (220, 'Can view hora extraordinaria', 55, 'view_horaextraordinaria');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (221, 'Can add dias trabajados aprobados', 56, 'add_diastrabajadosaprobados');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (222, 'Can change dias trabajados aprobados', 56, 'change_diastrabajadosaprobados');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (223, 'Can delete dias trabajados aprobados', 56, 'delete_diastrabajadosaprobados');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (224, 'Can view dias trabajados aprobados', 56, 'view_diastrabajadosaprobados');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (225, 'Can add cuadrillas', 57, 'add_cuadrillas');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (226, 'Can change cuadrillas', 57, 'change_cuadrillas');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (227, 'Can delete cuadrillas', 57, 'delete_cuadrillas');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (228, 'Can view cuadrillas', 57, 'view_cuadrillas');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (229, 'Can add codigo qr', 58, 'add_codigoqr');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (230, 'Can change codigo qr', 58, 'change_codigoqr');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (231, 'Can delete codigo qr', 58, 'delete_codigoqr');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (232, 'Can view codigo qr', 58, 'view_codigoqr');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (233, 'Can add produccion trabajador', 59, 'add_producciontrabajador');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (234, 'Can change produccion trabajador', 59, 'change_producciontrabajador');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (235, 'Can delete produccion trabajador', 59, 'delete_producciontrabajador');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (236, 'Can view produccion trabajador', 59, 'view_producciontrabajador');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (237, 'Can add comuna', 60, 'add_comuna');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (238, 'Can change comuna', 60, 'change_comuna');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (239, 'Can delete comuna', 60, 'delete_comuna');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (240, 'Can view comuna', 60, 'view_comuna');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (241, 'Can add registro egreso', 61, 'add_registroegreso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (242, 'Can change registro egreso', 61, 'change_registroegreso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (243, 'Can delete registro egreso', 61, 'delete_registroegreso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (244, 'Can view registro egreso', 61, 'view_registroegreso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (245, 'Can add registro ingreso', 62, 'add_registroingreso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (246, 'Can change registro ingreso', 62, 'change_registroingreso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (247, 'Can delete registro ingreso', 62, 'delete_registroingreso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (248, 'Can view registro ingreso', 62, 'view_registroingreso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (249, 'Can add registro pago efectivo', 63, 'add_registropagoefectivo');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (250, 'Can change registro pago efectivo', 63, 'change_registropagoefectivo');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (251, 'Can delete registro pago efectivo', 63, 'delete_registropagoefectivo');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (252, 'Can view registro pago efectivo', 63, 'view_registropagoefectivo');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (253, 'Can add registro pago transferencia', 64, 'add_registropagotransferencia');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (254, 'Can change registro pago transferencia', 64, 'change_registropagotransferencia');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (255, 'Can delete registro pago transferencia', 64, 'delete_registropagotransferencia');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (256, 'Can view registro pago transferencia', 64, 'view_registropagotransferencia');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (257, 'Can add salud trabajadores', 65, 'add_saludtrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (258, 'Can change salud trabajadores', 65, 'change_saludtrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (259, 'Can delete salud trabajadores', 65, 'delete_saludtrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (260, 'Can view salud trabajadores', 65, 'view_saludtrabajadores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (261, 'Can add sociedad', 66, 'add_sociedad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (262, 'Can change sociedad', 66, 'change_sociedad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (263, 'Can delete sociedad', 66, 'delete_sociedad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (264, 'Can view sociedad', 66, 'view_sociedad');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (265, 'Can add proforma transportista', 67, 'add_proformatransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (266, 'Can change proforma transportista', 67, 'change_proformatransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (267, 'Can delete proforma transportista', 67, 'delete_proformatransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (268, 'Can view proforma transportista', 67, 'view_proformatransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (269, 'Can add sub modulos movil', 68, 'add_submodulosmovil');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (270, 'Can change sub modulos movil', 68, 'change_submodulosmovil');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (271, 'Can delete sub modulos movil', 68, 'delete_submodulosmovil');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (272, 'Can view sub modulos movil', 68, 'view_submodulosmovil');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (273, 'Can add sub modulos web', 69, 'add_submodulosweb');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (274, 'Can change sub modulos web', 69, 'change_submodulosweb');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (275, 'Can delete sub modulos web', 69, 'delete_submodulosweb');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (276, 'Can view sub modulos web', 69, 'view_submodulosweb');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (277, 'Can add supervisores', 70, 'add_supervisores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (278, 'Can change supervisores', 70, 'change_supervisores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (279, 'Can delete supervisores', 70, 'delete_supervisores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (280, 'Can view supervisores', 70, 'view_supervisores');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (281, 'Can add solicitud traspaso', 71, 'add_solicitudtraspaso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (282, 'Can change solicitud traspaso', 71, 'change_solicitudtraspaso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (283, 'Can delete solicitud traspaso', 71, 'delete_solicitudtraspaso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (284, 'Can view solicitud traspaso', 71, 'view_solicitudtraspaso');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (285, 'Can add registro asistencia', 72, 'add_registroasistencia');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (286, 'Can change registro asistencia', 72, 'change_registroasistencia');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (287, 'Can delete registro asistencia', 72, 'delete_registroasistencia');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (288, 'Can view registro asistencia', 72, 'view_registroasistencia');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (289, 'Can add contrato trabajador', 73, 'add_contratotrabajador');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (290, 'Can change contrato trabajador', 73, 'change_contratotrabajador');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (291, 'Can delete contrato trabajador', 73, 'delete_contratotrabajador');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (292, 'Can view contrato trabajador', 73, 'view_contratotrabajador');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (293, 'Can add trabajador descuento', 74, 'add_trabajadordescuento');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (294, 'Can change trabajador descuento', 74, 'change_trabajadordescuento');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (295, 'Can delete trabajador descuento', 74, 'delete_trabajadordescuento');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (296, 'Can view trabajador descuento', 74, 'view_trabajadordescuento');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (297, 'Can add trabajador haber', 75, 'add_trabajadorhaber');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (298, 'Can change trabajador haber', 75, 'change_trabajadorhaber');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (299, 'Can delete trabajador haber', 75, 'delete_trabajadorhaber');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (300, 'Can view trabajador haber', 75, 'view_trabajadorhaber');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (301, 'Can add tramos', 76, 'add_tramos');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (302, 'Can change tramos', 76, 'change_tramos');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (303, 'Can delete tramos', 76, 'delete_tramos');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (304, 'Can view tramos', 76, 'view_tramos');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (305, 'Can add folio transportista', 77, 'add_foliotransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (306, 'Can change folio transportista', 77, 'change_foliotransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (307, 'Can delete folio transportista', 77, 'delete_foliotransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (308, 'Can view folio transportista', 77, 'view_foliotransportista');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (309, 'Can add unidad control', 78, 'add_unidadcontrol');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (310, 'Can change unidad control', 78, 'change_unidadcontrol');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (311, 'Can delete unidad control', 78, 'delete_unidadcontrol');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (312, 'Can view unidad control', 78, 'view_unidadcontrol');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (313, 'Can add registro mano obra persona', 79, 'add_registromanoobrapersona');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (314, 'Can change registro mano obra persona', 79, 'change_registromanoobrapersona');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (315, 'Can delete registro mano obra persona', 79, 'delete_registromanoobrapersona');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (316, 'Can view registro mano obra persona', 79, 'view_registromanoobrapersona');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (317, 'Can add vacaciones', 80, 'add_vacaciones');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (318, 'Can change vacaciones', 80, 'change_vacaciones');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (319, 'Can delete vacaciones', 80, 'delete_vacaciones');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (320, 'Can view vacaciones', 80, 'view_vacaciones');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (321, 'Can add vehiculos transporte', 81, 'add_vehiculostransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (322, 'Can change vehiculos transporte', 81, 'change_vehiculostransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (323, 'Can delete vehiculos transporte', 81, 'delete_vehiculostransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (324, 'Can view vehiculos transporte', 81, 'view_vehiculostransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (325, 'Can add documentos vehiculo', 82, 'add_documentosvehiculo');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (326, 'Can change documentos vehiculo', 82, 'change_documentosvehiculo');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (327, 'Can delete documentos vehiculo', 82, 'delete_documentosvehiculo');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (328, 'Can view documentos vehiculo', 82, 'view_documentosvehiculo');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (329, 'Can add factura venta sii por distribuir', 83, 'add_facturaventasiipordistribuir');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (330, 'Can change factura venta sii por distribuir', 83, 'change_facturaventasiipordistribuir');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (331, 'Can delete factura venta sii por distribuir', 83, 'delete_facturaventasiipordistribuir');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (332, 'Can view factura venta sii por distribuir', 83, 'view_facturaventasiipordistribuir');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (333, 'Can add factura compra sii por distribuir', 84, 'add_facturacomprasiipordistribuir');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (334, 'Can change factura compra sii por distribuir', 84, 'change_facturacomprasiipordistribuir');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (335, 'Can delete factura compra sii por distribuir', 84, 'delete_facturacomprasiipordistribuir');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (336, 'Can view factura compra sii por distribuir', 84, 'view_facturacomprasiipordistribuir');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (337, 'Can add configuracion sii automatica venta', 85, 'add_configuracionsiiautomaticaventa');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (338, 'Can change configuracion sii automatica venta', 85, 'change_configuracionsiiautomaticaventa');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (339, 'Can delete configuracion sii automatica venta', 85, 'delete_configuracionsiiautomaticaventa');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (340, 'Can view configuracion sii automatica venta', 85, 'view_configuracionsiiautomaticaventa');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (341, 'Can add log entry', 86, 'add_logentry');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (342, 'Can change log entry', 86, 'change_logentry');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (343, 'Can delete log entry', 86, 'delete_logentry');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (344, 'Can view log entry', 86, 'view_logentry');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (345, 'Can add session', 87, 'add_session');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (346, 'Can change session', 87, 'change_session');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (347, 'Can delete session', 87, 'delete_session');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (348, 'Can view session', 87, 'view_session');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (349, 'Can add application', 88, 'add_application');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (350, 'Can change application', 88, 'change_application');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (351, 'Can delete application', 88, 'delete_application');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (352, 'Can view application', 88, 'view_application');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (353, 'Can add access token', 89, 'add_accesstoken');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (354, 'Can change access token', 89, 'change_accesstoken');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (355, 'Can delete access token', 89, 'delete_accesstoken');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (356, 'Can view access token', 89, 'view_accesstoken');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (357, 'Can add grant', 90, 'add_grant');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (358, 'Can change grant', 90, 'change_grant');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (359, 'Can delete grant', 90, 'delete_grant');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (360, 'Can view grant', 90, 'view_grant');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (361, 'Can add refresh token', 91, 'add_refreshtoken');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (362, 'Can change refresh token', 91, 'change_refreshtoken');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (363, 'Can delete refresh token', 91, 'delete_refreshtoken');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (364, 'Can view refresh token', 91, 'view_refreshtoken');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (365, 'Can add id token', 92, 'add_idtoken');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (366, 'Can change id token', 92, 'change_idtoken');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (367, 'Can delete id token', 92, 'delete_idtoken');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (368, 'Can view id token', 92, 'view_idtoken');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (369, 'Can add crontab', 93, 'add_crontabschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (370, 'Can change crontab', 93, 'change_crontabschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (371, 'Can delete crontab', 93, 'delete_crontabschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (372, 'Can view crontab', 93, 'view_crontabschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (373, 'Can add interval', 94, 'add_intervalschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (374, 'Can change interval', 94, 'change_intervalschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (375, 'Can delete interval', 94, 'delete_intervalschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (376, 'Can view interval', 94, 'view_intervalschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (377, 'Can add periodic task', 95, 'add_periodictask');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (378, 'Can change periodic task', 95, 'change_periodictask');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (379, 'Can delete periodic task', 95, 'delete_periodictask');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (380, 'Can view periodic task', 95, 'view_periodictask');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (381, 'Can add periodic task track', 96, 'add_periodictasks');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (382, 'Can change periodic task track', 96, 'change_periodictasks');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (383, 'Can delete periodic task track', 96, 'delete_periodictasks');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (384, 'Can view periodic task track', 96, 'view_periodictasks');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (385, 'Can add solar event', 97, 'add_solarschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (386, 'Can change solar event', 97, 'change_solarschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (387, 'Can delete solar event', 97, 'delete_solarschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (388, 'Can view solar event', 97, 'view_solarschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (389, 'Can add clocked', 98, 'add_clockedschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (390, 'Can change clocked', 98, 'change_clockedschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (391, 'Can delete clocked', 98, 'delete_clockedschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (392, 'Can view clocked', 98, 'view_clockedschedule');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (393, 'Can add trabajador empresa transporte', 99, 'add_trabajadorempresatransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (394, 'Can change trabajador empresa transporte', 99, 'change_trabajadorempresatransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (395, 'Can delete trabajador empresa transporte', 99, 'delete_trabajadorempresatransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (396, 'Can view trabajador empresa transporte', 99, 'view_trabajadorempresatransporte');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (397, 'Can add folio comercial labor', 100, 'add_foliocomerciallabor');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (398, 'Can change folio comercial labor', 100, 'change_foliocomerciallabor');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (399, 'Can delete folio comercial labor', 100, 'delete_foliocomerciallabor');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (400, 'Can view folio comercial labor', 100, 'view_foliocomerciallabor');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (401, 'Can add turno horario', 101, 'add_turnohorario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (402, 'Can change turno horario', 101, 'change_turnohorario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (403, 'Can delete turno horario', 101, 'delete_turnohorario');
INSERT INTO public.auth_permission (id, name, content_type_id, codename) VALUES (404, 'Can view turno horario', 101, 'view_turnohorario');


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: clientes; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.clientes (id, rut, nombre, direccion, giro, nombre_rep_legal, direccion_rep_legal, holding_id, comuna_cliente) VALUES (2, '883368002', 'SOC AGRICOLA SAN MARIANO LTDA', 'Fundo Santa Filomena El Emboque, Linares', 'Venta al por mayor de frutas y verduras', 'Representante', 'Fundo Santa Filomena El Emboque, Linares', 4, NULL);
INSERT INTO public.clientes (id, rut, nombre, direccion, giro, nombre_rep_legal, direccion_rep_legal, holding_id, comuna_cliente) VALUES (4, '779057127', 'BAIKA SERVICIOS AGRICOLAS SPA', 'Avda del Parque 5275 of 302 Edif Terrazas 302, Vitacura, Santiago', 'Actividades de apoyo a la agricultura', 'Representante', 'Avda del Parque 5275 of 302 Edif Terrazas 302, Vitacura, Santiago', 4, NULL);
INSERT INTO public.clientes (id, rut, nombre, direccion, giro, nombre_rep_legal, direccion_rep_legal, holding_id, comuna_cliente) VALUES (5, '760729574', 'AGRICOLA SAN LEON SA', 'Fundo Marengo Km 5,5 Los Niches, Curico', 'Cultivo de frutas de pepita y hueso', 'Representante', 'Fundo Marengo Km 5,5 Los Niches, Curico', 4, NULL);
INSERT INTO public.clientes (id, rut, nombre, direccion, giro, nombre_rep_legal, direccion_rep_legal, holding_id, comuna_cliente) VALUES (6, '766953859', 'SUTIL ORGANIC FARMS SPA', 'Nueva Providencia 1860 , Providencia , Santiago', 'Actividades de apoyo a la agricultura', 'Representante', 'Nueva Providencia 1860 , Providencia , Santiago', 4, NULL);
INSERT INTO public.clientes (id, rut, nombre, direccion, giro, nombre_rep_legal, direccion_rep_legal, holding_id, comuna_cliente) VALUES (7, '967935808', 'AGRICOLA APF SA', 'Los Cibeles , sector La Puntilla, Longavi', 'Actividades de apoyo a la agricultura', 'Representante', 'Los Cibeles , sector La Puntilla, Longavi', 4, NULL);
INSERT INTO public.clientes (id, rut, nombre, direccion, giro, nombre_rep_legal, direccion_rep_legal, holding_id, comuna_cliente) VALUES (1, '145551515', 'AGRICOLA SPA', 'LOS PONIENTES 35', 'AGRICOLA', 'JUAN PEREZ', 'DIRECCION', 3, NULL);
INSERT INTO public.clientes (id, rut, nombre, direccion, giro, nombre_rep_legal, direccion_rep_legal, holding_id, comuna_cliente) VALUES (8, '848331007', 'COMPAÑIA AGRICOLA Y FORESTAL EL ALAMO LTDA', 'Fundo Papelucho camino a Cauquenes km 16, Parral', 'Agricola y Forestal', 'Vicente Aguirre Romero', 'Fundo Papelucho camino a Cauquenes km 16, Parral', 4, NULL);
INSERT INTO public.clientes (id, rut, nombre, direccion, giro, nombre_rep_legal, direccion_rep_legal, holding_id, comuna_cliente) VALUES (3, '781349909', 'SOC AGRICOLA EL PORVENIR SA', 'Fundo Las Mercedes sn, Longavi', 'Cría de ganado bobino para la producción', 'Representante', 'Fundo Las Mercedes sn, Longavi', 4, NULL);


--
-- Data for Name: campos_clientes; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.campos_clientes (id, nombre_campo, direccion_campo, comuna_campo, cliente_id, holding_id) VALUES (2, 'Fundo Santa Filomena', 'El Emboque sn', 'Linares', 2, 4);
INSERT INTO public.campos_clientes (id, nombre_campo, direccion_campo, comuna_campo, cliente_id, holding_id) VALUES (4, 'Fundo La Sexta', 'La Sexta interior 13', 'Longavi', 4, 4);
INSERT INTO public.campos_clientes (id, nombre_campo, direccion_campo, comuna_campo, cliente_id, holding_id) VALUES (5, 'Fundo El Copihue', 'Sector', 'Longavi', 5, 4);
INSERT INTO public.campos_clientes (id, nombre_campo, direccion_campo, comuna_campo, cliente_id, holding_id) VALUES (6, 'Fundo Santo Domingo', 'Talquita sn', 'Parral', 6, 4);
INSERT INTO public.campos_clientes (id, nombre_campo, direccion_campo, comuna_campo, cliente_id, holding_id) VALUES (7, 'Los Cibeles', 'Sector la Puntilla', 'Longavi', 7, 4);
INSERT INTO public.campos_clientes (id, nombre_campo, direccion_campo, comuna_campo, cliente_id, holding_id) VALUES (8, 'CAMPO_TESTING_2', 'DIRECCION 2', 'RETIRO', 1, 3);
INSERT INTO public.campos_clientes (id, nombre_campo, direccion_campo, comuna_campo, cliente_id, holding_id) VALUES (1, 'FUNDO LOS CIPRELES', 'ENCALDA 10', 'PARRAL', 1, 3);
INSERT INTO public.campos_clientes (id, nombre_campo, direccion_campo, comuna_campo, cliente_id, holding_id) VALUES (10, 'Fundo Papelucho', 'Camino a Cauquenes km 16', 'Parral', 8, 4);
INSERT INTO public.campos_clientes (id, nombre_campo, direccion_campo, comuna_campo, cliente_id, holding_id) VALUES (3, 'Fundo Las Mercedes', 'Las Mercedes sn', 'Longavi', 3, 4);
INSERT INTO public.campos_clientes (id, nombre_campo, direccion_campo, comuna_campo, cliente_id, holding_id) VALUES (9, 'Fundo Nueva Esperanza', 'Sector Esperanza plan', 'Longavi', 3, 4);


--
-- Data for Name: cargos; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: cargos_clientes; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: cuenta_origen; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.cuenta_origen (id, tipo_cuenta, numero_cuenta, banco_id, sociedad_id) VALUES (1, 'CTE', '2180525808', 1, 3);


--
-- Data for Name: cartola_movimiento; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: casas; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.casas (id, nombre, estado, holding_id) VALUES (1, 'CASA RETIRO', true, 3);
INSERT INTO public.casas (id, nombre, estado, holding_id) VALUES (2, 'CASA LUCERO', true, 4);
INSERT INTO public.casas (id, nombre, estado, holding_id) VALUES (3, 'CASA MAITENES', true, 4);
INSERT INTO public.casas (id, nombre, estado, holding_id) VALUES (4, 'SIN CASA', true, 4);


--
-- Data for Name: causales_finiquito; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: empresas_transporte; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.empresas_transporte (id, nombre, rut, direccion, holding_id, comuna, banco_id, metodo_pago, numero_cuenta, tipo_cuenta, alias, emite_factura) VALUES (1, 'EMPRESA T1', '145515115', 'DIRE 3', 3, NULL, NULL, NULL, NULL, NULL, NULL, false);
INSERT INTO public.empresas_transporte (id, nombre, rut, direccion, holding_id, comuna, banco_id, metodo_pago, numero_cuenta, tipo_cuenta, alias, emite_factura) VALUES (3, 'CRISTIAN ANTONIO ROJAS REBOLLEDO', '162755102', 'Las obras sn, Linares', 4, NULL, NULL, NULL, NULL, NULL, NULL, false);
INSERT INTO public.empresas_transporte (id, nombre, rut, direccion, holding_id, comuna, banco_id, metodo_pago, numero_cuenta, tipo_cuenta, alias, emite_factura) VALUES (4, 'DOMINGO ANTONIO QUEVEDO ZUÑIGA', '111761000', 'Sector El Lucero sn, Retiro', 4, NULL, NULL, NULL, NULL, NULL, NULL, false);
INSERT INTO public.empresas_transporte (id, nombre, rut, direccion, holding_id, comuna, banco_id, metodo_pago, numero_cuenta, tipo_cuenta, alias, emite_factura) VALUES (5, 'RAUL ANTONIO YAÑEZ MARTINEZ', '151558968', 'Sector cuentas claras sn, Longavi', 4, NULL, NULL, NULL, NULL, NULL, NULL, false);
INSERT INTO public.empresas_transporte (id, nombre, rut, direccion, holding_id, comuna, banco_id, metodo_pago, numero_cuenta, tipo_cuenta, alias, emite_factura) VALUES (6, 'TRANSPORTES SOFIA SPA', '780190647', 'San Jose Pc 73 Lote1A , Longavi', 4, NULL, NULL, NULL, NULL, NULL, NULL, false);
INSERT INTO public.empresas_transporte (id, nombre, rut, direccion, holding_id, comuna, banco_id, metodo_pago, numero_cuenta, tipo_cuenta, alias, emite_factura) VALUES (7, 'RAUL ANTONIO MAUREIRA SANCHEZ', '92893383', 'Libertad N° 98 Santa Amelia, Retiro', 4, NULL, NULL, NULL, NULL, NULL, NULL, false);
INSERT INTO public.empresas_transporte (id, nombre, rut, direccion, holding_id, comuna, banco_id, metodo_pago, numero_cuenta, tipo_cuenta, alias, emite_factura) VALUES (8, 'CARLOS ALBERTO RETAMAL ARAYA', '10919011K', 'Las obras sn, Linares', 4, NULL, NULL, NULL, NULL, NULL, NULL, false);
INSERT INTO public.empresas_transporte (id, nombre, rut, direccion, holding_id, comuna, banco_id, metodo_pago, numero_cuenta, tipo_cuenta, alias, emite_factura) VALUES (2, 'JOSE ISMAEL QUEZADA MARQUEZ', '66774279', 'Parcela 49 Poniente El Carmen, Longavi', 4, 'PARRAL', 3, 'TRANSFERENCIA', '15454545', 'CUENTA CORRIENTE', NULL, false);
INSERT INTO public.empresas_transporte (id, nombre, rut, direccion, holding_id, comuna, banco_id, metodo_pago, numero_cuenta, tipo_cuenta, alias, emite_factura) VALUES (9, 'TESTING', '182818281', 'DIRE 3', 4, 'PARRAL', 10, 'TRANSFERENCIA', '151515', 'CUENTA CORRIENTE', NULL, false);


--
-- Data for Name: vehiculos_transporte; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.vehiculos_transporte (id, ppu, modelo, year, color, num_pasajeros, marca, tipo, empresa_id, holding_id) VALUES (1, 'ASD44D', 'MODELO', 2010, 'VERDE', 5, 'NISSAN', 'SEDAN', 1, 3);
INSERT INTO public.vehiculos_transporte (id, ppu, modelo, year, color, num_pasajeros, marca, tipo, empresa_id, holding_id) VALUES (3, 'ZR6390-1', '9150', 2006, 'DORADO/AZUL/ROJO/CELESTE', 33, 'VOLKSWAGEN', 'BUS', 3, 4);
INSERT INTO public.vehiculos_transporte (id, ppu, modelo, year, color, num_pasajeros, marca, tipo, empresa_id, holding_id) VALUES (4, 'XG3179-8', 'LO71237', 2004, 'AZUL TURQUEZA/BLANCO', 26, 'MERCEDES BENZ', 'BUS', 3, 4);
INSERT INTO public.vehiculos_transporte (id, ppu, modelo, year, color, num_pasajeros, marca, tipo, empresa_id, holding_id) VALUES (5, 'DRTS81-8', '9150 EOD', 2012, 'VERDE / BLANCO / MARFIL', 31, 'VOLKSWAGEN', 'BUS', 4, 4);
INSERT INTO public.vehiculos_transporte (id, ppu, modelo, year, color, num_pasajeros, marca, tipo, empresa_id, holding_id) VALUES (6, 'WZ6174', 'H1SVX 2.5', 2007, 'AZUL', 12, 'HYUNDAI', 'MINI BUS', 8, 4);
INSERT INTO public.vehiculos_transporte (id, ppu, modelo, year, color, num_pasajeros, marca, tipo, empresa_id, holding_id) VALUES (7, 'YH8149', 'BESTA 2.7', 2005, 'BLANCO INVIERNO', 12, 'KIA', 'MINI BUS', 8, 4);
INSERT INTO public.vehiculos_transporte (id, ppu, modelo, year, color, num_pasajeros, marca, tipo, empresa_id, holding_id) VALUES (2, 'FBVV67', 'CETY', 2012, 'ROJO/BURDEO/BEIGE', 29, 'JAC', 'BUS', 2, 4);


--
-- Data for Name: choferes; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.choferes (id, nombre, rut, licencia, empresa_id, holding_id, vehiculo_id) VALUES (1, 'ELIAS', '16.266.162-1', 'A1,A4', 1, 3, 1);
INSERT INTO public.choferes (id, nombre, rut, licencia, empresa_id, holding_id, vehiculo_id) VALUES (2, 'DOMINGO ANTONIO QUEVEDO ZUÑIGA', '1.117.610-00', 'A2', 4, 4, 5);
INSERT INTO public.choferes (id, nombre, rut, licencia, empresa_id, holding_id, vehiculo_id) VALUES (3, 'ARNOLDO ANTONIO VILLALOBOS ARAVENA', '984.442-38', 'A3', 3, 4, 3);
INSERT INTO public.choferes (id, nombre, rut, licencia, empresa_id, holding_id, vehiculo_id) VALUES (4, 'ANIBAL ALFONSO QUEZADA MORALES', '1.433.144-05', 'A1', 2, 4, 2);
INSERT INTO public.choferes (id, nombre, rut, licencia, empresa_id, holding_id, vehiculo_id) VALUES (5, 'CARLOS ALBERTO RETAMAL ARAYA', '1.091.901-1k', 'A1', 8, 4, 6);


--
-- Data for Name: regiones; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: comunas; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: configuracion_sii_automatica; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: configuracion_sii_automatica_venta; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: contactos_clientes; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: documentos_variables; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.documentos_variables (id, nombre, tipo, archivo_pdf, variables, fecha_creacion, activo, holding_id) VALUES (9, 'Cont_Plazo_Fijo_Extranjero_Full', 'EXTRANJERO', 'contracts/formats/cont_plazo_fijo_extranjero_full.pdf', '[{"nombre": "fecha_emision", "ubicaciones": [{"id": "var-fecha_emision-1763587549627", "posX": 191.35286035714287, "posY": 87.99953418067825, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "fecha_ingreso", "ubicaciones": [{"id": "var-fecha_ingreso-1763587982894", "posX": 509.3928571428571, "posY": 400.10770668135973, "pagina": 2, "pageWidth": 612, "pageHeight": 792}, {"id": "var-fecha_ingreso-1763588045755", "posX": 242.24999999999997, "posY": 373.3933833217545, "pagina": 3, "pageWidth": 612, "pageHeight": 792}, {"id": "var-fecha_ingreso-1763588056364", "posX": 156.03571428571428, "posY": 565.8579402534556, "pagina": 4, "pageWidth": 612, "pageHeight": 792}, {"id": "var-fecha_ingreso-1763588104196", "posX": 428.0357142857143, "posY": 288.39326354119254, "pagina": 5, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "nombre_completo", "ubicaciones": [{"id": "var-nombre_completo-1763587558613", "posX": 117.17857142857142, "posY": 124.46446110725151, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763587997920", "posX": 212.49999999999997, "posY": 262.8932276070239, "pagina": 3, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588060833", "posX": 186.99999999999997, "posY": 456.57207196416164, "pagina": 4, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588088699", "posX": 170.60714285714283, "posY": 274.4289581486716, "pagina": 5, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588131305", "posX": 356.3928571428571, "posY": 669.0723714155666, "pagina": 5, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588139243", "posX": 358.21428571428567, "posY": 672.1080899791581, "pagina": 6, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588147403", "posX": 358.82142857142856, "posY": 672.1080899791581, "pagina": 7, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588159253", "posX": 358.82142857142856, "posY": 671.5009462664399, "pagina": 8, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588166717", "posX": 356.3928571428571, "posY": 667.85808399013, "pagina": 9, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588172437", "posX": 357.60714285714283, "posY": 667.85808399013, "pagina": 10, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588179793", "posX": 355.1785714285714, "posY": 667.85808399013, "pagina": 11, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588185355", "posX": 353.96428571428567, "posY": 669.679515128285, "pagina": 12, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "nic", "ubicaciones": [{"id": "var-nic-1763587563990", "posX": 460.82142857142856, "posY": 123.85731739453321, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nic-1763588005161", "posX": 248.32142857142856, "posY": 293.85755695565723, "pagina": 3, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nic-1763588065882", "posX": 180.32142857142856, "posY": 498.46498814172435, "pagina": 4, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nic-1763588094524", "posX": 479.6428571428571, "posY": 274.4289581486716, "pagina": 5, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "sociedad", "ubicaciones": [{"id": "var-sociedad-1763587617689", "posX": 79.53571428571428, "posY": 244.0717725127566, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "nombre_campo", "ubicaciones": [{"id": "var-nombre_campo-1763587623490", "posX": 355.7857142857143, "posY": 242.85748508732001, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "nacionalidad", "ubicaciones": [{"id": "var-nacionalidad-1763587573403", "posX": 144.5, "posY": 162.1073712957861, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "fecha_nacimiento", "ubicaciones": [{"id": "var-fecha_nacimiento-1763587577645", "posX": 324.21428571428567, "posY": 161.5002275830678, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "estado_civil", "ubicaciones": [{"id": "var-estado_civil-1763587584423", "posX": 503.32142857142856, "posY": 161.5002275830678, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "domicilio", "ubicaciones": [{"id": "var-domicilio-1763587590093", "posX": 152.39285714285714, "posY": 194.28598806985602, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "horario", "ubicaciones": [{"id": "var-horario-1763587632228", "posX": 77.10714285714285, "posY": 461.429221665908, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "afp", "ubicaciones": [{"id": "var-afp-1763587641732", "posX": 210.07142857142856, "posY": 371.5719521835996, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "salud", "ubicaciones": [{"id": "var-salud-1763587646781", "posX": 162.7142857142857, "posY": 389.17911985243035, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "telefono", "ubicaciones": [{"id": "var-telefono-1763587653686", "posX": 340.60714285714283, "posY": 552.5007785736531, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "correo", "ubicaciones": [{"id": "var-correo-1763587657279", "posX": 332.10714285714283, "posY": 580.4293893586948, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "banco", "ubicaciones": [{"id": "var-banco-1763587663631", "posX": 210.67857142857142, "posY": 304.1790000718683, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "numero_cuenta", "ubicaciones": [{"id": "var-numero_cuenta-1763587668384", "posX": 405.57142857142856, "posY": 290.82183839206573, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "cargo", "ubicaciones": [{"id": "var-cargo-1763588025980", "posX": 216.14285714285714, "posY": 322.3933114534173, "pagina": 3, "pageWidth": 612, "pageHeight": 792}, {"id": "var-cargo-1763588076898", "posX": 165.75, "posY": 528.8221737776394, "pagina": 4, "pageWidth": 612, "pageHeight": 792}, {"id": "var-cargo-1763588115903", "posX": 128.7142857142857, "posY": 289.0004072539108, "pagina": 5, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "area", "ubicaciones": [{"id": "var-area-1763588036408", "posX": 218.57142857142856, "posY": 347.28620367486764, "pagina": 3, "pageWidth": 612, "pageHeight": 792}, {"id": "var-area-1763588121520", "posX": 129.92857142857142, "posY": 301.7504252209951, "pagina": 5, "pageWidth": 612, "pageHeight": 792}]}]', '2025-11-19 21:28:07.236789+00', true, 4);
INSERT INTO public.documentos_variables (id, nombre, tipo, archivo_pdf, variables, fecha_creacion, activo, holding_id) VALUES (10, 'Cont_Plazo_Fijo_Extran_SnMariano_Full', 'EXTRANJERO', 'contracts/formats/cont_plazo_fijo_extran_snmariano_full.pdf', '[{"nombre": "fecha_emision", "ubicaciones": [{"id": "var-fecha_emision-1763587549627", "posX": 210.67857142857142, "posY": 84.3929760678437, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "fecha_ingreso", "ubicaciones": [{"id": "var-fecha_ingreso-1763587982894", "posX": 501.49999999999994, "posY": 399.5005629686414, "pagina": 2, "pageWidth": 612, "pageHeight": 792}, {"id": "var-fecha_ingreso-1763588056364", "posX": 242.85714285714283, "posY": 372.7862396090362, "pagina": 4, "pageWidth": 612, "pageHeight": 792}, {"id": "var-fecha_ingreso-1763588104196", "posX": 147.53571428571428, "posY": 569.5008025297655, "pagina": 5, "pageWidth": 612, "pageHeight": 792}, {"id": "var-fecha_ingreso-1763588718240", "posX": 491.1785714285714, "posY": 157.25022159403972, "pagina": 6, "pageWidth": 612, "pageHeight": 792}, {"id": "var-fecha_ingreso-1763588733098", "posX": 463.85714285714283, "posY": 179.71453896461682, "pagina": 7, "pageWidth": 612, "pageHeight": 792}, {"id": "var-fecha_ingreso-1763589218966", "posX": 438.96428571428567, "posY": 630.2151738015955, "pagina": 3, "pageWidth": 612, "pageHeight": 792}, {"id": "var-fecha_ingreso-1763589289422", "posX": 469.32142857142856, "posY": 199.7502814843207, "pagina": 9, "pageWidth": 612, "pageHeight": 792}, {"id": "var-fecha_ingreso-1763589301479", "posX": 467.49999999999994, "posY": 198.5359940588841, "pagina": 10, "pageWidth": 612, "pageHeight": 792}, {"id": "var-fecha_ingreso-1763589315114", "posX": 421.35714285714283, "posY": 290.82183839206573, "pagina": 11, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "nombre_completo", "ubicaciones": [{"id": "var-nombre_completo-1763587558613", "posX": 121.42857142857142, "posY": 124.46446110725151, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763587997920", "posX": 198.53571428571428, "posY": 111.7144431401672, "pagina": 3, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588060833", "posX": 209.4642857142857, "posY": 263.5003713197422, "pagina": 4, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588088699", "posX": 162.10714285714283, "posY": 456.57207196416164, "pagina": 5, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588139243", "posX": 120.82142857142856, "posY": 300.5361377955585, "pagina": 6, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588147403", "posX": 140.25, "posY": 288.39326354119254, "pagina": 7, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588166717", "posX": 121.42857142857142, "posY": 319.9647366025441, "pagina": 9, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588179793", "posX": 361.25, "posY": 670.2866588410033, "pagina": 11, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588185355", "posX": 358.21428571428567, "posY": 672.1080899791581, "pagina": 12, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nombre_completo-1763588323980", "posX": 136, "posY": 629.6080300888772, "pagina": 3, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763588433916", "posX": 86.21428571428571, "posY": 414.6791557865989, "pagina": 8, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763588487449", "posX": 118.39285714285714, "posY": 326.0361737297271, "pagina": 10, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763588508532", "posX": 358.82142857142856, "posY": 673.3223774045947, "pagina": 13, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763588514477", "posX": 357, "posY": 673.3223774045947, "pagina": 14, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763588519966", "posX": 359.4285714285714, "posY": 672.1080899791581, "pagina": 15, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763588527926", "posX": 360.6428571428571, "posY": 673.929521117313, "pagina": 16, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763588533601", "posX": 358.82142857142856, "posY": 670.8938025537216, "pagina": 17, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763588539105", "posX": 357.60714285714283, "posY": 671.5009462664399, "pagina": 18, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763589323530", "posX": 183.9642857142857, "posY": 273.21467072323503, "pagina": 11, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "nic", "ubicaciones": [{"id": "var-nic-1763588005161", "posX": 231.92857142857142, "posY": 135.39304793618092, "pagina": 3, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nic-1763588065882", "posX": 244.67857142857142, "posY": 291.42898210478404, "pagina": 4, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nic-1763588094524", "posX": 188.2142857142857, "posY": 500.89356299259754, "pagina": 5, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nic-1763588403015", "posX": 317.5357142857143, "posY": 299.3218503701219, "pagina": 6, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nic-1763588415935", "posX": 323, "posY": 285.35754497760104, "pagina": 7, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nic-1763588428762", "posX": 275.6428571428571, "posY": 411.6434372230074, "pagina": 8, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nic-1763588476578", "posX": 313.8928571428571, "posY": 320.57188031526243, "pagina": 9, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nic-1763588482944", "posX": 318.1428571428571, "posY": 326.64331744244544, "pagina": 10, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nic-1763589331027", "posX": 480.24999999999994, "posY": 273.82181443595334, "pagina": 11, "pageWidth": 612, "pageHeight": 792}, {"id": "var-nic-1763636398157", "posX": 480.85714285714283, "posY": 122.6430299690966, "pagina": 1, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "sociedad", "ubicaciones": [{"id": "var-sociedad-1763588343276", "posX": 213.7142857142857, "posY": 346.071916249431, "pagina": 4, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-sociedad-1763589259218", "posX": 182.14285714285714, "posY": 165.7502335720959, "pagina": 7, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "nombre_cliente", "ubicaciones": [{"id": "var-nombre_cliente-1763589174244", "posX": 75.28571428571428, "posY": 243.46462880003833, "pagina": 1, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "nombre_campo", "ubicaciones": [{"id": "var-nombre_campo-1763587623490", "posX": 353.96428571428567, "posY": 243.46462880003833, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "nacionalidad", "ubicaciones": [{"id": "var-nacionalidad-1763587573403", "posX": 139.03571428571428, "posY": 163.32165872122272, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "fecha_nacimiento", "ubicaciones": [{"id": "var-fecha_nacimiento-1763587577645", "posX": 320.57142857142856, "posY": 162.1073712957861, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "estado_civil", "ubicaciones": [{"id": "var-estado_civil-1763587584423", "posX": 501.49999999999994, "posY": 160.28594015763122, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "domicilio", "ubicaciones": [{"id": "var-domicilio-1763587590093", "posX": 151.78571428571428, "posY": 193.6788443571377, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "horario", "ubicaciones": [{"id": "var-horario-1763587632228", "posX": 71.03571428571428, "posY": 459.0006468150348, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "afp", "ubicaciones": [{"id": "var-afp-1763587641732", "posX": 209.4642857142857, "posY": 369.7505210454447, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "salud", "ubicaciones": [{"id": "var-salud-1763587646781", "posX": 159.07142857142856, "posY": 386.14340128883885, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "telefono", "ubicaciones": [{"id": "var-telefono-1763587653686", "posX": 350.32142857142856, "posY": 550.6793474354981, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "correo", "ubicaciones": [{"id": "var-correo-1763587657279", "posX": 338.1785714285714, "posY": 578.0008145078216, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "banco", "ubicaciones": [{"id": "var-banco-1763587663631", "posX": 211.89285714285714, "posY": 303.57185635915, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "numero_cuenta", "ubicaciones": [{"id": "var-numero_cuenta-1763587668384", "posX": 410.4285714285714, "posY": 292.0361258175023, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "cargo", "ubicaciones": [{"id": "var-cargo-1763588025980", "posX": 202.17857142857142, "posY": 152.3930718922933, "pagina": 3, "pageWidth": 612, "pageHeight": 792}, {"id": "var-cargo-1763588076898", "posX": 217.35714285714283, "posY": 320.57188031526243, "pagina": 4, "pageWidth": 612, "pageHeight": 792}, {"id": "var-cargo-1763588115903", "posX": 158.4642857142857, "posY": 527.6078863522027, "pagina": 5, "pageWidth": 612, "pageHeight": 792}, {"id": "var-cargo-1763588446718", "posX": 326.0357142857143, "posY": 411.6434372230074, "pagina": 8, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-cargo-1763589342766", "posX": 133.57142857142856, "posY": 289.0004072539108, "pagina": 11, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "area", "ubicaciones": [{"id": "var-area-1763589348751", "posX": 131.75, "posY": 304.7861437845866, "pagina": 11, "pageWidth": 612, "pageHeight": 792}]}]', '2025-11-19 21:42:40.596774+00', true, 4);
INSERT INTO public.documentos_variables (id, nombre, tipo, archivo_pdf, variables, fecha_creacion, activo, holding_id) VALUES (12, 'Cont_sacar_NIC', 'EXTRANJERO', 'contracts/formats/cont_sacar_nic_wg7TeMM.pdf', '[{"nombre": "fecha_emision", "ubicaciones": [{"id": "var-fecha_emision-1763642799707", "posX": 210.67857142857142, "posY": 101.3930000239561, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "fecha_ingreso", "ubicaciones": [{"id": "var-fecha_ingreso-1763642929647", "posX": 501.49999999999994, "posY": 415.89344321203555, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "nombre_completo", "ubicaciones": [{"id": "var-nombre_completo-1763642809665", "posX": 159.07142857142856, "posY": 135.39304793618092, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "dni", "ubicaciones": [{"id": "var-dni-1763642816976", "posX": 420.1428571428571, "posY": 134.7859042234626, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "nombre_cliente", "ubicaciones": [{"id": "var-nombre_cliente-1763642832291", "posX": 126.28571428571428, "posY": 221.6074551421795, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "nombre_campo", "ubicaciones": [{"id": "var-nombre_campo-1763642846896", "posX": 359.4285714285714, "posY": 219.78602400402463, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "nacionalidad", "ubicaciones": [{"id": "var-nacionalidad-1763642854998", "posX": 162.10714285714283, "posY": 156.03593416860312, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "fecha_nacimiento", "ubicaciones": [{"id": "var-fecha_nacimiento-1763642859533", "posX": 324.82142857142856, "posY": 156.03593416860312, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "estado_civil", "ubicaciones": [{"id": "var-estado_civil-1763642864671", "posX": 479.0357142857142, "posY": 156.03593416860312, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "domicilio", "ubicaciones": [{"id": "var-domicilio-1763642904764", "posX": 200.35714285714283, "posY": 176.071676688307, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "afp", "ubicaciones": [{"id": "var-afp-1763642915742", "posX": 193.67857142857142, "posY": 382.50053901252903, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "salud", "ubicaciones": [{"id": "var-salud-1763642919478", "posX": 195.49999999999997, "posY": 401.3219941067963, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "telefono", "ubicaciones": [{"id": "var-telefono-1763642940505", "posX": 352.75, "posY": 579.8222456459765, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "correo", "ubicaciones": [{"id": "var-correo-1763642945442", "posX": 352.1428571428571, "posY": 605.9294252928635, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}]', '2025-11-20 12:49:20.096079+00', true, 4);
INSERT INTO public.documentos_variables (id, nombre, tipo, archivo_pdf, variables, fecha_creacion, activo, holding_id) VALUES (13, 'Cont_Plazo_Fijo_Chileno_full', 'CHILENO', 'contracts/formats/cont_plazo_fijo_chileno_full.pdf', '[{"nombre": "fecha_emision", "ubicaciones": [{"id": "var-fecha_emision-1763648069709", "posX": 215.53571428571428, "posY": 103.21443116211101, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "fecha_ingreso", "ubicaciones": [{"id": "var-fecha_ingreso-1763648137857", "posX": 515.4642857142857, "posY": 333.929041995065, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-fecha_ingreso-1763648251490", "posX": 248.32142857142856, "posY": 375.2148144599094, "pagina": 3, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-fecha_ingreso-1763648286360", "posX": 151.17857142857142, "posY": 566.4650839661739, "pagina": 4, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-fecha_ingreso-1763648297807", "posX": 417.71428571428567, "posY": 292.6432695302206, "pagina": 5, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "nombre_completo", "ubicaciones": [{"id": "var-nombre_completo-1763648078983", "posX": 172.42857142857142, "posY": 140.8573413506456, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763648262652", "posX": 173.03571428571428, "posY": 459.60779052775314, "pagina": 4, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763648324776", "posX": 203.99999999999997, "posY": 276.25038928682653, "pagina": 5, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763648330790", "posX": 361.85714285714283, "posY": 670.2866588410033, "pagina": 5, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763648337959", "posX": 360.0357142857143, "posY": 669.0723714155666, "pagina": 6, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763648343205", "posX": 367.32142857142856, "posY": 672.7152336918764, "pagina": 7, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763648348664", "posX": 365.49999999999994, "posY": 671.5009462664399, "pagina": 8, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763648353578", "posX": 368.5357142857143, "posY": 666.0366528519752, "pagina": 9, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763648357529", "posX": 363.07142857142856, "posY": 669.0723714155666, "pagina": 10, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763648361985", "posX": 364.8928571428571, "posY": 669.0723714155666, "pagina": 11, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763648366426", "posX": 363.6785714285714, "posY": 666.6437965646934, "pagina": 12, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-nombre_completo-1763648509103", "posX": 225.85714285714283, "posY": 262.8932276070239, "pagina": 3, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "rut", "ubicaciones": [{"id": "var-rut-1763648083010", "posX": 470.5357142857142, "posY": 139.0359102124907, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-rut-1763648229342", "posX": 254.99999999999997, "posY": 291.42898210478404, "pagina": 3, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-rut-1763648270764", "posX": 199.74999999999997, "posY": 494.2149821526962, "pagina": 4, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-rut-1763648547675", "posX": 480.85714285714283, "posY": 270.78609587236184, "pagina": 5, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "sociedad", "ubicaciones": [{"id": "var-sociedad-1763648244896", "posX": 226.4642857142857, "posY": 345.4647725367127, "pagina": 3, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "nombre_cliente", "ubicaciones": [{"id": "var-nombre_cliente-1763648091115", "posX": 85.60714285714285, "posY": 240.42891023644682, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "nombre_campo", "ubicaciones": [{"id": "var-nombre_campo-1763648095313", "posX": 389.7857142857143, "posY": 240.42891023644682, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "nacionalidad", "ubicaciones": [{"id": "var-nacionalidad-1763648100200", "posX": 159.67857142857142, "posY": 166.35737728481422, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "fecha_nacimiento", "ubicaciones": [{"id": "var-fecha_nacimiento-1763648104112", "posX": 312.07142857142856, "posY": 167.57166471025081, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "estado_civil", "ubicaciones": [{"id": "var-estado_civil-1763648107899", "posX": 479.6428571428571, "posY": 170.000239561124, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "domicilio", "ubicaciones": [{"id": "var-domicilio-1763648463774", "posX": 202.17857142857142, "posY": 197.32170663344752, "pagina": 1, "pageWidth": 612, "pageHeight": 792}]}, {"nombre": "horario", "ubicaciones": [{"id": "var-horario-1763648114670", "posX": 86.21428571428571, "posY": 452.3220659751335, "pagina": 1, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "afp", "ubicaciones": [{"id": "var-afp-1763648125302", "posX": 193.07142857142856, "posY": 308.4290060608964, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "salud", "ubicaciones": [{"id": "var-salud-1763648130117", "posX": 200.9642857142857, "posY": 323.0004551661356, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "telefono", "ubicaciones": [{"id": "var-telefono-1763648152536", "posX": 350.9285714285714, "posY": 500.2864192798792, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "correo", "ubicaciones": [{"id": "var-correo-1763648156569", "posX": 352.1428571428571, "posY": 528.8221737776394, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "banco", "ubicaciones": [{"id": "var-banco-1763648203042", "posX": 207.03571428571428, "posY": 282.9289701267278, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "numero_cuenta", "ubicaciones": [{"id": "var-numero_cuenta-1763648209252", "posX": 148.14285714285714, "posY": 281.1075389885729, "pagina": 2, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "cargo", "ubicaciones": [{"id": "var-cargo-1763648236775", "posX": 227.67857142857142, "posY": 321.17902402798074, "pagina": 3, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-cargo-1763648278485", "posX": 176.07142857142856, "posY": 527.0007426394844, "pagina": 4, "pageWidth": 595.32001, "pageHeight": 841.92004}, {"id": "var-cargo-1763648311018", "posX": 136, "posY": 288.39326354119254, "pagina": 5, "pageWidth": 595.32001, "pageHeight": 841.92004}]}, {"nombre": "area", "ubicaciones": [{"id": "var-area-1763648314162", "posX": 155.42857142857142, "posY": 300.5361377955585, "pagina": 5, "pageWidth": 595.32001, "pageHeight": 841.92004}]}]', '2025-11-20 14:19:58.690418+00', true, 4);


--
-- Data for Name: estados_discapacidad; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: folio_comercial; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.folio_comercial (id, fecha_inicio_contrato, fecha_termino_contrato, estado, cliente_id, holding_id) VALUES (1, '2025-11-05', '2026-02-19', true, 1, 3);
INSERT INTO public.folio_comercial (id, fecha_inicio_contrato, fecha_termino_contrato, estado, cliente_id, holding_id) VALUES (4, '2025-11-03', '2025-11-13', true, 4, 4);
INSERT INTO public.folio_comercial (id, fecha_inicio_contrato, fecha_termino_contrato, estado, cliente_id, holding_id) VALUES (5, '2025-11-18', '2025-12-31', true, 8, 4);
INSERT INTO public.folio_comercial (id, fecha_inicio_contrato, fecha_termino_contrato, estado, cliente_id, holding_id) VALUES (6, '2025-11-19', '2025-12-15', true, 5, 4);
INSERT INTO public.folio_comercial (id, fecha_inicio_contrato, fecha_termino_contrato, estado, cliente_id, holding_id) VALUES (2, '2025-11-04', '2025-12-31', false, 2, 4);
INSERT INTO public.folio_comercial (id, fecha_inicio_contrato, fecha_termino_contrato, estado, cliente_id, holding_id) VALUES (3, '2025-11-04', '2025-11-19', true, 3, 4);


--
-- Data for Name: horarios; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.horarios (id, nombre, holding_id, domingo_colacion, domingo_fin, domingo_inicio, domingo_minutos_colacion, jueves_colacion, jueves_fin, jueves_inicio, jueves_minutos_colacion, lunes_colacion, lunes_fin, lunes_inicio, lunes_minutos_colacion, martes_colacion, martes_fin, martes_inicio, martes_minutos_colacion, miercoles_colacion, miercoles_fin, miercoles_inicio, miercoles_minutos_colacion, sabado_colacion, sabado_fin, sabado_inicio, sabado_minutos_colacion, sociedad_id, viernes_colacion, viernes_fin, viernes_inicio, viernes_minutos_colacion) VALUES (1, 'Jornada Testing', 3, false, NULL, NULL, 0, false, NULL, NULL, 0, false, NULL, NULL, 0, false, NULL, NULL, 0, false, NULL, NULL, 0, false, NULL, NULL, 0, NULL, false, NULL, NULL, 0);
INSERT INTO public.horarios (id, nombre, holding_id, domingo_colacion, domingo_fin, domingo_inicio, domingo_minutos_colacion, jueves_colacion, jueves_fin, jueves_inicio, jueves_minutos_colacion, lunes_colacion, lunes_fin, lunes_inicio, lunes_minutos_colacion, martes_colacion, martes_fin, martes_inicio, martes_minutos_colacion, miercoles_colacion, miercoles_fin, miercoles_inicio, miercoles_minutos_colacion, sabado_colacion, sabado_fin, sabado_inicio, sabado_minutos_colacion, sociedad_id, viernes_colacion, viernes_fin, viernes_inicio, viernes_minutos_colacion) VALUES (4, 'Lunes a viernes', 4, false, NULL, NULL, 0, true, '17:00:00', '08:00:00', 60, true, '17:00:00', '08:00:00', 60, true, '17:00:00', '08:00:00', 60, true, '17:00:00', '08:00:00', 60, false, NULL, NULL, 0, 3, true, '16:00:00', '08:00:00', 60);


--
-- Data for Name: unidad_control; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.unidad_control (id, nombre, cantidad, estado, holding_id) VALUES (1, 'UNIDAD', 10, true, 3);
INSERT INTO public.unidad_control (id, nombre, cantidad, estado, holding_id) VALUES (2, 'HECTAREA', 0, true, 4);
INSERT INTO public.unidad_control (id, nombre, cantidad, estado, holding_id) VALUES (3, 'JH', 0, true, 4);
INSERT INTO public.unidad_control (id, nombre, cantidad, estado, holding_id) VALUES (4, 'PLANTA', 0, true, 4);
INSERT INTO public.unidad_control (id, nombre, cantidad, estado, holding_id) VALUES (5, 'KILO', 1, true, 4);
INSERT INTO public.unidad_control (id, nombre, cantidad, estado, holding_id) VALUES (6, 'TOTEM', 9, true, 4);


--
-- Data for Name: labores; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.labores (id, nombre, especie, estado, holding_id, unidad_control_id) VALUES (1, 'LABOR', 'MANZANO', true, 3, 1);
INSERT INTO public.labores (id, nombre, especie, estado, holding_id, unidad_control_id) VALUES (2, 'RALEO DE MANZANAS', 'Manzanas', true, 4, 4);
INSERT INTO public.labores (id, nombre, especie, estado, holding_id, unidad_control_id) VALUES (3, 'DESCOLE LINEA DE RIEGO', 'Sin especie', true, 4, 2);
INSERT INTO public.labores (id, nombre, especie, estado, holding_id, unidad_control_id) VALUES (4, 'COSECHA DE ARANDANOS', 'Arandanos', true, 4, 5);
INSERT INTO public.labores (id, nombre, especie, estado, holding_id, unidad_control_id) VALUES (5, 'DESBROTE DE NOGALES', 'Nueces', true, 4, 2);
INSERT INTO public.labores (id, nombre, especie, estado, holding_id, unidad_control_id) VALUES (6, 'COSECHA DE CEREZAS', 'Cerezas', true, 4, 6);
INSERT INTO public.labores (id, nombre, especie, estado, holding_id, unidad_control_id) VALUES (7, 'PONER TUBETOS EN MANZANOS', 'Manzanas', true, 4, 4);
INSERT INTO public.labores (id, nombre, especie, estado, holding_id, unidad_control_id) VALUES (8, 'AMARRE DE MANZANOS', 'Manzanas', true, 4, 4);
INSERT INTO public.labores (id, nombre, especie, estado, holding_id, unidad_control_id) VALUES (9, 'PLANTACION DE MANZANOS', 'Manzanas', true, 4, 4);


--
-- Data for Name: tipos_impuesto_renta; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: tipos_jornada; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: contratos_trabajadores; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.contratos_trabajadores (id, fecha_inicio_contrato, fecha_termino_contrato, contrato_generado, causal_finiquito_id, cliente_id, comuna_prestacion_servicios_id, fundo_id, documento_id, folio_comercial_id, holding_id, horario_id, labor_id, trabajador_id, region_prestacion_servicios_id, tipo_discapacidad_id, tipo_impuesto_renta_id, tipo_jornada_id) VALUES (3, '2025-11-04', '2025-12-31', true, NULL, 2, NULL, 2, NULL, 2, 4, NULL, 4, 19, NULL, NULL, NULL, NULL);
INSERT INTO public.contratos_trabajadores (id, fecha_inicio_contrato, fecha_termino_contrato, contrato_generado, causal_finiquito_id, cliente_id, comuna_prestacion_servicios_id, fundo_id, documento_id, folio_comercial_id, holding_id, horario_id, labor_id, trabajador_id, region_prestacion_servicios_id, tipo_discapacidad_id, tipo_impuesto_renta_id, tipo_jornada_id) VALUES (4, '2025-11-12', '2025-12-15', true, NULL, 5, NULL, 5, NULL, 6, 4, NULL, 7, 25, NULL, NULL, NULL, NULL);
INSERT INTO public.contratos_trabajadores (id, fecha_inicio_contrato, fecha_termino_contrato, contrato_generado, causal_finiquito_id, cliente_id, comuna_prestacion_servicios_id, fundo_id, documento_id, folio_comercial_id, holding_id, horario_id, labor_id, trabajador_id, region_prestacion_servicios_id, tipo_discapacidad_id, tipo_impuesto_renta_id, tipo_jornada_id) VALUES (5, '2025-11-12', '2025-12-15', true, NULL, 5, NULL, 5, NULL, 6, 4, NULL, 7, 26, NULL, NULL, NULL, NULL);
INSERT INTO public.contratos_trabajadores (id, fecha_inicio_contrato, fecha_termino_contrato, contrato_generado, causal_finiquito_id, cliente_id, comuna_prestacion_servicios_id, fundo_id, documento_id, folio_comercial_id, holding_id, horario_id, labor_id, trabajador_id, region_prestacion_servicios_id, tipo_discapacidad_id, tipo_impuesto_renta_id, tipo_jornada_id) VALUES (6, '2025-11-12', '2025-12-15', true, NULL, 5, NULL, 5, NULL, 6, 4, NULL, 7, 27, NULL, NULL, NULL, NULL);
INSERT INTO public.contratos_trabajadores (id, fecha_inicio_contrato, fecha_termino_contrato, contrato_generado, causal_finiquito_id, cliente_id, comuna_prestacion_servicios_id, fundo_id, documento_id, folio_comercial_id, holding_id, horario_id, labor_id, trabajador_id, region_prestacion_servicios_id, tipo_discapacidad_id, tipo_impuesto_renta_id, tipo_jornada_id) VALUES (7, '2025-11-12', '2025-12-15', true, NULL, 5, NULL, 5, NULL, 6, 4, NULL, 7, 28, NULL, NULL, NULL, NULL);
INSERT INTO public.contratos_trabajadores (id, fecha_inicio_contrato, fecha_termino_contrato, contrato_generado, causal_finiquito_id, cliente_id, comuna_prestacion_servicios_id, fundo_id, documento_id, folio_comercial_id, holding_id, horario_id, labor_id, trabajador_id, region_prestacion_servicios_id, tipo_discapacidad_id, tipo_impuesto_renta_id, tipo_jornada_id) VALUES (10, '2025-11-12', '2025-12-15', true, NULL, 5, NULL, 5, NULL, 6, 4, NULL, 7, 31, NULL, NULL, NULL, NULL);
INSERT INTO public.contratos_trabajadores (id, fecha_inicio_contrato, fecha_termino_contrato, contrato_generado, causal_finiquito_id, cliente_id, comuna_prestacion_servicios_id, fundo_id, documento_id, folio_comercial_id, holding_id, horario_id, labor_id, trabajador_id, region_prestacion_servicios_id, tipo_discapacidad_id, tipo_impuesto_renta_id, tipo_jornada_id) VALUES (8, '2025-11-12', '2025-12-15', true, NULL, 5, NULL, 5, NULL, 6, 4, NULL, 7, 29, NULL, NULL, NULL, NULL);
INSERT INTO public.contratos_trabajadores (id, fecha_inicio_contrato, fecha_termino_contrato, contrato_generado, causal_finiquito_id, cliente_id, comuna_prestacion_servicios_id, fundo_id, documento_id, folio_comercial_id, holding_id, horario_id, labor_id, trabajador_id, region_prestacion_servicios_id, tipo_discapacidad_id, tipo_impuesto_renta_id, tipo_jornada_id) VALUES (11, '2025-11-12', '2025-12-15', true, NULL, 5, NULL, 5, NULL, 6, 4, NULL, 7, 32, NULL, NULL, NULL, NULL);
INSERT INTO public.contratos_trabajadores (id, fecha_inicio_contrato, fecha_termino_contrato, contrato_generado, causal_finiquito_id, cliente_id, comuna_prestacion_servicios_id, fundo_id, documento_id, folio_comercial_id, holding_id, horario_id, labor_id, trabajador_id, region_prestacion_servicios_id, tipo_discapacidad_id, tipo_impuesto_renta_id, tipo_jornada_id) VALUES (9, '2025-11-12', '2025-12-15', true, NULL, 5, NULL, 5, NULL, 6, 4, NULL, 7, 30, NULL, NULL, NULL, NULL);
INSERT INTO public.contratos_trabajadores (id, fecha_inicio_contrato, fecha_termino_contrato, contrato_generado, causal_finiquito_id, cliente_id, comuna_prestacion_servicios_id, fundo_id, documento_id, folio_comercial_id, holding_id, horario_id, labor_id, trabajador_id, region_prestacion_servicios_id, tipo_discapacidad_id, tipo_impuesto_renta_id, tipo_jornada_id) VALUES (2, '2025-11-04', '2025-12-31', false, NULL, 2, NULL, 2, NULL, 2, 4, NULL, 4, 18, NULL, NULL, NULL, NULL);


--
-- Data for Name: supervisores; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.supervisores (id, holding_id, usuario_id) VALUES (1, 3, 10);
INSERT INTO public.supervisores (id, holding_id, usuario_id) VALUES (3, 4, 15);


--
-- Data for Name: jefes_cuadrilla; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: cuadrillas; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: cuadrillas_trabajadores; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: cuentas; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: descuentos; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: pagos_transportista; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: detalle_pagos_transportista; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: developer; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: dias_trabajados_aprobados; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: django_celery_beat_clockedschedule; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: django_celery_beat_crontabschedule; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.django_celery_beat_crontabschedule (id, minute, hour, day_of_week, day_of_month, month_of_year, timezone) VALUES (1, '0', '4', '*', '*', '*', 'America/Santiago');
INSERT INTO public.django_celery_beat_crontabschedule (id, minute, hour, day_of_week, day_of_month, month_of_year, timezone) VALUES (2, '*', '*', '*', '*', '*', 'America/Santiago');


--
-- Data for Name: django_celery_beat_intervalschedule; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: django_celery_beat_solarschedule; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: django_celery_beat_periodictask; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.django_celery_beat_periodictask (id, name, task, args, kwargs, queue, exchange, routing_key, expires, enabled, last_run_at, total_run_count, date_changed, description, crontab_id, interval_id, solar_id, one_off, start_time, priority, headers, clocked_id, expire_seconds) VALUES (2, 'revisar-configuraciones-automaticas', 'contratista_test_app.tasks.revisar_configuraciones_pendientes', '[]', '{}', 'facturas_automaticas', NULL, NULL, NULL, true, '2026-03-06 05:23:00.009663+00', 125433, '2026-03-06 05:24:00.019925+00', '', 2, NULL, NULL, false, NULL, NULL, '{}', NULL, NULL);
INSERT INTO public.django_celery_beat_periodictask (id, name, task, args, kwargs, queue, exchange, routing_key, expires, enabled, last_run_at, total_run_count, date_changed, description, crontab_id, interval_id, solar_id, one_off, start_time, priority, headers, clocked_id, expire_seconds) VALUES (1, 'celery.backend_cleanup', 'celery.backend_cleanup', '[]', '{}', NULL, NULL, NULL, NULL, true, '2026-03-05 07:00:00.00716+00', 87, '2026-03-05 07:01:10.081726+00', '', 1, NULL, NULL, false, NULL, NULL, '{}', NULL, 43200);


--
-- Data for Name: django_celery_beat_periodictasks; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.django_celery_beat_periodictasks (ident, last_update) VALUES (1, '2026-02-16 06:57:28.142816+00');


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.django_migrations (id, app, name, applied) VALUES (1, 'contenttypes', '0001_initial', '2025-11-10 11:35:20.126712+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (2, 'contenttypes', '0002_remove_content_type_name', '2025-11-10 11:35:20.135256+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (3, 'auth', '0001_initial', '2025-11-10 11:35:20.188181+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (4, 'auth', '0002_alter_permission_name_max_length', '2025-11-10 11:35:20.194178+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (5, 'auth', '0003_alter_user_email_max_length', '2025-11-10 11:35:20.202192+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (6, 'auth', '0004_alter_user_username_opts', '2025-11-10 11:35:20.20844+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (7, 'auth', '0005_alter_user_last_login_null', '2025-11-10 11:35:20.2139+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (8, 'auth', '0006_require_contenttypes_0002', '2025-11-10 11:35:20.215535+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (9, 'auth', '0007_alter_validators_add_error_messages', '2025-11-10 11:35:20.223067+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (10, 'auth', '0008_alter_user_username_max_length', '2025-11-10 11:35:20.230284+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (11, 'auth', '0009_alter_user_last_name_max_length', '2025-11-10 11:35:20.235972+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (12, 'auth', '0010_alter_group_name_max_length', '2025-11-10 11:35:20.245588+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (13, 'auth', '0011_update_proxy_permissions', '2025-11-10 11:35:20.251271+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (14, 'auth', '0012_alter_user_first_name_max_length', '2025-11-10 11:35:20.25737+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (15, 'contratista_test_app', '0001_initial', '2025-11-10 11:35:30.35094+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (16, 'admin', '0001_initial', '2025-11-10 11:35:38.851021+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (17, 'admin', '0002_logentry_remove_auto_add', '2025-11-10 11:35:38.888775+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (18, 'admin', '0003_logentry_add_action_flag_choices', '2025-11-10 11:35:38.981709+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (19, 'django_celery_beat', '0001_initial', '2025-11-10 11:35:39.03514+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (20, 'django_celery_beat', '0002_auto_20161118_0346', '2025-11-10 11:35:39.054901+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (21, 'django_celery_beat', '0003_auto_20161209_0049', '2025-11-10 11:35:39.072339+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (22, 'django_celery_beat', '0004_auto_20170221_0000', '2025-11-10 11:35:39.081198+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (23, 'django_celery_beat', '0005_add_solarschedule_events_choices', '2025-11-10 11:35:39.087605+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (24, 'django_celery_beat', '0006_auto_20180322_0932', '2025-11-10 11:35:39.138257+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (25, 'django_celery_beat', '0007_auto_20180521_0826', '2025-11-10 11:35:39.161958+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (26, 'django_celery_beat', '0008_auto_20180914_1922', '2025-11-10 11:35:39.235354+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (27, 'django_celery_beat', '0006_auto_20180210_1226', '2025-11-10 11:35:39.2732+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (28, 'django_celery_beat', '0006_periodictask_priority', '2025-11-10 11:35:39.286289+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (29, 'django_celery_beat', '0009_periodictask_headers', '2025-11-10 11:35:39.303627+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (30, 'django_celery_beat', '0010_auto_20190429_0326', '2025-11-10 11:35:39.702909+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (31, 'django_celery_beat', '0011_auto_20190508_0153', '2025-11-10 11:35:39.729221+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (32, 'django_celery_beat', '0012_periodictask_expire_seconds', '2025-11-10 11:35:39.74297+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (33, 'django_celery_beat', '0013_auto_20200609_0727', '2025-11-10 11:35:39.758444+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (34, 'django_celery_beat', '0014_remove_clockedschedule_enabled', '2025-11-10 11:35:39.765658+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (35, 'django_celery_beat', '0015_edit_solarschedule_events_choices', '2025-11-10 11:35:39.775164+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (36, 'django_celery_beat', '0016_alter_crontabschedule_timezone', '2025-11-10 11:35:39.790207+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (37, 'django_celery_beat', '0017_alter_crontabschedule_month_of_year', '2025-11-10 11:35:39.801659+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (38, 'django_celery_beat', '0018_improve_crontab_helptext', '2025-11-10 11:35:39.814506+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (39, 'django_celery_beat', '0019_alter_periodictasks_options', '2025-11-10 11:35:39.820123+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (40, 'oauth2_provider', '0001_initial', '2025-11-10 11:35:40.474932+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (41, 'oauth2_provider', '0002_auto_20190406_1805', '2025-11-10 11:35:40.561592+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (42, 'oauth2_provider', '0003_auto_20201211_1314', '2025-11-10 11:35:40.603065+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (43, 'oauth2_provider', '0004_auto_20200902_2022', '2025-11-10 11:35:41.089161+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (44, 'oauth2_provider', '0005_auto_20211222_2352', '2025-11-10 11:35:41.699051+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (45, 'oauth2_provider', '0006_alter_application_client_secret', '2025-11-10 11:35:41.843745+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (46, 'oauth2_provider', '0007_application_post_logout_redirect_uris', '2025-11-10 11:35:41.885712+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (47, 'oauth2_provider', '0008_alter_accesstoken_token', '2025-11-10 11:35:41.927745+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (48, 'oauth2_provider', '0009_add_hash_client_secret', '2025-11-10 11:35:41.971183+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (49, 'oauth2_provider', '0010_application_allowed_origins', '2025-11-10 11:35:42.023011+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (50, 'oauth2_provider', '0011_refreshtoken_token_family', '2025-11-10 11:35:42.09959+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (51, 'oauth2_provider', '0012_add_token_checksum', '2025-11-10 11:35:42.523541+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (52, 'sessions', '0001_initial', '2025-11-10 11:35:42.543921+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (53, 'contratista_test_app', '0002_remove_contratotrabajador_empresa_transporte_and_more', '2025-11-12 15:00:29.049501+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (54, 'contratista_test_app', '0003_remove_labores_field', '2025-11-20 19:34:34.748048+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (55, 'contratista_test_app', '0004_remove_foliocomercial_valor_facturacion_and_more', '2025-11-20 19:34:35.264266+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (56, 'contratista_test_app', '0005_add_labores_with_through', '2025-11-20 19:34:35.372421+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (57, 'contratista_test_app', '0006_holding_firma_empleador', '2025-11-25 12:01:06.894605+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (58, 'contratista_test_app', '0007_empresastransporte_comuna', '2025-12-28 04:35:02.769856+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (59, 'contratista_test_app', '0008_empresastransporte_banco_and_more', '2025-12-29 02:03:38.027888+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (60, 'contratista_test_app', '0009_empresastransporte_alias_and_more', '2026-01-02 17:13:13.973545+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (61, 'contratista_test_app', '0010_remove_contactosclientes_rut_contacto_and_more', '2026-01-20 16:26:13.084908+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (62, 'contratista_test_app', '0011_remove_horarios_horas_domingo_and_more', '2026-01-26 07:46:06.733903+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (63, 'contratista_test_app', '0012_horarios_domingo_colacion_horarios_domingo_fin_and_more', '2026-01-26 18:03:12.669028+00');
INSERT INTO public.django_migrations (id, app, name, applied) VALUES (64, 'contratista_test_app', '0013_personaltrabajadores_huella_digital', '2026-02-04 18:32:44.753626+00');


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: documentos_chofer; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.documentos_chofer (id, tipo, imagen, documentos_rutas, fecha_subida, chofer_id) VALUES (1, 'foto_licencia_frontal', 'transporte/archivos_choferes/imagenes/FB-IMG-1761082342573.jpg', '[]', '2025-11-10 13:41:30.504271+00', 1);
INSERT INTO public.documentos_chofer (id, tipo, imagen, documentos_rutas, fecha_subida, chofer_id) VALUES (2, 'foto_licencia_trasera', 'transporte/archivos_choferes/imagenes/G2C1GdOWcAAe20W.png', '[]', '2025-11-10 13:41:30.508615+00', 1);
INSERT INTO public.documentos_chofer (id, tipo, imagen, documentos_rutas, fecha_subida, chofer_id) VALUES (3, 'foto_cedula_frontal', 'transporte/archivos_choferes/imagenes/72575616_2593468037380741_118914175408799744_n.jpg', '[]', '2025-11-10 13:41:30.511659+00', 1);
INSERT INTO public.documentos_chofer (id, tipo, imagen, documentos_rutas, fecha_subida, chofer_id) VALUES (4, 'foto_cedula_trasera', 'transporte/archivos_choferes/imagenes/ffee.jpeg', '[]', '2025-11-10 13:41:30.515755+00', 1);
INSERT INTO public.documentos_chofer (id, tipo, imagen, documentos_rutas, fecha_subida, chofer_id) VALUES (5, 'documentos_varios', '', '["transporte/archivos_choferes/documentos/chofer_1_1762782090_Errores-Archivo-Masivo (3) (1).pdf"]', '2025-11-10 13:41:30.519279+00', 1);


--
-- Data for Name: documentos_vehiculo; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.documentos_vehiculo (id, tipo, documentos_rutas, fecha_subida, vehiculo_id) VALUES (1, 'documentos_varios', '["transporte/archivos_vehiculos/documentos/vehiculo_1_1762781846_contrato_GENERAL CARRERA.pdf"]', '2025-11-10 13:37:26.515846+00', 1);


--
-- Data for Name: enlaces_auto_registro; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.enlaces_auto_registro (id, token, fecha_creacion, fecha_expiracion, ruts_permitidos, activo, usuario_creador_id, holding_id, perfil_id) VALUES (1, 'SutkNC6mOG4BJh8a', '2025-11-12 11:04:35.119792+00', '2025-11-13 11:04:35.118463+00', NULL, true, 12, 4, 12);
INSERT INTO public.enlaces_auto_registro (id, token, fecha_creacion, fecha_expiracion, ruts_permitidos, activo, usuario_creador_id, holding_id, perfil_id) VALUES (2, 'egUnIF4TocccR0o9', '2025-11-12 11:14:32.257939+00', '2025-11-13 11:14:32.255553+00', NULL, true, 12, 4, 12);


--
-- Data for Name: facturas_sii_distribuidas; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: facturas_sii_por_distribuir; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: facturas_venta_sii_distribuidas; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: facturas_venta_sii_por_distribuir; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: fc_labor_pago; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.fc_labor_pago (id, valor_pago_trabajador, valor_facturacion, folio_id, holding_id, labor_id) VALUES (3, 450, 675, 2, 4, 4);
INSERT INTO public.fc_labor_pago (id, valor_pago_trabajador, valor_facturacion, folio_id, holding_id, labor_id) VALUES (4, 2000, 3000, 2, 4, 6);
INSERT INTO public.fc_labor_pago (id, valor_pago_trabajador, valor_facturacion, folio_id, holding_id, labor_id) VALUES (7, 10000, 15000, 4, 4, 5);
INSERT INTO public.fc_labor_pago (id, valor_pago_trabajador, valor_facturacion, folio_id, holding_id, labor_id) VALUES (8, 2000, 3000, 5, 4, 6);
INSERT INTO public.fc_labor_pago (id, valor_pago_trabajador, valor_facturacion, folio_id, holding_id, labor_id) VALUES (9, 65, 97, 6, 4, 7);
INSERT INTO public.fc_labor_pago (id, valor_pago_trabajador, valor_facturacion, folio_id, holding_id, labor_id) VALUES (10, 75, 113, 6, 4, 8);
INSERT INTO public.fc_labor_pago (id, valor_pago_trabajador, valor_facturacion, folio_id, holding_id, labor_id) VALUES (11, 200, 300, 6, 4, 9);
INSERT INTO public.fc_labor_pago (id, valor_pago_trabajador, valor_facturacion, folio_id, holding_id, labor_id) VALUES (13, 300, 450, 3, 4, 2);


--
-- Data for Name: folio_comercial_fundos; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.folio_comercial_fundos (id, foliocomercial_id, camposclientes_id) VALUES (1, 1, 1);
INSERT INTO public.folio_comercial_fundos (id, foliocomercial_id, camposclientes_id) VALUES (2, 2, 2);
INSERT INTO public.folio_comercial_fundos (id, foliocomercial_id, camposclientes_id) VALUES (3, 3, 3);
INSERT INTO public.folio_comercial_fundos (id, foliocomercial_id, camposclientes_id) VALUES (4, 4, 4);
INSERT INTO public.folio_comercial_fundos (id, foliocomercial_id, camposclientes_id) VALUES (5, 5, 10);
INSERT INTO public.folio_comercial_fundos (id, foliocomercial_id, camposclientes_id) VALUES (6, 6, 5);


--
-- Data for Name: folio_comercial_horarios; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.folio_comercial_horarios (id, foliocomercial_id, horarios_id) VALUES (1, 1, 1);
INSERT INTO public.folio_comercial_horarios (id, foliocomercial_id, horarios_id) VALUES (7, 3, 4);


--
-- Data for Name: folio_comercial_transportistas; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.folio_comercial_transportistas (id, foliocomercial_id, empresastransporte_id) VALUES (1, 1, 1);
INSERT INTO public.folio_comercial_transportistas (id, foliocomercial_id, empresastransporte_id) VALUES (22, 2, 2);
INSERT INTO public.folio_comercial_transportistas (id, foliocomercial_id, empresastransporte_id) VALUES (23, 2, 3);
INSERT INTO public.folio_comercial_transportistas (id, foliocomercial_id, empresastransporte_id) VALUES (24, 2, 4);
INSERT INTO public.folio_comercial_transportistas (id, foliocomercial_id, empresastransporte_id) VALUES (27, 4, 4);
INSERT INTO public.folio_comercial_transportistas (id, foliocomercial_id, empresastransporte_id) VALUES (28, 5, 2);
INSERT INTO public.folio_comercial_transportistas (id, foliocomercial_id, empresastransporte_id) VALUES (29, 5, 3);
INSERT INTO public.folio_comercial_transportistas (id, foliocomercial_id, empresastransporte_id) VALUES (30, 6, 8);
INSERT INTO public.folio_comercial_transportistas (id, foliocomercial_id, empresastransporte_id) VALUES (32, 3, 2);


--
-- Data for Name: folio_comercial_vehiculos; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.folio_comercial_vehiculos (id, foliocomercial_id, vehiculostransporte_id) VALUES (1, 1, 1);
INSERT INTO public.folio_comercial_vehiculos (id, foliocomercial_id, vehiculostransporte_id) VALUES (48, 2, 2);
INSERT INTO public.folio_comercial_vehiculos (id, foliocomercial_id, vehiculostransporte_id) VALUES (49, 2, 3);
INSERT INTO public.folio_comercial_vehiculos (id, foliocomercial_id, vehiculostransporte_id) VALUES (50, 2, 4);
INSERT INTO public.folio_comercial_vehiculos (id, foliocomercial_id, vehiculostransporte_id) VALUES (51, 2, 5);
INSERT INTO public.folio_comercial_vehiculos (id, foliocomercial_id, vehiculostransporte_id) VALUES (52, 4, 5);
INSERT INTO public.folio_comercial_vehiculos (id, foliocomercial_id, vehiculostransporte_id) VALUES (53, 5, 2);
INSERT INTO public.folio_comercial_vehiculos (id, foliocomercial_id, vehiculostransporte_id) VALUES (54, 5, 3);
INSERT INTO public.folio_comercial_vehiculos (id, foliocomercial_id, vehiculostransporte_id) VALUES (55, 6, 6);
INSERT INTO public.folio_comercial_vehiculos (id, foliocomercial_id, vehiculostransporte_id) VALUES (56, 3, 2);


--
-- Data for Name: tramos_transportista; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.tramos_transportista (id, origen, destino, comentario, unidad_pago, holding_id) VALUES (2, 'CAMPAMENTOS', 'LAS MERCEDES', 'Desde campamentos Lucero-Maitenes a las Mercedes', 'VIAJE', 4);
INSERT INTO public.tramos_transportista (id, origen, destino, comentario, unidad_pago, holding_id) VALUES (3, 'RETIRO', 'LA SEXTA', 'Desde Retiro al predio la sexta', 'PASAJERO', 4);
INSERT INTO public.tramos_transportista (id, origen, destino, comentario, unidad_pago, holding_id) VALUES (4, 'CAMPAMENTOS', 'APF', 'Desde los campamentos al Fundo Los Cibeles de AFP', 'VIAJE', 4);
INSERT INTO public.tramos_transportista (id, origen, destino, comentario, unidad_pago, holding_id) VALUES (5, 'LAS OBRAS', 'NUEVA ESPERANZA', 'Desde las obras a nueva esperanza PORVENIR', 'PASAJERO', 4);
INSERT INTO public.tramos_transportista (id, origen, destino, comentario, unidad_pago, holding_id) VALUES (6, 'CAMPAMENTOS', 'NUEVA ESPERANZA', 'Nueva esperanza Porvenir', 'PASAJERO', 4);
INSERT INTO public.tramos_transportista (id, origen, destino, comentario, unidad_pago, holding_id) VALUES (7, 'LONGAVI', 'LAS MERCEDES', 'Desde Longavi a Porvenir Las Mercedes', 'PASAJERO', 4);
INSERT INTO public.tramos_transportista (id, origen, destino, comentario, unidad_pago, holding_id) VALUES (8, 'LAS OBRAS', 'EL EMBOQUE', 'Desde las obras a San Mariano', 'VIAJE', 4);
INSERT INTO public.tramos_transportista (id, origen, destino, comentario, unidad_pago, holding_id) VALUES (9, 'LAS OBRAS', 'SAN LEON', 'Desde las obras -Linares / Agrícola San Leon', 'PASAJERO', 4);


--
-- Data for Name: folios_transportes; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: haberes; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: historial_cambios_folio; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: registro_pagos_efectivo; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: registro_pagos_transferencia; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: historial_cambios_pago; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: horas_extraordinarias; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: jefes_cuadrilla_trabajadores; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: licencias_medicas; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: meses_cerrados; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: modulos_movil; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.modulos_movil (id, nombre, holding_id) VALUES (4, 'GESTION TRABAJADORES', 3);
INSERT INTO public.modulos_movil (id, nombre, holding_id) VALUES (5, 'MANO DE OBRA', 3);
INSERT INTO public.modulos_movil (id, nombre, holding_id) VALUES (6, 'COSECHA', 3);
INSERT INTO public.modulos_movil (id, nombre, holding_id) VALUES (7, 'GESTION TRABAJADORES', 4);
INSERT INTO public.modulos_movil (id, nombre, holding_id) VALUES (8, 'MANO DE OBRA', 4);
INSERT INTO public.modulos_movil (id, nombre, holding_id) VALUES (9, 'COSECHA', 4);


--
-- Data for Name: modulos_web; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (12, 'ADMINISTRACION', 3);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (13, 'RECURSOS HUMANOS', 3);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (14, 'CLIENTES', 3);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (15, 'COMERCIAL', 3);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (16, 'TRANSPORTE', 3);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (17, 'PAGOS', 3);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (18, 'INFORMES', 3);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (19, 'LEYES SOCIALES', 3);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (20, 'COSTOS', 3);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (21, 'TESORERIA', 3);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (22, 'ADMINISTRACION', 4);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (23, 'RECURSOS HUMANOS', 4);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (24, 'CLIENTES', 4);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (25, 'COMERCIAL', 4);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (26, 'TRANSPORTE', 4);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (27, 'PAGOS', 4);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (28, 'INFORMES', 4);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (29, 'LEYES SOCIALES', 4);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (30, 'COSTOS', 4);
INSERT INTO public.modulos_web (id, nombre, holding_id) VALUES (31, 'TESORERIA', 4);


--
-- Data for Name: oauth2_provider_application; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: oauth2_provider_idtoken; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: oauth2_provider_accesstoken; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: oauth2_provider_grant; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: oauth2_provider_refreshtoken; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: perfiles_modulos_movil; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.perfiles_modulos_movil (id, perfiles_id, modulosmovil_id) VALUES (1, 8, 4);
INSERT INTO public.perfiles_modulos_movil (id, perfiles_id, modulosmovil_id) VALUES (2, 8, 5);
INSERT INTO public.perfiles_modulos_movil (id, perfiles_id, modulosmovil_id) VALUES (3, 8, 6);
INSERT INTO public.perfiles_modulos_movil (id, perfiles_id, modulosmovil_id) VALUES (7, 18, 8);
INSERT INTO public.perfiles_modulos_movil (id, perfiles_id, modulosmovil_id) VALUES (8, 18, 9);
INSERT INTO public.perfiles_modulos_movil (id, perfiles_id, modulosmovil_id) VALUES (9, 18, 7);
INSERT INTO public.perfiles_modulos_movil (id, perfiles_id, modulosmovil_id) VALUES (10, 17, 8);
INSERT INTO public.perfiles_modulos_movil (id, perfiles_id, modulosmovil_id) VALUES (11, 17, 9);
INSERT INTO public.perfiles_modulos_movil (id, perfiles_id, modulosmovil_id) VALUES (12, 17, 7);


--
-- Data for Name: perfiles_modulos_web; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (11, 7, 12);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (12, 7, 13);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (13, 7, 14);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (14, 7, 15);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (15, 7, 16);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (16, 7, 17);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (17, 7, 18);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (18, 7, 19);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (19, 7, 20);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (20, 7, 21);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (21, 8, 12);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (22, 8, 13);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (23, 8, 14);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (24, 8, 15);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (25, 8, 16);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (26, 8, 17);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (27, 8, 18);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (28, 8, 19);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (29, 8, 20);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (30, 8, 21);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (31, 10, 22);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (32, 10, 23);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (33, 10, 24);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (34, 10, 25);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (35, 10, 26);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (36, 10, 27);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (37, 10, 28);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (38, 10, 29);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (39, 10, 30);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (40, 10, 31);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (51, 17, 22);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (52, 17, 23);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (53, 17, 26);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (54, 17, 27);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (55, 17, 28);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (56, 17, 29);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (57, 18, 22);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (58, 18, 23);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (59, 18, 24);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (60, 18, 25);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (61, 18, 26);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (62, 18, 27);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (63, 18, 28);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (64, 18, 29);
INSERT INTO public.perfiles_modulos_web (id, perfiles_id, modulosweb_id) VALUES (65, 18, 30);


--
-- Data for Name: submodulos_movil; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (11, 'ENROLLAR TRABAJADOR', 3, 4);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (12, 'ASIGNAR QR', 3, 4);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (13, 'INGRESAR RENDIMIENTO PERSONA MANO OBRA', 3, 5);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (14, 'INFORMES PERSONA MANO OBRA', 3, 5);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (15, 'INGRESAR RENDIMIENTO CUADRILLA MANO OBRA', 3, 5);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (16, 'INFORMES CUADRILLA MANO OBRA', 3, 5);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (17, 'INGRESAR RENDIMIENTO PERSONA COSECHA', 3, 6);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (18, 'INFORMES PERSONA COSECHA', 3, 6);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (19, 'INGRESAR RENDIMIENTO CUADRILLA COSECHA', 3, 6);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (20, 'INFORMES CUADRILLA COSECHA', 3, 6);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (21, 'ENROLLAR TRABAJADOR', 4, 7);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (22, 'ASIGNAR QR', 4, 7);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (23, 'INGRESAR RENDIMIENTO PERSONA MANO OBRA', 4, 8);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (24, 'INFORMES PERSONA MANO OBRA', 4, 8);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (25, 'INGRESAR RENDIMIENTO CUADRILLA MANO OBRA', 4, 8);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (26, 'INFORMES CUADRILLA MANO OBRA', 4, 8);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (27, 'INGRESAR RENDIMIENTO PERSONA COSECHA', 4, 9);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (28, 'INFORMES PERSONA COSECHA', 4, 9);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (29, 'INGRESAR RENDIMIENTO CUADRILLA COSECHA', 4, 9);
INSERT INTO public.submodulos_movil (id, nombre, holding_id, modulo_id) VALUES (30, 'INFORMES CUADRILLA COSECHA', 4, 9);


--
-- Data for Name: perfiles_submodulos_movil; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (1, 8, 11);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (2, 8, 12);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (3, 8, 13);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (4, 8, 14);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (5, 8, 15);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (6, 8, 16);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (7, 8, 17);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (8, 8, 18);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (9, 8, 19);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (10, 8, 20);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (21, 18, 21);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (22, 18, 22);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (23, 18, 23);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (24, 18, 24);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (25, 18, 25);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (26, 18, 26);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (27, 18, 27);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (28, 18, 28);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (29, 18, 29);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (30, 18, 30);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (31, 17, 21);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (32, 17, 22);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (33, 17, 23);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (34, 17, 24);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (35, 17, 25);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (36, 17, 26);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (37, 17, 27);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (38, 17, 28);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (39, 17, 29);
INSERT INTO public.perfiles_submodulos_movil (id, perfiles_id, submodulosmovil_id) VALUES (40, 17, 30);


--
-- Data for Name: submodulos_web; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (49, 'PERSONAL', 3, 12);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (50, 'PERFILES', 3, 12);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (51, 'USUARIOS', 3, 12);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (52, 'AREAS/CARGOS ADMINISTRACION', 3, 12);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (53, 'PARAMETROS ADMINISTRACION', 3, 12);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (54, 'CONTRATACION PERSONAL', 3, 13);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (55, 'CREAR CONTRATO', 3, 13);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (56, 'CONTRATOS FIRMADOS', 3, 13);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (57, 'MAESTRO TRABAJADORES', 3, 13);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (58, 'PARAMETROS RECURSOS HUMANOS', 3, 13);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (59, 'GENERAR CODIGOS QR', 3, 13);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (60, 'FORMATOS', 3, 13);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (61, 'LIBRO DE REMUNERACIONES ELECTRONICO', 3, 13);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (62, 'ADMINISTRAR CLIENTES', 3, 14);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (63, 'AREA/CARGOS CLIENTES', 3, 14);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (64, 'CONTACTOS', 3, 14);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (65, 'ACUERDO COMERCIAL', 3, 15);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (66, 'PARAMETROS COMERCIAL', 3, 15);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (67, 'TRANSPORTISTAS', 3, 16);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (68, 'VEHICULOS', 3, 16);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (69, 'CHOFERES', 3, 16);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (70, 'TRAMOS', 3, 16);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (71, 'ACUERDO TRANSPORTES', 3, 16);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (72, 'PAGO TRANSPORTISTA', 3, 16);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (73, 'PROFORMA', 3, 16);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (74, 'TRANSFERENCIA', 3, 17);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (75, 'EFECTIVO', 3, 17);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (76, 'PAGOS REALIZADOS', 3, 17);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (77, 'REPROCESAR PAGO', 3, 17);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (78, 'INFORME RENDIMIENTO', 3, 18);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (79, 'INFORME PAGO', 3, 18);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (80, 'INFORME TRANSPORTISTA', 3, 18);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (81, 'INFORME DIAS TRABAJADOS', 3, 19);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (82, 'HABERES DESCUENTOS', 3, 19);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (83, 'ARCHIVO PREVIRED', 3, 19);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (84, 'LIQUIDACIONES', 3, 19);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (85, 'ASIGNACION HABERES', 3, 19);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (86, 'ASIGNACION DESCUENTOS', 3, 19);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (87, 'FACTURAS COMPRA AUTOMATICO', 3, 20);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (88, 'FACTURAS COMPRA DISTRIBUIDAS', 3, 20);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (89, 'PARAMETROS FACTURA COMPRA', 3, 20);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (90, 'FACTURAS VENTA AUTOMATICO', 3, 20);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (91, 'FACTURAS VENTA DISTRIBUIDAS', 3, 20);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (92, 'PARAMETROS FACTURA VENTA', 3, 20);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (93, 'CUENTAS', 3, 20);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (94, 'PAGOS INGRESOS', 3, 21);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (95, 'PAGOS EGRESOS', 3, 21);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (96, 'HISTORIAL PAGOS', 3, 21);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (97, 'SOCIEDADES', 3, 12);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (98, 'AFP', 3, 12);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (99, 'SALUD', 3, 12);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (100, 'CASAS', 3, 13);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (101, 'HORARIOS', 3, 13);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (102, 'PARAMETROS RH', 3, 13);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (103, 'GENERACION CONTRATOS', 3, 13);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (104, 'PARAMETROS CLIENTES', 3, 14);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (105, 'UNIDAD DE CONTROL', 3, 15);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (106, 'LABORES', 3, 15);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (107, 'PARAMETROS TRANSPORTE', 3, 16);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (108, 'PARAMETROS LEYES SOCIALES', 3, 19);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (109, 'PARAMETROS COSTOS', 3, 20);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (110, 'FACTURAS COMPRAS', 3, 20);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (111, 'FACTURAS VENTAS', 3, 20);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (112, 'PERSONAL', 4, 22);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (113, 'PERFILES', 4, 22);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (114, 'USUARIOS', 4, 22);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (115, 'AREAS/CARGOS ADMINISTRACION', 4, 22);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (116, 'PARAMETROS ADMINISTRACION', 4, 22);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (117, 'SOCIEDADES', 4, 22);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (118, 'AFP', 4, 22);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (119, 'SALUD', 4, 22);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (120, 'CONTRATACION PERSONAL', 4, 23);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (121, 'CREAR CONTRATO', 4, 23);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (122, 'CONTRATOS FIRMADOS', 4, 23);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (123, 'MAESTRO TRABAJADORES', 4, 23);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (124, 'PARAMETROS RECURSOS HUMANOS', 4, 23);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (125, 'GENERAR CODIGOS QR', 4, 23);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (126, 'FORMATOS', 4, 23);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (127, 'LIBRO DE REMUNERACIONES ELECTRONICO', 4, 23);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (128, 'CASAS', 4, 23);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (129, 'HORARIOS', 4, 23);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (130, 'PARAMETROS RH', 4, 23);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (131, 'GENERACION CONTRATOS', 4, 23);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (132, 'ADMINISTRAR CLIENTES', 4, 24);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (133, 'AREA/CARGOS CLIENTES', 4, 24);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (134, 'CONTACTOS', 4, 24);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (135, 'PARAMETROS CLIENTES', 4, 24);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (136, 'ACUERDO COMERCIAL', 4, 25);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (137, 'PARAMETROS COMERCIAL', 4, 25);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (138, 'UNIDAD DE CONTROL', 4, 25);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (139, 'LABORES', 4, 25);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (140, 'TRANSPORTISTAS', 4, 26);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (141, 'VEHICULOS', 4, 26);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (142, 'CHOFERES', 4, 26);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (143, 'TRAMOS', 4, 26);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (144, 'ACUERDO TRANSPORTES', 4, 26);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (145, 'PAGO TRANSPORTISTA', 4, 26);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (146, 'PROFORMA', 4, 26);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (147, 'PARAMETROS TRANSPORTE', 4, 26);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (148, 'TRANSFERENCIA', 4, 27);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (149, 'EFECTIVO', 4, 27);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (150, 'PAGOS REALIZADOS', 4, 27);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (151, 'REPROCESAR PAGO', 4, 27);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (152, 'INFORME RENDIMIENTO', 4, 28);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (153, 'INFORME PAGO', 4, 28);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (154, 'INFORME TRANSPORTISTA', 4, 28);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (155, 'INFORME DIAS TRABAJADOS', 4, 29);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (156, 'HABERES DESCUENTOS', 4, 29);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (157, 'ARCHIVO PREVIRED', 4, 29);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (158, 'LIQUIDACIONES', 4, 29);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (159, 'ASIGNACION HABERES', 4, 29);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (160, 'ASIGNACION DESCUENTOS', 4, 29);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (161, 'PARAMETROS LEYES SOCIALES', 4, 29);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (162, 'FACTURAS COMPRA AUTOMATICO', 4, 30);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (163, 'FACTURAS COMPRA DISTRIBUIDAS', 4, 30);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (164, 'PARAMETROS FACTURA COMPRA', 4, 30);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (165, 'FACTURAS VENTA AUTOMATICO', 4, 30);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (166, 'FACTURAS VENTA DISTRIBUIDAS', 4, 30);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (167, 'PARAMETROS FACTURA VENTA', 4, 30);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (168, 'CUENTAS', 4, 30);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (169, 'PARAMETROS COSTOS', 4, 30);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (170, 'FACTURAS COMPRAS', 4, 30);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (171, 'FACTURAS VENTAS', 4, 30);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (172, 'PAGOS INGRESOS', 4, 31);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (173, 'PAGOS EGRESOS', 4, 31);
INSERT INTO public.submodulos_web (id, nombre, holding_id, modulo_id) VALUES (174, 'HISTORIAL PAGOS', 4, 31);


--
-- Data for Name: perfiles_submodulos_web; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (49, 7, 49);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (50, 7, 50);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (51, 7, 51);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (52, 7, 52);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (53, 7, 53);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (54, 7, 54);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (55, 7, 55);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (56, 7, 56);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (57, 7, 57);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (58, 7, 58);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (59, 7, 59);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (60, 7, 60);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (61, 7, 61);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (62, 7, 62);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (63, 7, 63);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (64, 7, 64);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (65, 7, 65);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (66, 7, 66);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (67, 7, 67);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (68, 7, 68);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (69, 7, 69);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (70, 7, 70);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (71, 7, 71);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (72, 7, 72);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (73, 7, 73);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (74, 7, 74);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (75, 7, 75);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (76, 7, 76);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (77, 7, 77);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (78, 7, 78);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (79, 7, 79);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (80, 7, 80);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (81, 7, 81);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (82, 7, 82);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (83, 7, 83);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (84, 7, 84);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (85, 7, 85);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (86, 7, 86);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (87, 7, 87);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (88, 7, 88);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (89, 7, 89);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (90, 7, 90);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (91, 7, 91);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (92, 7, 92);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (93, 7, 93);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (94, 7, 94);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (95, 7, 95);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (96, 7, 96);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (97, 8, 49);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (98, 8, 50);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (99, 8, 51);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (100, 8, 52);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (101, 8, 53);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (102, 8, 54);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (103, 8, 55);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (104, 8, 56);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (105, 8, 57);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (106, 8, 58);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (107, 8, 59);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (108, 8, 60);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (109, 8, 61);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (110, 8, 62);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (111, 8, 63);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (112, 8, 64);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (113, 8, 65);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (114, 8, 66);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (115, 8, 67);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (116, 8, 68);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (117, 8, 69);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (118, 8, 70);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (119, 8, 71);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (120, 8, 72);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (121, 8, 73);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (122, 8, 74);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (123, 8, 75);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (124, 8, 76);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (125, 8, 77);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (126, 8, 78);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (127, 8, 79);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (128, 8, 80);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (129, 8, 81);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (130, 8, 82);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (131, 8, 83);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (132, 8, 84);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (133, 8, 85);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (134, 8, 86);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (135, 8, 87);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (136, 8, 88);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (137, 8, 89);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (138, 8, 90);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (139, 8, 91);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (140, 8, 92);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (141, 8, 93);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (142, 8, 94);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (143, 8, 95);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (144, 8, 96);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (145, 7, 97);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (146, 7, 98);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (147, 7, 99);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (148, 7, 100);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (149, 7, 101);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (150, 7, 102);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (151, 7, 103);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (152, 7, 104);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (153, 7, 105);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (154, 7, 106);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (155, 7, 107);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (156, 7, 108);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (157, 7, 109);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (158, 7, 110);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (159, 7, 111);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (160, 10, 128);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (161, 10, 129);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (162, 10, 130);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (163, 10, 131);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (164, 10, 132);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (165, 10, 133);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (166, 10, 134);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (167, 10, 135);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (168, 10, 136);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (169, 10, 137);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (170, 10, 138);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (171, 10, 139);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (172, 10, 140);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (173, 10, 141);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (174, 10, 142);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (175, 10, 143);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (176, 10, 144);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (177, 10, 145);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (178, 10, 146);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (179, 10, 147);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (180, 10, 148);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (181, 10, 149);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (182, 10, 150);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (183, 10, 151);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (184, 10, 152);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (185, 10, 153);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (186, 10, 154);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (187, 10, 155);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (188, 10, 156);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (189, 10, 157);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (190, 10, 158);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (191, 10, 159);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (192, 10, 160);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (193, 10, 161);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (194, 10, 162);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (195, 10, 163);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (196, 10, 164);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (197, 10, 165);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (198, 10, 166);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (199, 10, 167);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (200, 10, 168);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (201, 10, 169);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (202, 10, 170);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (203, 10, 171);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (204, 10, 172);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (205, 10, 173);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (206, 10, 174);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (207, 10, 112);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (208, 10, 113);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (209, 10, 114);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (210, 10, 115);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (211, 10, 116);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (212, 10, 117);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (213, 10, 118);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (214, 10, 119);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (215, 10, 120);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (216, 10, 121);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (217, 10, 122);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (218, 10, 123);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (219, 10, 124);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (220, 10, 125);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (221, 10, 126);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (222, 10, 127);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (286, 17, 128);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (287, 17, 129);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (288, 17, 130);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (289, 17, 131);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (290, 17, 140);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (291, 17, 141);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (292, 17, 142);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (293, 17, 143);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (294, 17, 144);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (295, 17, 145);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (296, 17, 146);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (297, 17, 147);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (298, 17, 148);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (299, 17, 149);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (300, 17, 150);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (301, 17, 151);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (302, 17, 152);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (303, 17, 153);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (304, 17, 154);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (305, 17, 155);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (306, 17, 156);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (307, 17, 157);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (308, 17, 158);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (309, 17, 159);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (310, 17, 160);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (311, 17, 161);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (312, 17, 112);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (313, 17, 118);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (314, 17, 119);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (315, 17, 120);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (316, 17, 121);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (317, 17, 122);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (318, 17, 123);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (319, 17, 124);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (320, 17, 125);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (321, 17, 126);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (322, 17, 127);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (323, 18, 128);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (324, 18, 129);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (325, 18, 130);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (326, 18, 131);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (327, 18, 132);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (328, 18, 133);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (329, 18, 134);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (330, 18, 135);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (331, 18, 136);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (332, 18, 137);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (333, 18, 138);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (334, 18, 139);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (335, 18, 140);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (336, 18, 141);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (337, 18, 142);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (338, 18, 143);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (339, 18, 144);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (340, 18, 145);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (341, 18, 146);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (342, 18, 147);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (343, 18, 148);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (344, 18, 149);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (345, 18, 150);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (346, 18, 151);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (347, 18, 152);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (348, 18, 153);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (349, 18, 154);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (350, 18, 155);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (351, 18, 156);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (352, 18, 157);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (353, 18, 158);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (354, 18, 159);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (355, 18, 160);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (356, 18, 161);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (357, 18, 162);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (358, 18, 163);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (359, 18, 164);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (360, 18, 165);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (361, 18, 166);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (362, 18, 167);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (363, 18, 168);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (364, 18, 169);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (365, 18, 170);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (366, 18, 171);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (367, 18, 112);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (368, 18, 113);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (369, 18, 114);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (370, 18, 115);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (371, 18, 116);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (372, 18, 117);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (373, 18, 118);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (374, 18, 119);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (375, 18, 120);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (376, 18, 121);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (377, 18, 122);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (378, 18, 123);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (379, 18, 124);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (380, 18, 125);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (381, 18, 126);
INSERT INTO public.perfiles_submodulos_web (id, perfiles_id, submodulosweb_id) VALUES (382, 18, 127);


--
-- Data for Name: produccion; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: proformas_transportista; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: registro_asistencia; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.registro_asistencia (id, fecha_asistencia, estado, horas_registradas, fecha_registro, observaciones, holding_id, modificado_por_id, trabajador_id, supervisor_id) VALUES (2, '2025-11-19', 'A', 9.00, '2025-11-19 16:38:19.82517+00', NULL, 4, 12, 18, 3);
INSERT INTO public.registro_asistencia (id, fecha_asistencia, estado, horas_registradas, fecha_registro, observaciones, holding_id, modificado_por_id, trabajador_id, supervisor_id) VALUES (3, '2025-11-19', 'A', 9.00, '2025-11-19 17:29:39.253347+00', NULL, 4, 12, 19, 3);
INSERT INTO public.registro_asistencia (id, fecha_asistencia, estado, horas_registradas, fecha_registro, observaciones, holding_id, modificado_por_id, trabajador_id, supervisor_id) VALUES (4, '2025-11-20', 'A', 9.00, '2025-11-20 13:30:52.219618+00', NULL, 4, 12, 25, 3);
INSERT INTO public.registro_asistencia (id, fecha_asistencia, estado, horas_registradas, fecha_registro, observaciones, holding_id, modificado_por_id, trabajador_id, supervisor_id) VALUES (5, '2025-11-20', 'A', 9.00, '2025-11-20 13:34:41.462448+00', NULL, 4, 12, 26, 3);
INSERT INTO public.registro_asistencia (id, fecha_asistencia, estado, horas_registradas, fecha_registro, observaciones, holding_id, modificado_por_id, trabajador_id, supervisor_id) VALUES (6, '2025-11-20', 'A', 9.00, '2025-11-20 13:40:24.845011+00', NULL, 4, 12, 27, 3);
INSERT INTO public.registro_asistencia (id, fecha_asistencia, estado, horas_registradas, fecha_registro, observaciones, holding_id, modificado_por_id, trabajador_id, supervisor_id) VALUES (7, '2025-11-20', 'A', 9.00, '2025-11-20 13:43:46.834503+00', NULL, 4, 12, 28, 3);
INSERT INTO public.registro_asistencia (id, fecha_asistencia, estado, horas_registradas, fecha_registro, observaciones, holding_id, modificado_por_id, trabajador_id, supervisor_id) VALUES (8, '2025-11-20', 'A', 9.00, '2025-11-20 13:51:37.322436+00', NULL, 4, 12, 29, 3);
INSERT INTO public.registro_asistencia (id, fecha_asistencia, estado, horas_registradas, fecha_registro, observaciones, holding_id, modificado_por_id, trabajador_id, supervisor_id) VALUES (9, '2025-11-20', 'A', 9.00, '2025-11-20 13:56:50.285731+00', NULL, 4, 12, 30, 3);
INSERT INTO public.registro_asistencia (id, fecha_asistencia, estado, horas_registradas, fecha_registro, observaciones, holding_id, modificado_por_id, trabajador_id, supervisor_id) VALUES (10, '2025-11-20', 'A', 9.00, '2025-11-20 13:59:32.289693+00', NULL, 4, 12, 31, 3);
INSERT INTO public.registro_asistencia (id, fecha_asistencia, estado, horas_registradas, fecha_registro, observaciones, holding_id, modificado_por_id, trabajador_id, supervisor_id) VALUES (11, '2025-11-20', 'A', 9.00, '2025-11-20 14:00:45.434695+00', NULL, 4, 12, 32, 3);


--
-- Data for Name: registro_egreso; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: registro_ingreso; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: registro_mano_obra_persona; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: registro_pagos_efectivo_historial_cambios; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: registro_pagos_efectivo_producciones; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: registro_pagos_transferencia_historial_cambios; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: registro_pagos_transferencia_producciones; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: solicitud_traspaso; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: solicitud_traspaso_trabajadores; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: supervisores_trabajadores; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.supervisores_trabajadores (id, supervisores_id, personaltrabajadores_id) VALUES (2, 3, 18);
INSERT INTO public.supervisores_trabajadores (id, supervisores_id, personaltrabajadores_id) VALUES (3, 3, 19);
INSERT INTO public.supervisores_trabajadores (id, supervisores_id, personaltrabajadores_id) VALUES (4, 3, 25);
INSERT INTO public.supervisores_trabajadores (id, supervisores_id, personaltrabajadores_id) VALUES (5, 3, 26);
INSERT INTO public.supervisores_trabajadores (id, supervisores_id, personaltrabajadores_id) VALUES (6, 3, 27);
INSERT INTO public.supervisores_trabajadores (id, supervisores_id, personaltrabajadores_id) VALUES (7, 3, 28);
INSERT INTO public.supervisores_trabajadores (id, supervisores_id, personaltrabajadores_id) VALUES (8, 3, 29);
INSERT INTO public.supervisores_trabajadores (id, supervisores_id, personaltrabajadores_id) VALUES (9, 3, 30);
INSERT INTO public.supervisores_trabajadores (id, supervisores_id, personaltrabajadores_id) VALUES (10, 3, 31);
INSERT INTO public.supervisores_trabajadores (id, supervisores_id, personaltrabajadores_id) VALUES (11, 3, 32);


--
-- Data for Name: trabajador_descuento; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: trabajador_empresa_transporte; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.trabajador_empresa_transporte (id, chofer_id, holding_id, trabajador_id, transportista_id, vehiculo_id) VALUES (1, NULL, 4, 18, 3, NULL);
INSERT INTO public.trabajador_empresa_transporte (id, chofer_id, holding_id, trabajador_id, transportista_id, vehiculo_id) VALUES (2, NULL, 4, 19, 3, NULL);
INSERT INTO public.trabajador_empresa_transporte (id, chofer_id, holding_id, trabajador_id, transportista_id, vehiculo_id) VALUES (3, NULL, 4, 25, 8, NULL);
INSERT INTO public.trabajador_empresa_transporte (id, chofer_id, holding_id, trabajador_id, transportista_id, vehiculo_id) VALUES (4, NULL, 4, 26, 8, NULL);
INSERT INTO public.trabajador_empresa_transporte (id, chofer_id, holding_id, trabajador_id, transportista_id, vehiculo_id) VALUES (5, NULL, 4, 27, 8, NULL);
INSERT INTO public.trabajador_empresa_transporte (id, chofer_id, holding_id, trabajador_id, transportista_id, vehiculo_id) VALUES (6, NULL, 4, 28, 8, NULL);
INSERT INTO public.trabajador_empresa_transporte (id, chofer_id, holding_id, trabajador_id, transportista_id, vehiculo_id) VALUES (7, NULL, 4, 29, 8, NULL);
INSERT INTO public.trabajador_empresa_transporte (id, chofer_id, holding_id, trabajador_id, transportista_id, vehiculo_id) VALUES (8, NULL, 4, 30, 8, NULL);
INSERT INTO public.trabajador_empresa_transporte (id, chofer_id, holding_id, trabajador_id, transportista_id, vehiculo_id) VALUES (9, NULL, 4, 31, 8, NULL);
INSERT INTO public.trabajador_empresa_transporte (id, chofer_id, holding_id, trabajador_id, transportista_id, vehiculo_id) VALUES (10, NULL, 4, 32, 8, NULL);


--
-- Data for Name: trabajador_haber; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: usuarios_empresas_asignadas; Type: TABLE DATA; Schema: public; Owner: admin
--

INSERT INTO public.usuarios_empresas_asignadas (id, usuarios_id, sociedad_id) VALUES (1, 10, 2);
INSERT INTO public.usuarios_empresas_asignadas (id, usuarios_id, sociedad_id) VALUES (2, 13, 3);
INSERT INTO public.usuarios_empresas_asignadas (id, usuarios_id, sociedad_id) VALUES (3, 14, 3);
INSERT INTO public.usuarios_empresas_asignadas (id, usuarios_id, sociedad_id) VALUES (4, 15, 3);
INSERT INTO public.usuarios_empresas_asignadas (id, usuarios_id, sociedad_id) VALUES (5, 16, 3);
INSERT INTO public.usuarios_empresas_asignadas (id, usuarios_id, sociedad_id) VALUES (6, 17, 3);
INSERT INTO public.usuarios_empresas_asignadas (id, usuarios_id, sociedad_id) VALUES (7, 18, 3);


--
-- Data for Name: usuarios_groups; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: usuarios_user_permissions; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Data for Name: vacaciones; Type: TABLE DATA; Schema: public; Owner: admin
--



--
-- Name: afp_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.afp_id_seq', 24, true);


--
-- Name: apk_links_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.apk_links_id_seq', 1, false);


--
-- Name: areas_administracion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.areas_administracion_id_seq', 6, true);


--
-- Name: areas_clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.areas_clientes_id_seq', 4, true);


--
-- Name: areas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.areas_id_seq', 1, false);


--
-- Name: asociacion_codigo_qr_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.asociacion_codigo_qr_id_seq', 1, false);


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 404, true);


--
-- Name: banco_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.banco_id_seq', 17, true);


--
-- Name: campos_clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.campos_clientes_id_seq', 10, true);


--
-- Name: cargos_admnistracion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.cargos_admnistracion_id_seq', 13, true);


--
-- Name: cargos_clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.cargos_clientes_id_seq', 1, false);


--
-- Name: cargos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.cargos_id_seq', 1, false);


--
-- Name: cartola_movimiento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.cartola_movimiento_id_seq', 1, false);


--
-- Name: casas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.casas_id_seq', 4, true);


--
-- Name: causales_finiquito_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.causales_finiquito_id_seq', 1, false);


--
-- Name: ccaf_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.ccaf_id_seq', 1, false);


--
-- Name: choferes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.choferes_id_seq', 5, true);


--
-- Name: clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.clientes_id_seq', 8, true);


--
-- Name: comunas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.comunas_id_seq', 1, false);


--
-- Name: configuracion_sii_automatica_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.configuracion_sii_automatica_id_seq', 1, false);


--
-- Name: configuracion_sii_automatica_venta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.configuracion_sii_automatica_venta_id_seq', 1, false);


--
-- Name: contactos_clientes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.contactos_clientes_id_seq', 1, false);


--
-- Name: contratos_trabajadores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.contratos_trabajadores_id_seq', 11, true);


--
-- Name: cuadrillas_trabajadores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.cuadrillas_trabajadores_id_seq', 1, false);


--
-- Name: cuenta_origen_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.cuenta_origen_id_seq', 1, true);


--
-- Name: cuentas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.cuentas_id_seq', 1, false);


--
-- Name: descuentos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.descuentos_id_seq', 1, false);


--
-- Name: detalle_pagos_transportista_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.detalle_pagos_transportista_id_seq', 1, false);


--
-- Name: developer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.developer_id_seq', 1, false);


--
-- Name: dias_trabajados_aprobados_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.dias_trabajados_aprobados_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 1, false);


--
-- Name: django_celery_beat_clockedschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.django_celery_beat_clockedschedule_id_seq', 1, false);


--
-- Name: django_celery_beat_crontabschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.django_celery_beat_crontabschedule_id_seq', 2, true);


--
-- Name: django_celery_beat_intervalschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.django_celery_beat_intervalschedule_id_seq', 1, false);


--
-- Name: django_celery_beat_periodictask_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.django_celery_beat_periodictask_id_seq', 2, true);


--
-- Name: django_celery_beat_solarschedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.django_celery_beat_solarschedule_id_seq', 1, false);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 101, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 64, true);


--
-- Name: documentos_chofer_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.documentos_chofer_id_seq', 5, true);


--
-- Name: documentos_variables_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.documentos_variables_id_seq', 13, true);


--
-- Name: documentos_vehiculo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.documentos_vehiculo_id_seq', 1, true);


--
-- Name: empresas_transporte_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.empresas_transporte_id_seq', 9, true);


--
-- Name: enlaces_auto_registro_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.enlaces_auto_registro_id_seq', 2, true);


--
-- Name: estados_discapacidad_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.estados_discapacidad_id_seq', 1, false);


--
-- Name: facturas_sii_distribuidas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.facturas_sii_distribuidas_id_seq', 1, false);


--
-- Name: facturas_sii_por_distribuir_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.facturas_sii_por_distribuir_id_seq', 1, false);


--
-- Name: facturas_venta_sii_distribuidas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.facturas_venta_sii_distribuidas_id_seq', 1, false);


--
-- Name: facturas_venta_sii_por_distribuir_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.facturas_venta_sii_por_distribuir_id_seq', 1, false);


--
-- Name: fc_labor_pago_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.fc_labor_pago_id_seq', 13, true);


--
-- Name: folio_comercial_fundos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.folio_comercial_fundos_id_seq', 6, true);


--
-- Name: folio_comercial_horarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.folio_comercial_horarios_id_seq', 7, true);


--
-- Name: folio_comercial_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.folio_comercial_id_seq', 6, true);


--
-- Name: folio_comercial_transportistas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.folio_comercial_transportistas_id_seq', 32, true);


--
-- Name: folio_comercial_vehiculos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.folio_comercial_vehiculos_id_seq', 56, true);


--
-- Name: folios_transportes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.folios_transportes_id_seq', 1, false);


--
-- Name: haberes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.haberes_id_seq', 1, false);


--
-- Name: historial_cambios_folio_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.historial_cambios_folio_id_seq', 1, false);


--
-- Name: historial_cambios_pago_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.historial_cambios_pago_id_seq', 1, false);


--
-- Name: holding_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.holding_id_seq', 5, true);


--
-- Name: horarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.horarios_id_seq', 4, true);


--
-- Name: horas_extraordinarias_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.horas_extraordinarias_id_seq', 1, false);


--
-- Name: ips_regimenes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.ips_regimenes_id_seq', 1, false);


--
-- Name: jefes_cuadrilla_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.jefes_cuadrilla_id_seq', 1, true);


--
-- Name: jefes_cuadrilla_trabajadores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.jefes_cuadrilla_trabajadores_id_seq', 1, false);


--
-- Name: labores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.labores_id_seq', 9, true);


--
-- Name: licencias_medicas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.licencias_medicas_id_seq', 1, false);


--
-- Name: meses_cerrados_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.meses_cerrados_id_seq', 1, false);


--
-- Name: modulos_movil_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.modulos_movil_id_seq', 12, true);


--
-- Name: modulos_web_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.modulos_web_id_seq', 41, true);


--
-- Name: mutualidades_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.mutualidades_id_seq', 1, false);


--
-- Name: oauth2_provider_accesstoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.oauth2_provider_accesstoken_id_seq', 1, false);


--
-- Name: oauth2_provider_application_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.oauth2_provider_application_id_seq', 1, false);


--
-- Name: oauth2_provider_grant_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.oauth2_provider_grant_id_seq', 1, false);


--
-- Name: oauth2_provider_idtoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.oauth2_provider_idtoken_id_seq', 1, false);


--
-- Name: oauth2_provider_refreshtoken_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.oauth2_provider_refreshtoken_id_seq', 1, false);


--
-- Name: pagos_transportista_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.pagos_transportista_id_seq', 1, false);


--
-- Name: perfiles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.perfiles_id_seq', 18, true);


--
-- Name: perfiles_modulos_movil_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.perfiles_modulos_movil_id_seq', 12, true);


--
-- Name: perfiles_modulos_web_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.perfiles_modulos_web_id_seq', 65, true);


--
-- Name: perfiles_submodulos_movil_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.perfiles_submodulos_movil_id_seq', 40, true);


--
-- Name: perfiles_submodulos_web_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.perfiles_submodulos_web_id_seq', 382, true);


--
-- Name: personal_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.personal_id_seq', 32, true);


--
-- Name: produccion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.produccion_id_seq', 1, false);


--
-- Name: proformas_transportista_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.proformas_transportista_id_seq', 1, false);


--
-- Name: regiones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.regiones_id_seq', 1, false);


--
-- Name: registro_asistencia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.registro_asistencia_id_seq', 11, true);


--
-- Name: registro_egreso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.registro_egreso_id_seq', 1, false);


--
-- Name: registro_ingreso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.registro_ingreso_id_seq', 1, false);


--
-- Name: registro_mano_obra_persona_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.registro_mano_obra_persona_id_seq', 1, false);


--
-- Name: registro_pagos_efectivo_historial_cambios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.registro_pagos_efectivo_historial_cambios_id_seq', 1, false);


--
-- Name: registro_pagos_efectivo_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.registro_pagos_efectivo_id_seq', 1, false);


--
-- Name: registro_pagos_efectivo_producciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.registro_pagos_efectivo_producciones_id_seq', 1, false);


--
-- Name: registro_pagos_transferencia_historial_cambios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.registro_pagos_transferencia_historial_cambios_id_seq', 1, false);


--
-- Name: registro_pagos_transferencia_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.registro_pagos_transferencia_id_seq', 1, false);


--
-- Name: registro_pagos_transferencia_producciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.registro_pagos_transferencia_producciones_id_seq', 1, false);


--
-- Name: salud_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.salud_id_seq', 33, true);


--
-- Name: sociedad_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.sociedad_id_seq', 3, true);


--
-- Name: solicitud_traspaso_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.solicitud_traspaso_id_seq', 1, false);


--
-- Name: solicitud_traspaso_trabajadores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.solicitud_traspaso_trabajadores_id_seq', 1, false);


--
-- Name: submodulos_movil_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.submodulos_movil_id_seq', 40, true);


--
-- Name: submodulos_web_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.submodulos_web_id_seq', 237, true);


--
-- Name: supervisores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.supervisores_id_seq', 3, true);


--
-- Name: supervisores_trabajadores_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.supervisores_trabajadores_id_seq', 11, true);


--
-- Name: tipos_impuesto_renta_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.tipos_impuesto_renta_id_seq', 1, false);


--
-- Name: tipos_jornada_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.tipos_jornada_id_seq', 1, false);


--
-- Name: trabajador_descuento_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.trabajador_descuento_id_seq', 1, false);


--
-- Name: trabajador_empresa_transporte_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.trabajador_empresa_transporte_id_seq', 10, true);


--
-- Name: trabajador_haber_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.trabajador_haber_id_seq', 1, false);


--
-- Name: tramos_transportista_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.tramos_transportista_id_seq', 9, true);


--
-- Name: unidad_control_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.unidad_control_id_seq', 6, true);


--
-- Name: usuarios_empresas_asignadas_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.usuarios_empresas_asignadas_id_seq', 7, true);


--
-- Name: usuarios_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.usuarios_groups_id_seq', 1, false);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 18, true);


--
-- Name: usuarios_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.usuarios_user_permissions_id_seq', 1, false);


--
-- Name: vacaciones_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.vacaciones_id_seq', 1, false);


--
-- Name: vehiculos_transporte_id_seq; Type: SEQUENCE SET; Schema: public; Owner: admin
--

SELECT pg_catalog.setval('public.vehiculos_transporte_id_seq', 7, true);


--
-- PostgreSQL database dump complete
--

\unrestrict G48sY1urY2b5pygeepJFvEcN3ZcFeexkus36bh4k1ztQkMc2nwLDQQ565FI4fD3

