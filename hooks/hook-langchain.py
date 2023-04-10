from PyInstaller.utils.hooks import collect_data_files

datas = collect_data_files('langchain')

if __name__ == '__main__':
    print('datas')
    for d in datas:
        print(d)