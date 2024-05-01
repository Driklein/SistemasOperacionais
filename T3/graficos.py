import matplotlib.pyplot as plt

# Dados dos resultados fornecidos
results = {
    'Timectxsw': {'time': 3690.7},
    'Timesyscall': {'time': 508.1},
    'Timetctxsw': {'time': 3932.3},
    'Timetctxsw2': {'time': 3184.3},
    'Timetctxswws': {'time': 31550.9}
}

fig, ax = plt.subplots()

# Plotagem dos resultados para diferentes tipos de contexto
for threads, data in results.items():
    ax.bar(threads, data['time'], label=threads)

ax.set_ylabel('Tempo de Troca de Contexto (ns)')
ax.set_title('Comparação do Tempo de Troca de Contexto para Diferentes Tipos de Contexto')
ax.legend()

plt.savefig('grafico.png')
plt.show()
