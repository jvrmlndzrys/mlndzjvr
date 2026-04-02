import json
import os
import hashlib
from datetime import datetime

# ──────────────────────────────────────────────
#  RUTAS DE ARCHIVOS
# ──────────────────────────────────────────────
BASE_DIR       = os.path.dirname(os.path.abspath(__file__))
INVENTARIO_FILE = os.path.join(BASE_DIR, "inventario.json")
HISTORIAL_FILE  = os.path.join(BASE_DIR, "historial.json")
CONFIG_FILE     = os.path.join(BASE_DIR, "config.json")

STOCK_MINIMO   = 5   # alerta cuando quedan ≤ 5 unidades

# ──────────────────────────────────────────────
#  PERSISTENCIA — INVENTARIO
# ──────────────────────────────────────────────
INVENTARIO_DEFAULT = {
    'hamburguesa': {'precio': 5.50, 'cantidad': 20},
    'papas fritas': {'precio': 2.50, 'cantidad': 30},
    'refresco':     {'precio': 1.80, 'cantidad': 50},
    'hot dog':      {'precio': 3.00, 'cantidad': 15},
}

def cargar_inventario():
    if os.path.exists(INVENTARIO_FILE):
        with open(INVENTARIO_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return dict(INVENTARIO_DEFAULT)

def guardar_inventario(inv):
    with open(INVENTARIO_FILE, 'w', encoding='utf-8') as f:
        json.dump(inv, f, ensure_ascii=False, indent=4)

# ──────────────────────────────────────────────
#  PERSISTENCIA — HISTORIAL
# ──────────────────────────────────────────────
def cargar_historial():
    if os.path.exists(HISTORIAL_FILE):
        with open(HISTORIAL_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def guardar_historial(historial):
    with open(HISTORIAL_FILE, 'w', encoding='utf-8') as f:
        json.dump(historial, f, ensure_ascii=False, indent=4)

# ──────────────────────────────────────────────
#  PERSISTENCIA — CONFIG / CONTRASEÑA ADMIN
# ──────────────────────────────────────────────
PASSWORD_DEFAULT = "admin123"

def _hash(texto):
    return hashlib.sha256(texto.encode()).hexdigest()

def cargar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    cfg = {"password_hash": _hash(PASSWORD_DEFAULT)}
    guardar_config(cfg)
    return cfg

def guardar_config(cfg):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, ensure_ascii=False, indent=4)

def verificar_password(cfg):
    intento = input("🔐 Contraseña de administrador: ")
    return _hash(intento) == cfg["password_hash"]

# ──────────────────────────────────────────────
#  ALERTAS DE STOCK BAJO
# ──────────────────────────────────────────────
def revisar_stock_bajo(inv):
    bajos = [p for p, d in inv.items() if d['cantidad'] <= STOCK_MINIMO]
    if bajos:
        print("\n⚠️  ALERTA — Stock bajo:")
        for p in bajos:
            print(f"   • {p.capitalize()}: solo {inv[p]['cantidad']} unidades")

# ──────────────────────────────────────────────
#  TICKET / RECIBO
# ──────────────────────────────────────────────
def imprimir_ticket(pedido, inv, folio):
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    ancho = 38
    linea = "─" * ancho
    print(f"\n{'':>4}{'🧾 TICKET DE VENTA':^{ancho}}")
    print(f"  {linea}")
    print(f"  Folio : #{folio:04d}")
    print(f"  Fecha : {ahora}")
    print(f"  {linea}")
    total = 0.0
    for producto, cantidad in pedido.items():
        precio_u = inv[producto]['precio']
        subtotal = precio_u * cantidad
        total += subtotal
        print(f"  {producto.capitalize():<18} x{cantidad}  ${subtotal:>6.2f}")
    print(f"  {linea}")
    print(f"  {'TOTAL':>26}  ${total:>6.2f}")
    print(f"  {linea}")
    print(f"  {'¡Gracias por tu compra!':^{ancho}}")
    print(f"  {linea}\n")
    return total

# ──────────────────────────────────────────────
#  MENÚ PRINCIPAL — FUNCIONES
# ──────────────────────────────────────────────
def mostrar_menu(inv):
    print("\n╔══════════════════════════╗")
    print("║       📋 NUESTRO MENÚ    ║")
    print("╠══════════════════════════╣")
    for producto, detalles in inv.items():
        print(f"║  {producto.capitalize():<18} ${detalles['precio']:.2f}  ║")
    print("╚══════════════════════════╝")

def mostrar_inventario(inv):
    print("\n╔══════════════════════════════╗")
    print("║      📦 INVENTARIO ACTUAL    ║")
    print("╠══════════════════════════════╣")
    for producto, detalles in inv.items():
        alerta = " ⚠️" if detalles['cantidad'] <= STOCK_MINIMO else ""
        print(f"║  {producto.capitalize():<18} {detalles['cantidad']:>3} uds{alerta}")
    print("╚══════════════════════════════╝")
    revisar_stock_bajo(inv)

def procesar_cobro(inv, historial):
    pedido = {}
    print("\n─── 🛒 Proceso de Cobro ───")
    print("(escribe 'listo' para terminar el pedido)\n")

    while True:
        mostrar_menu(inv)
        producto_elegido = input("\nProducto: ").lower().strip()
        if producto_elegido == 'listo':
            break
        if producto_elegido not in inv:
            print("❌ Producto no encontrado.")
            continue
        try:
            cantidad = int(input(f"¿Cuántas unidades de '{producto_elegido}'?: "))
            if cantidad <= 0:
                print("❌ Ingresa un número mayor a cero.")
                continue
            disponible = inv[producto_elegido]['cantidad']
            if cantidad > disponible:
                print(f"❌ Solo hay {disponible} unidades disponibles.")
                continue
            pedido[producto_elegido] = pedido.get(producto_elegido, 0) + cantidad
            print(f"✅ {cantidad} '{producto_elegido}' añadidos.")
        except ValueError:
            print("❌ Ingresa un número válido.")

    if not pedido:
        print("⚠️  Pedido vacío, regresando al menú.")
        return

    # Calcular folio
    folio = len(historial) + 1

    # Imprimir ticket y obtener total
    total = imprimir_ticket(pedido, inv, folio)

    # Actualizar inventario
    for producto, cantidad in pedido.items():
        inv[producto]['cantidad'] -= cantidad
    guardar_inventario(inv)

    # Guardar en historial
    venta = {
        "folio": folio,
        "fecha": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "pedido": pedido,
        "total": round(total, 2)
    }
    historial.append(venta)
    guardar_historial(historial)

    # Revisar stock después de la venta
    revisar_stock_bajo(inv)

def ver_historial(historial):
    if not historial:
        print("\n📭 No hay ventas registradas aún.")
        return
    print(f"\n{'─'*45}")
    print(f"  📊 HISTORIAL DE VENTAS  ({len(historial)} ventas)")
    print(f"{'─'*45}")
    total_general = 0.0
    for v in historial:
        print(f"  #{v['folio']:04d} | {v['fecha']} | ${v['total']:.2f}")
        items = ", ".join([f"{p.capitalize()} x{c}" for p, c in v['pedido'].items()])
        print(f"       {items}")
    total_general = sum(v['total'] for v in historial)
    print(f"{'─'*45}")
    print(f"  💰 TOTAL ACUMULADO: ${total_general:.2f}")
    print(f"{'─'*45}")

def agregar_producto(inv, cfg):
    if not verificar_password(cfg):
        print("❌ Contraseña incorrecta.")
        return
    print("\n─── ➕ Agregar Nuevo Producto ───")
    nombre = input("Nombre del producto: ").lower().strip()
    if nombre in inv:
        print("⚠️  Este producto ya existe.")
        return
    try:
        precio   = float(input(f"Precio de '{nombre}': $"))
        cantidad = int(input(f"Cantidad inicial: "))
        if precio <= 0 or cantidad < 0:
            print("❌ Valores inválidos.")
            return
        inv[nombre] = {'precio': precio, 'cantidad': cantidad}
        guardar_inventario(inv)
        print(f"✅ '{nombre.capitalize()}' agregado exitosamente.")
    except ValueError:
        print("❌ Ingresa un número válido.")

def eliminar_producto(inv, cfg):
    if not verificar_password(cfg):
        print("❌ Contraseña incorrecta.")
        return
    print("\n─── 🗑️  Eliminar Producto ───")
    mostrar_inventario(inv)
    nombre = input("Nombre del producto a eliminar: ").lower().strip()
    if nombre not in inv:
        print("❌ Producto no encontrado.")
        return
    confirmar = input(f"¿Seguro que deseas eliminar '{nombre}'? (s/n): ").lower()
    if confirmar == 's':
        del inv[nombre]
        guardar_inventario(inv)
        print(f"✅ '{nombre.capitalize()}' eliminado.")
    else:
        print("Operación cancelada.")

def modificar_producto(inv, cfg):
    if not verificar_password(cfg):
        print("❌ Contraseña incorrecta.")
        return
    print("\n─── ✏️  Modificar Producto ───")
    mostrar_inventario(inv)
    nombre = input("Nombre del producto a modificar: ").lower().strip()
    if nombre not in inv:
        print("❌ Producto no encontrado.")
        return
    print(f"\nModificando '{nombre.capitalize()}'")
    print("  1. Modificar precio")
    print("  2. Modificar cantidad")
    opcion = input("Elige una opción: ").strip()
    try:
        if opcion == '1':
            nuevo = float(input("Nuevo precio: $"))
            if nuevo <= 0:
                print("❌ El precio debe ser mayor a 0.")
                return
            inv[nombre]['precio'] = nuevo
            print("✅ Precio actualizado.")
        elif opcion == '2':
            nuevo = int(input("Nueva cantidad: "))
            if nuevo < 0:
                print("❌ La cantidad no puede ser negativa.")
                return
            inv[nombre]['cantidad'] = nuevo
            print("✅ Cantidad actualizada.")
        else:
            print("❌ Opción no válida.")
            return
        guardar_inventario(inv)
    except ValueError:
        print("❌ Ingresa un número válido.")

def cambiar_password(cfg):
    if not verificar_password(cfg):
        print("❌ Contraseña incorrecta.")
        return
    nueva = input("Nueva contraseña: ").strip()
    if len(nueva) < 4:
        print("❌ La contraseña debe tener al menos 4 caracteres.")
        return
    confirmar = input("Confirma la nueva contraseña: ").strip()
    if nueva != confirmar:
        print("❌ Las contraseñas no coinciden.")
        return
    cfg['password_hash'] = _hash(nueva)
    guardar_config(cfg)
    print("✅ Contraseña actualizada exitosamente.")

# ──────────────────────────────────────────────
#  FUNCIÓN PRINCIPAL
# ──────────────────────────────────────────────
def main():
    inv      = cargar_inventario()
    historial = cargar_historial()
    cfg      = cargar_config()

    while True:
        print("\n╔════════════════════════════════════╗")
        print("║   🍔  App de tu Negocio v2.0  🍔   ║")
        print("╠════════════════════════════════════╣")
        print("║  1. Ver Menú                       ║")
        print("║  2. Ver Inventario                 ║")
        print("║  3. Iniciar Cobro                  ║")
        print("║  4. Ver Historial de Ventas        ║")
        print("║  ─── Admin ───────────────────     ║")
        print("║  5. Agregar Producto               ║")
        print("║  6. Eliminar Producto              ║")
        print("║  7. Modificar Producto             ║")
        print("║  8. Cambiar Contraseña Admin       ║")
        print("║  9. Salir                          ║")
        print("╚════════════════════════════════════╝")

        opcion = input("Elige una opción: ").strip()

        if   opcion == '1': mostrar_menu(inv)
        elif opcion == '2': mostrar_inventario(inv)
        elif opcion == '3': procesar_cobro(inv, historial)
        elif opcion == '4': ver_historial(historial)
        elif opcion == '5': agregar_producto(inv, cfg)
        elif opcion == '6': eliminar_producto(inv, cfg)
        elif opcion == '7': modificar_producto(inv, cfg)
        elif opcion == '8': cambiar_password(cfg)
        elif opcion == '9':
            print("\n👋 ¡Hasta pronto! Cerrando la app...\n")
            break
        else:
            print("❌ Opción no válida, intenta de nuevo.")

if __name__ == "__main__":
    main()
