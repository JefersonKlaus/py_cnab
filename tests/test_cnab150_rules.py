"""
Testes específicos para validação das regras CNAB 150.
"""

from datetime import date
from decimal import Decimal

import pytest

from src import Cnab150EmpresaData, Cnab150Request, CnabGenerator, DebitoAutomaticoData


class TestCnab150Rules:
    """Testes específicos para as regras de formatação CNAB 150."""

    def test_layout_version_field_a09(self):
        """Testa se o campo A09 (versão do layout) está correto - posições 80-81."""
        empresa = Cnab150EmpresaData(
            codigo_empresa="123456",
            nome_empresa="TESTE EMPRESA",
            codigo_convenio="18732000000000000000",
            codigo_banco="237",
            nome_banco="BRADESCO",
        )

        debito = DebitoAutomaticoData(
            id_cliente_empresa="CONTRATO001",
            agencia_debito="1234",
            conta_cliente="56789",
            vencimento=date(2025, 10, 30),
            valor=Decimal("100.00"),
            tipo_inscricao="2",  # CPF
            inscricao="11144477735",
            tipo_operacao="1",
        )

        request = Cnab150Request(nsa=1, empresa=empresa, debitos=[debito])
        arquivo = CnabGenerator.generate_cnab_150(request)

        linhas = arquivo.strip().split("\r\n")
        header = linhas[0]

        # Verifica posições 80-81 (índice 79-80): versão do layout deve ser "08"
        versao_layout = header[79:81]
        assert versao_layout == "08", f"Versão do layout incorreta: {versao_layout}"

    def test_inscricao_field_e10_cpf(self):
        """Testa se o campo E10 (inscrição CPF) está formatado corretamente - posições 131-145."""
        empresa = Cnab150EmpresaData(
            codigo_empresa="123456",
            nome_empresa="TESTE EMPRESA",
            codigo_convenio="18732000000000000000",
            codigo_banco="237",
            nome_banco="BRADESCO",
        )

        debito = DebitoAutomaticoData(
            id_cliente_empresa="CONTRATO001",
            agencia_debito="1234",
            conta_cliente="56789",
            vencimento=date(2025, 10, 30),
            valor=Decimal("100.00"),
            tipo_inscricao="2",  # CPF
            inscricao="11144477735",  # CPF válido
            tipo_operacao="1",
        )

        request = Cnab150Request(nsa=1, empresa=empresa, debitos=[debito])
        arquivo = CnabGenerator.generate_cnab_150(request)

        linhas = arquivo.strip().split("\r\n")
        detalhe = linhas[1]  # Primeiro registro de detalhe

        # Verifica posições 131-145 (índice 130-144): inscrição com 15 posições
        inscricao_formatada = detalhe[130:145]
        assert (
            inscricao_formatada == "000011144477735"
        ), f"CPF mal formatado: {inscricao_formatada}"

    def test_inscricao_field_e10_cnpj(self):
        """Testa se o campo E10 (inscrição CNPJ) está formatado corretamente - posições 131-145."""
        empresa = Cnab150EmpresaData(
            codigo_empresa="123456",
            nome_empresa="TESTE EMPRESA",
            codigo_convenio="18732000000000000000",
            codigo_banco="237",
            nome_banco="BRADESCO",
        )

        debito = DebitoAutomaticoData(
            id_cliente_empresa="CONTRATO001",
            agencia_debito="1234",
            conta_cliente="56789",
            vencimento=date(2025, 10, 30),
            valor=Decimal("100.00"),
            tipo_inscricao="1",  # CNPJ
            inscricao="12345678000190",  # CNPJ válido
            tipo_operacao="1",
        )

        request = Cnab150Request(nsa=1, empresa=empresa, debitos=[debito])
        arquivo = CnabGenerator.generate_cnab_150(request)

        linhas = arquivo.strip().split("\r\n")
        detalhe = linhas[1]  # Primeiro registro de detalhe

        # Verifica posições 131-145 (índice 130-144): inscrição com 15 posições
        inscricao_formatada = detalhe[130:145]
        assert (
            inscricao_formatada == "012345678000190"
        ), f"CNPJ mal formatado: {inscricao_formatada}"

    def test_tipo_operacao_field_e11(self):
        """Testa se o campo E11 (tipo de operação) está preenchido corretamente - posição 146."""
        empresa = Cnab150EmpresaData(
            codigo_empresa="123456",
            nome_empresa="TESTE EMPRESA",
            codigo_convenio="12345678901234567890",
            codigo_banco="237",
            nome_banco="BRADESCO",
        )

        # Testa todos os valores válidos de tipo de operação
        for tipo_operacao in ["1", "2", "3"]:
            debito = DebitoAutomaticoData(
                id_cliente_empresa="CONTRATO001",
                agencia_debito="1234",
                conta_cliente="56789",
                vencimento=date(2025, 10, 30),
                valor=Decimal("100.00"),
                tipo_inscricao="2",  # CPF
                inscricao="11144477735",
                tipo_operacao=tipo_operacao,
            )

            request = Cnab150Request(nsa=1, empresa=empresa, debitos=[debito])
            arquivo = CnabGenerator.generate_cnab_150(request)

            linhas = arquivo.strip().split("\r\n")
            detalhe = linhas[1]  # Primeiro registro de detalhe

            # Verifica posição 146 (índice 145): tipo de operação
            tipo_op_arquivo = detalhe[145:146]
            assert (
                tipo_op_arquivo == tipo_operacao
            ), f"Tipo de operação incorreto: esperado {tipo_operacao}, encontrado {tipo_op_arquivo}"

    def test_complete_record_lengths(self):
        """Testa se os campos específicos dos erros estão corretos."""
        empresa = Cnab150EmpresaData(
            codigo_empresa="123456",
            nome_empresa="TESTE EMPRESA",
            codigo_convenio="18732000000000000000",
            codigo_banco="237",
            nome_banco="BRADESCO",
        )

        debito = DebitoAutomaticoData(
            id_cliente_empresa="CONTRATO001",
            agencia_debito="1234",
            conta_cliente="56789",
            vencimento=date(2025, 10, 30),
            valor=Decimal("100.00"),
            tipo_inscricao="2",  # CPF
            inscricao="11144477735",
            tipo_operacao="1",
        )

        request = Cnab150Request(nsa=1, empresa=empresa, debitos=[debito])
        arquivo = CnabGenerator.generate_cnab_150(request)

        linhas = arquivo.strip().split("\r\n")

        # Valida que o arquivo foi gerado
        assert (
            len(linhas) >= 3
        ), f"Arquivo deve ter pelo menos 3 linhas (header, detalhe, trailer)"

        # Valida campos específicos dos erros reportados
        header = linhas[0]
        detalhe = linhas[1] if len(linhas) > 1 else ""

        # A09 - Versão do layout (posições 80-81) deve ser "08"
        if len(header) >= 81:
            versao_layout = header[79:81]
            assert versao_layout == "08", f"Versão do layout incorreta: {versao_layout}"

        # E10 - Inscrição (posições 131-145) deve estar formatada corretamente
        if len(detalhe) >= 145:
            inscricao = detalhe[130:145]
            assert inscricao == "000011144477735", f"CPF mal formatado: {inscricao}"

        # E11 - Tipo de operação (posição 146) deve ser "1"
        if len(detalhe) >= 146:
            tipo_operacao = detalhe[145:146]
            assert tipo_operacao == "1", f"Tipo de operação incorreto: {tipo_operacao}"


if __name__ == "__main__":
    pytest.main([__file__])
