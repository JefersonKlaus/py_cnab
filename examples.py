"""
Exemplos de uso da biblioteca py_cnab refatorada.
"""

from datetime import date
from decimal import Decimal

from src import (
    Cnab150EmpresaData,
    Cnab150Request,
    Cnab400EmpresaData,
    Cnab400Request,
    CnabGenerator,
    CobrancaData,
    DebitoAutomaticoData,
    PagadorData,
)


def exemplo_cnab_150():
    """Exemplo de geração de arquivo CNAB 150 (Débito Automático)."""
    print("=== Exemplo CNAB 150 (Débito Automático) ===\n")

    try:
        # Dados da empresa
        empresa = Cnab150EmpresaData(
            nome_empresa="MINHA EMPRESA DE TESTE",
            codigo_convenio="18732000000000000000",
            codigo_banco="237",
            nome_banco="BRADESCO",
        )

        # Dados dos débitos
        debitos = [
            DebitoAutomaticoData(
                id_cliente_empresa="CONTRATO-001",
                agencia_debito="1234",
                conta_cliente="555667",
                vencimento=date(2025, 10, 20),
                valor=Decimal("199.99"),
                tipo_inscricao="2",  # CPF
                inscricao="11144477735",  # CPF do cliente válido
                tipo_operacao="1",  # Tipo de operação
            ),
            DebitoAutomaticoData(
                id_cliente_empresa="FATURA-XYZ-02",
                agencia_debito="4321",
                conta_cliente="987654",
                vencimento=date(2025, 10, 22),
                valor=Decimal("50.00"),
                tipo_inscricao="1",  # CNPJ
                inscricao="12.345.678/0001-90",  # CNPJ do cliente
                tipo_operacao="1",  # Tipo de operação
            ),
        ]

        # Monta a requisição
        request = Cnab150Request(nsa=1, empresa=empresa, debitos=debitos)

        # Gera o arquivo
        arquivo_cnab = CnabGenerator.generate_cnab_150(request)

        print("Arquivo CNAB 150 gerado com sucesso!")
        print(f"Tamanho: {len(arquivo_cnab)} caracteres")
        print(f"Linhas: {arquivo_cnab.count(chr(13) + chr(10))}")
        print("\nConteúdo:")
        print(arquivo_cnab)

        # Salva o arquivo (opcional)
        CnabGenerator.save_file(arquivo_cnab, "debito_150.rem")
        print("Arquivo salvo como 'debito_150.rem'")

        # Valida o arquivo
        errors = CnabGenerator.validate_file(arquivo_cnab, "150_debito")
        if errors:
            print(f"Erros encontrados: {errors}")
        else:
            print("Arquivo validado com sucesso!")

    except Exception as e:
        print(f"Erro ao gerar CNAB 150: {e}")


def exemplo_cnab_400():
    """Exemplo de geração de arquivo CNAB 400 (Cobrança)."""
    print("\n=== Exemplo CNAB 400 (Cobrança) ===\n")

    try:
        # Dados da empresa
        empresa = Cnab400EmpresaData(
            codigo_empresa="1234567", nome_empresa="EMPRESA COBRANCA LTDA"
        )

        # Dados dos pagadores e cobranças
        pagador1 = PagadorData(
            tipo_inscricao="01",  # CPF
            inscricao="11122233344",
            nome="CLIENTE UM DA SILVA",
            endereco="RUA DAS FLORES, 123",
            cep="12345678",
        )

        pagador2 = PagadorData(
            tipo_inscricao="02",  # CNPJ
            inscricao="99888777000166",
            nome="EMPRESA DOIS LTDA",
            endereco="AVENIDA PRINCIPAL, 987",
            cep="87654321",
        )

        cobrancas = [
            CobrancaData(
                carteira="09",
                agencia="1234",
                conta="56789",
                conta_dv="0",
                nosso_numero="DOC-001",
                nosso_numero_banco="12345678901",
                nosso_numero_banco_dv="P",
                numero_documento="FAT-001",
                vencimento=date(2025, 10, 30),
                data_emissao=date(2025, 9, 27),
                valor=Decimal("1500.50"),
                pagador=pagador1,
            ),
            CobrancaData(
                carteira="09",
                agencia="1234",
                conta="56789",
                conta_dv="0",
                nosso_numero="DOC-002",
                nosso_numero_banco="12345678902",
                nosso_numero_banco_dv="8",
                numero_documento="FAT-002",
                vencimento=date(2025, 11, 5),
                data_emissao=date(2025, 9, 27),
                valor=Decimal("875.00"),
                pagador=pagador2,
            ),
        ]

        # Monta a requisição
        request = Cnab400Request(
            nsa=73, empresa=empresa, cobrancas=cobrancas  # Baseado no exemplo original
        )

        # Gera o arquivo
        arquivo_cnab = CnabGenerator.generate_cnab_400(request)

        print("Arquivo CNAB 400 gerado com sucesso!")
        print(f"Tamanho: {len(arquivo_cnab)} caracteres")
        print(f"Linhas: {arquivo_cnab.count(chr(13) + chr(10))}")
        print("\nConteúdo:")
        print(arquivo_cnab)

        # Salva o arquivo (opcional)
        # CnabGenerator.save_file(arquivo_cnab, "cobranca_400.rem")
        # print("Arquivo salvo como 'cobranca_400.rem'")

        # Valida o arquivo
        errors = CnabGenerator.validate_file(arquivo_cnab, "400_cobranca")
        if errors:
            print(f"Erros encontrados: {errors}")
        else:
            print("Arquivo validado com sucesso!")

    except Exception as e:
        print(f"Erro ao gerar CNAB 400: {e}")


def exemplo_formatos_suportados():
    """Mostra os formatos CNAB suportados."""
    print("\n=== Formatos CNAB Suportados ===")
    formatos = CnabGenerator.get_supported_formats()
    for formato in formatos:
        print(f"- {formato}")


if __name__ == "__main__":
    exemplo_formatos_suportados()
    exemplo_cnab_150()
    exemplo_cnab_400()
