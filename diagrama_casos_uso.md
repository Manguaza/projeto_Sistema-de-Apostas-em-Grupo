
Participante --> (Entrar no sistema)
Participante --> (Sair do sistema)
Participante --> (Cadastrar grupo)
Participante --> (Listar grupos)
Participante --> (Pesquisar grupo)
Participante --> (Criar aposta)
Participante --> (Listar apostas)
Participante --> (Pesquisar aposta)
Participante --> (Entrar em aposta)
Participante --> (Aceitar requisitos)
Participante --> (Consultar saldo)
Participante --> (Adicionar saldo fictício)
Participante --> (Visualizar resultado)

Administrador --> (Entrar no sistema)
Administrador --> (Sair do sistema)
Administrador --> (Cadastrar usuário)
Administrador --> (Listar usuários)
Administrador --> (Atualizar usuário)
Administrador --> (Excluir usuário)
Administrador --> (Cadastrar grupo)
Administrador --> (Atualizar grupo)
Administrador --> (Excluir grupo)
Administrador --> (Cadastrar aposta)
Administrador --> (Atualizar aposta)
Administrador --> (Excluir aposta)
Administrador --> (Cadastrar resultado)
Administrador --> (Finalizar aposta)
Administrador --> (Resolver conflito)

(Entrar em aposta) ..> (Aceitar requisitos) : include
(Entrar em aposta) ..> (Bloquear saldo) : include
(Finalizar aposta) ..> (Definir vencedor) : include
(Finalizar aposta) ..> (Transferir prêmio) : include
```
