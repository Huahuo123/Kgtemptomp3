# -*- coding: utf-8 -*-
#!/usr/bin/env python3

"""Main module."""
import os
import os.path
import json

# KgtempFile class
class KgtempFile:
    def _init_(self,singName,singerName):
        self.singName = singName
        self.singerName = singerName

# files path
while True:
    path = input("请输入酷狗缓存文件路径：")
    lrcPath = input("请输入酷狗歌词缓存文件路径：")
    # check input path is a dir or not
    if (os.path.isdir(path) & os.path.isdir(lrcPath)):
        break
    else:
        print("输入的路径有错误，请重新输入！")
        continue

# file list
fileList = []
fileName = []
fileHash = []

# file info dict
fileInfo = {}

# get fileList fun
def getFileList(path,fileList):
    fileNameList = os.listdir(path)
    try:
        for temp in fileNameList:
            pathTemp = os.path.join(path,temp)
            if True == os.path.isdir(pathTemp):
                getFileList(pathTemp,fileList)
            elif pathTemp[pathTemp.rfind('.') + 1:] == "kgtemp":
                fileList.append(pathTemp)
    except PermissionError:
        pass
               
# get fileName fun
def getFileName(lrcPath,fileName,fileHash):
    tempVal = []
    singNameList = os.listdir(lrcPath)
    # 文件名和时间
    fileTime = []
    time = 0
    # 文件按时间降序排列
    for i in singNameList:
        time = os.stat(lrcPath + "\\" + i).st_mtime
        tup = (i,time)
        fileTime.append(tup)
    # 排序
    fileTime.sort(key = lambda x:x[1],reverse = True)
    # 重新赋值
    singNameList = []
    for i in fileTime:
        singNameList.append(i[0])
    # 处理歌词文件名操作
    try:
        for lrcTemp in singNameList:
            singPath = os.path.join(lrcPath,lrcTemp)
            if os.path.splitext(singPath)[1] == ".krc":
                #处理文件名和哈希值
                tempVal = lrcTemp.split("-",3)
                fileName.append(tempVal[0] + "-" + tempVal[1])
                fileHash.append(tempVal[2])
    except PermissionError:
        pass
             
# get fileLists
getFileList(path,fileList)
getFileName(lrcPath,fileName,fileHash)

# 保存歌曲数量
fileInfo.update({"singsNumber":str(len(fileHash))})

# singJson文件存放位置
jsonPath = lrcPath + "\\singJson.json"

# 更新singJson文件操作
jsonOldDict = {}
if True == os.path.exists(jsonPath):
    #如果存在则加载json文件为字典    
    with open(jsonPath,"r") as f:
        jsonOldDict = json.load(f)
    if int(jsonOldDict["singsNumber"]) == len(fileHash):
        print("歌词文件无需更新！")
    else:
        # 更新歌词记录
        for i in range (0,len(fileHash) - int(jsonOldDict["singsNumber"])):
            jsonOldDict.update({fileHash[i]:fileName[i]})
        # 更新singJson文件
        singJsonNew = json.dumps(jsonOldDict,ensure_ascii = False)
        # 删除旧singJson文件
        os.remove(jsonPath)
        # 写入新singJson文件
        with open(jsonPath,"w") as f:
            f.write(singJsonNew)
else:
    # deal with sings info 
    for i in range (0,len(fileHash)):
        fileInfo.update({fileHash[i]:fileName[i]})    
    # json save sings info
    singJson = json.dumps(fileInfo,ensure_ascii = False)
    with open(jsonPath,"w") as f:
        f.write(singJson)
        
# tips
print("正在解密中.........")

# decrypt and save
keyHex = [0xAC,0xEC,0xDF,0x57]

# 需要解密文件hash
hashTemp = []
strTemp = []
for i in fileList:
    strTemp = i.split(".",1)
    strTemp = strTemp[0].split("\\",3)
    hashTemp.append(strTemp[3])

# 解密操作
for i in range (0,len(fileList)):
    mp3Out = open((path + "\\" + jsonOldDict[hashTemp[i]] + ".mp3"),"wb")
    file = open(fileList[i],"rb")
    fileB = open(fileList[i],"rb")
    fileB.read()
    sum = fileB.tell()
    fileB.close()
    print("第" + str(i) + "个文件大小：" + '%.0f'%(sum/1024)  + "KB")
    # start reading kgtemp file from 1024 bytes
    file.seek(1024,1)
    while file.tell() != sum:
        tempByte = file.read(4)
        length = 0
        fileBytes = bytearray(tempByte)
        while length < len(fileBytes):
            key = keyHex[length]
            keyHigh = key >> 4
            keyLow = key & 0xF
            buf = fileBytes[length]
            bufHigh = buf >> 4
            bufLow = buf & 0xF
            resLow = bufLow ^ keyLow
            resHigh = bufHigh ^ keyHigh ^ resLow & 0xF
            fileBytes[length] = resHigh << 4 | resLow
            length = length + 1
        mp3Out.write(fileBytes)
    mp3Out.close()
    file.close()
    print("第" + str(i) + "个已完成")
# tips
print("全部完成！")
