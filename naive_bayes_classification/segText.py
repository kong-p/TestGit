import jieba
import os


def readFile(path):
    with open(path, 'r', encoding='gb2312', errors='ignore') as file:
        content = file.read()
        return content


def saveFile(path, result):
    with open(path, 'w', encoding='gb2312', errors='ignore') as file:
        file.writelines(result)


def listdirInMac(path):
    os_list = os.listdir(path)
    for item in os_list:
        if item.startswith('.') and os.path.isfile(os.path.join(path, item)):
            os_list.remove(item)
    return os_list


def getStopWord(path):
    stopWordList = readFile(path).splitlines()
    return stopWordList


#  分词，去停用词，去单个字
def segText(inputpath, resultpath):
    # 返回inputpath指定的文件夹包含的文件或文件夹的名字的列表
    fatherLists = listdirInMac(inputpath)
    for eachdir in fatherLists:
        eachPath = inputpath + eachdir + "/"
        each_resultPath = resultpath + eachdir + "/"
        # 目录不存在则创建目录
        if not os.path.exists(each_resultPath):
            os.makedirs(each_resultPath)
        # 获取每个文件夹中的每个文本文件的路径
        childLists = listdirInMac(eachPath)
        for eachfile in childLists:
            eachFilePath = eachPath + eachfile
            # 获取每个文本文件的路径
            content = readFile(eachFilePath)
            # 删除多余空行与空格，strip()处理的时候，如果不带参数，默认是清除两边的空白符
            result = (str(content)).replace("\r\n", "").strip()
            cutResult = list(jieba.cut(result))
            wordList = []
            for word in cutResult:
                if(len(word) > 1):
                    if word not in stopWordList:
                        wordList.append(word)
            saveFile(each_resultPath + eachfile, " ".join(wordList))


#  合并文件
def mergeText(inputpath,resultpath):
    resultFile = open(resultpath, 'w')
    fatherLists = listdirInMac(inputpath)
    for eachdir in fatherLists:
        eachPath = inputpath + eachdir + "/"
        childLists = listdirInMac(eachPath)
        for eachfile in childLists:
            for line in readFile(eachPath + eachfile):
                line.strip('\n')
                resultFile.write(line)
            if(eachdir == "财经"):
                resultFile.write("\n" + "A" + str(os.path.splitext(eachfile)[0]) + " ")
            elif(eachdir == "电脑"):
                resultFile.write("\n" + "B" + str(os.path.splitext(eachfile)[0]) + " ")
            elif(eachdir == "房产"):
                resultFile.write("\n" + "C" + str(os.path.splitext(eachfile)[0]) + " ")
            elif(eachdir == "教育"):
                resultFile.write("\n" + "D" + str(os.path.splitext(eachfile)[0]) + " ")
            elif (eachdir == "科技"):
                resultFile.write("\n" + "E" + str(os.path.splitext(eachfile)[0]) + " ")
            elif (eachdir == "汽车"):
                resultFile.write ( "\n" + "F" + str ( os.path.splitext ( eachfile )[0] ) + " " )
            elif (eachdir == "人才"):
                resultFile.write ( "\n" + "G" + str ( os.path.splitext ( eachfile )[0] ) + " " )
            elif (eachdir == "体育"):
                resultFile.write ( "\n" + "H" + str ( os.path.splitext ( eachfile )[0] ) + " " )
            elif (eachdir == "卫生"):
                resultFile.write ( "\n" + "I" + str ( os.path.splitext ( eachfile )[0] ) + " " )
            elif (eachdir == "娱乐"):
                resultFile.write ( "\n" + "J" + str ( os.path.splitext ( eachfile )[0] ) + " " )
    resultFile.close()


if __name__=='__main__':
    stopWordList = getStopWord("/Users/kong_p/Downloads/wenbenfenlei/stopword.txt")
    segText("/Users/kong_p/Downloads/text/test_set/", "/Users/kong_p/Downloads/text/segResult/")
    mergeText("/Users/kong_p/Downloads/text/segResult/", "/Users/kong_p/Downloads/text/result.txt")