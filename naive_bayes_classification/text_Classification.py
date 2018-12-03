import collections
import math
import sys
import random

def shuffle(inFile):
    '''
        简单的乱序操作，用于生成训练集和测试集
    '''
    textLines = [line.strip() for line in open(inFile)]
    print("正在准备训练和测试数据，请稍后...")
    random.shuffle(textLines)  # 将textLines随机排列
    num = len(textLines)
    trainText = textLines[:int(3*num/5)]  # 取前3/5做训练集
    testText = textLines[int(3*num/5):]  # 取后2/5做测试集
    print("准备训练和测试数据准备完毕，下一步...")
    return trainText, testText

# 总共10中类别，给每一类一个编号
labels = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
def label2id(label):
    for i in range(len(labels)):
        if label == labels[i]:
            return i
    raise Exception('Error label %s' % (label))


def doc_dict():
    # 构造和类别数等长的0向量,返回一个长度为len(labels),每个元素的初始值都为0的list
    return [0] * len(labels)


def mutual_info(N, Nij, Ni_, N_j):
    # 计算互信息
    return Nij * 1.0 / N * math.log(N * (Nij+1) * 1.0/(Ni_*N_j))/math.log(2)

# 遍历文件，统计每个词在每个类别出现的次数，和每类的文档数，并写入特征文件
def count_for_cates(trainText, featureFile):
    # 初始化一个长度为10，每个元素的初始值都是0的list
    docCount = [0] * len(labels)
    wordCount = collections.defaultdict(doc_dict)
    # 扫描文件和计数
    for line in trainText:
        label, text = line.strip().split(' ', 1)  # 返回的是两个list
        index = label2id(label[0])
        words = text.split(' ')
        for word in words:
            wordCount[word][index] += 1
            docCount[index] += 1
    # 计算互信息值
    print("计算互信息，提取特征词中，请稍后...")
    miDict = collections.defaultdict(doc_dict)
    # 总共的文档数
    N = sum(docCount)
    for k, vs in wordCount.items():
        for i in range(len(vs)):
            N11 = vs[i]
            N10 = sum(vs) - N11
            N01 = docCount[i] - N11
            N00 = N - N11 - N10 - N01
            mi = mutual_info(N, N11, N10+N11, N01+N11) + mutual_info(N, N10, N10+N11, N00+N10) + mutual_info(N, N01, N01+N11, N01+N00) + mutual_info(N, N00, N00 + N10, N00 + N01)
            miDict[k][i] = mi
    fWords = set()
    for i in range(len(docCount)):
        keyf = lambda x:x[1][i]
        sortedDict = sorted(miDict.items(), key=keyf, reverse=True)
        for j in range(100):
            fWords.add(sortedDict[j][0])
    out = open(featureFile, 'w')
    # 输出各个类的文档数
    out.write(str(docCount)+"\n")
    # 输出互信息最高的词作为特征词
    for fword in fWords:
        out.write(fword+"\n")
    print("特征词写入完毕...")
    out.close()


def load_feature_words(featureFile):
    '''
        从特征文件导入特征词
    '''
    f = open(featureFile)
    #各个类的文档数目
    docCounts = eval(f.readline())
    features = set()
    #读取特征词
    for line in f:
        features.add(line.strip())
    f.close()
    return docCounts, features


def train_bayes(featureFile, textFile, modelFile):
    '''
        训练贝叶斯模型，实际上计算每个类中特征词的出现次数
    '''
    print("使用朴素贝叶斯训练中...")
    docCounts, features = load_feature_words(featureFile)
    wordCount = collections.defaultdict(doc_dict)
    # 每类文档特征词出现的次数
    tCount = [0]*len(docCounts)
    for line in textFile:
        lable,text = line.strip().split(' ', 1)
        index = label2id(lable[0])
        words = text.split(' ')
        for word in words:
            if word in features:
                tCount[index] += 1
                wordCount[word][index] += 1
    outModel = open(modelFile, 'w')
    #拉普拉斯平滑
    print("训练完毕，写入模型...")
    for k, v in wordCount.items():
        scores = [(v[i]+1) * 1.0 / (tCount[i]+len(wordCount)) for i in range(len(v))]
        outModel.write(k+"\t"+str(scores)+"\n")
    outModel.close()


def load_model(modelFile):
    '''
        从模型文件中导入计算好的贝叶斯模型
    '''
    print ("加载模型中...")
    f = open(modelFile)
    scores = {}
    for line in f:
        word, counts = line.strip().rsplit('\t', 1)
        scores[word] = eval(counts)
    f.close()
    return scores

def predict(featureFile, modelFile, testText):
    '''
        预测文档的类标，标准输入每一行为一个文档
    '''
    docCounts, features = load_feature_words(featureFile)
    docScores = [math.log(count * 1.0 /sum(docCounts)) for count in docCounts]
    scores = load_model(modelFile)
    rCount = 0
    docCount = 0
    print ("正在使用测试数据验证模型效果...")
    for line in testText:
        lable,text = line.strip().split(' ', 1)
        index = label2id(lable[0])
        words = text.split(' ')
        preValues = list(docScores)
        for word in words:
            if word in features:
                for i in range(len(preValues)):
                    preValues[i]+=math.log(scores[word][i])
        m = max(preValues)
        pIndex = preValues.index(m)
        if pIndex == index:
            rCount += 1
        #print lable,lables[pIndex],text
        docCount += 1
    print("总共测试文本量: %d , 预测正确的类别量: %d, 朴素贝叶斯分类器准确度:%f" %(docCount, rCount, rCount * 1.0 / docCount))


if __name__=="__main__":
    if len(sys.argv) != 4:
        print ("Usage: python text_classification.py result.txt feature_file.out model_file.out")
        sys.exit()

    inFile = sys.argv[1]
    print(inFile)
    featureFile = sys.argv[2]
    print(featureFile)
    modelFile = sys.argv[3]
    print(modelFile)

    trainText, testText = shuffle(inFile)
    count_for_cates(trainText, featureFile)
    train_bayes(featureFile, trainText, modelFile)
    predict(featureFile, modelFile, testText)