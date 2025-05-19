#!/usr/bin/env python3
"""
Script para formatação de código em projetos Flutter/Dart.
Formata arquivos Dart mesmo quando formatadores específicos não estão disponíveis.

Uso:
    python format_code.py [diretório]
"""

import os
import sys
import subprocess
import time
import re
from concurrent.futures import ThreadPoolExecutor
import shutil


def clean_format_dart_file(file_path):
    """Aplica uma limpeza básica de formatação a um arquivo Dart."""
    try:
        print(f"Formatando com limpeza básica: {os.path.basename(file_path)}")

        # Tentar abrir e ler o arquivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Aplicar transformações de formatação básica para Dart

        # 1. Remover linhas em branco consecutivas (limite a 2 linhas vazias)
        processed_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

        # 2. Remover espaços em branco no final das linhas
        processed_content = re.sub(r'[ \t]+$', '', processed_content, flags=re.MULTILINE)

        # 3. Substituir tabs por 2 espaços (padrão do Dart)
        processed_content = processed_content.replace('\t', '  ')

        # 4. Adicionar espaço após vírgulas em listas/parâmetros
        processed_content = re.sub(r',\s*([^\s])', r', \1', processed_content)

        # 5. Espaço ao redor de operadores
        for op in ['=', '+', '-', '*', '/', '>=', '<=', '==', '!=', '=>']:
            processed_content = re.sub(r'([^\s])' + re.escape(op) + r'([^\s])', r'\1 ' + op + r' \2', processed_content)

        # 6. Espaço após ponto e vírgula em for loops
        processed_content = re.sub(r';([^\s])', r'; \1', processed_content)

        # 7. Garantir chaves em novas linhas consistentes
        processed_content = re.sub(r'}\s*else', '}\nelse', processed_content)

        # 8. Indentação consistente em blocos (simplificado)

        # Salvar o arquivo processado
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(processed_content)

        return True

    except Exception as e:
        print(f"  ✗ Erro ao processar {file_path}: {str(e)}")
        return False


def format_dart_file_with_command(file_path):
    """Tenta formatar um arquivo Dart usando comandos externos."""
    # Tentar usar dart format
    if shutil.which('dart'):
        try:
            result = subprocess.run(
                ['dart', 'format', file_path],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                print(f"  ✓ Formatado com dart format: {os.path.basename(file_path)}")
                return True
        except Exception:
            pass

    # Tentar usar flutter format como alternativa
    if shutil.which('flutter'):
        try:
            result = subprocess.run(
                ['flutter', 'format', file_path],
                capture_output=True, text=True, check=False
            )
            if result.returncode == 0:
                print(f"  ✓ Formatado com flutter format: {os.path.basename(file_path)}")
                return True
        except Exception:
            pass

    # Se nenhum comando funcionar, retornar False
    return False


def find_dart_files(project_dir):
    """Encontra todos os arquivos .dart em um diretório recursivamente."""
    dart_files = []

    for root, _, files in os.walk(project_dir):
        for file in files:
            if file.endswith('.dart'):
                full_path = os.path.abspath(os.path.join(root, file))
                dart_files.append(full_path)

    return dart_files


def format_dart_files(project_dir, max_workers=None):
    """Formata todos os arquivos Dart em um projeto Flutter."""
    project_dir = os.path.abspath(project_dir)
    print(f"Formatando arquivos Dart em: {project_dir}")

    if not os.path.isdir(project_dir):
        print(f"Erro: {project_dir} não é um diretório válido.")
        return

    # Encontrar arquivos Dart
    dart_files = find_dart_files(project_dir)
    total_files = len(dart_files)

    if total_files == 0:
        print("Nenhum arquivo .dart encontrado no projeto.")
        return

    print(f"Encontrados {total_files} arquivos .dart para formatar.")

    # Verificar se dart format está disponível
    has_dart_format = shutil.which('dart') is not None or shutil.which('flutter') is not None
    print(f"Formatador dart/flutter: {'✓ Disponível' if has_dart_format else '✗ Não disponível'}")

    if not has_dart_format:
        print("Aviso: Formatadores dart e flutter não estão disponíveis.")
        print("Será aplicada uma formatação básica nos arquivos Dart.")

    # Iniciar cronômetro
    start_time = time.time()

    # Formatar arquivos
    success_count = 0

    for file_path in dart_files:
        rel_path = os.path.relpath(file_path, project_dir)
        print(f"Processando: {rel_path}")

        # Tentar formatar com comando, se disponível
        if has_dart_format and format_dart_file_with_command(file_path):
            success_count += 1
        # Caso contrário, ou se falhar, aplicar limpeza básica
        elif clean_format_dart_file(file_path):
            success_count += 1
        # Se ambos falharem, registrar falha
        else:
            print(f"  ✗ Falha ao formatar: {rel_path}")

    # Calcular tempo total
    elapsed_time = time.time() - start_time

    # Exibir resumo
    print("\n" + "=" * 50)
    print(f"Tempo total: {elapsed_time:.2f} segundos")
    print(f"Arquivos formatados: {success_count}/{total_files}")
    if success_count < total_files:
        print(f"Falhas: {total_files - success_count}")


if __name__ == "__main__":
    # Obter diretório do projeto a partir dos argumentos ou usar o diretório atual
    project_dir = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()

    # Número de workers (threads) a serem usados
    max_workers = None  # Usar o padrão baseado no número de CPUs

    format_dart_files(project_dir, max_workers)