def uploadFile(userID, filePath):
    if userAuthentication(userID) == True:
        fileID = saveFile(filePath)
        if fileID:
            return 'success:' + filePath
    return 'failed'

def deleteFile(userID, filePath):
    if userAuthentication(userID) == True:
        if deleteFile(filePath):
            return 'deleted:' + filePath


def textExtraction(userID, filePath):
    if userAuthentication(userID):
        # textData = performTextExtraction(fileID)
        with open(filePath, 'r') as file:
            return file.readlines()
    return 'failed'

def performNlpAnalysis(userID, filePath):
    if userAuthentication(userID):
        text = textExtraction(filePath)
        if textExtraction(filePath):
            sentimentText = text.sentiment
            if sentimentText > 0:
                return 'Positive'
            elif sentimentText < 0:
                return 'Negative'
            else:
                return 'Neutral'    
    return 'failed'

def userAuthentication(userID):
    return True

def saveFile(filePath):
    return True

def deleteFile(filePath):
    return True

