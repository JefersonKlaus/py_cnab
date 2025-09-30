"""
Testes unitários para a biblioteca py_cnab.
"""

import pytest
from datetime import date
from decimal import Decimal

from src.models import (
    Cnab150EmpresaData,
    Cnab400EmpresaData,
    DebitoAutomaticoData,
    PagadorData,
    CobrancaData,
    Cnab150Request,
    Cnab400Request,
)
from src import CnabGenerator


class TestModels:
    """Testes para os models de dados."""

    def test_cnab150_empresa_data_valid(self):
        """Testa criação válida de dados da empresa CNAB 150."""
        empresa = Cnab150EmpresaData(
            codigo_empresa="123456",
            nome_empresa="TESTE EMPRESA",
            codigo_convenio="12345678901234567890",
            codigo_banco="237",
            nome_banco="BRADESCO",
        )
        assert empresa.codigo_empresa == "123456"
        assert empresa.nome_empresa == "TESTE EMPRESA"

    def test_cnab150_empresa_data_invalid(self):
        """Testa validação de dados inválidos."""
        with pytest.raises(ValueError, match="Código da empresa é obrigatório"):
            Cnab150EmpresaData(
                codigo_empresa="",
                nome_empresa="TESTE",
                codigo_convenio="123",
                codigo_banco="237",
                nome_banco="BRADESCO",
            )

    def test_debito_automatico_data_valid(self):
        """Testa criação válida de débito automático."""
        debito = DebitoAutomaticoData(
            id_cliente_empresa="CONTRATO001",
            agencia_debito="1234",
            conta_cliente="56789-0",
            vencimento=date(2025, 10, 30),
            valor=Decimal("199.99"),
            tipo_inscricao="2",  # CPF
            inscricao="12345678901",
        )
        assert debito.id_cliente_empresa == "CONTRATO001"
        assert debito.valor == Decimal("199.99")
        assert debito.tipo_inscricao == "2"
        assert debito.inscricao == "12345678901"  # Limpo de caracteres especiais

    def test_debito_automatico_data_invalid_valor(self):
        """Testa validação de valor inválido."""
        with pytest.raises(ValueError, match="Valor deve ser positivo"):
            DebitoAutomaticoData(
                id_cliente_empresa="CONTRATO001",
                agencia_debito="1234",
                conta_cliente="56789-0",
                vencimento=date(2025, 10, 30),
                valor=Decimal("0"),
                tipo_inscricao="2",
                inscricao="12345678901",
            )

    def test_debito_automatico_data_invalid_tipo_inscricao(self):
        """Testa validação de tipo de inscrição inválido."""
        with pytest.raises(
            ValueError,
            match="Tipo de inscrição deve ser '1' \\(CNPJ\\) ou '2' \\(CPF\\)",
        ):
            DebitoAutomaticoData(
                id_cliente_empresa="CONTRATO001",
                agencia_debito="1234",
                conta_cliente="56789-0",
                vencimento=date(2025, 10, 30),
                valor=Decimal("100.00"),
                tipo_inscricao="3",  # Tipo inválido
                inscricao="12345678901",
            )

    def test_debito_automatico_data_invalid_cpf_length(self):
        """Testa validação de tamanho de CPF inválido."""
        with pytest.raises(ValueError, match="CPF deve ter exatamente 11 dígitos"):
            DebitoAutomaticoData(
                id_cliente_empresa="CONTRATO001",
                agencia_debito="1234",
                conta_cliente="56789-0",
                vencimento=date(2025, 10, 30),
                valor=Decimal("100.00"),
                tipo_inscricao="2",  # CPF
                inscricao="123456789",  # CPF com apenas 9 dígitos
            )

    def test_debito_automatico_data_invalid_cnpj_length(self):
        """Testa validação de tamanho de CNPJ inválido."""
        with pytest.raises(ValueError, match="CNPJ deve ter exatamente 14 dígitos"):
            DebitoAutomaticoData(
                id_cliente_empresa="CONTRATO001",
                agencia_debito="1234",
                conta_cliente="56789-0",
                vencimento=date(2025, 10, 30),
                valor=Decimal("100.00"),
                tipo_inscricao="1",  # CNPJ
                inscricao="123456789012",  # CNPJ com apenas 12 dígitos
            )

    def test_debito_automatico_data_inscricao_format_cleanup(self):
        """Testa limpeza de caracteres especiais na inscrição."""
        debito = DebitoAutomaticoData(
            id_cliente_empresa="CONTRATO001",
            agencia_debito="1234",
            conta_cliente="56789-0",
            vencimento=date(2025, 10, 30),
            valor=Decimal("100.00"),
            tipo_inscricao="1",  # CNPJ
            inscricao="12.345.678/0001-90",  # CNPJ com formatação
        )
        # Deve remover caracteres especiais
        assert debito.inscricao == "12345678000190"


class TestCnabGenerator:
    """Testes para o gerador CNAB."""

    def test_generate_cnab_150_success(self):
        """Testa geração bem-sucedida de CNAB 150."""
        empresa = Cnab150EmpresaData(
            codigo_empresa="123456",
            nome_empresa="TESTE EMPRESA",
            codigo_convenio="12345678901234567890",
            codigo_banco="237",
            nome_banco="BRADESCO",
        )

        debito = DebitoAutomaticoData(
            id_cliente_empresa="CONTRATO001",
            agencia_debito="1234",
            conta_cliente="56789-0",
            vencimento=date(2025, 10, 30),
            valor=Decimal("199.99"),
            tipo_inscricao="2",  # CPF
            inscricao="12345678901",
        )

        request = Cnab150Request(nsa=1, empresa=empresa, debitos=[debito])
        arquivo = CnabGenerator.generate_cnab_150(request)

        # Verifica se o arquivo foi gerado
        assert arquivo is not None
        assert len(arquivo) > 0

        # Verifica quebras de linha CNAB
        assert "\r\n" in arquivo

        # Verifica se tem pelo menos 3 linhas (header, detalhe, trailer)
        linhas = arquivo.split("\r\n")
        assert len(linhas) >= 4  # 3 linhas + linha vazia no final

    def test_validate_file_cnab_150(self):
        """Testa validação de arquivo CNAB 150."""
        empresa = Cnab150EmpresaData(
            codigo_empresa="123456",
            nome_empresa="TESTE EMPRESA",
            codigo_convenio="12345678901234567890",
            codigo_banco="237",
            nome_banco="BRADESCO",
        )

        debito = DebitoAutomaticoData(
            id_cliente_empresa="CONTRATO001",
            agencia_debito="1234",
            conta_cliente="56789-0",
            vencimento=date(2025, 10, 30),
            valor=Decimal("199.99"),
            tipo_inscricao="1",  # CNPJ
            inscricao="12.345.678/0001-90",
        )

        request = Cnab150Request(nsa=1, empresa=empresa, debitos=[debito])
        arquivo = CnabGenerator.generate_cnab_150(request)

        # Valida o arquivo
        errors = CnabGenerator.validate_file(arquivo, "150_debito")
        assert len(errors) == 0, f"Arquivo inválido: {errors}"

    def test_get_supported_formats(self):
        """Testa listagem de formatos suportados."""
        formats = CnabGenerator.get_supported_formats()
        assert "150_debito" in formats
        assert "400_cobranca" in formats


if __name__ == "__main__":
    pytest.main([__file__])
