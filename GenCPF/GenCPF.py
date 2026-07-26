import random
import subprocess

# Gera 9 dígitos aleatórios
cpf = ''.join(str(random.randint(0, 9)) for _ in range(9))

# Calcula primeiro dígito verificador
soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
resto = soma % 11
dv1 = 0 if resto < 2 else 11 - resto
cpf += str(dv1)

# Calcula segundo dígito verificador
soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
resto = soma % 11
dv2 = 0 if resto < 2 else 11 - resto
cpf += str(dv2)

# Copia para clipboard
process = subprocess.Popen(['clip'], stdin=subprocess.PIPE)
process.communicate(cpf.encode('utf-8'))

print(f"CPF gerado e copiado: {cpf}")
