import utils


def menu():
    while True:
        print("\n--- SISTEMA DE GASTOS ---")
        print("1. Registrar gasto")
        print("2. Registrar ingreso")
        print("3. Mostrar gastos")
        print("4. Mostrar ingresos")
        print("5. Calcular balance")
        print("6. Mostrar gastos por categoría")
        print("7. Mostrar gastos mensuales")
        print("8. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            utils.registrarGastos()
        elif opcion == "2":
            utils.registrarIngresos()
        elif opcion == "3":
            utils.mostrarGastos()
        elif opcion == "4":
            utils.mostrarIngresos()
        elif opcion == "5":
            utils.calcularBalance()
        elif opcion == "6":
            utils.gastosPorCategoria()
        elif opcion == "7":
            utils.gastosMensuales()
        elif opcion == "8":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")

menu()