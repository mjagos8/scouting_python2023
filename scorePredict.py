import mysql.connector
import sys
import argparse
import configparser
import statbotics

sb = statbotics.Statbotics()

# parser to choose the database where the table will be written
parser = argparse.ArgumentParser()
parser.add_argument("-db", "--database", help = "Choices: dev1, dev2, testing, production", required=True)
parser.add_argument("-host", "--host", help = "Host choices: aws, localhost", required=True)
parser.add_argument("-sb", "--statbotics", help = "Use data from statbotics: true, false", required=True)
args = parser.parse_args()
input_db = args.database
input_host = args.host
input_sb = args.statbotics

config = configparser.ConfigParser()
config.read('helpers/config.ini')

host = config[input_host+"-"+input_db]['host']
user = config[input_host+"-"+input_db]['user']
passwd = config[input_host+"-"+input_db]['passwd']
database = config[input_host+"-"+input_db]['database']

conn = mysql.connector.connect(user=user, passwd=passwd, host=host, database=database)
cursor = conn.cursor()

query = "SELECT eventID, BAeventID FROM events WHERE currentEvent = 1"
cursor.execute(query)
eventData = cursor.fetchall()
eventID = eventData[0][0]
BAeventID = eventData[0][1]

query =f"select matchID, red1, red2, red3, blue1, blue2, blue3, matchNum from matches where eventID = {eventID} and actualTime is null"
cursor.execute(query)
futureMatches = cursor.fetchall()
print('please be patient - statbotics API is not the fastest')
for item in futureMatches:
    matchID = item[0]
    matchNum = item[7]
#     print(f"MatchID = {matchID}, MatchNum = {matchNum}, RED: {match[1]}, {match[2]}, {match[3]} BLUE: {match[4]}, {match[5]}, {match[6]} ")
    
    if input_sb == 'true':
        # get data from statbotic
        BAmatchID = f"{BAeventID}_qm{matchNum}"
        statboticMatchData=sb.get_match(BAmatchID)
        SBredScorePred = round(statboticMatchData['red_epa_sum'], 0)
        SBredAutoScorePred = round(statboticMatchData['red_auto_epa_sum'], 0)
        SBredTeleScorePred = round(statboticMatchData['red_teleop_epa_sum'], 0)
        SBredEndgameScorePred = round(statboticMatchData['red_endgame_epa_sum'], 0)
        SBblueScorePred = round(statboticMatchData['blue_epa_sum'], 0)
        SBblueAutoScorePred = round(statboticMatchData['blue_auto_epa_sum'], 0)
        SBblueTeleScorePred = round(statboticMatchData['blue_teleop_epa_sum'], 0)
        SBblueEndgameScorePred = round(statboticMatchData['blue_endgame_epa_sum'], 0)
        SBwinner = statboticMatchData['epa_winner']
        SBredWinProb = statboticMatchData['epa_win_prob']
        SBblueWinProb = 1 - SBredWinProb
        SBredWinProb = (100 * SBredWinProb)
        SBblueWinProb = (100 * SBblueWinProb)

    # get red alliance data from CEanalysisGraphs
    query = f"SELECT team, autoScoreMean, autoRampMean, teleLowMean, teleMidMean, teleHighMean, rampMean FROM CEanalysisGraphs " \
            f"WHERE team IN ('{item[1]}', '{item[2]}', '{item[3]}') and eventID = {eventID}"
    cursor.execute(query)
    redAllianceData = cursor.fetchall()
    red1AutoPts, red2AutoPts, red3AutoPts = [t[1] for t in redAllianceData]
    red1AutoRampPts, red2AutoRampPts, red3AutoRampPts = [t[2] for t in redAllianceData]
    red1TeleLowPieces, red2TeleLowPieces, red3TeleLowPieces = [t[3] for t in redAllianceData]
    red1TeleMidPieces, red2TeleMidPieces, red3TeleMidPieces = [t[4] for t in redAllianceData]
    red1TeleHighPieces, red2TeleHighPieces, red3TeleHighPieces = [t[5] for t in redAllianceData]
    red1EndgamePts, red2EndgamePts, red3EndgamePts = [t[6] for t in redAllianceData]
    
     # get blue alliance data from CEanalysisGraphs
    query = f"SELECT team, autoScoreMean, teleScoreMean, rampMean, autoRampMean FROM CEanalysisGraphs " \
            f"WHERE team IN ('{item[4]}', '{item[5]}', '{item[6]}') and eventID = {eventID}"
    cursor.execute(query)
    blueAllianceData = cursor.fetchall()
    blue1AutoPts, blue2AutoPts, blue3AutoPts = [t[1] for t in blueAllianceData]
    blue1AutoRampPts, blue2AutoRampPts, blue3AutoRampPts = [t[2] for t in blueAllianceData]
    blue1TeleLowPieces, blue2TeleLowPieces, blue3TeleLowPieces = [t[3] for t in blueAllianceData]
    blue1TeleMidPieces, blue2TeleMidPieces, blue3TeleMidPieces = [t[4] for t in blueAllianceData]
    blue1TeleHighPieces, blue2TeleHighPieces, blue3TeleHighPieces = [t[5] for t in blueAllianceData]
    blue1EndgamePts, blue2EndgamePts, blue3EndgamePts = [t[6] for t in blueAllianceData]

    # calculate # of game pieces that can be scored
    redTotalAuto = red1AutoPts + red2AutoPts + red3AutoPts
    redTeleLowPieces = red1TeleLowPieces + red2TeleLowPieces + red3TeleLowPieces
    redTeleMidPieces = red1TeleMidPieces + red2TeleMidPieces + red3TeleMidPieces
    redTeleHighPieces = red1TeleHighPieces + red2TeleHighPieces + red3TeleHighPieces
    if redTeleHighPieces > 9:
        redHighRemainder = 9 - redTeleHighPieces
    if redTeleMidPieces > 9:
        redMidRemainder = 9 - redTeleMidPieces
    if redTeleLowPieces > 9:
        redLowRemainder = 9 - redTeleLowPieces
    totalRemainder = redHighRemainder + redMidRemainder + redLowRemainder
    if totalRemainder < 27:





    redTotalEndgame = round((red1EndgamePts + red2EndgamePts + red3EndgamePts), 0)
    if (red1AutoRampPts > 8 or red2AutoRampPts > 8 or red3AutoRampPts > 8):
        redPredAutoPts = 12
    elif (red1AutoRampPts > 4 or red2AutoRampPts > 4 or red3AutoRampPts > 4):
        redPredAutoPts = 8
    else:
        redPredAutoPts = 0
    redTotalAuto = round((redTotalAuto + redPredAutoPts), 0)
    redTotalPts = round((redTotalAuto + redTotalTele + redTotalEndgame), 0)

    if (blue1AutoPts is not None) and (blue2AutoPts is not None) and (blue3AutoPts is not None):
        blueTotalAuto = blue1AutoPts + blue2AutoPts + blue3AutoPts
    else:
        blueTotalAuto = 0
        print('i am blue auto here')
    if (blue1TelePts is not None) and (blue2TelePts is not None) and (blue3TelePts is not None):
        blueTotalTele = round((blue1TelePts + blue2TelePts + blue3TelePts), 0)
    else:
        blueTotalTele = 0
        print('i am here blue tele')
    if (blue1EndgamePts is not None) and (blue2EndgamePts is not None) and (blue3EndgamePts is not None):
        blueTotalEndgame = round((blue1EndgamePts + blue2EndgamePts + blue3EndgamePts), 0)
    else:
        blueTotalEndgame = 0
    if (blue1AutoRampPts > 8 or blue2AutoRampPts > 8 or blue3AutoRampPts > 8):
        bluePredAutoPts = 12
    elif (blue1AutoRampPts > 4 or blue2AutoRampPts > 4 or blue3AutoRampPts > 4):
        bluePredAutoPts = 8
    else:
        bluePredAutoPts = 0
    blueTotalAuto = round((blueTotalAuto + bluePredAutoPts), 0)
    blueTotalPts = round((blueTotalAuto + blueTotalTele + blueTotalEndgame), 0)

    if input_sb == 'true':
        updateQuery = f"UPDATE matches SET redPredScore = {redTotalPts}, " \
            f"bluePredScore = {blueTotalPts}, " \
            f"redPredAuto = {redTotalAuto}, " \
            f"bluePredAuto = {blueTotalAuto}, " \
            f"redPredTele = {redTotalTele}, " \
            f"bluePredTele = {blueTotalTele}, " \
            f"redPredEndgame = {redTotalEndgame}, " \
            f"bluePredEndgame = {blueTotalEndgame}, " \
            f"SBredPredScore = {SBredScorePred}, " \
            f"SBbluePredScore = {SBblueScorePred}, " \
            f"SBredPredAuto = {SBredAutoScorePred}, " \
            f"SBbluePredAuto = {SBblueAutoScorePred}, " \
            f"SBredPredTele = {SBredTeleScorePred}, " \
            f"SBbluePredTele = {SBblueTeleScorePred}, " \
            f"SBredPredEndgame = {SBredEndgameScorePred}, " \
            f"SBbluePredEndgame = {SBblueEndgameScorePred}, " \
            f"SBredWinProb = {int(SBredWinProb)}, " \
            f"SBblueWinProb = {int(SBblueWinProb)} " \
            f"WHERE matchID = {matchID}"
    else:
        updateQuery = f"UPDATE matches SET redPredScore = {redTotalPts}, " \
            f"bluePredScore = {blueTotalPts}, " \
            f"redPredAuto = {redTotalAuto}, " \
            f"bluePredAuto = {blueTotalAuto}, " \
            f"redPredTele = {redTotalTele}, " \
            f"bluePredTele = {blueTotalTele}, " \
            f"redPredEndgame = {redTotalEndgame}, " \
            f"bluePredEndgame = {blueTotalEndgame}, " \
            f"WHERE matchID = {matchID}"
    cursor.execute(updateQuery)
    conn.commit()

cursor.close()
conn.close()




# auto_dist = np.random.normal(loc=auto_avg, scale=auto_std, size=n_iter)
# tele_dist = np.random.normal(loc=tele_avg, scale=tele_std, size=n_iter)
# end_dist = np.random.normal(loc=end_avg, scale=end_std, size=n_iter)

# sums = auto_dist + tele_dist + end_dist
# mean = np.mean(sums)
# std_dev = np.std(sums)