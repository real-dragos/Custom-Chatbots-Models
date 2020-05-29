from datetime import datetime
import pathlib
import sqlite3
import json
import os
import constants



timeframe = '2015-01'
scriptPath = os.path.dirname(__file__)

sqlTransaction = []
connection = sqlite3.connect('{}.db'.format(constants.DATABASE_NAME + timeframe))
cursor = connection.cursor()

# create the table were we store the valuable and processed data
def createTable():
    cursor.execute("""CREATE TABLE IF NOT EXISTS messages
                   (parentId TEXT PRIMARY KEY,
                    id TEXT UNIQUE,
                    parent TEXT,
                    content TEXT,
                    topic TEXT,
                    unixTime INT,
                    score INT
                   )""")


# replace the new lines with the word new_line so it can be tokenized
# also replace the double quotes with single quotes to normalize the data
def formatContent(rawContent):
    content = rawContent.replace("\n", constants.NEW_LINE).replace(
        "\r", constants.NEW_LINE).replace("\t", constants.NEW_LINE).replace('"', "'")
    return content

# find the parent of the current message and return it if it exists, False otherwise
def getParentContent(pid):
    try:
        sql = """SELECT content FROM messages WHERE id = '{}'""".format(
            pid)
        cursor.execute(sql)
        result = cursor.fetchone()
        if result != None:
            return result[0]
        return None
    except Exception as e:
        print("Parent doesn't exist", e)
        return None
 
 # get a record based on the provided parent ID   
def getRecord(pid):
    try:
        sql = """SELECT * FROM messages WHERE parentId = '{}'""".format(
            pid);
        cursor.execute(sql)
        result = cursor.fetchone()
        if result != None:
            return {
                "parentId": result[0],
                "id": result[1],
                "parent": result[2],
                "content": result[3],
                "topic": result[4],
                "unixTime": result[5],
                "score": result[6]
            }
        return None
    except Exception as e:
        print("Item not found", e)
        return None

#  validate the content based on the rules below
def isContentValid(content):
    if len(content.split(' ')) > constants.MAXIMUM_NUMBER_OF_WORDS or len(content) < 1:
        return False
    elif content == '[deleted]' or content == '[removed]':
        return False
    elif len(content) > constants.MAXIMUM_NUMBER_OF_CHARS:
        return False
    else:
        return True

def transactionBuilder(sql):
    global sqlTransaction
    sqlTransaction.append(sql)
    if len(sqlTransaction) > constants.TRANSACTION_SIZE:
        cursor.execute('BEGIN TRANSACTION')
        for query in sqlTransaction:
            try:
                cursor.execute(query)
            except:
                pass
        connection.commit()
        sqlTransaction = []

# updates the data having the specified parentID
def updateRecord(parentId, id, parentData, content, topic, createdUtc, score):
    try:
        sql = """UPDATE messages SET parentId = '{}', id = '{}', parent = '{}', content = '{}', topic = '{}', unixTime = {}, score = {} WHERE parentId = '{}'""".format(parentId, id, parentData, content, topic, createdUtc, score, parentId)
        transactionBuilder(sql)
    except Exception as e:
        print('Error updating item', e)

# adds a new item to the database
def addNewRecord(parentId, id, parentData, content, topic, createdUtc, score):
    try:
        if parentData is None:
            sql = """INSERT INTO messages (parentId, id, parent, content, topic, unixTime, score) VALUES ('{}','{}', NULL,'{}','{}',{},{})""".format(parentId, id, content, topic, createdUtc, score)
        else:
            sql = """INSERT INTO messages (parentId, id, parent, content, topic, unixTime, score) VALUES ('{}','{}','{}','{}','{}',{},{})""".format(parentId, id, parentData, content, topic, createdUtc, score)
        transactionBuilder(sql)
    except Exception as e:
        print('Error adding item', e)

def cleanDatabase():
    try:
        sql = """DELETE FROM messages WHERE parent IS NULL OR parent = 'None'"""
        cursor.execute(sql);
        connection.commit()
    except Exception as e:
        print("error deleting rows", e)

# process the raw data and validates it
def processRawData():
    counter = 0
    pairedRows = 0

    with open(f"{scriptPath}/RC_{timeframe}", buffering=constants.BUFFER_SIZE) as dataSet:
        for record in dataSet:
            counter += 1
            recordJson = json.loads(record)
            id = recordJson['name']
            parentId = recordJson['parent_id']
            # the message has to be processed in advance for tokenization
            content = formatContent(recordJson['body'])
            createdUtc = recordJson['created_utc']
            score = recordJson['score']
            topic = recordJson['subreddit']
            parentData = getParentContent(parentId)

            if score >= constants.MINIMUM_ACCEPTED_SCORE and isContentValid(content):
                existingItem = getRecord(parentId)
                if existingItem is not None:
                    if score > existingItem['score']:
                        updateRecord(parentId, id, parentData, content, topic, createdUtc, score)
                else:
                    if parentData is not None:
                        pairedRows += 1
                    addNewRecord(parentId, id, parentData, content, topic, createdUtc, score)
            
            if counter % 100000 == 0:
                print("Total rows read: {}, Paired rows: {}, Time: {}".format(counter, pairedRows, str(datetime.now())))
                           
if __name__ == "__main__":
    # createTable()
    # processRawData()
    cleanDatabase()
