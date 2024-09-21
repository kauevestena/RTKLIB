from scripts.lib import *

for estacao in estacoes:
    lat, lon, h = estacoes[estacao]

    for ano in anos:

        for mes in meses:

            for dia in tqdm(days_of_month(mes, ano)):
                folderpath = os.path.join(folder, estacao, str(ano), str(mes), str(dia))

                create_dir(folderpath)

                for horario in tqdm(horarios):
                    print(f"Baixando o arquivo {estacao}-{ano}-{mes}-{dia}-{horario}")

                    conteudo = baixar_arquivo_bruto(
                        dia=dia,
                        mes=mes,
                        ano=ano,
                        horario=horario,
                        caminho_da_pasta=folderpath,
                    )

                    horario_final = horario + 6

                    if horario_final == 24:
                        horario_final = 0

                    processar_arquivo(
                        conteudo=conteudo,
                        caminho_pasta=folderpath,
                        lat_alvo=lat,
                        lon_alvo=lon,
                        h_alvo=h,
                        ano=ano,
                        mes=mes,
                        dia=dia,
                        horario_inicial=horario,
                        horario_final=horario_final,
                    )
