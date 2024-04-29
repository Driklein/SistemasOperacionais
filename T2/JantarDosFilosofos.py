import threading
import time
import random

NUMERO_DE_FILOSOFOS = 5
TEMPO_MAXIMO_PENSANDO = 3
TEMPO_MAXIMO_COMENDO = 2
TOTAL_DE_SERVIDAS_DO_MACARRAO = 50

class Filosofo(threading.Thread):
    def __init__(self, id, garfo_esquerda, garfo_direita, semaforo, macarrao):
        threading.Thread.__init__(self)
        self.id = id
        self.garfo_esquerda = garfo_esquerda
        self.garfo_direita = garfo_direita
        self.semaforo = semaforo
        self.macarrao = macarrao
        self.quantidade_de_comidas = 0
        self.macarrao_terminou = False

    def run(self):
        while True:
            self.pensar()
            if not self.macarrao_terminou:
                self.comer()
            else:
                self.imprimir_quantidade_de_comidas()
                break

    def pensar(self):
        print(f"Filósofo {self.id} está pensando.")
        time.sleep(random.uniform(0, TEMPO_MAXIMO_PENSANDO))

    def comer(self):
        self.semaforo.acquire() 
       
        # Se blocking for True (padrão): o programa ficará parado até que o semáforo esteja disponível
        # Se blocking for False: o programa não ficará parado e retornará imediatamente, mesmo que o semáforo não esteja disponível.
        if self.garfo_esquerda.acquire(blocking=False):  # Tenta adquirir o garfo esquerdo

            if self.garfo_direita.acquire(blocking=False):  # Tenta adquirir o garfo direito

                # Ambos os garfos foram adquiridos

                #Se ainda resta macarrão para servir
                if self.macarrao.sobrando() > 0:
                    print(f"Filósofo {self.id} está comendo.")
                    self.quantidade_de_comidas += 1
                    self.macarrao.servir()
                    time.sleep(random.uniform(0, TEMPO_MAXIMO_COMENDO))
                    self.garfo_esquerda.release() 
                    self.garfo_direita.release()  
                    self.semaforo.release()
                    print(f"Restam {self.macarrao.sobrando()} servidas.")
                else:
                    print(f"Filósofo {self.id} não pode comer, não há mais macarrão.")
                    self.garfo_esquerda.release()
                    self.garfo_direita.release()
                    self.semaforo.release()
                    self.macarrao_terminou = True
            else:
                # Se o garfo direito não estiver disponível, solta o garfo esquerdo
                self.garfo_esquerda.release()
                self.pensar()  # Volta a pensar
        else:
            self.pensar()  # Volta a pensar

    def imprimir_quantidade_de_comidas(self):
        print(f"Filósofo {self.id} comeu {self.quantidade_de_comidas} vezes.")


class Macarrao:
    def __init__(self, servidas=TOTAL_DE_SERVIDAS_DO_MACARRAO):
        self.servidas = servidas
        self.lock = threading.Lock()

    def sobrando(self):
        with self.lock:
            return self.servidas

    def servir(self):
        with self.lock:
            self.servidas -= 1


def main():
    # Inicialização dos garfos
    garfos = []
    for i in range(NUMERO_DE_FILOSOFOS):
        garfo = threading.Semaphore(1)
        garfos.append(garfo)

    # Semáforo para garantir que os filósofos não peguem garfos ao mesmo tempo
    semaforo = threading.Semaphore(NUMERO_DE_FILOSOFOS - 1)

    #Prato de macarrão com 50 servidas
    macarrao = Macarrao(TOTAL_DE_SERVIDAS_DO_MACARRAO)

    # Lista para armazenar os filósofos
    filosofos = []

    # Criando os filósofos e adicionando à lista
    for i in range(NUMERO_DE_FILOSOFOS):
        
        # Determinando os garfos esquerdo e direito de cada filósofo
        garfo_esquerda = garfos[i]
        garfo_direita_index = i + 1
        
        if garfo_direita_index == NUMERO_DE_FILOSOFOS: 
            garfo_direita_index = 0
        garfo_direita = garfos[garfo_direita_index]
        
        # Criando um filósofo com seu ID, garfos e semáforo
        filosofo = Filosofo(i, garfo_esquerda, garfo_direita, semaforo, macarrao)
        filosofos.append(filosofo)

    # Iniciando as threads filósofos 
    for filosofo in filosofos:
        filosofo.start()

    # Aguardando as threads filósofos terminarem
    for filosofo in filosofos:
        filosofo.join()


if __name__ == "__main__":
    main()