import psycopg2 as pg
import pandas.io.sql as psql
from datetime import datetime, timedelta
import pytz
import sys
import json
import copy
import pandas as pd
from slackclient import SlackClient
import configparser

# test 

print("Python version")
print (sys.version)
print("Version info.")
print (sys.version_info)

def getKanjiDbConnection(dbhost, dbport, dbname, dbuser, dbpass):
  conn_str = "host={0} port={1} dbname={2} user={3} password={4}".format(dbhost, dbport, dbname, dbuser, dbpass)

  try:
    conn = pg.connect(conn_str)
    #print("Welcome to Jupyter Notebook.  You are connected to the Kanji database!")
    return conn
  except pg.OperationalError:
    #print("You are not connected to the database.")
    return None

_LOG_DEBUG = 0
_LOG_INFO  = 1
_LOG_ERROR = 2

config = configparser.ConfigParser()
config.read("../analytics_secrets.ini")
_LOG_LEVEL = int(config['DEFAULT']['loglevel'])
_UTC_OFFSET = int(config['DEFAULT']['utcoffset'])

def logger(level, message):
    if level >= _LOG_LEVEL:
      print(message)

_OPEN_STATUS = 10000
_WORKING_STATUS = 10001
_UNASSIGNED_USER = 10006

#the block is constructed here from the Slack template, we replace keys as needed later
openticketmessage = "[\
   {\"type\": \"section\", \
		\"text\": { \
			\"type\": \"mrkdwn\", \
			\"text\": \"*<fakeLink.toUserProfiles.com|Iris / Zelda 1-1>*\\nTuesday, January 21 4:00-4:30pm\\nBuilding 2 - Havarti Cheese (3)\\n2 guests\" \
		}, \
		\"accessory\": { \
			\"type\": \"image\", \
			\"image_url\": \"https://api.slack.com/img/blocks/bkb_template_images/notifications.png\", \
			\"alt_text\": \"calendar thumbnail\" \
		} \
	}, \
    { \
		\"type\": \"section\", \
		\"text\": { \
			\"type\": \"mrkdwn\", \
			\"text\": \"*Accessory text.*\" \
		}, \
		\"accessory\": { \
			\"type\": \"button\", \
			\"text\": { \
				\"type\": \"plain_text\", \
				\"text\": \"BUTTON_TEXT\" \
			}, \
			\"value\": \"BUTTON_VALUE\", \
			\"action_id\": \"button\" \
		} \
	} \
]"

def slackticket(nodename, location, description, mentions, impact, urgency, locationimageurl, _SLACK_TOKEN, _SLACK_CHANNEL, ticketid, ticketts):
        timestamp = datetime.now()
        # start key replacement
        blockmessage = json.loads(openticketmessage)
        print(blockmessage[0]["accessory"]["image_url"])
        blockmessage[0]["accessory"]["image_url"] = locationimageurl
        blockmessage[0]["text"]["text"] = "*ALERT {}* at {} \
                        \n*{} {}* \
                        \nticket #{} {}".format(location, timestamp.strftime("%-I:%M %p %A, %B %e, %Y"), nodename, description, ticketid, mentions)

        blockmessage[1]["text"]["text"] = "*To work this issue, click the button...*"
        blockmessage[1]["accessory"]["text"]["text"] = "I got it!"
        blockmessage[1]["accessory"]["value"] = "accept"
        blockmessage[1]["accessory"]["action_id"] = "{0}".format(ticketid)
        # end key replacement

        sc = SlackClient(_SLACK_TOKEN)
        if ticketts==0:
          response = sc.api_call("chat.postMessage", link_names=1, channel=_SLACK_CHANNEL, blocks=blockmessage)
        else:        
          response = sc.api_call("chat.postMessage", link_names=1, channel=_SLACK_CHANNEL, ts=ticketts, blocks=blockmessage)
                
        if not 'ok' in response or not response['ok']:
          logger(_LOG_ERROR, "kanjiticketing Error posting message to Slack channel {}".format(_SLACK_CHANNEL))
          logger(_LOG_ERROR, blockmessage)
          logger(_LOG_ERROR, response)
          return 0
        else:
          logger(_LOG_INFO, "Ok posting message to Slack channel")
          logger(_LOG_DEBUG, "Message ts = {}".format(response['ts']))
          return response['ts']
    
def slackreissueticket(nodename, location, description, mentions, impact, urgency, locationimageurl, _SLACK_TOKEN, _SLACK_CHANNEL, ticketid, ticketts, status, ticketopenage, ticketopentime):
        timestamp = datetime.now()
        ticketopentime = ticketopentime + timedelta(hours = _UTC_OFFSET)
        # start key replacement
        blockmessage = json.loads(openticketmessage)
        print(blockmessage[0]["accessory"]["image_url"])
        blockmessage[0]["accessory"]["image_url"] = locationimageurl
        blockmessage[0]["text"]["text"] = "*ALERT REISSUE {}* at {} \
                        *{} {}* \
                        \nticket #{} first issued {} has been opened for {} \n{}".format(location, timestamp.strftime("%-I:%M %p %A, %B %e, %Y"), \
                                                                       nodename, description, ticketid, ticketopentime.strftime("%-I:%M %p %A, %B %e, %Y"), ticketopenage, mentions)
        if status == _OPEN_STATUS:
          blockmessage[1]["text"]["text"] = "*To work this issue, click the button...*"
          blockmessage[1]["accessory"]["text"]["text"] = "I got it!"
          blockmessage[1]["accessory"]["value"] = "accept"
        elif status == _WORKING_STATUS:
          blockmessage[1]["text"]["text"] = "*To close this issue, click the button...*"
          blockmessage[1]["accessory"]["text"]["text"] = "Issue Resolved!"
          blockmessage[1]["accessory"]["value"] = "close"
        blockmessage[1]["accessory"]["action_id"] = "{0}".format(ticketid)
        # end key replacement

        sc = SlackClient(_SLACK_TOKEN)
        response = sc.api_call("chat.update", channel=_SLACK_CHANNEL, link_names=1, ts=ticketts, text="REISSUE", blocks=blockmessage)        
                
        if not 'ok' in response or not response['ok']:
          logger(_LOG_ERROR, "kanjiticketing Error posting message to Slack channel")
          logger(_LOG_ERROR, blockmessage)
          logger(_LOG_ERROR, response)
          return 0
        else:
          logger(_LOG_INFO, "Ok posting message to Slack channel")
          logger(_LOG_DEBUG, "Message ts = {}".format(response['ts']))
          return response['ts']


def openticket(conn, nodeid, locationid, description, impact, urgency, type, ticketchannelid):
    sqlinsert = "INSERT INTO kanji_ticket (opentimestamp, lastupdatetimestamp, node_id, location_id, description, \
                 type_id, status_id, slackticketchannel_id, ackuser_id) \
                 VALUES ('{}', '{}', '{}', '{}', '{}', {}, {}, {}, {}) ".format(datetime.now(), datetime.now(), nodeid, locationid,                 description, type, _OPEN_STATUS, ticketchannelid, _UNASSIGNED_USER)
    logger(_LOG_DEBUG, sqlinsert)
    cur = conn.cursor()
    cur.execute(sqlinsert)    
    conn.commit()
    cur.execute('SELECT LASTVAL()')
    ticketid = cur.fetchone()[0]
    logger(_LOG_DEBUG, ticketid)
    return ticketid

def ticketExists(conn, nodeid, tickettype, status):    
    logger(_LOG_DEBUG, "Checking tickets for {} {} {}".format(nodeid, tickettype, status))
    statusclause = '('
    for n, stat in enumerate(status):
        statusclause += 'status_id=' + str(status[n])
        if n<len(status)-1:
          statusclause += ' OR '
    statusclause += ')'
    logger(_LOG_DEBUG, "Status clause {}".format(statusclause))
    ticketquery = "SELECT * FROM kanji_ticket WHERE node_id={} AND type_id={} AND {} ORDER BY opentimestamp DESC".format(nodeid, tickettype, statusclause)
    logger(_LOG_DEBUG, ticketquery)
    #tickets = querydb(ticketquery)
            
    df = pd.read_sql(ticketquery, conn)
    if len(df)>0:
          logger(_LOG_DEBUG, "Found a ticket.")
          return df             
    else:
        logger(_LOG_DEBUG, "No ticket found.")
        return None

def updateTicket(conn, idticket, ts):
    updatequery = "UPDATE kanji_ticket SET lastupdatetimestamp = NOW(), ticketts='{}' WHERE idticket={}".format(ts, idticket)
    logger(_LOG_DEBUG, updatequery)
    cur = conn.cursor()
    cur.execute(updatequery)    
    conn.commit()
    
def updateTicketStatus(conn, idticket, status):
    updatequery = "UPDATE kanji_ticket SET status_id={} WHERE idticket={}".format(status, idticket)
    logger(_LOG_DEBUG, updatequery)
    cur = conn.cursor()
    cur.execute(updatequery)    
    conn.commit()


