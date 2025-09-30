"""
Models para representar os dados de entrada dos diferentes layouts CNAB.
Define estruturas claras e validadas para cada tipo de arquivo.
"""

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import List, Optional


@dataclass
class EmpresaData:
    """Dados básicos da empresa para qualquer layout CNAB."""

    codigo_empresa: str
    nome_empresa: str

    def __post_init__(self):
        if not self.codigo_empresa:
            raise ValueError("Código da empresa é obrigatório")
        if not self.nome_empresa:
            raise ValueError("Nome da empresa é obrigatório")


@dataclass
class Cnab150EmpresaData(EmpresaData):
    """Dados específicos da empresa para CNAB 150."""

    codigo_convenio: str
    codigo_banco: str
    nome_banco: str

    def __post_init__(self):
        super().__post_init__()
        if not self.codigo_convenio:
            raise ValueError("Código do convênio é obrigatório")
        if not self.codigo_banco:
            raise ValueError("Código do banco é obrigatório")
        if not self.nome_banco:
            raise ValueError("Nome do banco é obrigatório")


@dataclass
class Cnab400EmpresaData(EmpresaData):
    """Dados específicos da empresa para CNAB 400."""

    pass  # Para CNAB 400, os dados básicos são suficientes


@dataclass
class DebitoAutomaticoData:
    """Dados para débito automático CNAB 150."""

    id_cliente_empresa: str
    agencia_debito: str
    conta_cliente: str
    vencimento: date
    valor: Decimal
    tipo_inscricao: str  # '1' = CNPJ, '2' = CPF
    inscricao: str
    tipo_operacao: str = "1"  # '1', '2' ou '3'
    codigo_movimento: str = "0"
    utilizacao_cheque_especial: str = (
        "2"  # '1'=permite, '2'=não permite (padrão: não permite)
    )
    opcao_debito_parcial: str = (
        "2"  # '1'=permite parcial/pós-vencimento, '2'=não permite pós-vencimento (padrão: não permite)
    )

    def __post_init__(self):
        if not self.id_cliente_empresa:
            raise ValueError("ID do cliente na empresa é obrigatório")
        if not self.agencia_debito:
            raise ValueError("Agência para débito é obrigatória")
        if not self.conta_cliente:
            raise ValueError("Conta do cliente é obrigatória")
        if self.valor <= 0:
            raise ValueError("Valor deve ser positivo")
        if self.tipo_inscricao not in ["1", "2"]:
            raise ValueError("Tipo de inscrição deve ser '1' (CNPJ) ou '2' (CPF)")
        if not self.inscricao:
            raise ValueError("Inscrição (CPF/CNPJ) é obrigatória")
        if self.tipo_operacao not in ["1", "2", "3"]:
            raise ValueError("Tipo de operação deve ser '1', '2' ou '3'")

        # Converte float para Decimal se necessário
        if isinstance(self.valor, (int, float)):
            self.valor = Decimal(str(self.valor))

        # Limpa caracteres não numéricos da inscrição
        self.inscricao = "".join(filter(str.isdigit, self.inscricao))

        # Valida tamanho da inscrição
        if self.tipo_inscricao == "2":  # CPF
            if len(self.inscricao) != 11:
                raise ValueError("CPF deve ter exatamente 11 dígitos")
        elif self.tipo_inscricao == "1":  # CNPJ
            if len(self.inscricao) != 14:
                raise ValueError("CNPJ deve ter exatamente 14 dígitos")


@dataclass
class PagadorData:
    """Dados do pagador para cobrança."""

    tipo_inscricao: str  # '01' = CPF, '02' = CNPJ
    inscricao: str
    nome: str
    endereco: str
    cep: str

    def __post_init__(self):
        if self.tipo_inscricao not in ["01", "02"]:
            raise ValueError("Tipo de inscrição deve ser '01' (CPF) ou '02' (CNPJ)")
        if not self.inscricao:
            raise ValueError("Inscrição (CPF/CNPJ) é obrigatória")
        if not self.nome:
            raise ValueError("Nome do pagador é obrigatório")
        if not self.endereco:
            raise ValueError("Endereço é obrigatório")
        if not self.cep:
            raise ValueError("CEP é obrigatório")


@dataclass
class CobrancaData:
    """Dados para cobrança CNAB 400."""

    carteira: str
    agencia: str
    conta: str
    conta_dv: str
    nosso_numero: str
    nosso_numero_banco: str
    nosso_numero_banco_dv: str
    numero_documento: str
    vencimento: date
    data_emissao: date
    valor: Decimal
    pagador: PagadorData
    ocorrencia: str = "01"  # '01' = Remessa

    def __post_init__(self):
        if not self.carteira:
            raise ValueError("Carteira é obrigatória")
        if not self.agencia:
            raise ValueError("Agência é obrigatória")
        if not self.conta:
            raise ValueError("Conta é obrigatória")
        if not self.conta_dv:
            raise ValueError("Dígito verificador da conta é obrigatório")
        if not self.nosso_numero:
            raise ValueError("Nosso número é obrigatório")
        if not self.numero_documento:
            raise ValueError("Número do documento é obrigatório")
        if self.valor <= 0:
            raise ValueError("Valor deve ser positivo")

        # Converte float para Decimal se necessário
        if isinstance(self.valor, (int, float)):
            self.valor = Decimal(str(self.valor))


@dataclass
class CnabRequest:
    """Request base para geração de arquivos CNAB."""

    nsa: int  # Número Sequencial do Arquivo

    def __post_init__(self):
        if self.nsa < 0:
            raise ValueError("NSA deve ser zero ou um número positivo")


@dataclass
class Cnab150Request(CnabRequest):
    """Request específico para CNAB 150."""

    empresa: Cnab150EmpresaData
    debitos: List[DebitoAutomaticoData] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not self.debitos:
            raise ValueError("Lista de débitos não pode estar vazia")


@dataclass
class Cnab400Request(CnabRequest):
    """Request específico para CNAB 400."""

    empresa: Cnab400EmpresaData
    cobrancas: List[CobrancaData] = field(default_factory=list)

    def __post_init__(self):
        super().__post_init__()
        if not self.cobrancas:
            raise ValueError("Lista de cobranças não pode estar vazia")
