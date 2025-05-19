import re
from colorama import Fore, Style


def validate_config(config):
    """Valida se a configuração do app está correta."""
    valid = True

    # Verificar se as seções obrigatórias existem
    if 'app' not in config:
        print(f"{Fore.RED}Erro: Seção 'app' não encontrada na configuração{Style.RESET_ALL}")
        valid = False
    else:
        # Verificar campos obrigatórios na seção 'app'
        if 'name' not in config['app']:
            print(f"{Fore.RED}Erro: Campo 'name' não encontrado na seção 'app'{Style.RESET_ALL}")
            valid = False
        if 'package' not in config['app']:
            print(f"{Fore.RED}Erro: Campo 'package' não encontrado na seção 'app'{Style.RESET_ALL}")
            valid = False
            if not re.match(r'^[a-z][a-z0-9_]*(\.[a-z0-9_]+)+[0-9a-z_]', config['app']['package']):
                print(f"{Fore.RED}Erro: Campo 'package' inválido na seção 'app'{Style.RESET_ALL}")
                valid = False