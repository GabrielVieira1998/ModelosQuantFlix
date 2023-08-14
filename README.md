# Importando os dados tick a tick da Binance
1. Acessar o link: https://www.binance.com/en/landing/data
2. Ir até 'Book Ticker'
3. Selecionar 'USDⓢ-M' 
4. Digitar dentro de 'Symbol (Max: 5)' o symbol desejado
5. Selecionar o tipo de intervalo.
6. Selecionar o período.
5. Fazer o download e jogar o arquivo em csv dentro da pasta 'data'.


# Otimização
Para rodar uma otimização, basta chamar a função 'Optimizer' dentro do 'main.py' e definir os ranges dos parâmetros que quer otimizar. 

# Backtest
Para rodar um backtest, basta chamar a função 'backtester' dentro do 'main.py' e definir os parâmetros que quer otimizar.  

# Lembrete
Estou filtrando a quantidade de dados para ser utilizado na otimização (1 semana) dentro do 'main.py', porque minha máquina não aguentava a base de dados inteira para rodar os testes. 


