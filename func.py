""" 
    BIBLIOTECA PARA SIMPLIFICAR A EXTRAÇÃO DE QUESTÃO DO PDF DO GRUPO
    EXATAS.

    AUTOR: NELSON PIRES (MANDELA)
    DATA: 05/2019
    VERSÃO: 1.0
"""

#######################################################################
###################  MODULES AND PACKAGES   ###########################
#######################################################################
import glob, os, re, json, io


#######################################################################
##########################  CLASSES   #################################
#######################################################################

class extra:

    """ FUNÇÕES EXTRAS """

    def orgLista(lista):

        """
            FUNCAO:
            ----------
                Organizar uma lista de strings alphanumérica levando em
                consideracao a ordem dos numeros nela presente.

            Parametros
            ----------
                lista : Lista
                    Lista que deseja que seja organizada.
                
            Retorno
            ----------
                lista : Lista
                    Lista da entrada organizada.
        """

        convert = lambda text: int(text) if text.isdigit() else text
        alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
        return sorted(lista, key = alphanum_key)

    def proximoNumero(bd, materia, assunto, name):

        """
            FUNCAO:
            ----------
                Achar qual sera o proximo numero de uma questao na
                pasta do banco de dados informada.

            Parametros
            ----------
                bd : String
                    Endereço do banco de dados.
                
                materia : String
                    Nome da materia da lista para procurar uma pasta.
                
                assunto : String
                    Nome do assunto da lista para procurar uma pasta.

                name : String
                    Sigla do vestibular para procurar o nome.

            Retorno
            ----------
                proxNum : Int
                    Proximo numero que uma questao podera ser salva.
        """
        
        last = None
        try:
            for f in extra.orgLista(glob.glob(bd+"/"+materia+"/"+assunto+"/"+name+"_*")):
                last = os.path.basename(f)
        except Exception as e:
            print(e)
        if (last is None):
            proxNum = 1
        else:
            num = re.split('(\d{1,})', last)
            proxNum = int(num[1])
            proxNum = proxNum + 1
        
        return proxNum

    def escreveJSON(bd, materia, assunto, name, ano=None, enunciado=None, alternativas=None, gabarito=None, imagem=None):

        """
            FUNCAO:
            ----------
                Escrever o arquivo JSON.

            Parametros
            ----------
                bd : String
                    Endereço do banco de dados.
                
                materia : String
                    Nome da materia da lista para procurar uma pasta.
                
                assunto : String
                    Nome do assunto da lista para procurar uma pasta.

                name : String
                    Sigla do vestibular para procurar o nome acrescido
                    do _num que representa o numero da questao.
                
                ano : Int
                    Representa o ano da questao.
                
                enunciado: String
                    Corresponde ao texto e pergunta da questao.
                
                alternativas: String
                    Corresponde as alternativas caso existam.
                
                gabarito : Caractere ou String
                    Caractere que corresponde a alternativa que da
                    resposta.
                
                imagem : Int
                    Inteiro que corresponde quantas imagens/tabelas 
                    foram encontradas na imagem. Como o nome segue um
                    padrao entao apenas o nome da questao ja eh 
                    suficiente para determinar qual sera o nome das
                    imagens e assim adicionar elas ao JSON.
                
            Retorno
            ----------
                Nenhum
        """
        print("ESCREVENDO ARQUIVO JSON DO ARQUIVO: ", name)
        nome_final = (
                                bd + "/" +
                                materia + "/" +
                                assunto + "/" +
                                name +".JSON")
        
        enunciado = re.sub('(\\n)', " ", enunciado)
        alternativas = re.sub('(\\n)', " ", alternativas)

        data = {}
        try:
            data['ano'] = ano
            data['enunciado'] = enunciado
            data['alternativas'] = alternativas
            data['gabarito'] = gabarito
            data['acertos'] = 0
            data ['erros'] = 0
            data['ranking'] = ""
            if imagem == 0:
                data['imagem'] = ""
            else:
                imagens = ""
                i = 0
                for i in range(imagem):
                    imagens = imagens + name + "_" + str(i+1) + ";"
                data['imagem'] = imagens
        
        except Exception as e:
            print(e)

        with io.open(nome_final, 'w', encoding='utf8') as outfile:
            json.dump(data, outfile, sort_keys=True, indent=2, ensure_ascii=False)
            