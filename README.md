SAFE - Speech Alignment & Feature Extraction
---------
Passos para rodar o script python
---------
1. Crie a pasta "C:\Praat" e coloque o "Praat.exe" nela.
2. Crie a pasta "C:\Praat\Aligner" e coloque os arquivos listados abaixo nela.
	- scripts:
		. "AudioTrimmer.praat";
		. "VVunitAligner.praat";
		. "Aligner.py";
		. "Aligner.bat";
	- opcionais:
		. AlignerStarter.bat [OPCIONAL].
		. AlignerStarter.lnk [OPCIONAL].
		. LEIA-ME [OPCIONAL].
	- som e texto:
		. todos os arquivos a serem processados deve estar nas pastas:
			> ".\AmE\FEM";
			> ".\AmE\MAL";
			> ".\BPT\FEM";
			> ".\BPT\MAL".
		. lembre-se que a dupla de cada experimento deve ter o mesmo nome, só mudando a extensão.
			> "soundName.flac";
			> "soundName.vtt".
3. No Windows Explorer, navegue a até a pasta "C:\Praat\Aligner".
4. Selecione o arquivo "AlignerStarter.bat" e execute-o como administrador. Se o atalho já estiver configurado para ser executado com administrador, basta dar um duplo clique no "AlignerStarter.lnk".
5. Após a conclusão da execução, os arquivos de saída ".txt", ".flac" e ".TextGrid" estarão na subpasta "output\".
Nota: os arquivos gerados terão os mesmos nomes dos arquivos de entrada adicionados de um sufixo "_trimmed".
--------------------------------
--------------------------------
Resumo do script Aligner.py
--------------------------------
1. [Retag Files]
	1. Varre os diretórios LAN\SEX e efetua cópia para o diretório corrente e renomeação dos nomes dos arquivos.
2. [Diretório de saída] Preparação dos diretórios output\ e output\temp\.
3. [Loop principal] Início do loop principal.
4. [DataPreparator] Varre o diretório atual e coleta todos os nomes de arquivos .flac.
	Nota: Os arquivos .vtt devem estar com os mesmos nomes dos arquivos .flac.
5. [DataPreparator] Abre o arquivo .vtt e coleta os tempos:
	- startTime = tempo inicial do segundo intervalo;
	- endTime = tempo final do antepenúltimo intervalo.
6. [DataPreparator] Gera o arquivo "*_trimmed.txt" no diretório output\temp\.
7. [DataPreparator] Configura os argumentos a serem passados para o script do praat:
	- soundName: nome do arquivo no loop de varredura dos arquivos .flac do diretório local;
	- startTime: tempo coletado do arquivo .vtt;
	- endTime: tempo coletado do arquivo .vtt;
	- silence: 0.5 sec.
	Nota: como o script do praat será chamado via função da biblioteca subprocess, todos os argumentos precisam estar como string.
8. [DataPreparator] Chamada do script AudioTrimmer.praat com os argumentos definidos.
	- Se o retorno for OK [0], o arquivo de som cortado será gerado (*_trimmed.flac) no diretório output\temp\.
	- Caso contrário, será sinalizado erro.
7. [Aligner] Chamada do script Aligner.bat para rodar o MFA, passando via argumento, o dicionário e o modelo acústico.
	- Se o retorno for OK [0], o arquivo TextGrid será gerado (*_trimmed.TextGrid) no diretório output\temp\.
	- Caso contrário, será sinalizado erro.
8. [Reprocessor] Chamada do script VVunitAligner.praat com os argumentos definidos.
	- Se o retorno for OK [0], os arquivos de TextGrid e analytics (*_trimmed.TextGrid, *_trimmed_MFA.TextGrid, *_trimmed_MFA_VV.TextGrid, *_trimmed_analytics.txt) são gerados no diretório output\temp\.
	- Caso contrário, será sinalizado erro.
9. [File transfer] Após a conclusão da rodada de processamento, todos os arquivos do diretório output\temp\ são transferidos para o diretório output\. No fim, são 6 arquivos por experimento.
10. [Loop principal] Fim do loop principal.
11. [Summary] Após a conclusão do processamento de todos os arquivos de som, os arquivos de analytics são varridos para se fazer a contabilização geral das estatísticas. Esta totalização é registrada no arquivo Global_Sumary_Analytics.txt, na pasta output\.
--------------------------------
--------------------------------
Resumo do script do praat AudioTrimmer.praat
--------------------------------
1. Recebe os argumentos na sequência do form.
2. Limpa os objetos da instância corrente do praat.
3. Como os arquivos de som são estéreos, há necessidade de seleção de um canal.
4. Utiliza os tempos de início e fim, ampliando a janela com uma pequena parcela de silêncio no início e no fim.
5. Efetua o corte do sinal de fala considerando a janela temporal configurada.
6. Executa uma pré-delimitação de TextGrid com base no sinal de fala cortado.
7. Salva os arquivos de "*_trimmed.TextGrid" e "*_trimmed.flac" no diretório do script do praat.
	Nota: depois, no script do python, os referidos arquivos são transferidos para a subpasta "\output".
--------------------------------
--------------------------------
Resumo do script .bat Aligner.bat
--------------------------------
1. Ativa o ambiente do conda "aligner" (criado pelo usuário).
2. Executa o comando de alinhamento:
	mfa align [OPTIONS] CORPUS_DIRECTORY DICTIONARY_PATH ACOUSTIC_MODEL_PATH OUTPUT_DIRECTORY
	- [OPTION] = --clean	remove arquivos da execução anterior.
	- CORPUS_DIRECTORY = C:\Praat\Aligner\output	diretório dos arquivos de som e texto.
	- DICTIONARY_PATH = portuguese_brazil_mfa (passado por argumento)	caminho do dicionário.
	- ACOUSTIC_MODEL_PATH = portuguese_mfa (passado por argumento)	caminho do modelo acústico.
	- OUTPUT_DIRECTORY = C:\Praat\Aligner\output.
	Nota: os arquivos de TextGrid já são gerados na subpasta "\output".
--------------------------------
--------------------------------
Instalação do MFA
--------------------------------
1. Acesse o prompt do Anaconda como administrador.

2. Execute o comando:
	
	conda create -n aligner -c conda-forge montreal-forced-aligner
	
para criar um novo ambiente no conda ("aligner") e instalar o MFA.

3. Certifique-se de que você está no novo ambiente criado com o comando:

	conda activate aligner

Nota: para desativar o ambiente, use o comando: conda deactivate.

4. Instale o dicionário e o modelo acústico, usando os seguintes comandos:
	
	mfa model download acoustic portuguese_mfa
	mfa model download dictionary portuguese_brazil_mfa
	mfa model download dictionary portuguese_portugal_mfa
	
	mfa model download acoustic english_mfa
	mfa model download dictionary english_mfa
	mfa model download dictionary english_us_mfa
	mfa model download dictionary english_uk_mfa
	mfa model download dictionary english_india_mfa
	
	mfa model list acoustic
	mfa model list dictionary
	
	mfa align --clean C:\Praat portuguese_brazil_mfa portuguese_mfa C:\Praat
	
Nota: para execução dos comandos mfa é preciso estar com o ambiente do conda "aligner" ativado.
--------------------------------
Para assistir um vídeo demo do SAFE, clique aqui: https://www.dropbox.com/scl/fo/kilbnwc0v56rcw3iwzemj/AGq2RHHxuNX7_vWV4jAhAQQ?rlkey=jb86p3451lirovh603s0k9u2q&dl=0
--------------------------------
================================
