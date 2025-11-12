# tests/config/test_settings.py
import pytest
from pydantic import ValidationError
from src.config.settings import get_settings, Settings
# from pydantic_settings import SettingsConfigDict # Não é mais necessário importar aqui

# Fixture para limpar o cache de get_settings antes e depois de cada teste.
@pytest.fixture
def clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()

def test_settings_loads_from_env_vars(monkeypatch, clear_settings_cache):
    """
    Testa se as configurações são carregadas corretamente das variáveis de ambiente.
    """
    with monkeypatch.context() as m: # Use monkeypatch.context para garantir que as alterações sejam desfeitas
        # Corrigido: Usar m.setitem para modificar a chave 'env_file' no dicionário model_config
        m.setitem(Settings.model_config, 'env_file', None) # Define env_file como None para não carregar arquivo

        m.setenv("BIGDATACORP_TOKEN_ID", "test_token_id")
        m.setenv("BIGDATACORP_ACCESS_TOKEN", "test_access_token")
        m.setenv("DW_HOST", "127.0.0.1")
        m.setenv("DW_DATABASE", "test_db")
        m.setenv("DW_PORT", "1234") # Monkeypatch seta string, Pydantic converte para int
        m.setenv("DW_USER", "test_user")
        m.setenv("DW_PASS", "test_pass")

        settings = get_settings()

        assert settings.BIGDATACORP_TOKEN_ID == "test_token_id"
        assert settings.BIGDATACORP_ACCESS_TOKEN == "test_access_token"
        assert settings.DW_HOST == "127.0.0.1"
        assert settings.DW_DATABASE == "test_db"
        assert settings.DW_PORT == 1234 # Verifica se a conversão para int funcionou
        assert settings.DW_USER == "test_user"
        assert settings.DW_PASS == "test_pass"

def test_settings_missing_required_env_var_raises_error(monkeypatch, clear_settings_cache):
    """
    Testa se um erro é levantado quando uma variável de ambiente obrigatória está faltando.
    """
    with monkeypatch.context() as m: # Use monkeypatch.context para garantir que as alterações sejam desfeitas
        # Corrigido: Usar m.setitem para modificar a chave 'env_file' no dicionário model_config
        m.setitem(Settings.model_config, 'env_file', None) # Define env_file como None para não carregar arquivo

        # Mocka a maioria das variáveis, mas omite uma (BIGDATACORP_ACCESS_TOKEN)
        m.setenv("BIGDATACORP_TOKEN_ID", "test_token_id")
        # BIGDATACORP_ACCESS_TOKEN está intencionalmente ausente
        m.setenv("DW_HOST", "127.0.0.1")
        m.setenv("DW_DATABASE", "test_db")
        m.setenv("DW_PORT", "1234")
        m.setenv("DW_USER", "test_user")
        m.setenv("DW_PASS", "test_pass")
        
        # Garante que a variável ausente não está definida no ambiente do teste
        m.delenv("BIGDATACORP_ACCESS_TOKEN", raising=False)

        # Espera que o Pydantic levante uma ValidationError
        with pytest.raises(ValidationError):
            get_settings()

def test_get_settings_uses_cache(monkeypatch):
    """
    Testa se get_settings usa o cache, retornando a mesma instância com as configurações
    da primeira chamada, mesmo que as variáveis de ambiente mudem depois.
    """
    get_settings.cache_clear() # Limpa o cache explicitamente para este teste

    with monkeypatch.context() as m: # Use monkeypatch.context para garantir que as alterações sejam desfeitas
        # Corrigido: Usar m.setitem para modificar a chave 'env_file' no dicionário model_config
        m.setitem(Settings.model_config, 'env_file', None)

        # Primeira carga de configurações
        m.setenv("BIGDATACORP_TOKEN_ID", "value_1")
        m.setenv("BIGDATACORP_ACCESS_TOKEN", "access_1")
        m.setenv("DW_HOST", "host_1")
        m.setenv("DW_DATABASE", "db_1")
        m.setenv("DW_PORT", "1111")
        m.setenv("DW_USER", "user_1")
        m.setenv("DW_PASS", "pass_1")
        
        settings_instance_1 = get_settings()

        # Muda as variáveis de ambiente APÓS a primeira carga
        m.setenv("BIGDATACORP_TOKEN_ID", "value_2")
        m.setenv("DW_HOST", "host_2")
        
        # Chama get_settings novamente. Deve retornar a instância cacheada.
        settings_instance_2 = get_settings() 

        # Verifica se é a mesma instância de objeto
        assert settings_instance_1 is settings_instance_2
        # Verifica se os valores são os da primeira carga, pois o cache foi usado
        assert settings_instance_2.BIGDATACORP_TOKEN_ID == "value_1" 
        assert settings_instance_2.DW_HOST == "host_1" 

    get_settings.cache_clear() # Limpa o cache após o teste (opcional, mas boa prática)