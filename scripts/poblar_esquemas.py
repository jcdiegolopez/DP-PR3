"""Fill the twelve training databases (tr_*) with reproducible fake data.

Seed 2026 makes every run identical. Ids are explicit (1..n), so foreign keys
are drawn from the known range of the parent table. Totals that depend on
detail rows are computed with an UPDATE after the detail is inserted.
Text is stored without accents, like the schema comments.
"""
import argparse
import random
import unicodedata
from datetime import date, datetime, timedelta

import pymysql
from faker import Faker

SEMILLA = 2026
rng = random.Random(SEMILLA)
Faker.seed(SEMILLA)
fes = Faker("es_MX")
fen = Faker("en_US")

DESDE, HASTA = date(2023, 1, 1), date(2025, 12, 31)
DEPTOS = ["Guatemala", "Quetzaltenango", "Escuintla", "Alta Verapaz", "Sacatepequez",
          "Huehuetenango", "Peten", "Izabal", "Chiquimula", "Zacapa", "San Marcos",
          "Jutiapa", "Retalhuleu", "Solola", "Chimaltenango", "Santa Rosa"]
MUNIS = {"Guatemala": ["Guatemala", "Mixco", "Villa Nueva", "San Miguel Petapa"],
         "Quetzaltenango": ["Quetzaltenango", "Salcaja"], "Escuintla": ["Escuintla", "Santa Lucia"],
         "Alta Verapaz": ["Coban"], "Sacatepequez": ["Antigua Guatemala"],
         "Huehuetenango": ["Huehuetenango"], "Peten": ["Flores"], "Izabal": ["Puerto Barrios"],
         "Chiquimula": ["Chiquimula"], "Zacapa": ["Zacapa"], "San Marcos": ["San Marcos"],
         "Jutiapa": ["Jutiapa"], "Retalhuleu": ["Retalhuleu"], "Solola": ["Solola"],
         "Chimaltenango": ["Chimaltenango"], "Santa Rosa": ["Cuilapa"]}


def limpia(t: str) -> str:
    return unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()


def nom(): return limpia(fes.first_name())
def ape(): return limpia(fes.last_name())
def fecha(a=DESDE, b=HASTA): return a + timedelta(days=rng.randint(0, max((b - a).days, 0)))
def fechahora(a=DESDE, b=HASTA):
    return datetime.combine(fecha(a, b), datetime.min.time()) + timedelta(
        hours=rng.randint(7, 21), minutes=rng.randint(0, 59))
def dinero(a, b): return round(rng.uniform(a, b), 2)
def nit(): return f"{rng.randint(100000, 9999999)}-{rng.choice('0123456789K')}"
def dpi(): return "".join(str(rng.randint(0, 9)) for _ in range(13))
def tel(): return f"{rng.choice('2345')}{rng.randint(1000000, 9999999)}"
def correo(n, a): return limpia(f"{n}.{a}{rng.randint(1, 99)}@{rng.choice(['correo.com', 'mail.gt', 'ejemplo.org'])}".lower()).replace(" ", "")
def fk(n): return rng.randint(1, n)
def peso(opciones):
    return rng.choices([o for o, _ in opciones], weights=[w for _, w in opciones])[0]
def depto():
    d = rng.choice(DEPTOS)
    return d, rng.choice(MUNIS[d])


def ins(cur, tabla, cols, filas):
    sql = f"INSERT INTO `{tabla}` ({', '.join(f'`{c}`' for c in cols)}) VALUES ({', '.join(['%s'] * len(cols))})"
    for i in range(0, len(filas), 1000):
        cur.executemany(sql, filas[i:i + 1000])


# ---------------------------------------------------------------- supermercado
def pob_supermercado(c):
    suc = []
    for i in range(1, 13):
        d, m = depto()
        suc.append((i, f"Super {m} {i}", d, m, f"{rng.randint(1, 20)} avenida {rng.randint(1, 30)}-{rng.randint(1, 99)}",
                    fecha(date(2012, 1, 1), date(2022, 12, 31)), rng.randint(400, 3500)))
    ins(c, "sucursales", ["id_sucursal", "nombre", "departamento", "municipio", "direccion", "fecha_apertura", "area_m2"], suc)
    cli = []
    for i in range(1, 301):
        n, a = nom(), ape()
        cli.append((i, nit(), n, a, correo(n, a), tel(), rng.choice(DEPTOS), fecha()))
    ins(c, "clientes", ["id_cliente", "nit", "nombre", "apellido", "correo", "telefono", "departamento", "fecha_registro"], cli)
    cats = ["Lacteos", "Carnes", "Frutas y verduras", "Abarrotes", "Bebidas", "Panaderia", "Limpieza", "Cuidado personal", "Snacks", "Congelados"]
    ins(c, "categorias", ["id_categoria", "nombre", "descripcion"], [(i + 1, n, f"Productos de {n.lower()}") for i, n in enumerate(cats)])
    ins(c, "proveedores", ["id_proveedor", "nombre", "nit", "telefono", "ciudad"],
        [(i, limpia(fes.company()), nit(), tel(), rng.choice(MUNIS[rng.choice(DEPTOS)])) for i in range(1, 16)])
    base = ["Leche entera", "Queso fresco", "Pollo", "Carne molida", "Manzana", "Tomate", "Arroz", "Frijol negro", "Aceite", "Agua pura",
            "Gaseosa", "Jugo de naranja", "Pan frances", "Jabon liquido", "Detergente", "Shampoo", "Galletas", "Papas fritas", "Helado", "Pizza congelada"]
    prods = []
    for i in range(1, 121):
        p = dinero(3, 90)
        prods.append((i, f"{rng.choice(base)} {rng.choice(['500g', '1kg', '1L', 'paquete', 'grande'])} {i}", fk(10), fk(15), p, round(p * rng.uniform(0.55, 0.85), 2), int(rng.random() > 0.08)))
    ins(c, "productos", ["id_producto", "nombre", "id_categoria", "id_proveedor", "precio_unitario", "costo", "activo"], prods)
    puestos = ["cajero", "bodeguero", "gerente", "supervisor", "empacador"]
    ins(c, "empleados", ["id_empleado", "nombre", "apellido", "puesto", "id_sucursal", "fecha_contratacion", "salario"],
        [(i, nom(), ape(), rng.choice(puestos), fk(12), fecha(date(2015, 1, 1), HASTA), dinero(3200, 9500)) for i in range(1, 61)])
    ventas, det = [], []
    for i in range(1, 3001):
        ventas.append((i, fk(300) if rng.random() > 0.3 else None, fk(12), fk(60), fechahora(), peso([("efectivo", 50), ("tarjeta", 40), ("transferencia", 10)]), 0))
        for _ in range(rng.randint(1, 5)):
            p = rng.choice(prods)
            cant = rng.randint(1, 6)
            desc = round(p[4] * cant * rng.choice([0.05, 0.1]), 2) if rng.random() < 0.15 else 0
            det.append((len(det) + 1, i, p[0], cant, p[4], desc))
    ins(c, "ventas", ["id_venta", "id_cliente", "id_sucursal", "id_empleado", "fecha_venta", "metodo_pago", "total"], ventas)
    ins(c, "detalle_ventas", ["id_detalle", "id_venta", "id_producto", "cantidad", "precio_unitario", "descuento"], det)
    c.execute("UPDATE ventas v SET total = (SELECT ROUND(SUM(d.cantidad*d.precio_unitario - d.descuento), 2) FROM detalle_ventas d WHERE d.id_venta = v.id_venta)")


# ----------------------------------------------------------------- universidad
def pob_universidad(c):
    facs = ["Ingenieria", "Ciencias y Humanidades", "Educacion", "Ciencias Economicas", "Ciencias de la Salud"]
    ins(c, "facultades", ["id_facultad", "nombre"], [(i + 1, n) for i, n in enumerate(facs)])
    carr = ["Ingenieria en Computacion", "Ingenieria Civil", "Ingenieria Industrial", "Ingenieria Electronica", "Psicologia", "Comunicacion",
            "Educacion Primaria", "Administracion de Empresas", "Contaduria", "Economia", "Nutricion", "Enfermeria"]
    fac_de = [1, 1, 1, 1, 2, 2, 3, 4, 4, 4, 5, 5]
    ins(c, "carreras", ["id_carrera", "nombre", "id_facultad", "duracion_semestres"],
        [(i + 1, n, fac_de[i], rng.choice([8, 10, 10, 12])) for i, n in enumerate(carr)])
    ins(c, "catedraticos", ["id_catedratico", "nombre", "apellido", "id_facultad", "grado_academico", "fecha_ingreso"],
        [(i, nom(), ape(), fk(5), peso([("licenciatura", 45), ("maestria", 40), ("doctorado", 15)]), fecha(date(2005, 1, 1), HASTA)) for i in range(1, 41)])
    est = []
    for i in range(1, 401):
        ing = fecha(date(2019, 1, 1), HASTA)
        est.append((i, f"{ing.year % 100}{rng.randint(100, 999)}", nom(), ape(), fk(12), ing, rng.choice("MF"), rng.choice(DEPTOS)))
    ins(c, "estudiantes", ["id_estudiante", "carne", "nombre", "apellido", "id_carrera", "fecha_ingreso", "genero", "departamento_origen"], est)
    temas = ["Calculo", "Algebra", "Fisica", "Programacion", "Estadistica", "Contabilidad", "Etica", "Redaccion", "Bases de datos", "Redes"]
    cursos = [(i, f"CC{i:03d}", f"{rng.choice(temas)} {rng.choice(['I', 'II', 'III', 'IV'])}", rng.choice([3, 4, 5]), 1 + (i - 1) // 5) for i in range(1, 61)]
    ins(c, "cursos", ["id_curso", "codigo", "nombre", "creditos", "id_carrera"], cursos)
    ciclos = []
    for k, (a, n) in enumerate([(2023, 1), (2023, 2), (2024, 1), (2024, 2), (2025, 1), (2025, 2)], 1):
        ini = date(a, 1, 25) if n == 1 else date(a, 7, 20)
        ciclos.append((k, a, n, ini, ini + timedelta(days=130)))
    ins(c, "ciclos", ["id_ciclo", "anio", "numero", "fecha_inicio", "fecha_fin"], ciclos)
    ins(c, "secciones", ["id_seccion", "id_curso", "id_ciclo", "id_catedratico", "cupo", "aula"],
        [(i, fk(60), fk(6), fk(40), rng.choice([25, 30, 40, 50]), f"A-{rng.randint(101, 420)}") for i in range(1, 201)])
    visto, insc = set(), []
    while len(insc) < 3000:
        e, s = fk(400), fk(200)
        if (e, s) in visto:
            continue
        visto.add((e, s))
        insc.append([len(insc) + 1, e, s])
    c.execute("SELECT id_seccion, id_ciclo FROM secciones")
    ciclo_de = dict(c.fetchall())
    filas = []
    for i, e, s in insc:
        ci = ciclo_de[s]
        ini = ciclos[ci - 1][3]
        if ci == 6:
            nota, estado = None, "en_curso"
        else:
            nota = round(rng.gauss(72, 16), 2)
            nota = min(max(nota, 20), 100)
            estado = "aprobado" if nota >= 61 else "reprobado"
        filas.append((i, e, s, ini - timedelta(days=rng.randint(1, 15)), nota, estado))
    ins(c, "inscripciones", ["id_inscripcion", "id_estudiante", "id_seccion", "fecha_inscripcion", "nota", "estado"], filas)


# ----------------------------------------------------------------------- banco
def pob_banco(c):
    ag = []
    for i in range(1, 11):
        d, m = depto()
        ag.append((i, f"Agencia {m} {i}", d, m, fecha(date(2005, 1, 1), date(2022, 12, 31))))
    ins(c, "agencias", ["id_agencia", "nombre", "departamento", "municipio", "fecha_apertura"], ag)
    ocup = ["comerciante", "docente", "ingeniero", "agricultor", "medico", "estudiante", "contador", "piloto"]
    ins(c, "clientes", ["id_cliente", "dpi", "nombre", "apellido", "fecha_nacimiento", "ocupacion", "id_agencia", "fecha_alta"],
        [(i, dpi(), nom(), ape(), fecha(date(1955, 1, 1), date(2004, 12, 31)), rng.choice(ocup), fk(10), fecha()) for i in range(1, 301)])
    ins(c, "tipos_cuenta", ["id_tipo", "nombre", "tasa_interes_anual", "cuota_manejo"],
        [(1, "ahorro", 2.50, 0), (2, "monetaria", 0.50, 25), (3, "plazo fijo", 5.25, 0), (4, "ahorro programado", 3.75, 10)])
    ins(c, "cuentas", ["id_cuenta", "numero_cuenta", "id_cliente", "id_tipo", "saldo", "fecha_apertura", "estado"],
        [(i, f"{rng.randint(10, 99)}-{rng.randint(1000000, 9999999)}-{rng.randint(0, 9)}", fk(300), fk(4), dinero(0, 250000), fecha(), peso([("activa", 85), ("inactiva", 10), ("cerrada", 5)])) for i in range(1, 451)])
    tipos = ["deposito", "retiro", "transferencia", "pago_servicio"]
    tr = []
    for i in range(1, 4001):
        t = rng.choice(tipos)
        tr.append((i, fk(450), t, dinero(10, 5000) if t != "pago_servicio" else dinero(20, 900), fechahora(), f"{t} {rng.randint(1000, 9999)}"))
    ins(c, "transacciones", ["id_transaccion", "id_cuenta", "tipo", "monto", "fecha_hora", "descripcion"], tr)
    pres, pagos = [], []
    for i in range(1, 121):
        monto, tasa, plazo = dinero(5000, 300000), dinero(8, 22), rng.choice([12, 24, 36, 48, 60])
        desemb = fecha()
        k = min(plazo, max(0, (HASTA - desemb).days // 30))
        estado = "cancelado" if k >= plazo else peso([("vigente", 80), ("en_mora", 20)])
        pres.append((i, fk(300), monto, tasa, plazo, desemb, estado))
        cuota = round(monto * (1 + tasa / 100 * plazo / 12) / plazo, 2)
        for n in range(1, k + 1):
            pagos.append((len(pagos) + 1, i, n, desemb + timedelta(days=30 * n + rng.randint(0, 5)), cuota))
    ins(c, "prestamos", ["id_prestamo", "id_cliente", "monto_aprobado", "tasa_anual", "plazo_meses", "fecha_desembolso", "estado"], pres)
    ins(c, "pagos_prestamo", ["id_pago", "id_prestamo", "numero_cuota", "fecha_pago", "monto_pagado"], pagos)
    tj = []
    for i in range(1, 251):
        em = fecha(date(2021, 1, 1), HASTA)
        t = rng.choice(["debito", "credito"])
        tj.append((i, fk(450), t, em, em + timedelta(days=365 * 4), dinero(3000, 60000) if t == "credito" else None))
    ins(c, "tarjetas", ["id_tarjeta", "id_cuenta", "tipo", "fecha_emision", "fecha_vencimiento", "limite_credito"], tj)


# -------------------------------------------------------------------- hospital
def pob_hospital(c):
    esp = ["Medicina general", "Pediatria", "Cardiologia", "Ginecologia", "Traumatologia", "Dermatologia", "Neurologia", "Oftalmologia", "Gastroenterologia", "Psiquiatria"]
    ins(c, "especialidades", ["id_especialidad", "nombre"], [(i + 1, n) for i, n in enumerate(esp)])
    ins(c, "medicos", ["id_medico", "nombre", "apellido", "id_especialidad", "colegiado", "fecha_contratacion", "salario"],
        [(i, nom(), ape(), fk(10), str(rng.randint(10000, 29999)), fecha(date(2008, 1, 1), HASTA), dinero(9000, 32000)) for i in range(1, 31)])
    ins(c, "pacientes", ["id_paciente", "nombre", "apellido", "fecha_nacimiento", "genero", "departamento", "telefono", "tipo_sangre", "afiliado_seguro"],
        [(i, nom(), ape(), fecha(date(1940, 1, 1), date(2024, 12, 31)), rng.choice("MF"), rng.choice(DEPTOS), tel(), rng.choice(["O+", "O-", "A+", "A-", "B+", "AB+"]), int(rng.random() < 0.45)) for i in range(1, 401)])
    ins(c, "consultorios", ["id_consultorio", "nombre", "piso"], [(i, f"Consultorio {i}", 1 + (i - 1) // 4) for i in range(1, 13)])
    motivos = ["control", "dolor de cabeza", "fiebre", "dolor abdominal", "revision anual", "lesion", "tos persistente", "alergia"]
    citas = [(i, fk(400), fk(30), fk(12), fechahora(), rng.choice(motivos), peso([("atendida", 70), ("cancelada", 15), ("pendiente", 15)]), dinero(150, 650)) for i in range(1, 2501)]
    ins(c, "citas", ["id_cita", "id_paciente", "id_medico", "id_consultorio", "fecha_hora", "motivo", "estado", "costo"], citas)
    dx = [("J00", "Resfriado comun", "leve"), ("I10", "Hipertension esencial", "moderada"), ("E11", "Diabetes tipo 2", "moderada"), ("K29", "Gastritis", "leve"), ("J45", "Asma", "moderada"), ("S82", "Fractura de pierna", "grave"), ("L20", "Dermatitis atopica", "leve"), ("A09", "Gastroenteritis", "leve")]
    diag, rec = [], []
    meds = 30
    for ci in citas:
        if ci[6] != "atendida":
            continue
        if rng.random() < 0.8:
            d = rng.choice(dx)
            diag.append((len(diag) + 1, ci[0], d[0], d[1], d[2]))
        if rng.random() < 0.55:
            for m in rng.sample(range(1, meds + 1), rng.randint(1, 3)):
                rec.append((len(rec) + 1, ci[0], m, rng.choice(["1 cada 8 horas", "1 cada 12 horas", "1 al dia"]), rng.choice([3, 5, 7, 10, 14])))
    ins(c, "diagnosticos", ["id_diagnostico", "id_cita", "codigo_cie10", "descripcion", "gravedad"], diag)
    nombres = ["Paracetamol", "Ibuprofeno", "Amoxicilina", "Loratadina", "Omeprazol", "Metformina", "Losartan", "Salbutamol", "Diclofenaco", "Azitromicina"]
    ins(c, "medicamentos", ["id_medicamento", "nombre", "laboratorio", "precio"],
        [(i, f"{rng.choice(nombres)} {rng.choice(['250mg', '500mg', '100mg'])}", limpia(fes.company()), dinero(4, 180)) for i in range(1, meds + 1)])
    ins(c, "recetas", ["id_receta", "id_cita", "id_medicamento", "dosis", "dias_tratamiento"], rec)
    hosp = []
    for i in range(1, 151):
        ing = fecha()
        dias = rng.randint(1, 14)
        egr = ing + timedelta(days=dias) if rng.random() < 0.9 and ing + timedelta(days=dias) <= HASTA else None
        hosp.append((i, fk(400), fk(30), ing, egr, f"H-{rng.randint(100, 350)}", round(dias * dinero(800, 2500), 2) if egr else None))
    ins(c, "hospitalizaciones", ["id_hospitalizacion", "id_paciente", "id_medico", "fecha_ingreso", "fecha_egreso", "habitacion", "costo_total"], hosp)


# --------------------------------------------------------------------- telecom
def pob_telecom(c):
    ins(c, "customers", ["customer_id", "first_name", "last_name", "national_id", "email", "phone_number", "city", "registration_date"],
        [(i, (n := nom()), (a := ape()), dpi(), correo(n, a), tel(), rng.choice(MUNIS[rng.choice(DEPTOS)]), fecha(date(2018, 1, 1), HASTA)) for i in range(1, 301)])
    ins(c, "plans", ["plan_id", "plan_name", "monthly_fee", "data_gb", "minutes_included"],
        [(1, "Basic", 49.00, 2, 100), (2, "Plus", 99.00, 8, 300), (3, "Premium", 149.00, 20, 1000), (4, "Unlimited", 249.00, 60, 5000), (5, "Student", 59.00, 5, 200), (6, "Family", 199.00, 40, 2000)])
    subs, facts, pags = [], [], []
    for i in range(1, 401):
        ini = fecha(date(2021, 1, 1), HASTA - timedelta(days=60))
        est = peso([("active", 75), ("suspended", 8), ("cancelled", 17)])
        fin = ini + timedelta(days=rng.randint(60, 900)) if est == "cancelled" else None
        if fin and fin > HASTA:
            fin = HASTA
        subs.append((i, fk(300), fk(6), ini, fin, est))
        for k in range(rng.randint(2, 8)):
            em = ini + timedelta(days=30 * (k + 1))
            if em > HASTA or (fin and em > fin):
                break
            monto = dinero(49, 249)
            pagada = int(rng.random() < 0.85)
            facts.append((len(facts) + 1, i, em, em + timedelta(days=15), monto, pagada))
            if pagada:
                pags.append((len(pags) + 1, len(facts), em + timedelta(days=rng.randint(0, 20)), monto, rng.choice(["cash", "card", "transfer", "app"])))
    ins(c, "subscriptions", ["subscription_id", "customer_id", "plan_id", "start_date", "end_date", "status"], subs)
    ins(c, "invoices", ["invoice_id", "subscription_id", "issue_date", "due_date", "amount", "paid"], facts)
    ins(c, "payments", ["payment_id", "invoice_id", "payment_date", "amount_paid", "payment_method"], pags)
    ins(c, "recharges", ["recharge_id", "subscription_id", "recharge_date", "amount", "channel"],
        [(i, fk(400), fechahora(), rng.choice([10, 20, 30, 50, 100]), rng.choice(["store", "app", "bank", "website"])) for i in range(1, 1501)])
    ins(c, "calls", ["call_id", "subscription_id", "call_start", "duration_seconds", "destination_type"],
        [(i, fk(400), fechahora(), rng.randint(5, 3600), peso([("local", 60), ("national", 30), ("international", 10)])) for i in range(1, 4001)])
    tk = []
    for i in range(1, 501):
        ab = fechahora()
        cer = ab + timedelta(hours=rng.randint(1, 240)) if rng.random() < 0.85 else None
        tk.append((i, fk(300), ab, cer, rng.choice(["billing", "coverage", "device", "other"]), peso([("low", 40), ("medium", 40), ("high", 20)])))
    ins(c, "support_tickets", ["ticket_id", "customer_id", "opened_at", "closed_at", "category", "priority"], tk)


# ------------------------------------------------------------------- aerolinea
def pob_aerolinea(c):
    ap = [("GUA", "La Aurora International", "Guatemala City", "Guatemala"), ("MEX", "Benito Juarez International", "Mexico City", "Mexico"),
          ("MIA", "Miami International", "Miami", "United States"), ("IAH", "George Bush Intercontinental", "Houston", "United States"),
          ("LAX", "Los Angeles International", "Los Angeles", "United States"), ("JFK", "John F Kennedy International", "New York", "United States"),
          ("ATL", "Hartsfield Jackson Atlanta", "Atlanta", "United States"), ("SAL", "El Salvador International", "San Salvador", "El Salvador"),
          ("SJO", "Juan Santamaria International", "San Jose", "Costa Rica"), ("PTY", "Tocumen International", "Panama City", "Panama"),
          ("BOG", "El Dorado International", "Bogota", "Colombia"), ("MAD", "Adolfo Suarez Madrid Barajas", "Madrid", "Spain"),
          ("CUN", "Cancun International", "Cancun", "Mexico"), ("BZE", "Philip Goldson International", "Belize City", "Belize"),
          ("TGU", "Toncontin International", "Tegucigalpa", "Honduras")]
    ins(c, "airports", ["airport_id", "iata_code", "airport_name", "city", "country"], [(i + 1, *a) for i, a in enumerate(ap)])
    modelos = [("A320", "Airbus", 180), ("A321", "Airbus", 220), ("B737-800", "Boeing", 189), ("B737 MAX 8", "Boeing", 178), ("E190", "Embraer", 100), ("ATR 72", "ATR", 70)]
    ins(c, "aircraft", ["aircraft_id", "model", "manufacturer", "capacity", "purchase_date"],
        [(i, *modelos[(i - 1) % 6], fecha(date(2010, 1, 1), date(2022, 12, 31))) for i in range(1, 13)])
    pares = set()
    while len(pares) < 40:
        a, b = fk(15), fk(15)
        if a != b:
            pares.add((a, b))
    rutas = [(i + 1, a, b, rng.randint(300, 9000)) for i, (a, b) in enumerate(sorted(pares))]
    ins(c, "routes", ["route_id", "origin_airport_id", "destination_airport_id", "distance_km"], rutas)
    vuelos = []
    for i in range(1, 401):
        r = rng.choice(rutas)
        sal = fechahora(date(2024, 1, 1), date(2026, 3, 31))
        est = "scheduled" if sal.date() > HASTA else peso([("completed", 82), ("delayed", 12), ("cancelled", 6)])
        vuelos.append((i, r[0], fk(12), sal, sal + timedelta(minutes=int(r[3] / 800 * 60) + 30), est, dinero(90, 900)))
    ins(c, "flights", ["flight_id", "route_id", "aircraft_id", "departure_time", "arrival_time", "status", "base_price"], vuelos)
    nac = ["Guatemala", "Mexico", "United States", "El Salvador", "Honduras", "Costa Rica", "Spain", "Colombia"]
    ins(c, "passengers", ["passenger_id", "first_name", "last_name", "passport_number", "nationality", "birth_date"],
        [(i, fen.first_name(), fen.last_name(), f"P{rng.randint(1000000, 9999999)}", rng.choice(nac), fecha(date(1950, 1, 1), date(2015, 12, 31))) for i in range(1, 401)])
    book, tick = [], []
    mult = {"economy": 1.0, "business": 2.4, "first": 4.0}
    for i in range(1, 601):
        book.append((i, fk(400), fecha(date(2023, 10, 1), HASTA), 0, rng.choice(["website", "app", "agency", "counter"])))
        for _ in range(rng.randint(1, 3)):
            v = rng.choice(vuelos)
            cl = peso([("economy", 80), ("business", 15), ("first", 5)])
            tick.append((len(tick) + 1, i, v[0], f"{rng.randint(1, 35)}{rng.choice('ABCDEF')}", cl, round(v[6] * mult[cl], 2)))
    ins(c, "bookings", ["booking_id", "passenger_id", "booking_date", "total_amount", "channel"], book)
    ins(c, "tickets", ["ticket_id", "booking_id", "flight_id", "seat_number", "fare_class", "price_paid"], tick)
    c.execute("UPDATE bookings b SET total_amount = (SELECT ROUND(SUM(t.price_paid), 2) FROM tickets t WHERE t.booking_id = b.booking_id)")
    ins(c, "crew_members", ["crew_id", "first_name", "last_name", "role", "hire_date"],
        [(i, fen.first_name(), fen.last_name(), peso([("pilot", 15), ("copilot", 15), ("attendant", 70)]), fecha(date(2008, 1, 1), HASTA)) for i in range(1, 61)])
    fc = []
    for v in vuelos:
        for m in rng.sample(range(1, 61), rng.randint(4, 6)):
            fc.append((v[0], m))
    ins(c, "flight_crew", ["flight_id", "crew_id"], fc)


# --------------------------------------------------------------- tienda online
def pob_tienda_online(c):
    paises = ["Guatemala", "Mexico", "United States", "Spain", "Colombia", "Chile", "Argentina"]
    ins(c, "users", ["user_id", "full_name", "email", "country", "signup_date"],
        [(i, f"{fen.first_name()} {fen.last_name()}", f"user{i}@{rng.choice(['mail.com', 'correo.gt', 'web.net'])}", rng.choice(paises), fecha()) for i in range(1, 301)])
    cats = ["Electronics", "Books", "Home", "Toys", "Clothing", "Sports", "Beauty", "Garden"]
    ins(c, "categories", ["category_id", "category_name"], [(i + 1, n) for i, n in enumerate(cats)])
    pr = ["Wireless Mouse", "Notebook", "Desk Lamp", "Board Game", "T-Shirt", "Yoga Mat", "Face Cream", "Plant Pot", "Headphones", "Backpack"]
    prods = [(i, f"{rng.choice(pr)} {i}", fk(8), dinero(5, 600), rng.randint(0, 300), fecha(date(2021, 1, 1), HASTA)) for i in range(1, 101)]
    ins(c, "products", ["product_id", "product_name", "category_id", "price", "stock", "created_at"], prods)
    ordenes, items, pagos, envios = [], [], [], []
    for i in range(1, 1501):
        f = fechahora()
        est = peso([("delivered", 65), ("shipped", 12), ("pending", 10), ("cancelled", 13)])
        ordenes.append((i, fk(300), f, est, rng.choice(paises), 0))
        for _ in range(rng.randint(1, 4)):
            p = rng.choice(prods)
            items.append((len(items) + 1, i, p[0], rng.randint(1, 5), p[3]))
        if est != "cancelled":
            pagos.append((len(pagos) + 1, i, rng.choice(["card", "paypal", "transfer"]), f + timedelta(minutes=rng.randint(1, 600)), 0))
        if est in ("shipped", "delivered"):
            env = f.date() + timedelta(days=rng.randint(1, 4))
            envios.append((len(envios) + 1, i, rng.choice(["DHL", "FedEx", "Cargo Express", "Correos"]), env, env + timedelta(days=rng.randint(2, 12)) if est == "delivered" else None))
    ins(c, "orders", ["order_id", "user_id", "order_date", "status", "shipping_country", "total_amount"], ordenes)
    ins(c, "order_items", ["item_id", "order_id", "product_id", "quantity", "unit_price"], items)
    c.execute("UPDATE orders o SET total_amount = (SELECT ROUND(SUM(i.quantity*i.unit_price), 2) FROM order_items i WHERE i.order_id = o.order_id)")
    ins(c, "payments", ["payment_id", "order_id", "method", "paid_at", "amount"], pagos)
    c.execute("UPDATE payments p SET amount = (SELECT total_amount FROM orders o WHERE o.order_id = p.order_id)")
    ins(c, "shipments", ["shipment_id", "order_id", "carrier", "shipped_date", "delivered_date"], envios)
    entregadas = {o[0] for o in ordenes if o[3] == "delivered"}
    cand = [it for it in items if it[1] in entregadas]
    dev = [(i + 1, it[0], fecha(), rng.choice(["defective", "wrong size", "not as described", "changed mind"]), round(it[3] * it[4] * rng.choice([1, 1, 0.8]), 2)) for i, it in enumerate(rng.sample(cand, 150))]
    ins(c, "order_returns", ["return_id", "item_id", "return_date", "reason", "refund_amount"], dev)
    ins(c, "reviews", ["review_id", "product_id", "user_id", "rating", "review_date", "comment_text"],
        [(i, fk(100), fk(300), peso([(5, 40), (4, 30), (3, 15), (2, 8), (1, 7)]), fecha(), rng.choice(["Great product", "Good value", "Not what I expected", "Works fine", "Would buy again"])) for i in range(1, 601)])


# ------------------------------------------------------------------------ cine
def pob_cine(c):
    gen = ["Action", "Comedy", "Drama", "Horror", "Animation", "Sci-Fi", "Romance"]
    tit = ["The Last Horizon", "Midnight Garden", "Iron Tide", "Paper Moons", "The Silent Harbor", "Neon Streets", "Little Comet", "Broken Compass", "Echo Valley", "Red Lanterns",
           "Summer of Glass", "The Final Vote", "Wild Orchard", "Dust and Thunder", "Moonlit Road", "The Clockmaker", "Blue Mesa", "Hidden Currents", "Crown of Ash", "Tiny Giants",
           "Night Train West", "The Lighthouse Keeper", "Golden Hour", "Frozen Signal", "Orbit Nine"]
    ins(c, "movies", ["movie_id", "title", "genre", "duration_min", "release_date", "age_rating"],
        [(i + 1, t, rng.choice(gen), rng.randint(80, 175), fecha(date(2022, 1, 1), HASTA), rng.choice(["G", "PG", "PG-13", "R"])) for i, t in enumerate(tit)])
    ins(c, "theaters", ["theater_id", "theater_name", "city", "opened_date"],
        [(1, "Cine Plaza Central", "Guatemala City", date(2008, 5, 1)), (2, "Cine Mixco Mall", "Mixco", date(2012, 3, 15)), (3, "Cine Xela", "Quetzaltenango", date(2015, 8, 20)),
         (4, "Cine Antigua", "Antigua Guatemala", date(2018, 11, 2)), (5, "Cine Escuintla Centro", "Escuintla", date(2020, 2, 10))])
    ins(c, "halls", ["hall_id", "theater_id", "hall_name", "seats", "is_3d"],
        [(i, 1 + (i - 1) // 4, f"Hall {1 + (i - 1) % 4}", rng.choice([80, 120, 160, 200]), int(rng.random() < 0.3)) for i in range(1, 21)])
    ins(c, "screenings", ["screening_id", "movie_id", "hall_id", "start_time", "ticket_price"],
        [(i, fk(25), fk(20), fechahora(date(2024, 1, 1), HASTA), rng.choice([35, 40, 45, 55, 65])) for i in range(1, 601)])
    ins(c, "customers", ["customer_id", "full_name", "email", "birth_date", "joined_date"],
        [(i, f"{fen.first_name()} {fen.last_name()}", f"fan{i}@correo.gt", fecha(date(1960, 1, 1), date(2010, 12, 31)), fecha()) for i in range(1, 301)])
    ins(c, "tickets", ["ticket_id", "screening_id", "customer_id", "seat_label", "purchase_time", "price_paid"],
        [(i, fk(600), fk(300) if rng.random() > 0.4 else None, f"{rng.choice('ABCDEFGHIJ')}{rng.randint(1, 20)}", fechahora(date(2024, 1, 1), HASTA), rng.choice([35, 40, 45, 55, 65])) for i in range(1, 3001)])
    ins(c, "concessions", ["item_id", "item_name", "price"],
        [(1, "Popcorn small", 20), (2, "Popcorn large", 35), (3, "Soda", 15), (4, "Nachos", 30), (5, "Candy", 12), (6, "Hot dog", 28), (7, "Water", 8), (8, "Combo", 60)])
    ins(c, "concession_sales", ["sale_id", "ticket_id", "item_id", "quantity"], [(i, fk(3000), fk(8), rng.randint(1, 3)) for i in range(1, 1501)])


# ------------------------------------------------------------------ inventario
def pob_inventario(c):
    ins(c, "bod", ["bod_id", "nom_bod", "ubic", "cap_max"],
        [(i, f"Bodega {n}", u, rng.choice([5000, 10000, 20000])) for i, (n, u) in enumerate([("Central", "Guatemala"), ("Norte", "Coban"), ("Occidente", "Quetzaltenango"), ("Oriente", "Chiquimula"), ("Costa", "Escuintla")], 1)])
    ins(c, "prov", ["prov_id", "nom_prov", "nit", "tel", "pais"],
        [(i, limpia(fes.company()), nit(), tel(), rng.choice(["Guatemala", "Mexico", "El Salvador", "Estados Unidos", "China"])) for i in range(1, 13)])
    cats = ["Herramientas", "Electricos", "Plomeria", "Pinturas", "Ferreteria", "Seguridad", "Jardin", "Oficina"]
    ins(c, "cat_prod", ["cat_id", "nom_cat"], [(i + 1, n) for i, n in enumerate(cats)])
    base = ["Martillo", "Taladro", "Cable", "Tubo PVC", "Pintura blanca", "Clavos", "Casco", "Guantes", "Manguera", "Cinta"]
    prods = []
    for i in range(1, 101):
        p = dinero(5, 800)
        prods.append((i, f"P{i:04d}", f"{rng.choice(base)} {i}", fk(8), fk(12), p, round(p * rng.uniform(1.15, 1.6), 2), rng.randint(5, 50)))
    ins(c, "prod", ["prod_id", "cod", "nom_prod", "cat_id", "prov_id", "pre_cmp", "pre_vta", "stk_min"], prods)
    pares = set()
    while len(pares) < 300:
        pares.add((fk(5), fk(100)))
    ins(c, "exis", ["exis_id", "bod_id", "prod_id", "cant_exis", "fec_act"], [(i + 1, b, p, rng.randint(0, 500), fecha(date(2025, 6, 1), HASTA)) for i, (b, p) in enumerate(sorted(pares))])
    ins(c, "mov_inv", ["mov_id", "prod_id", "bod_id", "tip_mov", "cant", "fec_mov", "usr"],
        [(i, fk(100), fk(5), peso([("ent", 40), ("sal", 50), ("aju", 10)]), rng.randint(1, 200), fechahora(), rng.choice(["jperez", "mlopez", "agarcia", "rcastillo"])) for i in range(1, 3001)])
    ordenes, det = [], []
    for i in range(1, 151):
        fo = fecha()
        est = peso([("recibida", 70), ("pendiente", 20), ("anulada", 10)])
        fe = fo + timedelta(days=rng.randint(3, 30)) if est == "recibida" else None
        ordenes.append((i, fk(12), fo, fe, 0, est))
        for _ in range(rng.randint(1, 5)):
            p = rng.choice(prods)
            det.append((len(det) + 1, i, p[0], rng.randint(5, 300), p[5]))
    ins(c, "ord_cmp", ["ord_id", "prov_id", "fec_ord", "fec_ent", "mto_tot", "est"], ordenes)
    ins(c, "det_ord_cmp", ["det_id", "ord_id", "prod_id", "cant", "pre_unit"], det)
    c.execute("UPDATE ord_cmp o SET mto_tot = (SELECT ROUND(SUM(d.cant*d.pre_unit), 2) FROM det_ord_cmp d WHERE d.ord_id = o.ord_id)")


# --------------------------------------------------------------------- planilla
def pob_planilla(c):
    ins(c, "dep", ["dep_id", "nom_dep", "ubic"],
        [(i + 1, n, u) for i, (n, u) in enumerate([("Finanzas", "Edificio A"), ("Recursos Humanos", "Edificio A"), ("Tecnologia", "Edificio B"), ("Ventas", "Edificio C"), ("Operaciones", "Planta"), ("Legal", "Edificio A"), ("Mercadeo", "Edificio C"), ("Logistica", "Planta")])])
    pue = [("Gerente", 18000, 35000), ("Analista", 6000, 12000), ("Asistente", 3500, 6000), ("Desarrollador", 8000, 20000), ("Contador", 6500, 13000), ("Vendedor", 4000, 9000),
           ("Supervisor", 7000, 14000), ("Operario", 3200, 5500), ("Abogado", 9000, 22000), ("Disenador", 5500, 11000), ("Coordinador", 7500, 15000), ("Auditor", 8000, 16000),
           ("Piloto de reparto", 4000, 7000), ("Recepcionista", 3300, 5000), ("Director", 30000, 55000)]
    ins(c, "pue", ["pue_id", "nom_pue", "sal_min", "sal_max"], [(i + 1, *p) for i, p in enumerate(pue)])
    emp = []
    for i in range(1, 151):
        pid = fk(15)
        emp.append((i, nom(), ape(), dpi(), fecha(date(1965, 1, 1), date(2003, 12, 31)), fecha(date(2012, 1, 1), HASTA), fk(8), pid,
                    dinero(pue[pid - 1][1], pue[pid - 1][2]), None if i <= 10 else fk(10), "activo" if rng.random() < 0.9 else "retirado"))
    ins(c, "emp", ["emp_id", "nom", "ape", "dpi", "fec_nac", "fec_ing", "dep_id", "pue_id", "sal_base", "jefe_id", "est"], emp)
    pla = []
    for e in emp:
        for anio in (2024, 2025):
            for mes in range(1, 13):
                if date(anio, mes, 28) < e[5] or (e[10] == "retirado" and anio == 2025 and mes > 6):
                    continue
                dev = e[8]
                igss = round(dev * 0.0483, 2)
                isr = round(max(dev - 8000, 0) * 0.05, 2)
                pla.append((len(pla) + 1, e[0], mes, anio, dev, igss, isr, 250.00, round(dev - igss - isr + 250, 2)))
    ins(c, "pla", ["pla_id", "emp_id", "mes", "anio", "sal_dev", "igss", "isr", "bono", "sal_liq"], pla)
    vac = []
    for i in range(1, 201):
        ini = fecha(date(2023, 1, 1), date(2025, 11, 30))
        d = rng.choice([5, 10, 15])
        vac.append((i, fk(150), ini, ini + timedelta(days=d + d // 5), d))
    ins(c, "vac", ["vac_id", "emp_id", "fec_ini", "fec_fin", "dias"], vac)
    ins(c, "aus", ["aus_id", "emp_id", "fec_aus", "mot", "justif"],
        [(i, fk(150), fecha(), (m := rng.choice(["enfermedad", "personal", "sin aviso"])), int(m != "sin aviso" and rng.random() < 0.8)) for i in range(1, 401)])
    ins(c, "eva", ["eva_id", "emp_id", "anio", "punt"], [(2 * i + k + 1, i + 1, 2024 + k, round(min(100, max(40, rng.gauss(78, 11))), 1)) for i in range(150) for k in (0, 1)])
    caps = ["Excel avanzado", "Liderazgo", "Seguridad industrial", "Atencion al cliente", "Ciberseguridad", "Gestion del tiempo", "Primeros auxilios", "Ingles tecnico"]
    ins(c, "cap", ["cap_id", "nom_cap", "fec_cap", "hrs"], [(i, f"{rng.choice(caps)} {i}", fecha(), rng.choice([4, 8, 16, 24])) for i in range(1, 21)])
    pares = set()
    while len(pares) < 400:
        pares.add((fk(150), fk(20)))
    ins(c, "emp_cap", ["emp_id", "cap_id"], sorted(pares))


# -------------------------------------------------------------------- delivery
def pob_delivery(c):
    ins(c, "zona", ["zona_id", "nom_zona", "mun"],
        [(i, f"Zona {z}", m) for i, (z, m) in enumerate([(1, "Guatemala"), (4, "Guatemala"), (7, "Guatemala"), (9, "Guatemala"), (10, "Guatemala"), (11, "Guatemala"), (15, "Guatemala"), (16, "Guatemala"), (1, "Mixco"), (4, "Mixco"), (1, "Villa Nueva"), (2, "Villa Nueva")], 1)])
    tipos = ["pizza", "tipica", "hamburguesas", "sushi", "pollo frito", "mariscos", "vegetariana", "postres"]
    rests = [(i, f"{rng.choice(['El', 'La', 'Casa', 'Don'])} {limpia(fes.last_name())} {i}", fk(12), rng.choice(tipos), fecha(date(2021, 1, 1), HASTA), round(rng.uniform(3.2, 5.0), 1)) for i in range(1, 31)]
    ins(c, "restau", ["rest_id", "nom_rest", "zona_id", "tipo_coc", "fec_afil", "calif"], rests)
    platos = ["Pizza familiar", "Pepian", "Hamburguesa doble", "Rollo california", "Combo de pollo", "Ceviche", "Ensalada", "Pastel de chocolate", "Tacos", "Pasta alfredo"]
    plat = [(i, 1 + (i - 1) // 7 % 30, f"{rng.choice(platos)} {i}", dinero(18, 140), int(rng.random() > 0.07)) for i in range(1, 211)]
    ins(c, "plat", ["plat_id", "rest_id", "nom_plat", "pre", "disp"], plat)
    ins(c, "cli", ["cli_id", "nom", "tel", "zona_id", "fec_reg"], [(i, f"{nom()} {ape()}", tel(), fk(12), fecha()) for i in range(1, 301)])
    ins(c, "repa", ["repa_id", "nom", "vehiculo", "fec_ing", "activo"], [(i, f"{nom()} {ape()}", rng.choice(["moto", "moto", "bicicleta", "carro"]), fecha(date(2021, 1, 1), HASTA), int(rng.random() < 0.85)) for i in range(1, 26)])
    por_rest = {}
    for p in plat:
        por_rest.setdefault(p[1], []).append(p)
    ped, det = [], []
    for i in range(1, 2501):
        r = fk(30)
        fp = fechahora()
        est = peso([("entregado", 85), ("cancelado", 8), ("en_camino", 7)])
        fe = fp + timedelta(minutes=rng.randint(20, 75)) if est == "entregado" else None
        ped.append((i, fk(300), r, None if est == "cancelado" else fk(25), fp, fe, est, 0, 0 if rng.random() < 0.5 else rng.choice([5, 10, 15, 20])))
        for _ in range(rng.randint(1, 4)):
            p = rng.choice(por_rest[r])
            det.append((len(det) + 1, i, p[0], rng.randint(1, 3), p[3]))
    ins(c, "ped", ["ped_id", "cli_id", "rest_id", "repa_id", "fec_ped", "fec_ent", "est", "mto_tot", "propina"], ped)
    ins(c, "det_ped", ["det_id", "ped_id", "plat_id", "cant", "pre_unit"], det)
    c.execute("UPDATE ped p SET mto_tot = (SELECT ROUND(SUM(d.cant*d.pre_unit), 2) FROM det_ped d WHERE d.ped_id = p.ped_id)")
    ent = [p for p in ped if p[6] == "entregado"]
    res = [(i + 1, p[0], peso([(5, 40), (4, 30), (3, 15), (2, 8), (1, 7)]), rng.choice(["Muy rico", "Llego tarde", "Todo bien", "Excelente servicio", "Faltaba un platillo"]), p[5].date() + timedelta(days=rng.randint(0, 3))) for i, p in enumerate(rng.sample(ent, 1200))]
    ins(c, "resena", ["res_id", "ped_id", "punt", "coment", "fec_res"], res)


# --------------------------------------------------------------------- seguros
def pob_seguros(c):
    ins(c, "ase", ["ase_id", "nom", "ape", "dpi", "fec_nac", "tel", "dep", "fec_reg"],
        [(i, nom(), ape(), dpi(), fecha(date(1950, 1, 1), date(2004, 12, 31)), tel(), rng.choice(DEPTOS), fecha(date(2021, 1, 1), HASTA)) for i in range(1, 301)])
    ins(c, "ram", ["ram_id", "nom_ram"], [(1, "vida"), (2, "auto"), (3, "salud"), (4, "hogar")])
    ins(c, "agen", ["agen_id", "nom", "fec_ing", "comis_pct"], [(i, f"{nom()} {ape()}", fecha(date(2010, 1, 1), HASTA), round(rng.uniform(5, 18), 2)) for i in range(1, 16)])
    pol, sini, pag, ben, aju = [], [], [], [], []
    for i in range(1, 501):
        ini = fecha(date(2022, 1, 1), HASTA)
        fin = ini + timedelta(days=365)
        ram = fk(4)
        est = "cancelada" if rng.random() < 0.05 else ("vigente" if fin >= HASTA else "vencida")
        mto = dinero(20000, 800000)
        prima = round(mto * rng.uniform(0.01, 0.05), 2)
        pol.append((i, fk(300), ram, fk(15), ini, fin, mto, prima, est))
        for k in range(min(12, max(1, (HASTA - ini).days // 30))):
            pag.append((len(pag) + 1, i, ini + timedelta(days=30 * k + rng.randint(0, 4)), round(prima / 12, 2), rng.choice(["debito", "tarjeta", "efectivo"])))
        if ram == 1:
            n = rng.randint(1, 3)
            cuotas = [round(100 / n, 2)] * n
            cuotas[-1] = round(100 - sum(cuotas[:-1]), 2)
            for pc in cuotas:
                ben.append((len(ben) + 1, i, f"{nom()} {ape()}", rng.choice(["conyuge", "hijo", "padre", "hermano"]), pc))
    ins(c, "pol", ["pol_id", "ase_id", "ram_id", "agen_id", "fec_ini", "fec_fin", "mto_ase", "prima_anual", "est"], pol)
    ins(c, "pag_prima", ["pag_id", "pol_id", "fec_pag", "mto", "metodo"], pag)
    ins(c, "benef", ["benef_id", "pol_id", "nom", "parent", "pct"], ben)
    for i in range(1, 251):
        p = rng.choice(pol)
        fs = fecha(p[4], min(p[5], HASTA))
        recl = round(p[6] * rng.uniform(0.01, 0.3), 2)
        est = peso([("pagado", 55), ("rechazado", 15), ("abierto", 30)])
        mp = None if est == "abierto" else (0.0 if est == "rechazado" else round(recl * rng.uniform(0.6, 1.0), 2))
        sini.append((i, p[0], fs, fs + timedelta(days=rng.randint(0, 10)), recl, mp, est, rng.choice(["Colision vehicular", "Robo", "Incendio", "Hospitalizacion", "Dano por agua", "Fallecimiento"])))
        if est != "abierto" or rng.random() < 0.3:
            aju.append((len(aju) + 1, i, f"{nom()} {ape()}", fs + timedelta(days=rng.randint(5, 25)), "procede" if est == "pagado" else rng.choice(["procede", "no_procede"])))
    ins(c, "sini", ["sini_id", "pol_id", "fec_sini", "fec_rep", "mto_recl", "mto_pag", "est", "descr"], sini)
    ins(c, "ajust", ["ajust_id", "sini_id", "nom_ajust", "fec_insp", "dictamen"], aju)


FUNCIONES = {f.__name__[4:]: f for f in (
    pob_supermercado, pob_universidad, pob_banco, pob_hospital, pob_telecom, pob_aerolinea,
    pob_tienda_online, pob_cine, pob_inventario, pob_planilla, pob_delivery, pob_seguros)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--password", default="root")
    ap.add_argument("--solo", nargs="*", help="only these schemas")
    args = ap.parse_args()
    conn = pymysql.connect(host=args.host, user="root", password=args.password, charset="utf8mb4", autocommit=False)
    cur = conn.cursor()
    for nombre, fn in FUNCIONES.items():
        if args.solo and nombre not in args.solo:
            continue
        cur.execute(f"USE `tr_{nombre}`")
        cur.execute("SET FOREIGN_KEY_CHECKS=0")
        cur.execute("SHOW TABLES")
        for (t,) in cur.fetchall():
            cur.execute(f"TRUNCATE TABLE `{t}`")
        cur.execute("SET FOREIGN_KEY_CHECKS=1")
        fn(cur)
        conn.commit()
        cur.execute("SELECT SUM(table_rows) FROM information_schema.tables WHERE table_schema = DATABASE()")
        print(f"tr_{nombre}: ~{int(cur.fetchone()[0] or 0)} filas")
    conn.close()


if __name__ == "__main__":
    main()
