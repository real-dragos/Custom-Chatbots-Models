import sqlite3
import pandas as pd
import constants


def createTrainingFiles(data, filename, parentColumn, childColumn):
    with open("{}.from".format(filename),'a', encoding ='utf8') as fromFile:
        with open("{}.to".format(filename),'a', encoding ='utf8') as toFile:
            for i in range(len(data)):
                parent = data[parentColumn].values[i]
                child = data[childColumn].values[i]
                if parent is not None and child is not None:
                    fromFile.write(str(parent).strip() + '\n')
                    toFile.write(str(child).strip() + '\n')

def prepareData():
    timeframes =  ['2015-01']
    for timeframe in timeframes:
        connection = sqlite3.connect('{}.db'.format(constants.DATABASE_NAME + timeframe))
        cursor = connection.cursor()
        limit = constants.RETRIEVAL_SIZE
        lastUnix = 0
        currentLength = limit
        counter = 0
        testDone = False
        while currentLength == limit:
            data = pd.read_sql("SELECT * FROM messages where unixTime > {} ORDER BY unixTime ASC LIMIT {}".format(lastUnix, limit), connection)
            lastUnix = data.tail(1)['unixTime'].values[0]
            currentLength = len(data)
            
            if not testDone:
                createTrainingFiles(data, 'test', 'parent', 'content')
                testDone = True
            else:
                createTrainingFiles(data, 'training', 'parent', 'content')
            
            counter += 1
            if counter % 10 == 0:
                print(counter*limit,' rows processed so far')
            
if __name__ == "__main__":
    # prepareData()