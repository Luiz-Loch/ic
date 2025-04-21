import project_utils

if __name__ == '__main__':
    BUCKET: str = 'benchmarks-ic'
    TESTE_FILE: str = './teste.txt'
    instance_id = project_utils.get_instance_id()
    instance_name = project_utils.get_instance_name(instance_id)

    print('Iniciando o script...')

    print(f'ID da instância: {instance_id}')
    if instance_name:
        print(f'Nome da instância: {instance_name}')
    else:
        print('Nome da instância não encontrado')

    # Tentativa de upload de arquivo para o bucket
    s3_file = f'{instance_name}/teste'
    if project_utils.upload_to_aws(TESTE_FILE, BUCKET, s3_file):
        print(f'Arquivo `{TESTE_FILE}` enviado para o bucket {BUCKET} com sucesso!')
    else:
        print(f'Erro ao enviar o arquivo `{TESTE_FILE}` para o bucket {BUCKET}')