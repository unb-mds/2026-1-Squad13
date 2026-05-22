"""baseline_and_delay_metrics

Revision ID: 71f8ba3e30f7
Revises: 
Create Date: 2026-05-22 09:25:20.308405

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = '71f8ba3e30f7'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # 1. Criar baseline_tramitacao se não existir
    if 'baseline_tramitacao' not in tables:
        op.create_table('baseline_tramitacao',
        sa.Column('baseline_id', sa.Integer(), nullable=False),
        sa.Column('escopo', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('tipo', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('regime_tramitacao', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('fase_codigo', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('mediana_dias', sa.Integer(), nullable=False),
        sa.Column('origem_dados', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('baseline_id'),
        sa.UniqueConstraint('escopo', 'tipo', 'regime_tramitacao', 'fase_codigo', name='uq_baseline_tramitacao_escopo_tipo_regime_fase', postgresql_nulls_not_distinct=True)
        )
        op.create_index(op.f('ix_baseline_tramitacao_escopo'), 'baseline_tramitacao', ['escopo'], unique=False)
        op.create_index(op.f('ix_baseline_tramitacao_fase_codigo'), 'baseline_tramitacao', ['fase_codigo'], unique=False)
        op.create_index(op.f('ix_baseline_tramitacao_origem_dados'), 'baseline_tramitacao', ['origem_dados'], unique=False)
        op.create_index(op.f('ix_baseline_tramitacao_regime_tramitacao'), 'baseline_tramitacao', ['regime_tramitacao'], unique=False)
        op.create_index(op.f('ix_baseline_tramitacao_tipo'), 'baseline_tramitacao', ['tipo'], unique=False)

    # 2. Criar fase_analitica se não existir
    if 'fase_analitica' not in tables:
        op.create_table('fase_analitica',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('codigo', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('nome', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('ordem_logica', sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_fase_analitica_codigo'), 'fase_analitica', ['codigo'], unique=True)
        op.create_index(op.f('ix_fase_analitica_ordem_logica'), 'fase_analitica', ['ordem_logica'], unique=False)

    # 3. Criar log_coleta_batch se não existir
    if 'log_coleta_batch' not in tables:
        op.create_table('log_coleta_batch',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('data_hora', sa.DateTime(), nullable=False),
        sa.Column('fonte', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('itens_coletados', sa.Integer(), nullable=False),
        sa.Column('mensagem_erro', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_log_coleta_batch_fonte'), 'log_coleta_batch', ['fonte'], unique=False)

    # 4. Criar orgaolegislativo se não existir
    if 'orgaolegislativo' not in tables:
        op.create_table('orgaolegislativo',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('sigla', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('nome', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('casa', sa.Enum('CAMARA', 'SENADO', 'AMBAS', name='casalegislativa'), nullable=False),
        sa.Column('id_origem', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_orgaolegislativo_id_origem'), 'orgaolegislativo', ['id_origem'], unique=False)
        op.create_index(op.f('ix_orgaolegislativo_sigla'), 'orgaolegislativo', ['sigla'], unique=False)

    # 5. Criar ou atualizar proposicao
    if 'proposicao' in tables:
        columns = [col['name'] for col in inspector.get_columns('proposicao')]
        
        # Novas colunas a adicionar condicionalmente
        new_cols = {
            'indice_atraso_relativo': sa.Column('indice_atraso_relativo', sa.Float(), nullable=True),
            'indice_atraso_fase_atual': sa.Column('indice_atraso_fase_atual', sa.Float(), nullable=True),
            'indice_espera_improdutiva': sa.Column('indice_espera_improdutiva', sa.Float(), nullable=True),
            'status_atraso': sa.Column('status_atraso', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            'dias_decorridos_total': sa.Column('dias_decorridos_total', sa.Integer(), nullable=True),
            'dias_esperados_total': sa.Column('dias_esperados_total', sa.Integer(), nullable=True),
            'baseline_grupo_id': sa.Column('baseline_grupo_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
            'data_calculo_metricas': sa.Column('data_calculo_metricas', sa.DateTime(), nullable=True),
        }
        
        for col_name, col_obj in new_cols.items():
            if col_name not in columns:
                op.add_column('proposicao', col_obj)
    else:
        op.create_table('proposicao',
        sa.Column('id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('tipo', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('numero', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('ano', sa.Integer(), nullable=False),
        sa.Column('ementa', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('ementa_resumida', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('autor', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('uf_autor', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('orgao_origem', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('status', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('orgao_atual', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('data_apresentacao', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('data_ultima_movimentacao', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('tempo_total_dias', sa.Integer(), nullable=True),
        sa.Column('tem_atraso', sa.Boolean(), nullable=True),
        sa.Column('tem_previsao_ia', sa.Boolean(), nullable=True),
        sa.Column('link_oficial', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('data_encerramento', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('previsao_aprovacao_dias', sa.Integer(), nullable=True),
        sa.Column('indice_atraso_relativo', sa.Float(), nullable=True),
        sa.Column('indice_atraso_fase_atual', sa.Float(), nullable=True),
        sa.Column('indice_espera_improdutiva', sa.Float(), nullable=True),
        sa.Column('status_atraso', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('dias_decorridos_total', sa.Integer(), nullable=True),
        sa.Column('dias_esperados_total', sa.Integer(), nullable=True),
        sa.Column('baseline_grupo_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('data_calculo_metricas', sa.DateTime(), nullable=True),
        sa.Column('tags', sa.JSON().with_variant(postgresql.JSONB(astext_type=sa.Text()), 'postgresql'), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )

    # 6. Criar user se não existir
    if 'user' not in tables:
        op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('perfil', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)

    # 7. Criar apensamento se não existir
    if 'apensamento' not in tables:
        op.create_table('apensamento',
        sa.Column('apensamento_id', sa.Integer(), nullable=False),
        sa.Column('materia_apensada_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('materia_principal_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('data_apensacao', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('casa', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('fonte_endpoint', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('payload_bruto', sa.JSON(), nullable=True),
        sa.Column('confianca', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['materia_apensada_id'], ['proposicao.id'], ),
        sa.PrimaryKeyConstraint('apensamento_id')
        )
        op.create_index(op.f('ix_apensamento_materia_apensada_id'), 'apensamento', ['materia_apensada_id'], unique=False)
        op.create_index(op.f('ix_apensamento_materia_principal_id'), 'apensamento', ['materia_principal_id'], unique=False)

    # 8. Criar evento_tramitacao se não existir
    if 'evento_tramitacao' not in tables:
        op.create_table('evento_tramitacao',
        sa.Column('evento_id', sa.Integer(), nullable=False),
        sa.Column('proposicao_id', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('data_evento', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('sequencia', sa.Integer(), nullable=False),
        sa.Column('sigla_orgao', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('descricao_original', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('tipo_evento', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('fase_analitica_id', sa.Integer(), nullable=True),
        sa.Column('deliberativo', sa.Boolean(), nullable=False),
        sa.Column('mudou_fase', sa.Boolean(), nullable=False),
        sa.Column('mudou_orgao', sa.Boolean(), nullable=False),
        sa.Column('remessa_ou_retorno', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column('dias_na_etapa', sa.Integer(), nullable=False),
        sa.Column('tem_atraso', sa.Boolean(), nullable=False),
        sa.Column('marca_apensacao', sa.Boolean(), nullable=False),
        sa.Column('relevante', sa.Boolean(), nullable=False),
        sa.Column('payload_bruto', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['fase_analitica_id'], ['fase_analitica.id'], ),
        sa.ForeignKeyConstraint(['proposicao_id'], ['proposicao.id'], ),
        sa.PrimaryKeyConstraint('evento_id')
        )
        op.create_index(op.f('ix_evento_tramitacao_fase_analitica_id'), 'evento_tramitacao', ['fase_analitica_id'], unique=False)
        op.create_index('ix_evento_tramitacao_prop_data_seq', 'evento_tramitacao', ['proposicao_id', 'data_evento', 'sequencia'], unique=False)
        op.create_index(op.f('ix_evento_tramitacao_proposicao_id'), 'evento_tramitacao', ['proposicao_id'], unique=False)
        op.create_index(op.f('ix_evento_tramitacao_sigla_orgao'), 'evento_tramitacao', ['sigla_orgao'], unique=False)
        op.create_index(op.f('ix_evento_tramitacao_tipo_evento'), 'evento_tramitacao', ['tipo_evento'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_evento_tramitacao_tipo_evento'), table_name='evento_tramitacao')
    op.drop_index(op.f('ix_evento_tramitacao_sigla_orgao'), table_name='evento_tramitacao')
    op.drop_index(op.f('ix_evento_tramitacao_proposicao_id'), table_name='evento_tramitacao')
    op.drop_index('ix_evento_tramitacao_prop_data_seq', table_name='evento_tramitacao')
    op.drop_index(op.f('ix_evento_tramitacao_fase_analitica_id'), table_name='evento_tramitacao')
    op.drop_table('evento_tramitacao')
    op.drop_index(op.f('ix_apensamento_materia_principal_id'), table_name='apensamento')
    op.drop_index(op.f('ix_apensamento_materia_apensada_id'), table_name='apensamento')
    op.drop_table('apensamento')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    op.drop_table('proposicao')
    op.drop_index(op.f('ix_orgaolegislativo_sigla'), table_name='orgaolegislativo')
    op.drop_index(op.f('ix_orgaolegislativo_id_origem'), table_name='orgaolegislativo')
    op.drop_table('orgaolegislativo')
    op.drop_index(op.f('ix_log_coleta_batch_fonte'), table_name='log_coleta_batch')
    op.drop_table('log_coleta_batch')
    op.drop_index(op.f('ix_fase_analitica_ordem_logica'), table_name='fase_analitica')
    op.drop_index(op.f('ix_fase_analitica_codigo'), table_name='fase_analitica')
    op.drop_table('fase_analitica')
    op.drop_index(op.f('ix_baseline_tramitacao_tipo'), table_name='baseline_tramitacao')
    op.drop_index(op.f('ix_baseline_tramitacao_regime_tramitacao'), table_name='baseline_tramitacao')
    op.drop_index(op.f('ix_baseline_tramitacao_origem_dados'), table_name='baseline_tramitacao')
    op.drop_index(op.f('ix_baseline_tramitacao_fase_codigo'), table_name='baseline_tramitacao')
    op.drop_index(op.f('ix_baseline_tramitacao_escopo'), table_name='baseline_tramitacao')
    op.drop_table('baseline_tramitacao')
    
    # Drop custom PostgreSQL enum type
    op.execute("DROP TYPE IF EXISTS casalegislativa")
    # ### end Alembic commands ###
