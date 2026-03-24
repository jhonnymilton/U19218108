#!/usr/bin/env python3
"""
Gestión de Tienda – Interfaz Gráfica (Tkinter)
Ejecutar: python3 store_gui.py
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import datetime
import json
import os

DATA_FILE = "tienda_data.json"

# ─────────────────────────────────────────────
#  Paleta de colores
# ─────────────────────────────────────────────
C = {
    "bg"       : "#F0F4F8",
    "sidebar"  : "#1E293B",
    "header"   : "#0F172A",
    "accent"   : "#3B82F6",
    "accent2"  : "#10B981",
    "danger"   : "#EF4444",
    "warning"  : "#F59E0B",
    "white"    : "#FFFFFF",
    "text"     : "#1E293B",
    "text_light": "#64748B",
    "border"   : "#CBD5E1",
    "row_even" : "#F8FAFC",
    "row_odd"  : "#FFFFFF",
    "green_bg" : "#D1FAE5",
    "red_bg"   : "#FEE2E2",
}

FONTS = {
    "title"  : ("Segoe UI", 18, "bold"),
    "heading": ("Segoe UI", 12, "bold"),
    "body"   : ("Segoe UI", 10),
    "small"  : ("Segoe UI", 9),
    "mono"   : ("Consolas", 10),
}

# ─────────────────────────────────────────────
#  Persistencia
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
#  Widget helpers
# ─────────────────────────────────────────────

def make_button(parent, text, command, color=None, width=14, **kw):
    color = color or C["accent"]
    btn = tk.Button(
        parent, text=text, command=command,
        bg=color, fg=C["white"], font=FONTS["body"],
        relief="flat", cursor="hand2", width=width,
        activebackground=color, activeforeground=C["white"],
        padx=8, pady=5, **kw
    )
    btn.bind("<Enter>", lambda e: btn.config(bg=_darken(color)))
    btn.bind("<Leave>", lambda e: btn.config(bg=color))
    return btn


def _darken(hex_color: str) -> str:
    r = max(0, int(hex_color[1:3], 16) - 30)
    g = max(0, int(hex_color[3:5], 16) - 30)
    b = max(0, int(hex_color[5:7], 16) - 30)
    return f"#{r:02x}{g:02x}{b:02x}"


def make_label_val(parent, label: str, value: str, row: int,
                   val_color=None, bold_val=False):
    tk.Label(parent, text=label, font=FONTS["body"],
             bg=C["white"], fg=C["text_light"], anchor="w"
             ).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=2)
    font = (FONTS["body"][0], FONTS["body"][1], "bold") if bold_val else FONTS["body"]
    tk.Label(parent, text=value, font=font,
             bg=C["white"], fg=val_color or C["text"], anchor="w"
             ).grid(row=row, column=1, sticky="w", pady=2)


def styled_treeview(parent, columns: list, heights: int = 18) -> ttk.Treeview:
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Store.Treeview",
                    background=C["white"], fieldbackground=C["white"],
                    foreground=C["text"], rowheight=26,
                    font=FONTS["body"], borderwidth=0)
    style.configure("Store.Treeview.Heading",
                    background=C["header"], foreground=C["white"],
                    font=FONTS["heading"], relief="flat", padding=6)
    style.map("Store.Treeview",
              background=[("selected", C["accent"])],
              foreground=[("selected", C["white"])])

    tv = ttk.Treeview(parent, columns=columns, show="headings",
                      height=heights, style="Store.Treeview",
                      selectmode="browse")
    tv.tag_configure("even", background=C["row_even"])
    tv.tag_configure("odd",  background=C["row_odd"])
    tv.tag_configure("low",  background="#FEF9C3")   # stock bajo
    tv.tag_configure("out",  background=C["red_bg"]) # sin stock
    return tv


def add_scrollbar(parent, widget, fill="both"):
    vsb = ttk.Scrollbar(parent, orient="vertical",   command=widget.yview)
    hsb = ttk.Scrollbar(parent, orient="horizontal",  command=widget.xview)
    widget.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    vsb.pack(side="right",  fill="y")
    hsb.pack(side="bottom", fill="x")
    widget.pack(side="left", fill=fill, expand=True)


# ─────────────────────────────────────────────
#  Diálogo genérico de formulario
# ─────────────────────────────────────────────

class FormDialog(tk.Toplevel):
    """
    Ventana modal con campos de formulario.
    fields = [("Label", "tipo", valor_default), ...]
    tipos: str | float | int
    """
    def __init__(self, parent, title: str, fields: list):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=C["white"])
        self.result = None
        self.entries = []

        # Header
        tk.Label(self, text=title, font=FONTS["title"],
                 bg=C["header"], fg=C["white"], pady=12, padx=20
                 ).pack(fill="x")

        # Fields frame
        frm = tk.Frame(self, bg=C["white"], padx=24, pady=16)
        frm.pack(fill="both", expand=True)

        for i, (label, tipo, default) in enumerate(fields):
            tk.Label(frm, text=label, font=FONTS["body"],
                     bg=C["white"], fg=C["text"], anchor="w"
                     ).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 12))
            var = tk.StringVar(value=str(default) if default is not None else "")
            entry = ttk.Entry(frm, textvariable=var, font=FONTS["body"], width=24)
            entry.grid(row=i, column=1, sticky="ew", pady=5)
            self.entries.append((tipo, var))

        frm.columnconfigure(1, weight=1)

        # Buttons
        btn_frm = tk.Frame(self, bg=C["white"], pady=12, padx=24)
        btn_frm.pack(fill="x")
        make_button(btn_frm, "Cancelar", self.destroy,
                    color=C["text_light"], width=12).pack(side="right", padx=(6, 0))
        make_button(btn_frm, "Guardar", self._guardar,
                    color=C["accent2"], width=12).pack(side="right")

        self.grab_set()
        self.entries[0][1]  # focus first
        self.transient(parent)
        self.wait_window()

    def _guardar(self):
        result = []
        for tipo, var in self.entries:
            raw = var.get().strip().replace(",", ".")
            try:
                if tipo == float:
                    result.append(float(raw))
                elif tipo == int:
                    result.append(int(raw))
                else:
                    if not raw:
                        messagebox.showwarning("Campo vacío", "Todos los campos son obligatorios.",
                                               parent=self)
                        return
                    result.append(raw)
            except ValueError:
                messagebox.showerror("Valor inválido",
                                     f"Valor incorrecto: '{raw}'", parent=self)
                return
        self.result = result
        self.destroy()


# ─────────────────────────────────────────────
#  Pestaña Productos
# ─────────────────────────────────────────────

class ProductosTab(tk.Frame):
    COLS = ("ID", "Nombre", "Categoría", "Costo", "Precio", "Ganancia", "Margen", "Stock")
    WIDTHS = (40, 180, 120, 80, 80, 80, 70, 60)

    def __init__(self, parent, datos: dict, refresh_cb):
        super().__init__(parent, bg=C["bg"])
        self.datos     = datos
        self.refresh_cb = refresh_cb
        self._build()

    def _build(self):
        # Toolbar
        bar = tk.Frame(self, bg=C["bg"], pady=10, padx=16)
        bar.pack(fill="x")
        tk.Label(bar, text="Productos", font=FONTS["title"],
                 bg=C["bg"], fg=C["text"]).pack(side="left")

        btn_frame = tk.Frame(bar, bg=C["bg"])
        btn_frame.pack(side="right")
        make_button(btn_frame, "+ Agregar",    self.agregar,   color=C["accent2"], width=11).pack(side="left", padx=3)
        make_button(btn_frame, "✎ Editar",     self.editar,    color=C["accent"],  width=11).pack(side="left", padx=3)
        make_button(btn_frame, "✕ Eliminar",   self.eliminar,  color=C["danger"],  width=11).pack(side="left", padx=3)
        make_button(btn_frame, "≡ Stock",      self.ajustar,   color=C["warning"], width=11).pack(side="left", padx=3)

        # Tabla
        tbl_frame = tk.Frame(self, bg=C["bg"], padx=16, pady=0)
        tbl_frame.pack(fill="both", expand=True)

        container = tk.Frame(tbl_frame, bg=C["border"], bd=1, relief="solid")
        container.pack(fill="both", expand=True)

        self.tv = styled_treeview(container, self.COLS)
        for col, w in zip(self.COLS, self.WIDTHS):
            anchor = "e" if col in ("Costo", "Precio", "Ganancia", "Margen", "Stock") else "w"
            self.tv.heading(col, text=col)
            self.tv.column(col, width=w, anchor=anchor, stretch=(col == "Nombre"))
        add_scrollbar(container, self.tv)

        # Status bar
        self.status_var = tk.StringVar()
        tk.Label(self, textvariable=self.status_var, font=FONTS["small"],
                 bg=C["bg"], fg=C["text_light"], anchor="w", padx=16, pady=4
                 ).pack(fill="x")

        self.refresh()

    def refresh(self):
        for row in self.tv.get_children():
            self.tv.delete(row)
        productos = self.datos["productos"]
        for i, p in enumerate(productos.values()):
            gan    = p["precio"] - p["costo"]
            margen = (gan / p["precio"] * 100) if p["precio"] else 0
            tag    = "even" if i % 2 == 0 else "odd"
            if p["stock"] == 0:
                tag = "out"
            elif p["stock"] <= 5:
                tag = "low"
            self.tv.insert("", "end", iid=p["id"], tags=(tag,), values=(
                p["id"], p["nombre"], p["categoria"],
                f"${p['costo']:.2f}", f"${p['precio']:.2f}",
                f"${gan:.2f}", f"{margen:.1f}%", p["stock"]
            ))
        total = len(productos)
        sin   = sum(1 for p in productos.values() if p["stock"] == 0)
        bajo  = sum(1 for p in productos.values() if 0 < p["stock"] <= 5)
        msg   = f"  {total} productos   |   Sin stock: {sin}   |   Stock bajo (≤5): {bajo}"
        self.status_var.set(msg)

    def _selected_pid(self):
        sel = self.tv.selection()
        if not sel:
            messagebox.showinfo("Sin selección", "Seleccione un producto primero.")
            return None
        return sel[0]

    def agregar(self):
        dlg = FormDialog(self, "Agregar Producto", [
            ("Nombre",          str,   ""),
            ("Categoría",       str,   ""),
            ("Costo unitario",  float, ""),
            ("Precio de venta", float, ""),
            ("Stock inicial",   int,   0),
        ])
        if dlg.result is None:
            return
        nombre, cat, costo, precio, stock = dlg.result
        if precio <= 0 or costo <= 0:
            messagebox.showerror("Error", "Costo y precio deben ser > 0")
            return
        pid = str(self.datos["siguiente_id"])
        self.datos["productos"][pid] = {
            "id": pid, "nombre": nombre, "categoria": cat,
            "costo": costo, "precio": precio, "stock": stock,
        }
        self.datos["siguiente_id"] += 1
        guardar_datos(self.datos)
        self.refresh()
        self.refresh_cb()

    def editar(self):
        pid = self._selected_pid()
        if pid is None:
            return
        p = self.datos["productos"][pid]
        dlg = FormDialog(self, f"Editar – {p['nombre']}", [
            ("Nombre",          str,   p["nombre"]),
            ("Categoría",       str,   p["categoria"]),
            ("Costo unitario",  float, p["costo"]),
            ("Precio de venta", float, p["precio"]),
            ("Stock",           int,   p["stock"]),
        ])
        if dlg.result is None:
            return
        nombre, cat, costo, precio, stock = dlg.result
        p.update(nombre=nombre, categoria=cat, costo=costo, precio=precio, stock=stock)
        guardar_datos(self.datos)
        self.refresh()
        self.refresh_cb()

    def eliminar(self):
        pid = self._selected_pid()
        if pid is None:
            return
        nombre = self.datos["productos"][pid]["nombre"]
        if messagebox.askyesno("Confirmar", f"¿Eliminar '{nombre}'?"):
            del self.datos["productos"][pid]
            guardar_datos(self.datos)
            self.refresh()
            self.refresh_cb()

    def ajustar(self):
        pid = self._selected_pid()
        if pid is None:
            return
        p = self.datos["productos"][pid]
        nuevo = simpledialog.askinteger(
            "Ajustar Stock",
            f"Nuevo stock para '{p['nombre']}' (actual: {p['stock']}):",
            minvalue=0, parent=self
        )
        if nuevo is not None:
            p["stock"] = nuevo
            guardar_datos(self.datos)
            self.refresh()
            self.refresh_cb()


# ─────────────────────────────────────────────
#  Pestaña Ventas
# ─────────────────────────────────────────────

class VentasTab(tk.Frame):
    HIST_COLS = ("Fecha", "Producto", "Cant.", "Precio c/u", "Descuento", "Total", "Ganancia")
    HIST_WIDTHS = (145, 170, 50, 90, 80, 90, 90)

    def __init__(self, parent, datos: dict, refresh_cb):
        super().__init__(parent, bg=C["bg"])
        self.datos      = datos
        self.refresh_cb = refresh_cb
        self._build()

    def _build(self):
        tk.Label(self, text="Registrar Venta", font=FONTS["title"],
                 bg=C["bg"], fg=C["text"], padx=16, pady=10, anchor="w"
                 ).pack(fill="x")

        panes = tk.PanedWindow(self, orient="horizontal",
                               bg=C["bg"], sashwidth=6, sashrelief="flat")
        panes.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        # ── Panel izquierdo: formulario ──
        form_outer = tk.Frame(panes, bg=C["white"], relief="solid", bd=1)
        panes.add(form_outer, width=340)

        tk.Label(form_outer, text="Nueva Venta", font=FONTS["heading"],
                 bg=C["header"], fg=C["white"], padx=14, pady=8, anchor="w"
                 ).pack(fill="x")

        form = tk.Frame(form_outer, bg=C["white"], padx=16, pady=14)
        form.pack(fill="both", expand=True)

        labels = ["Producto (ID)", "Cantidad", "Descuento %"]
        self.sale_vars = [tk.StringVar() for _ in labels]
        defaults = ["", "1", "0"]
        for i, (lbl, var, dflt) in enumerate(zip(labels, self.sale_vars, defaults)):
            var.set(dflt)
            tk.Label(form, text=lbl, font=FONTS["body"],
                     bg=C["white"], fg=C["text"], anchor="w"
                     ).grid(row=i, column=0, sticky="w", pady=6)
            ttk.Entry(form, textvariable=var, font=FONTS["body"], width=18
                      ).grid(row=i, column=1, sticky="ew", pady=6, padx=(10, 0))
        form.columnconfigure(1, weight=1)

        # Vista previa de precio
        sep = tk.Frame(form, bg=C["border"], height=1)
        sep.grid(row=3, column=0, columnspan=2, sticky="ew", pady=10)

        self.preview_frame = tk.Frame(form, bg=C["white"])
        self.preview_frame.grid(row=4, column=0, columnspan=2, sticky="ew")

        self.preview_labels = {}
        preview_rows = [
            ("producto_lbl", "Producto:"),
            ("costo_lbl",    "Costo unitario:"),
            ("precio_lbl",   "Precio de venta:"),
            ("total_lbl",    "Total:"),
            ("ganancia_lbl", "Ganancia:"),
            ("stock_lbl",    "Stock disponible:"),
        ]
        for r, (key, txt) in enumerate(preview_rows):
            tk.Label(self.preview_frame, text=txt, font=FONTS["small"],
                     bg=C["white"], fg=C["text_light"], anchor="w"
                     ).grid(row=r, column=0, sticky="w", pady=1)
            lbl = tk.Label(self.preview_frame, text="—", font=FONTS["small"],
                           bg=C["white"], fg=C["text"], anchor="w")
            lbl.grid(row=r, column=1, sticky="w", padx=(8, 0), pady=1)
            self.preview_labels[key] = lbl

        # Botones
        btn_frm = tk.Frame(form_outer, bg=C["white"], pady=12, padx=16)
        btn_frm.pack(fill="x")
        make_button(btn_frm, "Vista previa", self._preview,
                    color=C["accent"], width=13).pack(side="left", padx=(0, 6))
        make_button(btn_frm, "✔ Confirmar venta", self._confirmar,
                    color=C["accent2"], width=16).pack(side="left")

        # ── Panel derecho: historial ──
        hist_outer = tk.Frame(panes, bg=C["white"], relief="solid", bd=1)
        panes.add(hist_outer)

        tk.Label(hist_outer, text="Historial de Ventas", font=FONTS["heading"],
                 bg=C["header"], fg=C["white"], padx=14, pady=8, anchor="w"
                 ).pack(fill="x")

        hist_container = tk.Frame(hist_outer, bg=C["border"], bd=0)
        hist_container.pack(fill="both", expand=True, padx=1, pady=1)

        self.hist_tv = styled_treeview(hist_container, self.HIST_COLS, heights=20)
        for col, w in zip(self.HIST_COLS, self.HIST_WIDTHS):
            anchor = "e" if col not in ("Fecha", "Producto") else "w"
            self.hist_tv.heading(col, text=col)
            self.hist_tv.column(col, width=w, anchor=anchor, stretch=(col == "Producto"))
        add_scrollbar(hist_container, self.hist_tv)

        self.refresh()

    def _get_product(self):
        pid = self.sale_vars[0].get().strip()
        return self.datos["productos"].get(pid)

    def _preview(self):
        p = self._get_product()
        if not p:
            messagebox.showerror("Error", "Producto no encontrado. Ingrese un ID válido.")
            return
        try:
            qty      = int(self.sale_vars[1].get())
            desc_pct = float(self.sale_vars[2].get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Cantidad y descuento deben ser números.")
            return
        if qty <= 0:
            messagebox.showerror("Error", "La cantidad debe ser ≥ 1")
            return

        precio_final = p["precio"] * (1 - desc_pct / 100)
        total        = precio_final * qty
        ganancia     = (precio_final - p["costo"]) * qty

        self.preview_labels["producto_lbl"].config(text=p["nombre"])
        self.preview_labels["costo_lbl"].config(   text=f"${p['costo']:.2f}")
        self.preview_labels["precio_lbl"].config(  text=f"${precio_final:.2f}")
        self.preview_labels["total_lbl"].config(   text=f"${total:.2f}",    fg=C["accent"],  font=(*FONTS["small"][:2], "bold"))
        self.preview_labels["ganancia_lbl"].config(text=f"${ganancia:.2f}", fg=C["accent2"], font=(*FONTS["small"][:2], "bold"))
        stock_color = C["danger"] if qty > p["stock"] else C["accent2"]
        self.preview_labels["stock_lbl"].config(text=str(p["stock"]), fg=stock_color)

    def _confirmar(self):
        p = self._get_product()
        if not p:
            messagebox.showerror("Error", "Producto no encontrado.")
            return
        try:
            qty      = int(self.sale_vars[1].get())
            desc_pct = float(self.sale_vars[2].get().replace(",", "."))
        except ValueError:
            messagebox.showerror("Error", "Datos inválidos.")
            return

        if qty <= 0:
            messagebox.showerror("Error", "Cantidad debe ser ≥ 1")
            return
        if qty > p["stock"]:
            messagebox.showerror("Error", f"Stock insuficiente. Disponible: {p['stock']}")
            return

        precio_final = p["precio"] * (1 - desc_pct / 100)
        total        = precio_final * qty
        ganancia     = (precio_final - p["costo"]) * qty

        venta = {
            "fecha"        : datetime.datetime.now().isoformat(timespec="seconds"),
            "producto_id"  : p["id"],
            "producto"     : p["nombre"],
            "cantidad"     : qty,
            "costo_unit"   : p["costo"],
            "precio_unit"  : precio_final,
            "descuento_pct": desc_pct,
            "total"        : total,
            "ganancia"     : ganancia,
        }
        self.datos["ventas"].append(venta)
        p["stock"] -= qty
        guardar_datos(self.datos)

        messagebox.showinfo("Venta registrada",
                            f"Venta confirmada\nTotal: ${total:.2f}  |  Ganancia: ${ganancia:.2f}")
        # Reset form
        self.sale_vars[0].set("")
        self.sale_vars[1].set("1")
        self.sale_vars[2].set("0")
        for lbl in self.preview_labels.values():
            lbl.config(text="—", fg=C["text"], font=FONTS["small"])

        self.refresh()
        self.refresh_cb()

    def refresh(self):
        for row in self.hist_tv.get_children():
            self.hist_tv.delete(row)
        ventas = self.datos["ventas"][-100:][::-1]  # Últimas 100, más recientes primero
        for i, v in enumerate(ventas):
            tag = "even" if i % 2 == 0 else "odd"
            self.hist_tv.insert("", "end", tags=(tag,), values=(
                v["fecha"][:19],
                v["producto"],
                v["cantidad"],
                f"${v['precio_unit']:.2f}",
                f"{v['descuento_pct']:.1f}%",
                f"${v['total']:.2f}",
                f"${v['ganancia']:.2f}",
            ))


# ─────────────────────────────────────────────
#  Pestaña Reportes
# ─────────────────────────────────────────────

class ReportesTab(tk.Frame):
    def __init__(self, parent, datos: dict):
        super().__init__(parent, bg=C["bg"])
        self.datos = datos
        self._build()

    def _build(self):
        tk.Label(self, text="Reportes", font=FONTS["title"],
                 bg=C["bg"], fg=C["text"], padx=16, pady=10, anchor="w"
                 ).pack(fill="x")

        outer = tk.Frame(self, bg=C["bg"], padx=16, pady=0)
        outer.pack(fill="both", expand=True)

        # ── Fila 1: tarjetas KPI ──
        kpi_frame = tk.Frame(outer, bg=C["bg"])
        kpi_frame.pack(fill="x", pady=(0, 14))
        self.kpi_cards = {}
        kpis = [
            ("total_productos", "Productos",         C["accent"]),
            ("total_ventas",    "Ventas realizadas", C["accent2"]),
            ("ingresos",        "Ingresos totales",  "#8B5CF6"),
            ("ganancias",       "Ganancias totales", C["accent2"]),
            ("margen",          "Margen general",    C["warning"]),
        ]
        for key, label, color in kpis:
            card = tk.Frame(kpi_frame, bg=color, padx=16, pady=12, relief="flat")
            card.pack(side="left", fill="x", expand=True, padx=(0, 8))
            tk.Label(card, text=label, font=FONTS["small"],
                     bg=color, fg="white", anchor="w").pack(fill="x")
            val_lbl = tk.Label(card, text="—", font=("Segoe UI", 16, "bold"),
                               bg=color, fg="white", anchor="w")
            val_lbl.pack(fill="x")
            self.kpi_cards[key] = val_lbl

        # ── Fila 2: tabla rentabilidad + alertas ──
        row2 = tk.Frame(outer, bg=C["bg"])
        row2.pack(fill="both", expand=True)

        # Tabla rentabilidad
        rent_outer = tk.Frame(row2, bg=C["white"], relief="solid", bd=1)
        rent_outer.pack(side="left", fill="both", expand=True, padx=(0, 8))
        tk.Label(rent_outer, text="Rentabilidad por Producto", font=FONTS["heading"],
                 bg=C["header"], fg=C["white"], padx=12, pady=7, anchor="w"
                 ).pack(fill="x")
        rent_cont = tk.Frame(rent_outer, bg=C["border"])
        rent_cont.pack(fill="both", expand=True, padx=1, pady=1)

        rent_cols = ("Producto", "Costo", "Precio", "Ganancia", "Margen", "Stock")
        self.rent_tv = styled_treeview(rent_cont, rent_cols, heights=14)
        for col, w in zip(rent_cols, (180, 80, 80, 80, 70, 60)):
            anc = "w" if col == "Producto" else "e"
            self.rent_tv.heading(col, text=col)
            self.rent_tv.column(col, width=w, anchor=anc, stretch=(col == "Producto"))
        self.rent_tv.tag_configure("top",  background="#D1FAE5")
        self.rent_tv.tag_configure("even", background=C["row_even"])
        self.rent_tv.tag_configure("odd",  background=C["row_odd"])
        add_scrollbar(rent_cont, self.rent_tv)

        # Panel alertas
        alert_outer = tk.Frame(row2, bg=C["white"], relief="solid", bd=1, width=220)
        alert_outer.pack(side="left", fill="y")
        alert_outer.pack_propagate(False)
        tk.Label(alert_outer, text="Alertas de Stock", font=FONTS["heading"],
                 bg=C["danger"], fg=C["white"], padx=12, pady=7, anchor="w"
                 ).pack(fill="x")
        self.alert_text = tk.Text(alert_outer, font=FONTS["small"],
                                  bg=C["white"], fg=C["text"],
                                  relief="flat", state="disabled",
                                  wrap="word", padx=10, pady=8)
        self.alert_text.pack(fill="both", expand=True)

        make_button(self, "↻  Actualizar Reporte", self.refresh,
                    color=C["accent"], width=22
                    ).pack(pady=10)

        self.refresh()

    def refresh(self):
        productos = self.datos["productos"]
        ventas    = self.datos["ventas"]

        total_ventas    = sum(v["total"]    for v in ventas)
        total_ganancias = sum(v["ganancia"] for v in ventas)
        margen_gral     = (total_ganancias / total_ventas * 100) if total_ventas else 0

        self.kpi_cards["total_productos"].config(text=str(len(productos)))
        self.kpi_cards["total_ventas"].config(   text=str(len(ventas)))
        self.kpi_cards["ingresos"].config(       text=f"${total_ventas:,.2f}")
        self.kpi_cards["ganancias"].config(      text=f"${total_ganancias:,.2f}")
        self.kpi_cards["margen"].config(         text=f"{margen_gral:.1f}%")

        # Tabla rentabilidad
        for row in self.rent_tv.get_children():
            self.rent_tv.delete(row)
        filas = []
        for p in productos.values():
            gan    = p["precio"] - p["costo"]
            margen = (gan / p["precio"] * 100) if p["precio"] else 0
            filas.append((p["nombre"], p["costo"], p["precio"], gan, margen, p["stock"]))
        filas.sort(key=lambda x: x[4], reverse=True)
        for i, (nombre, costo, precio, gan, margen, stock) in enumerate(filas):
            tag = "top" if i == 0 else ("even" if i % 2 == 0 else "odd")
            self.rent_tv.insert("", "end", tags=(tag,), values=(
                nombre, f"${costo:.2f}", f"${precio:.2f}",
                f"${gan:.2f}", f"{margen:.1f}%", stock
            ))

        # Alertas
        sin_stock = [p for p in productos.values() if p["stock"] == 0]
        bajo      = [p for p in productos.values() if 0 < p["stock"] <= 5]
        self.alert_text.config(state="normal")
        self.alert_text.delete("1.0", "end")
        if sin_stock:
            self.alert_text.insert("end", "SIN STOCK\n", "header")
            for p in sin_stock:
                self.alert_text.insert("end", f"  • {p['nombre']}\n")
            self.alert_text.insert("end", "\n")
        if bajo:
            self.alert_text.insert("end", "STOCK BAJO (≤5)\n", "header")
            for p in bajo:
                self.alert_text.insert("end", f"  • {p['nombre']} ({p['stock']})\n")
        if not sin_stock and not bajo:
            self.alert_text.insert("end", "✓ Todo el stock está en buen nivel.")
        self.alert_text.tag_configure("header", font=(*FONTS["small"][:2], "bold"),
                                      foreground=C["danger"])
        self.alert_text.config(state="disabled")


# ─────────────────────────────────────────────
#  Ventana principal
# ─────────────────────────────────────────────

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gestión de Tienda")
        self.geometry("1100x680")
        self.minsize(900, 560)
        self.configure(bg=C["bg"])
        self.datos = cargar_datos()

        self._build_header()
        self._build_notebook()

    def _build_header(self):
        hdr = tk.Frame(self, bg=C["header"], pady=0)
        hdr.pack(fill="x")
        tk.Label(hdr, text="  🏪  Gestión de Tienda",
                 font=("Segoe UI", 13, "bold"),
                 bg=C["header"], fg=C["white"], pady=10
                 ).pack(side="left")
        self.fecha_lbl = tk.Label(hdr, font=FONTS["small"],
                                  bg=C["header"], fg="#94A3B8", padx=16)
        self.fecha_lbl.pack(side="right")
        self._tick()

    def _tick(self):
        now = datetime.datetime.now().strftime("%d/%m/%Y  %H:%M:%S")
        self.fecha_lbl.config(text=now)
        self.after(1000, self._tick)

    def _build_notebook(self):
        style = ttk.Style()
        style.configure("TNotebook",          background=C["bg"], borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=C["border"], foreground=C["text_light"],
                        font=FONTS["body"], padding=(18, 8))
        style.map("TNotebook.Tab",
                  background=[("selected", C["white"])],
                  foreground=[("selected", C["accent"])])

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        def refresh_all():
            self.tab_productos.refresh()
            self.tab_ventas.refresh()
            self.tab_reportes.refresh()

        self.tab_productos = ProductosTab(nb, self.datos, refresh_all)
        self.tab_ventas    = VentasTab(nb, self.datos, refresh_all)
        self.tab_reportes  = ReportesTab(nb, self.datos)

        nb.add(self.tab_productos, text="  📦  Productos  ")
        nb.add(self.tab_ventas,    text="  💰  Ventas     ")
        nb.add(self.tab_reportes,  text="  📊  Reportes   ")


if __name__ == "__main__":
    app = App()
    app.mainloop()
