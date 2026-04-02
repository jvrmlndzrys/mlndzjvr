# 🍔 App de tu Negocio v2.0

Sistema de gestión de negocio de comida rápida hecho en Python.

## ✅ Funcionalidades

| # | Función | Estado |
|---|---------|--------|
| 1 | Ver menú con precios | ✅ |
| 2 | Ver inventario con alertas de stock | ✅ |
| 3 | Procesar cobro con ticket impreso | ✅ |
| 4 | Historial de ventas con total acumulado | ✅ |
| 5 | Agregar producto (requiere clave admin) | ✅ |
| 6 | Eliminar producto (requiere clave admin) | ✅ |
| 7 | Modificar precio/cantidad (requiere clave admin) | ✅ |
| 8 | Cambiar contraseña de administrador | ✅ |
| 9 | Persistencia de datos en JSON | ✅ |
| 10 | Alerta automática de stock bajo | ✅ |

## 🚀 Cómo ejecutar

```bash
python3 comida.py
```

## 🔐 Contraseña de administrador

La contraseña por defecto es:
```
admin123
```
Se puede cambiar desde la opción **8** del menú principal.

## 📁 Archivos generados automáticamente

| Archivo | Descripción |
|---------|-------------|
| `inventario.json` | Guarda el inventario (no se pierde al cerrar) |
| `historial.json` | Registra todas las ventas realizadas |
| `config.json` | Guarda la contraseña del administrador (encriptada) |

## 📋 Requisitos

- Python 3.6 o superior
- Sin dependencias externas (solo librería estándar)
