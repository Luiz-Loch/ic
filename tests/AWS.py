import modulos

if __name__ == '__main__':
    BUCKET = 'benchmarks-ic'
    TESTE_FILE = 'teste.txt'
    instance_id = modulos.get_instance_id()
    instance_name = modulos.get_instance_name(instance_id)

    print('Iniciando o script...')

    print(f'ID da Instância: {instance_id}')
    if instance_name:
        print(f'Nome da Instância: {instance_name}')
    else:
        print('Nome da Instância não encontrado')

    # O arquivo `execution_times.json` é enviado para o bucket com o nome `execution_times.json`
    s3_file = f'{instance_name}/Teste'
    if modulos.upload_to_aws(TESTE_FILE, BUCKET, s3_file):
        print(f'Arquivo `{TESTE_FILE}` enviado para o bucket {BUCKET} com sucesso!')
    else:
        print(f'Erro ao enviar o arquivo `{TESTE_FILE}` para o bucket {BUCKET}')