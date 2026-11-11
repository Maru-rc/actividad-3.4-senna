"""
Módulo de nómina - Transportes del Gran Caribe Colombiano S.C.A. (TransCaribeCol)
Aplicación de consola. Persistencia en archivo plano TXT.
"""

import os

ARCHIVO = "nomina.txt"
SEP = "|"

# ---------------------------------------------------------------- Constantes
VALOR_HORA_ADMIN = 20000
VALOR_HORA_EXTRA = 25000
ARL_ADMIN = 0.00522

VALOR_HORA_OPERATIVO = 40000
IBC_OPERATIVO = 0.40
SALUD_OPERATIVO = 0.125
PENSION_OPERATIVO = 0.16

SALUD_ADMIN = 0.04
PENSION_ADMIN = 0.04

# cargo: (horas mensuales, % ARL)
CARGOS_OPERATIVOS = {
    "1": ("Conductor", 160, 0.01044),
    "2": ("Oficios Generales", 100, 0.00522),
    "3": ("Vigilancia", 336, 0.04350),
}

ENCABEZADO = ["Nombre", "Tipo", "Cargo", "HT", "Salario", "HE", "TPHE",
              "Salud", "Pension", "ARL", "Total a pagar"]

# Estructura de datos en memoria: lista de listas (matriz)
nomina = []


# ------------------------------------------------------------------ Cálculos
def calcular_administrativo(nombre, cargo, horas, horas_extra):
    salario = horas * VALOR_HORA_ADMIN
    tphe = horas_extra * VALOR_HORA_EXTRA
    base = salario + tphe                      # las extras cuentan para prestaciones
    salud = round(base * SALUD_ADMIN)
    pension = round(base * PENSION_ADMIN)
    arl = round(base * ARL_ADMIN)
    total = base - salud - pension - arl
    return [nombre, "ADMINISTRATIVO", cargo, horas, salario, horas_extra,
            tphe, salud, pension, arl, total]


def calcular_operativo(nombre, cargo, horas, porc_arl):
    salario = horas * VALOR_HORA_OPERATIVO
    ibc = salario * IBC_OPERATIVO              # Índice Base de Cotización (40%)
    salud = round(ibc * SALUD_OPERATIVO)
    pension = round(ibc * PENSION_OPERATIVO)
    arl = round(ibc * porc_arl)
    # La empresa paga el valor completo; salud, pensión y ARL son un estimado
    # de lo que el trabajador debe pagar por su cuenta.
    total = salario
    return [nombre, "OPERATIVO", cargo, horas, salario, 0, 0,
            salud, pension, arl, total]


# ------------------------------------------------------------------- Entradas
def leer_texto(msg):
    while True:
        v = input(msg).strip()
        if v:
            return v
        print("  El campo no puede estar vacío.")


def leer_entero(msg, minimo=0):
    while True:
        try:
            v = int(input(msg))
            if v >= minimo:
                return v
            print(f"  Debe ser un número >= {minimo}.")
        except ValueError:
            print("  Ingrese un número entero válido.")


# ----------------------------------------------------------------- Opciones
def registrar_administrativo():
    print("\n--- Registrar empleado ADMINISTRATIVO ---")
    nombre = leer_texto("Nombre completo: ")
    cargo = leer_texto("Cargo: ")
    horas = leer_entero("Horas trabajadas (HT): ")
    extras = leer_entero("Horas extras (HE): ")
    registro = calcular_administrativo(nombre, cargo, horas, extras)
    nomina.append(registro)
    mostrar_volante(registro)
    print("Empleado registrado.")


def registrar_operativo():
    print("\n--- Registrar trabajador OPERATIVO ---")
    nombre = leer_texto("Nombre completo: ")
    print("Cargo:")
    for k, (c, h, a) in CARGOS_OPERATIVOS.items():
        print(f"  {k}. {c} ({h} h/mes, ARL {a * 100:.3f}%)")
    op = ""
    while op not in CARGOS_OPERATIVOS:
        op = input("Seleccione cargo: ").strip()
    cargo, horas, arl = CARGOS_OPERATIVOS[op]
    registro = calcular_operativo(nombre, cargo, horas, arl)
    nomina.append(registro)
    mostrar_volante(registro)
    print("Trabajador registrado.")


def fmt(n):
    return f"${n:,.0f}".replace(",", ".")


def mostrar_volante(r):
    print("\n" + "=" * 52)
    print("   TransCaribeCol S.C.A. - VOLANTE DE PAGO")
    print("=" * 52)
    print(f"Nombre : {r[0]}")
    print(f"Tipo   : {r[1]}")
    print(f"Cargo  : {r[2]}")
    print("-" * 52)
    print(f"Horas trabajadas (HT)   : {r[3]}")
    print(f"Salario                 : {fmt(r[4])}")
    if r[1] == "ADMINISTRATIVO":
        print(f"Horas extras (HE)       : {r[5]}")
        print(f"Total horas extras TPHE : {fmt(r[6])}")
    if r[1] == "ADMINISTRATIVO":
        print(f"Salud                   : {fmt(r[7])}")
        print(f"Pensión                 : {fmt(r[8])}")
        print(f"ARL                     : {fmt(r[9])}")
        print("-" * 52)
        print(f"TOTAL A PAGAR           : {fmt(r[10])}")
    else:
        print(f"TOTAL A PAGAR           : {fmt(r[10])}")
        print("-" * 52)
        print("Aportes estimados a cargo del trabajador:")
        print(f"  Salud                 : {fmt(r[7])}")
        print(f"  Pensión               : {fmt(r[8])}")
        print(f"  ARL                   : {fmt(r[9])}")
        print(f"  Total aportes         : {fmt(r[7] + r[8] + r[9])}")
    print("=" * 52)


def listar_nomina():
    if not nomina:
        print("\nNo hay empleados registrados.")
        return
    print("\n" + " | ".join(ENCABEZADO))
    print("-" * 110)
    for r in nomina:
        print(" | ".join(str(x) for x in r))
    print(f"\nTotal nómina a pagar: {fmt(sum(r[10] for r in nomina))}")


def ver_volante():
    if not nomina:
        print("\nNo hay empleados registrados.")
        return
    for i, r in enumerate(nomina, 1):
        print(f"  {i}. {r[0]} ({r[1]})")
    i = leer_entero("Número de empleado: ", 1)
    if i <= len(nomina):
        mostrar_volante(nomina[i - 1])
    else:
        print("  Número fuera de rango.")


# ------------------------------------------------------------- Archivo TXT
def guardar_txt():
    with open(ARCHIVO, "w", encoding="utf-8") as f:
        f.write(SEP.join(ENCABEZADO) + "\n")
        for r in nomina:
            f.write(SEP.join(str(x) for x in r) + "\n")
    print(f"\nNómina guardada en '{ARCHIVO}' ({len(nomina)} registros).")


def cargar_txt():
    if not os.path.exists(ARCHIVO):
        print(f"\nNo existe el archivo '{ARCHIVO}'.")
        return
    nomina.clear()
    with open(ARCHIVO, encoding="utf-8") as f:
        next(f, None)  # salta encabezado
        for linea in f:
            p = linea.strip().split(SEP)
            if len(p) != len(ENCABEZADO):
                continue
            nomina.append(p[:3] + [int(x) for x in p[3:]])
    print(f"\nSe cargaron {len(nomina)} registros desde '{ARCHIVO}'.")


# -------------------------------------------------------------------- Menú
def menu():
    cargar_txt() if os.path.exists(ARCHIVO) else None
    while True:
        print("\n===== NÓMINA TRANSCARIBECOL =====")
        print("1. Registrar empleado administrativo")
        print("2. Registrar trabajador operativo")
        print("3. Listar nómina")
        print("4. Ver volante de pago")
        print("5. Guardar en archivo TXT")
        print("6. Cargar desde archivo TXT")
        print("0. Salir")
        op = input("Opción: ").strip()
        if op == "1":
            registrar_administrativo()
        elif op == "2":
            registrar_operativo()
        elif op == "3":
            listar_nomina()
        elif op == "4":
            ver_volante()
        elif op == "5":
            guardar_txt()
        elif op == "6":
            cargar_txt()
        elif op == "0":
            guardar_txt()
            print("¡Hasta luego!")
            break
        else:
            print("Opción inválida.")


menu()