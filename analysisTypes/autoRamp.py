import statistics

def autoRamp(analysis, rsRobotMatchData, rsRobotL2MatchData, rsRobotPitData):
    # Initialize the rsCEA record set and define variables specific to this function which lie outside the for loop
    rsCEA = {}
    rsCEA['analysisTypeID'] = 4
    numberOfMatchesPlayed = 0
    autoRampList = []

    for matchResults in rsRobotMatchData:
        rsCEA['team'] = matchResults[analysis.columns.index('team')]
        rsCEA['eventID'] = matchResults[analysis.columns.index('eventID')]
        preNoShow = matchResults[analysis.columns.index('preNoShow')]
        scoutingStatus = matchResults[analysis.columns.index('scoutingStatus')]
        if preNoShow == 1:
            rsCEA['M' + str(matchResults[analysis.columns.index('teamMatchNum')]) + 'D'] = 'DNS'
        elif scoutingStatus == 2:
            rsCEA['M' + str(matchResults[analysis.columns.index('teamMatchNum')]) + 'D'] = 'UR'
        else:

            autoRamp = matchResults[analysis.columns.index('autoRamp')]
            score1 = matchResults[analysis.columns.index('autoScore1')]
            score2 = matchResults[analysis.columns.index('autoScore2')]
            score3 = matchResults[analysis.columns.index('autoScore3')]
            score4 = matchResults[analysis.columns.index('autoScore4')]
            autoMB = matchResults[analysis.columns.index('autoMB')]
            
            if autoMB == 2:
                mbDisplay = "*"
            else:
                mbDisplay = ""

            numGamePieces = 0
            if score1 > 0:
                numGamePieces += 1
            if score2 > 0:
                numGamePieces += 1
            if score3 > 0:
                numGamePieces += 1
            if score4 > 0:
                numGamePieces += 1

            if autoRamp == 0: #No Attempt
                autoRampValue = 0
                autoRampDisplay = "NA"
                autoRampColor = 0 #White   
            elif autoRamp == 1: #Failed Attempt
                autoRampDisplay = "F"
                autoRampValue = 0
                autoRampColor = 1 #Black
                autoRampList.append(autoRampValue)
            elif autoRamp == 2: #Docked Not Engaged
                autoRampDisplay = "8"
                autoRampValue = 8
                autoRampColor = 3 #Yellow
                autoRampList.append(autoRampValue)
            elif autoRamp == 3: #Docked And Engaged
                autoRampDisplay = "12"
                autoRampValue = 12
                autoRampList.append(autoRampValue)
                if numGamePieces == 0:
                    autoRampColor = 4 #Green
                else: #with move bonus or piece placement
                    autoRampColor = 5 #Blue
            
            autoRampDisplay = autoRampDisplay + mbDisplay

            numberOfMatchesPlayed += 1
            rsCEA['M' + str(matchResults[analysis.columns.index('teamMatchNum')]) + 'D'] = autoRampDisplay
            rsCEA['M' + str(matchResults[analysis.columns.index('teamMatchNum')]) + 'V'] = autoRampValue
            rsCEA['M' + str(matchResults[analysis.columns.index('teamMatchNum')]) + 'F'] = autoRampColor

    if len(autoRampList) == 0:
        mean = 0
        median = 0
    else:
        mean = round(statistics.mean(autoRampList), 1)
        median = round(statistics.median(autoRampList), 1)
    rsCEA['S1V'] = mean
    rsCEA['S1D'] = str(mean)
    rsCEA['S2V'] = median
    rsCEA['S2D'] = str(median)

    return rsCEA