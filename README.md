# Biblioteca py_cnab - Gerador de Arquivos CNAB

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Uma biblioteca Python moderna e robusta para geração de arquivos CNAB (Centro Nacional de Automação Bancária), seguindo as melhores práticas de desenvolvimento e princípios SOLID.

## 📋 Características

- **Arquitetura Limpa**: Implementação seguindo princípios SOLID
- **Type Hints**: Código completamente tipado para melhor IDE support
- **Validação Automática**: Validação de dados na criação dos models
- **Extensível**: Fácil adição de novos formatos CNAB
- **Testável**: Arquitetura que facilita testes unitários
- **Interface Simples**: API intuitiva e bem documentada

## 🏗️ Formatos Suportados

- **CNAB 150** - Débito Automático
- **CNAB 400** - Cobrança

## 📦 Instalação

```bash
# Clone o repositório
git clone https://github.com/JefersonKlaus/py_cnab.git
cd py_cnab

# Instale as dependências (se houver)
pip install -r requirements.txt
```

## 🚀 Uso Rápido

### CNAB 150 - Débito Automático

```python
from datetime import date
from decimal import Decimal
from src import (
    CnabGenerator, Cnab150EmpresaData, 
    DebitoAutomaticoData, Cnab150Request
)

# Dados da empresa
empresa = Cnab150EmpresaData(
    nome_empresa="MINHA EMPRESA",
    codigo_convenio="12345678901234567890",
    codigo_banco="237",
    nome_banco="BRADESCO"
)

# Dados do débito
debito = DebitoAutomaticoData(
    id_cliente_empresa="CONTRATO001",
    agencia_debito="1234",
    conta_cliente="56789-0",
    vencimento=date(2025, 10, 30),
    valor=Decimal("199.99")
)

# Gera o arquivo
request = Cnab150Request(nsa=1, empresa=empresa, debitos=[debito])
arquivo = CnabGenerator.generate_cnab_150(request)

# Salva o arquivo
CnabGenerator.save_file(arquivo, "debito_150.rem")
```

### CNAB 400 - Cobrança

```python
from datetime import date
from decimal import Decimal
from src import (
    CnabGenerator, Cnab400EmpresaData, PagadorData,
    CobrancaData, Cnab400Request
)

# Dados da empresa
empresa = Cnab400EmpresaData(
    codigo_empresa="123456",
    nome_empresa="MINHA EMPRESA"
)

# Dados do pagador
pagador = PagadorData(
    tipo_inscricao="01",  # CPF
    inscricao="12345678901",
    nome="CLIENTE DA SILVA",
    endereco="RUA DAS FLORES, 123",
    cep="12345678"
)

# Dados da cobrança
cobranca = CobrancaData(
    carteira="09",
    agencia="1234",
    conta="56789",
    conta_dv="0",
    nosso_numero="DOC001",
    nosso_numero_banco="12345678901",
    nosso_numero_banco_dv="P",
    numero_documento="FAT001",
    vencimento=date(2025, 10, 30),
    data_emissao=date.today(),
    valor=Decimal("1500.50"),
    pagador=pagador
)

# Gera o arquivo
request = Cnab400Request(nsa=1, empresa=empresa, cobrancas=[cobranca])
arquivo = CnabGenerator.generate_cnab_400(request)

# Salva o arquivo
CnabGenerator.save_file(arquivo, "cobranca_400.rem")
```

## 📁 Estrutura do Projeto

```
py_cnab/
├── src/
│   ├── __init__.py              # API pública
│   ├── models.py                # Models de dados (dataclasses)
│   ├── utils.py                 # Utilitários e formatadores
│   ├── interfaces/              # Interfaces e contratos
│   │   ├── __init__.py
│   │   └── cnab_builder_interface.py
│   ├── builders/                # Implementações específicas
│   │   ├── __init__.py
│   │   ├── cnab150_builder.py
│   │   └── cnab400_builder.py
│   ├── services/                # Lógica de negócio
│   │   ├── __init__.py
│   │   └── cnab_service.py
│   └── factories/               # Factory pattern
│       ├── __init__.py
│       └── cnab_factory.py
├── examples.py                  # Exemplos de uso
├── cnab_generator.py           # Arquivo original (para referência)
├── README.md
└── LICENSE
```

## ⚙️ Arquitetura

O projeto utiliza uma arquitetura modular com:
- **Models**: Estruturas de dados com validação
- **Builders**: Construtores específicos para cada formato
- **Services**: Lógica de geração e manipulação de arquivos
- **Factory**: Criação dinâmica de builders

## 🔧 Como Adicionar Novos Formatos

1. Criar dataclass para o novo formato em `models.py`
2. Implementar builder que herda de `ICnabBuilder`
3. Registrar na factory
4. Adicionar método público se necessário
```python
# 1. Novo builder
class CnabNovoFormatoBuilder(ICnabBuilder):
    # implementação...

# 2. Registrar na factory
CnabBuilderFactory.register_builder(
    CnabFormat.NOVO_FORMATO, 
    CnabNovoFormatoBuilder
)
```

## ✅ Validação

A biblioteca inclui validação automática:

```python
# Validação automática nos models
try:
    empresa = Cnab150EmpresaData(
        nome_empresa="",  # ❌ Erro: obrigatório
        # ...
    )
except ValueError as e:
    print(f"Erro de validação: {e}")

# Validação de arquivo gerado
errors = CnabGenerator.validate_file(arquivo, "150_debito")
if errors:
    print(f"Arquivo inválido: {errors}")
```

## 📋 Exemplos Completos

Execute o arquivo de exemplos:

```bash
python examples.py
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 📞 Suporte

- 📧 Email: [jefersonklaus@gmail.com]
- 🐛 Issues: [GitHub Issues](https://github.com/JefersonKlaus/py_cnab/issues)

---

⭐ Se este projeto te ajudou, considere dar uma estrela no repositório!