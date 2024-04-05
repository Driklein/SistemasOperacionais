import os
import sys
import subprocess

def executar_comando(comando):
    partes_comando = comando.split()
    executavel = partes_comando[0]
    argumentos = partes_comando[1:]

    try:
        if "/" in executavel:
            os.execve(executavel, [executavel] + argumentos, os.environ)
        else:
            for diretorio in os.environ["PATH"].split(":"):
                caminho = os.path.join(diretorio, executavel)
                if os.path.isfile(caminho) and os.access(caminho, os.X_OK):
                    os.execve(caminho, [caminho] + argumentos, os.environ)
            raise FileNotFoundError

    except FileNotFoundError:
        print(f"Comando não encontrado: {executavel}", file=sys.stderr)
        sys.exit(1)

def dividir_comandos(linha):
    comandos = []
    partes = linha.split("|")
    for parte in partes:
        comandos.append(parte.strip())
    return comandos

def analisar_redirecionamentos(comando):
    redirecionamentos = {'entrada': None, 'saida': None, 'segundo_plano': False}

    partes = comando.split("<")
    if len(partes) > 1:
        redirecionamentos['entrada'] = partes[1].strip()

    partes = partes[0].split(">")
    if len(partes) > 1:
        redirecionamentos['saida'] = partes[1].strip()

    if '&' in partes[-1]: 
        redirecionamentos['segundo_plano'] = True

    comando_sem_espaco = partes[0].replace('&', '').strip()
    return comando_sem_espaco, redirecionamentos

def main():
    while True:
        linha = input(f"{os.getcwd()} $ ")
        if not linha:
            continue
        comandos = dividir_comandos(linha)
        aux = comandos[0].split(" ")
        leitura_anterior = None

        if aux[0] == "cd":
            os.chdir(aux[1])
            
        else:
            for i, comando in enumerate(comandos):
                comando, redirecionamentos = analisar_redirecionamentos(comando)
                
                entrada = sys.stdin
                if redirecionamentos['entrada'] and os.path.isfile(redirecionamentos['entrada']):
                    entrada = open(redirecionamentos['entrada'], 'r')
                elif leitura_anterior:
                    entrada = leitura_anterior
                
                saida = sys.stdout
                
                #Arquivo de teste de escrita de saida esta sendo gera mas a escrita nao fica salva dentro dele, ficando vazio
                if i == len(comandos) - 1 and redirecionamentos['saida']:
                    with open(redirecionamentos['saida'], 'w') as saida_file:
                        proc = subprocess.Popen(comando.split(), stdin=entrada, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        stdout, stderr = proc.communicate()
                        saida_file.write(stdout.decode())
                        saida_file.write(stderr.decode())

                
                if comando.strip() == "exit":  
                    return

                if i < len(comandos) - 1:
                    descritor_entrada = entrada.fileno()
                    descritor_saida = saida.fileno()
                    entrada = leitura_anterior
                    leitura_anterior = subprocess.Popen(comando.split(), stdin=entrada, stdout=subprocess.PIPE).stdout
                    saida = subprocess.PIPE
                    os.dup2(descritor_entrada, 0)
                    os.dup2(descritor_saida, 1)
                else:
                    proc = subprocess.Popen(comando.split(), stdin=entrada, stdout=saida)
                    if not redirecionamentos['segundo_plano']:
                        proc.communicate()

if __name__ == "__main__":
    main()

