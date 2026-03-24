import csv
import os
import re
from datetime import datetime


# EXCEPCIONES

# Excepción personalizada para manejar el comando 'salir' en cualquier input
class SalirMenu(Exception):
    pass


# ESTRUCTURAS DE DATOS GLOBALES

contratos = {}
seguimientos = {}


# FUNCIONES AUXILIARES

def limpiar_consola():
    # Limpia la pantalla dependiendo del sistema operativo
    os.system('cls' if os.name == 'nt' else 'clear')

def leer_dato(mensaje):
    # Lee el input y verifica si el usuario quiere cancelar
    entrada = input(mensaje).strip()
    if entrada.lower() == 'salir':
        raise SalirMenu()
    return entrada

def validar_formato_fecha(fecha_str):
    # Retorna True si la fecha cumple el formato dd/mm/aaaa y es válida
    try:
        datetime.strptime(fecha_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validar_correo(correo):
    # Valida que el texto tenga estructura basica de correo
    patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(patron, correo) is not None

def obtener_nombre_contratista(item):
    """
    Función auxiliar que reemplaza a la función lambda original.
    Recibe un 'item' que es una tupla: (numero_contrato, diccionario_de_datos).
    Retorna el nombre del contratista en minúsculas para ordenar alfabéticamente.
    """
    numero_contrato, datos = item
    return datos['contratista'].lower()


# MANEJO DE ARCHIVOS CSV

def cargar_datos():
    global contratos, seguimientos
    
    # Carga de contratos
    if os.path.exists('contratos.csv'):
        with open('contratos.csv', mode='r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                contratos[fila['numero_contrato']] = fila

    # Carga de seguimientos
    if os.path.exists('seguimientos.csv'):
        with open('seguimientos.csv', mode='r', encoding='utf-8') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                num_contrato = fila['numero_contrato']
                if num_contrato not in seguimientos:
                    seguimientos[num_contrato] = []
                seguimientos[num_contrato].append(fila)

def guardar_datos():
    # Guardar los contratos
    if contratos:
        with open('contratos.csv', mode='w', encoding='utf-8', newline='') as archivo:
            campos = ['numero_contrato', 'contratista', 'objeto', 'fecha_inicio', 'fecha_fin', 'valor', 'supervisor', 'estado', 'correo']
            escritor = csv.DictWriter(archivo, fieldnames=campos)
            escritor.writeheader()
            for num, datos in contratos.items():
                fila = {'numero_contrato': num}
                fila.update(datos)
                escritor.writerow(fila)

    # Guardar los seguimientos
    if seguimientos:
        with open('seguimientos.csv', mode='w', encoding='utf-8', newline='') as archivo:
            campos = ['numero_contrato', 'fecha', 'descripcion', 'avance', 'observacion']
            escritor = csv.DictWriter(archivo, fieldnames=campos)
            escritor.writeheader()
            for num, lista in seguimientos.items():
                for seg in lista:
                    fila = {'numero_contrato': num}
                    fila.update(seg)
                    escritor.writerow(fila)


# FUNCIONALIDADES PRINCIPALES

def registrar_nuevo_contrato():
    print("\n--- REGISTRO DE CONTRATO ---")
    print("(Escriba 'salir' para cancelar la operacion)")
    
    try:
        # Validar numero de contrato
        while True:
            num = leer_dato("Numero de contrato: ")
            if num in contratos:
                print("Error: El contrato ya existe.")
            elif num == "":
                print("Error: El numero no puede estar vacio.")
            else:
                break
        
        contratista = leer_dato("Nombre del contratista: ")
        objeto = leer_dato("Objeto del contrato: ")
        
        # Validar fechas
        while True:
            f_inicio = leer_dato("Fecha de inicio (DD/MM/AAAA): ")
            f_fin = leer_dato("Fecha de terminacion (DD/MM/AAAA): ")
            
            if not validar_formato_fecha(f_inicio) or not validar_formato_fecha(f_fin):
                print("Error: Formato de fecha invalido. Use DD/MM/AAAA.")
                continue
            
            fecha1 = datetime.strptime(f_inicio, "%d/%m/%Y")
            fecha2 = datetime.strptime(f_fin, "%d/%m/%Y")
            
            if fecha1 > fecha2:
                print("Error: La fecha de inicio no puede ser mayor a la fecha de terminacion.")
            else:
                break
        
        # Validar valor
        while True:
            try:
                valor = float(leer_dato("Valor total del contrato ($): "))
                if valor > 0:
                    break
                print("Error: El valor debe ser mayor a 0.")
            except ValueError:
                print("Error: Ingrese un valor numerico valido.")
        
        supervisor = leer_dato("Nombre del supervisor: ")
        
        # Validar estado
        while True:
            estado = leer_dato("Estado (ACTIVO | SUSPENDIDO | TERMINADO): ").upper()
            if estado in ['ACTIVO', 'SUSPENDIDO', 'TERMINADO']:
                break
            print("Error: Estado no valido.")
            
        # Validar correo
        while True:
            correo = leer_dato("Correo de contacto: ")
            if validar_correo(correo):
                break
            print("Error: Formato de correo incorrecto.")

        # Guardar en memoria
        contratos[num] = {
            'contratista': contratista,
            'objeto': objeto,
            'fecha_inicio': f_inicio,
            'fecha_fin': f_fin,
            'valor': valor,
            'supervisor': supervisor,
            'estado': estado,
            'correo': correo
        }
        print("\nContrato registrado correctamente.")

    except SalirMenu:
        print("\nOperacion cancelada por el usuario.")

def mostrar_lista_contratos():
    print("\n--- LISTADO DE CONTRATOS ---")
    if not contratos:
        print("No hay contratos para mostrar.")
        return
    
    # ORDENAMIENTO: Se reemplazó la función lambda por la función 'obtener_nombre_contratista'
    contratos_ordenados = sorted(contratos.items(), key=obtener_nombre_contratista)
    
    print("-" * 65)
    print(f"{'No.':<10} | {'Contratista':<20} | {'Estado':<12} | {'Valor ($)':<15}")
    print("-" * 65)
    
    for num, datos in contratos_ordenados:
        nombre = datos['contratista'][:18] # Truncar si es muy largo
        valor = float(datos['valor'])
        print(f"{num:<10} | {nombre:<20} | {datos['estado']:<12} | {valor:<15.2f}")

def buscar_contrato():
    print("\n--- BUSQUEDA DE CONTRATO ---")
    try:
        num = leer_dato("Ingrese el numero de contrato (o 'salir'): ")
        
        if num in contratos:
            datos = contratos[num]
            print("\nInformacion del contrato:")
            print(f"- Contratista: {datos['contratista']}")
            print(f"- Valor:       ${float(datos['valor']):,.2f}")
            print(f"- Vigencia:    {datos['fecha_inicio']} a {datos['fecha_fin']}")
            print(f"- Estado:      {datos['estado']}")
            print(f"- Supervisor:  {datos['supervisor']}")
            print(f"- Correo:      {datos['correo']}")
            
            # Mostrar seguimientos asociados
            if num in seguimientos:
                print("\nSeguimientos registrados:")
                for seg in seguimientos[num]:
                    print(f"  [{seg['fecha']}] Avance: {seg['avance']}% - {seg['descripcion']}")
            else:
                print("\nNo hay seguimientos registrados para este contrato.")
        else:
            print("\nEl contrato especificado no existe.")
            
    except SalirMenu:
        print("\nBusqueda cancelada.")

def menu_seguimientos():
    print("\n--- GESTION DE SEGUIMIENTOS ---")
    try:
        num = leer_dato("Ingrese el numero de contrato: ")
        
        if num not in contratos:
            print("Error: Contrato no encontrado.")
            return
            
        print(f"\nContrato seleccionado: {contratos[num]['contratista']}")
        print("1. Agregar nuevo seguimiento")
        print("2. Ver historial y promedio de avance")
        opcion = leer_dato("Seleccione una opcion (1-2): ")
        
        if opcion == '1':
            while True:
                fecha = leer_dato("Fecha del registro (DD/MM/AAAA): ")
                if validar_formato_fecha(fecha):
                    break
                print("Error: Formato invalido.")
                
            desc = leer_dato("Descripcion breve: ")
            
            while True:
                try:
                    avance = float(leer_dato("Porcentaje de avance (0-100): "))
                    if 0 <= avance <= 100:
                        break
                    print("Error: El valor debe estar entre 0 y 100.")
                except ValueError:
                    print("Error: Ingrese un valor numerico.")
                    
            obs = leer_dato("Observaciones: ")
            
            if num not in seguimientos:
                seguimientos[num] = []
                
            seguimientos[num].append({
                'fecha': fecha,
                'descripcion': desc,
                'avance': avance,
                'observacion': obs
            })
            print("\nSeguimiento registrado exitosamente.")
            
        elif opcion == '2':
            if num not in seguimientos or not seguimientos[num]:
                print("\nNo hay seguimientos para mostrar.")
            else:
                suma_avance = 0
                print("\nHistorial:")
                for seg in seguimientos[num]:
                    print(f"- Fecha: {seg['fecha']} | Avance: {seg['avance']}% | Desc: {seg['descripcion']}")
                    suma_avance += float(seg['avance'])
                
                promedio = suma_avance / len(seguimientos[num])
                print(f"\n> Promedio de avance general: {promedio:.2f}%")
        else:
            print("Opcion invalida.")
            
    except SalirMenu:
        print("\nOperacion cancelada.")

def mostrar_estadisticas():
    print("\n--- ESTADISTICAS DEL SISTEMA ---")
    if not contratos:
        print("No hay informacion suficiente para generar estadisticas.")
        return

    total_contratos = len(contratos)
    conteo_estados = {'ACTIVO': 0, 'SUSPENDIDO': 0, 'TERMINADO': 0}
    suma_valor = 0
    max_valor = -1
    min_valor = float('inf')
    
    fecha_actual = datetime.now()
    contratos_por_vencer = []

    for num, datos in contratos.items():
        valor = float(datos['valor'])
        
        conteo_estados[datos['estado']] += 1
        suma_valor += valor
        
        if valor > max_valor:
            max_valor = valor
        if valor < min_valor:
            min_valor = valor
            
        fecha_fin = datetime.strptime(datos['fecha_fin'], "%d/%m/%Y")
        dias_restantes = (fecha_fin - fecha_actual).days
        
        if 0 <= dias_restantes <= 30:
            contratos_por_vencer.append((num, datos['contratista'], dias_restantes))

    print(f"Total de contratos: {total_contratos}")
    print("\nDesglose por estado:")
    print(f"- Activos:     {conteo_estados['ACTIVO']}")
    print(f"- Suspendidos: {conteo_estados['SUSPENDIDO']}")
    print(f"- Terminados:  {conteo_estados['TERMINADO']}")
    
    print(f"\nValor total acumulado: ${suma_valor:,.2f}")
    print(f"Promedio por contrato: ${suma_valor/total_contratos:,.2f}")
    print(f"Contrato mayor valor:  ${max_valor:,.2f}")
    print(f"Contrato menor valor:  ${min_valor:,.2f}")
    
    print("\nContratos proximos a vencer (30 dias):")
    if contratos_por_vencer:
        for num, nombre, dias in contratos_por_vencer:
            print(f"- {num} ({nombre}): vence en {dias} dias.")
    else:
        print("- Ninguno en este momento.")


# CICLO PRINCIPAL

def main():
    limpiar_consola()
    cargar_datos()
    
    
    print(" SISTEMA DE SUPERVISION DE CONTRATOS")
    
    print(f"Registros cargados: {len(contratos)}")
    
    while True:
        print("\n MENU PRINCIPAL ")
        print("1. Registrar contrato")
        print("2. Listar contratos")
        print("3. Buscar contrato")
        print("4. Gestionar seguimientos")
        print("5. Ver estadisticas")
        print("6. Guardar y Salir")
        
        opcion = input("\nSeleccione una opcion: ").strip()
        
        if opcion == '1':
            registrar_nuevo_contrato()
        elif opcion == '2':
            mostrar_lista_contratos()
        elif opcion == '3':
            buscar_contrato()
        elif opcion == '4':
            menu_seguimientos()
        elif opcion == '5':
            mostrar_estadisticas()
        elif opcion == '6' or opcion.lower() == 'salir':
            print("\nGuardando informacion en archivos CSV...")
            guardar_datos()
            print("Datos guardados correctamente. Saliendo del sistema.")
            break
        else:
            print("Opcion invalida. Intente nuevamente.")

if __name__ == "__main__":
    main()