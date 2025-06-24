class Declaracion:
    def __init__(self, numero, tipo, valor_aduanero):
        self.numero = numero
        self.tipo = tipo
        self.valor_aduanero = valor_aduanero

    def calcular_impuesto(self):
        tasa = 0.06  # ejemplo de tasa aduanera
        return self.valor_aduanero * tasa


# Ejemplo de uso
if __name__ == "__main__":
    d = Declaracion("DUA-2025-001", "Importación", 10000)
    print(f"Impuesto: ${d.calcular_impuesto():,.2f}")
