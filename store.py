#!/usr/bin/env python3
"""
Aplicación de Gestión de Tienda
Permite administrar productos, ventas, costos, ganancias e inventario.
"""

import json
import os
import datetime
from typing import Optional

DATA_FILE = "tienda_data.json"


# ─────────────────────────────────────────────
#  Almacenamiento
# ─────────────────────────────────────────────

def cargar_datos() -> dict:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"productos": {}, "ventas": [], "siguiente_id": 1}


def guardar_datos(datos: dict) -> None:
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, indent=2, ensure_ascii=False)


# ─────────────────────────────────────────────
#  Helpers de consola
# ─────────────────────────────────────────────

def limpiar():
    os.system("cls" if os.name == "nt" else "clear")


def separador(char="─", ancho=60):
    print(char * ancho)


def titulo(texto: str):
    separador("═")
    print(f"  {texto}")
    separador("═")


def pedir_float(prompt: str, minimo: float = 0.0) -> float:
    while True:
        try:
            valor = float(input(prompt).replace(",", "."))
            if valor < minimo:
                print(f"  El valor debe ser >= {minimo}")
                continue
            return valor
        except ValueError:
            print("  Ingrese un número válido.")


def pedir_int(prompt: str, minimo: int = 0) -> int:
    while True:
        try:
            valor = int(input(prompt))
            if valor < minimo:
                print(f"  El valor debe ser >= {minimo}")
                continue
            return valor
        except ValueError:
            print("  Ingrese un número entero válido.")


def pedir_texto(prompt: str) -> str:
    while True:
        valor = input(prompt).strip()
        if valor:
            return valor
        print("  El campo no puede estar vacío.")


# ─────────────────────────────────────────────
#  Productos
# ─────────────────────────────────────────────

def agregar_producto(datos: dict) -> None:
    titulo("AGREGAR PRODUCTO")
    nombre     = pedir_texto("  Nombre del producto : ")
    categoria  = pedir_texto("  Categoría           : ")
    costo      = pedir_float("  Costo unitario ($)  : ", 0.01)
    precio     = pedir_float("  Precio de venta ($) : ", 0.01)
    stock      = pedir_int ("  Stock inicial       : ", 0)

    pid = str(datos["siguiente_id"])
    datos["productos"][pid] = {
        "id": pid,
        "nombre": nombre,
        "categoria": categoria,
        "costo": costo,
        "precio": precio,
        "stock": stock,
    }
    datos["siguiente_id"] += 1
    guardar_datos(datos)
    ganancia = precio - costo
    margen   = (ganancia / precio * 100) if precio else 0
    print(f"\n  ✓ Producto #{pid} guardado.")
    print(f"    Ganancia por unidad: ${ganancia:.2f}  |  Margen: {margen:.1f}%")
    input("\n  Presione Enter para continuar...")


def listar_productos(datos: dict, pausa: bool = True) -> None:
    titulo("LISTADO DE PRODUCTOS")
    productos = datos["productos"]
    if not productos:
        print("  No hay productos registrados.")
        if pausa:
            input("\n  Presione Enter para continuar...")
        return

    fmt = "{:<4} {:<22} {:<14} {:>9} {:>9} {:>9} {:>7} {:>6}"
    print(fmt.format("ID", "Nombre", "Categoría", "Costo", "Precio", "Ganancia", "Margen", "Stock"))
    separador()
    for p in productos.values():
        gan    = p["precio"] - p["costo"]
        margen = (gan / p["precio"] * 100) if p["precio"] else 0
        print(fmt.format(
            p["id"],
            p["nombre"][:22],
            p["categoria"][:14],
            f"${p['costo']:.2f}",
            f"${p['precio']:.2f}",
            f"${gan:.2f}",
            f"{margen:.1f}%",
            p["stock"],
        ))
    separador()
    if pausa:
        input("\n  Presione Enter para continuar...")


def buscar_producto(datos: dict, pid: Optional[str] = None):
    if pid is None:
        pid = input("  ID del producto: ").strip()
    return datos["productos"].get(pid)


def editar_producto(datos: dict) -> None:
    titulo("EDITAR PRODUCTO")
    listar_productos(datos, pausa=False)
    p = buscar_producto(datos)
    if not p:
        print("  Producto no encontrado.")
        input("\n  Presione Enter para continuar...")
        return

    print(f"\n  Editando: {p['nombre']}  (deje en blanco para no cambiar)")
    campos = [
        ("nombre",    "  Nuevo nombre       : ", str,   None),
        ("categoria", "  Nueva categoría    : ", str,   None),
        ("costo",     "  Nuevo costo ($)    : ", float, 0.01),
        ("precio",    "  Nuevo precio ($)   : ", float, 0.01),
        ("stock",     "  Nuevo stock        : ", int,   0),
    ]
    for campo, prompt, tipo, minimo in campos:
        entrada = input(prompt).strip()
        if not entrada:
            continue
        try:
            valor = tipo(entrada.replace(",", "."))
            if minimo is not None and valor < minimo:
                print(f"  Valor mínimo: {minimo} — sin cambios.")
                continue
            p[campo] = valor
        except ValueError:
            print("  Valor inválido — sin cambios.")

    guardar_datos(datos)
    print("  ✓ Producto actualizado.")
    input("\n  Presione Enter para continuar...")


def eliminar_producto(datos: dict) -> None:
    titulo("ELIMINAR PRODUCTO")
    listar_productos(datos, pausa=False)
    p = buscar_producto(datos)
    if not p:
        print("  Producto no encontrado.")
        input("\n  Presione Enter para continuar...")
        return
    confirmar = input(f"  ¿Eliminar '{p['nombre']}'? (s/n): ").strip().lower()
    if confirmar == "s":
        del datos["productos"][p["id"]]
        guardar_datos(datos)
        print("  ✓ Producto eliminado.")
    else:
        print("  Cancelado.")
    input("\n  Presione Enter para continuar...")


def ajustar_stock(datos: dict) -> None:
    titulo("AJUSTAR STOCK")
    listar_productos(datos, pausa=False)
    p = buscar_producto(datos)
    if not p:
        print("  Producto no encontrado.")
        input("\n  Presione Enter para continuar...")
        return
    print(f"  Stock actual de '{p['nombre']}': {p['stock']}")
    nuevo = pedir_int("  Nuevo stock: ", 0)
    p["stock"] = nuevo
    guardar_datos(datos)
    print("  ✓ Stock actualizado.")
    input("\n  Presione Enter para continuar...")


# ─────────────────────────────────────────────
#  Ventas
# ─────────────────────────────────────────────

def registrar_venta(datos: dict) -> None:
    titulo("REGISTRAR VENTA")
    listar_productos(datos, pausa=False)

    p = buscar_producto(datos)
    if not p:
        print("  Producto no encontrado.")
        input("\n  Presione Enter para continuar...")
        return

    print(f"\n  Producto : {p['nombre']}")
    print(f"  Precio   : ${p['precio']:.2f}  |  Stock: {p['stock']}")

    cantidad = pedir_int("  Cantidad a vender: ", 1)
    if cantidad > p["stock"]:
        print(f"  Stock insuficiente (disponible: {p['stock']}).")
        input("\n  Presione Enter para continuar...")
        return

    descuento = pedir_float("  Descuento % (0 si no hay): ", 0.0)
    precio_final = p["precio"] * (1 - descuento / 100)
    total        = precio_final * cantidad
    ganancia     = (precio_final - p["costo"]) * cantidad

    venta = {
        "fecha"        : datetime.datetime.now().isoformat(timespec="seconds"),
        "producto_id"  : p["id"],
        "producto"     : p["nombre"],
        "cantidad"     : cantidad,
        "costo_unit"   : p["costo"],
        "precio_unit"  : precio_final,
        "descuento_pct": descuento,
        "total"        : total,
        "ganancia"     : ganancia,
    }
    datos["ventas"].append(venta)
    p["stock"] -= cantidad
    guardar_datos(datos)

    print(f"\n  ─── Resumen de venta ───")
    print(f"  Precio c/u : ${precio_final:.2f}")
    print(f"  Cantidad   : {cantidad}")
    print(f"  Total      : ${total:.2f}")
    print(f"  Ganancia   : ${ganancia:.2f}")
    print(f"  Stock rest.: {p['stock']}")
    input("\n  Presione Enter para continuar...")


def historial_ventas(datos: dict) -> None:
    titulo("HISTORIAL DE VENTAS")
    ventas = datos["ventas"]
    if not ventas:
        print("  No hay ventas registradas.")
        input("\n  Presione Enter para continuar...")
        return

    fmt = "{:<20} {:<22} {:>6} {:>9} {:>9} {:>9}"
    print(fmt.format("Fecha", "Producto", "Cant.", "Precio", "Total", "Ganancia"))
    separador()
    for v in ventas[-50:]:          # Últimas 50
        print(fmt.format(
            v["fecha"][:19],
            v["producto"][:22],
            v["cantidad"],
            f"${v['precio_unit']:.2f}",
            f"${v['total']:.2f}",
            f"${v['ganancia']:.2f}",
        ))
    separador()
    if len(ventas) > 50:
        print(f"  (Mostrando últimas 50 de {len(ventas)} ventas)")
    input("\n  Presione Enter para continuar...")


# ─────────────────────────────────────────────
#  Reportes
# ─────────────────────────────────────────────

def reporte_general(datos: dict) -> None:
    titulo("REPORTE GENERAL")
    productos = datos["productos"]
    ventas    = datos["ventas"]

    # ── Inventario
    total_inv_costo  = sum(p["costo"]  * p["stock"] for p in productos.values())
    total_inv_precio = sum(p["precio"] * p["stock"] for p in productos.values())
    sin_stock        = [p for p in productos.values() if p["stock"] == 0]
    stock_bajo       = [p for p in productos.values() if 0 < p["stock"] <= 5]

    # ── Ventas
    total_ventas    = sum(v["total"]    for v in ventas)
    total_ganancias = sum(v["ganancia"] for v in ventas)
    total_costo_v   = total_ventas - total_ganancias
    margen_gral     = (total_ganancias / total_ventas * 100) if total_ventas else 0

    # ── Producto más vendido
    conteo: dict = {}
    for v in ventas:
        conteo[v["producto"]] = conteo.get(v["producto"], 0) + v["cantidad"]
    top_prod = max(conteo, key=conteo.get) if conteo else "—"

    print(f"  {'INVENTARIO':─<50}")
    print(f"  Productos registrados : {len(productos)}")
    print(f"  Valor al costo        : ${total_inv_costo:,.2f}")
    print(f"  Valor al precio venta : ${total_inv_precio:,.2f}")
    print(f"  Productos sin stock   : {len(sin_stock)}")
    print(f"  Productos stock ≤ 5   : {len(stock_bajo)}")

    print(f"\n  {'VENTAS':─<50}")
    print(f"  Total de transacciones: {len(ventas)}")
    print(f"  Ingresos totales      : ${total_ventas:,.2f}")
    print(f"  Costo de ventas       : ${total_costo_v:,.2f}")
    print(f"  Ganancias totales     : ${total_ganancias:,.2f}")
    print(f"  Margen general        : {margen_gral:.1f}%")
    print(f"  Producto más vendido  : {top_prod}")

    if sin_stock:
        print(f"\n  {'ALERTAS — Sin stock':─<50}")
        for p in sin_stock:
            print(f"    #{p['id']} {p['nombre']}")

    if stock_bajo:
        print(f"\n  {'ALERTAS — Stock bajo (≤ 5)':─<50}")
        for p in stock_bajo:
            print(f"    #{p['id']} {p['nombre']}  stock={p['stock']}")

    input("\n  Presione Enter para continuar...")


def reporte_rentabilidad(datos: dict) -> None:
    titulo("RENTABILIDAD POR PRODUCTO")
    productos = datos["productos"]
    if not productos:
        print("  Sin productos.")
        input("\n  Presione Enter para continuar...")
        return

    filas = []
    for p in productos.values():
        gan    = p["precio"] - p["costo"]
        margen = (gan / p["precio"] * 100) if p["precio"] else 0
        filas.append((p["nombre"], p["costo"], p["precio"], gan, margen))

    filas.sort(key=lambda x: x[4], reverse=True)
    fmt = "{:<24} {:>9} {:>9} {:>9} {:>8}"
    print(fmt.format("Producto", "Costo", "Precio", "Ganancia", "Margen"))
    separador()
    for nombre, costo, precio, gan, margen in filas:
        print(fmt.format(nombre[:24], f"${costo:.2f}", f"${precio:.2f}", f"${gan:.2f}", f"{margen:.1f}%"))
    separador()
    input("\n  Presione Enter para continuar...")


# ─────────────────────────────────────────────
#  Menús
# ─────────────────────────────────────────────

def menu_productos(datos: dict) -> None:
    opciones = {
        "1": ("Listar productos",       lambda: listar_productos(datos)),
        "2": ("Agregar producto",       lambda: agregar_producto(datos)),
        "3": ("Editar producto",        lambda: editar_producto(datos)),
        "4": ("Eliminar producto",      lambda: eliminar_producto(datos)),
        "5": ("Ajustar stock",          lambda: ajustar_stock(datos)),
        "0": ("Volver",                 None),
    }
    while True:
        limpiar()
        titulo("GESTIÓN DE PRODUCTOS")
        for k, (desc, _) in opciones.items():
            print(f"  [{k}] {desc}")
        separador()
        op = input("  Opción: ").strip()
        if op == "0":
            break
        if op in opciones and opciones[op][1]:
            limpiar()
            opciones[op][1]()


def menu_ventas(datos: dict) -> None:
    opciones = {
        "1": ("Registrar venta",    lambda: registrar_venta(datos)),
        "2": ("Historial de ventas",lambda: historial_ventas(datos)),
        "0": ("Volver",             None),
    }
    while True:
        limpiar()
        titulo("GESTIÓN DE VENTAS")
        for k, (desc, _) in opciones.items():
            print(f"  [{k}] {desc}")
        separador()
        op = input("  Opción: ").strip()
        if op == "0":
            break
        if op in opciones and opciones[op][1]:
            limpiar()
            opciones[op][1]()


def menu_reportes(datos: dict) -> None:
    opciones = {
        "1": ("Reporte general",        lambda: reporte_general(datos)),
        "2": ("Rentabilidad por producto", lambda: reporte_rentabilidad(datos)),
        "0": ("Volver",                 None),
    }
    while True:
        limpiar()
        titulo("REPORTES")
        for k, (desc, _) in opciones.items():
            print(f"  [{k}] {desc}")
        separador()
        op = input("  Opción: ").strip()
        if op == "0":
            break
        if op in opciones and opciones[op][1]:
            limpiar()
            opciones[op][1]()


def menu_principal(datos: dict) -> None:
    while True:
        limpiar()
        titulo("GESTIÓN DE TIENDA  v1.0")
        print("  [1] Productos")
        print("  [2] Ventas")
        print("  [3] Reportes")
        print("  [0] Salir")
        separador()
        op = input("  Opción: ").strip()
        if op == "1":
            menu_productos(datos)
        elif op == "2":
            menu_ventas(datos)
        elif op == "3":
            menu_reportes(datos)
        elif op == "0":
            print("\n  Hasta luego!\n")
            break


# ─────────────────────────────────────────────
#  Entry point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    datos = cargar_datos()
    menu_principal(datos)
