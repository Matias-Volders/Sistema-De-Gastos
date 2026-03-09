import persistencia
import gastos
import ingresos
import balance

def menu():
    while True:
        print("\n--- SISTEMA DE GASTOS ---")
        print("1. Registrar gasto")
        print("2. Registrar ingreso")
        print("3. Mostrar gastos")
        print("4. Mostrar ingresos")
        print("5. Calcular balance total")
        print("6. Mostrar gastos por categoría")
        print("7. Mostrar balance mensual")
        print("8. Editar gasto")
        print("9. Editar ingreso")
        print("10. Eliminar gasto")
        print("11. Eliminar ingreso")
        print("12. Salir")

        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            gastos.registrarGastos()
        elif opcion == "2":
            ingresos.registrarIngresos()
        elif opcion == "3":
            gastos.mostrarGastos()
        elif opcion == "4":
            ingresos.mostrarIngresos()
        elif opcion == "5":
            balance.calcularBalance()
        elif opcion == "6":
            gastos.gastosPorCategoria()
        elif opcion == "7":
            balance.balanceMensual()
        elif opcion == "8":
            gastos.editarGasto()
        elif opcion == "9":
            ingresos.editarIngreso()
        elif opcion == "10":
            gastos.eliminarGasto()
        elif opcion == "11":
            ingresos.eliminarIngreso()
        elif opcion == "12":
            print("Saliendo del sistema...")
            break
        else:
            print("Opción inválida. Intente nuevamente.")

if __name__ == "__main__":
    persistencia.cargar_gastos()
    persistencia.cargar_ingresos()
    menu()