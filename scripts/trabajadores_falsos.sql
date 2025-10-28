-- ============================================
-- 1. INSERTAR 10 TRABAJADORES EN LA TABLA PERSONAL
-- ============================================

-- COMANDO A CORRER: docker exec -i contratista_postgres psql -U admin -d contratista_db < scripts/trabajadores_falsos.sql
INSERT INTO personal (
    holding_id,
    casa_id,
    transportista_id,
    vehiculo_id,
    nombres,
    apellidos,
    rut,
    estado,
    afiliado_afc,
    pensionado_vejez,
    cargas_familiares_legales,
    cargas_familiares_maternales,
    cargas_familiares_invalidez,
    subsidio_trabajador_joven,
    fecha_ingreso,
    nacionalidad,
    sexo
) VALUES
    (1, 1, 1, 1, 'PEDRO ANTONIO', 'GONZALEZ ROJAS', '16789234', true, true, false, 0, false, 0, false, CURRENT_DATE, 'CHILENA', 'Hombre'),
    (1, 1, 1, 1, 'MARIA ISABEL', 'MARTINEZ SILVA', '17234567', true, true, false, 0, false, 0, false, CURRENT_DATE, 'CHILENA', 'Mujer'),
    (1, 1, 1, 1, 'CARLOS EDUARDO', 'FERNANDEZ LOPEZ', '18456789', true, true, false, 0, false, 0, false, CURRENT_DATE, 'CHILENA', 'Hombre'),
    (1, 1, 1, 1, 'ANA LUCIA', 'RODRIGUEZ MUNOZ', '19567890', true, true, false, 0, false, 0, false, CURRENT_DATE, 'CHILENA', 'Mujer'),
    (1, 1, 1, 1, 'JOSE MIGUEL', 'VALENZUELA CASTRO', '20123456', true, true, false, 0, false, 0, false, CURRENT_DATE, 'CHILENA', 'Hombre'),
    (1, 1, 1, 1, 'CLAUDIA PATRICIA', 'PEREZ DIAZ', '21345678', true, true, false, 0, false, 0, false, CURRENT_DATE, 'CHILENA', 'Mujer'),
    (1, 1, 1, 1, 'ROBERTO ANDRES', 'MORALES SOTO', '22456789', true, true, false, 0, false, 0, false, CURRENT_DATE, 'CHILENA', 'Hombre'),
    (1, 1, 1, 1, 'FRANCISCA ANDREA', 'CONTRERAS VEGA', '23567890', true, true, false, 0, false, 0, false, CURRENT_DATE, 'CHILENA', 'Mujer'),
    (1, 1, 1, 1, 'DIEGO ALEJANDRO', 'RAMIREZ HERRERA', '24678901', true, true, false, 0, false, 0, false, CURRENT_DATE, 'CHILENA', 'Hombre'),
    (1, 1, 1, 1, 'VALENTINA NICOLE', 'TORRES PIZARRO', '25789012', true, true, false, 0, false, 0, false, CURRENT_DATE, 'CHILENA', 'Mujer');


-- ============================================
-- 2. ASIGNAR TRABAJADORES AL SUPERVISOR 3
-- ============================================

INSERT INTO supervisores_trabajadores (supervisores_id, personaltrabajadores_id)
SELECT 3, id 
FROM personal 
WHERE rut IN (
    '16789234', '17234567', '18456789', '19567890', '20123456',
    '21345678', '22456789', '23567890', '24678901', '25789012'
);


-- ============================================
-- 3. CREAR CONTRATOS ASOCIANDO AL FOLIO 1
-- ============================================

INSERT INTO contratos_trabajadores (
    holding_id,
    trabajador_id,
    folio_comercial_id,
    empresa_transporte_id,
    fecha_inicio_contrato,
    fecha_termino_contrato
)
SELECT 
    1,                    -- holding_id
    p.id,                 -- trabajador_id
    1,                    -- folio_comercial_id (el folio que existe)
    1,                    -- empresa_transporte_id
    '2025-09-11',         -- fecha_inicio_contrato (mismo que el folio)
    '2025-10-09'          -- fecha_termino_contrato (mismo que el folio)
FROM personal p
WHERE p.rut IN (
    '16789234', '17234567', '18456789', '19567890', '20123456',
    '21345678', '22456789', '23567890', '24678901', '25789012'
);


-- ============================================
-- 4. VERIFICACIONES COMPLETAS
-- ============================================

-- Ver los trabajadores recién insertados con todos sus datos
SELECT 
    p.id,
    p.nombres,
    p.apellidos,
    p.rut,
    p.casa_id,
    c.nombre as casa_nombre,
    p.transportista_id,
    e.nombre as transportista_nombre,
    p.vehiculo_id,
    v.ppu as vehiculo_ppu,
    p.estado
FROM personal p
LEFT JOIN casas c ON p.casa_id = c.id
LEFT JOIN empresas_transporte e ON p.transportista_id = e.id
LEFT JOIN vehiculos_transporte v ON p.vehiculo_id = v.id
WHERE p.rut IN (
    '16789234', '17234567', '18456789', '19567890', '20123456',
    '21345678', '22456789', '23567890', '24678901', '25789012'
)
ORDER BY p.id;

-- Ver los contratos con folio
SELECT 
    ct.id as contrato_id,
    p.id as trabajador_id,
    p.nombres,
    p.apellidos,
    p.rut,
    ct.folio_comercial_id,
    ct.fecha_inicio_contrato,
    ct.fecha_termino_contrato,
    ct.empresa_transporte_id
FROM contratos_trabajadores ct
INNER JOIN personal p ON ct.trabajador_id = p.id
WHERE p.rut IN (
    '16789234', '17234567', '18456789', '19567890', '20123456',
    '21345678', '22456789', '23567890', '24678901', '25789012'
)
ORDER BY p.id;

-- Ver la relación completa: supervisor → trabajadores → contratos → folio
SELECT 
    s.id as supervisor_id,
    u.rut as supervisor_rut,
    up.nombres as supervisor_nombre,
    p.id as trabajador_id,
    p.nombres as trabajador_nombre,
    p.apellidos,
    p.rut as trabajador_rut,
    c.nombre as casa,
    e.nombre as transportista,
    v.ppu as vehiculo,
    ct.folio_comercial_id,
    fc.fecha_inicio_contrato as folio_inicio,
    fc.fecha_termino_contrato as folio_termino
FROM supervisores s
INNER JOIN usuarios u ON s.usuario_id = u.id
INNER JOIN personal up ON u.persona_id = up.id
INNER JOIN supervisores_trabajadores st ON st.supervisores_id = s.id
INNER JOIN personal p ON st.personaltrabajadores_id = p.id
LEFT JOIN casas c ON p.casa_id = c.id
LEFT JOIN empresas_transporte e ON p.transportista_id = e.id
LEFT JOIN vehiculos_transporte v ON p.vehiculo_id = v.id
LEFT JOIN contratos_trabajadores ct ON ct.trabajador_id = p.id
LEFT JOIN folio_comercial fc ON ct.folio_comercial_id = fc.id
WHERE s.id = 3
ORDER BY p.id;

-- Contar trabajadores del supervisor 3 asociados al folio 1
SELECT 
    COUNT(*) as total_trabajadores,
    fc.id as folio_id,
    fc.fecha_inicio_contrato,
    fc.fecha_termino_contrato
FROM supervisores_trabajadores st
INNER JOIN personal p ON st.personaltrabajadores_id = p.id
INNER JOIN contratos_trabajadores ct ON ct.trabajador_id = p.id
INNER JOIN folio_comercial fc ON ct.folio_comercial_id = fc.id
WHERE st.supervisores_id = 3 AND ct.folio_comercial_id = 1
GROUP BY fc.id, fc.fecha_inicio_contrato, fc.fecha_termino_contrato;