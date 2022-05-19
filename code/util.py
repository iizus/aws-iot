from glob import glob


def __get_certs_path_of(project_name:str, cert_type:str) -> str:
    certs_path = f"certs/{project_name}/*.{cert_type}"
    cert_path = glob(certs_path)[0]
    return cert_path


if __name__ == '__main__':
    cert_path:str = __get_certs_path_of(project_name='test', cert_type='crt')
    print(cert_path)