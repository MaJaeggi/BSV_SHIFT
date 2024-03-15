import numpy as np

def poissonpredict(df, gamedate, historylength, cutoff=-1):
    # set the amount of simulations to run on each game
    simulatedgames = 100000

    # only use games before the date we want to predict
    historical = df.loc[df["date"] < gamedate]

    # make sure we only use games that have valid scores
    historical = historical.loc[df["homeScore"] > -1]

    # limit historical data to set length
    historical = historical.tail(historylength)

    # games to predict
    topredict = df.loc[df["date"] == gamedate]

    # get average home and away scores for entire competition
    homeAvg = historical["homeScore"].mean()
    awayAvg = historical["awayScore"].mean()

    # loop through the games we want to predict
    for i in topredict.index:
        ht = topredict.ix[i, "homeTeam"]
        at = topredict.ix[i, "awayTeam"]

        # get average goals scored and conceded for home team
        homeTeamHomeAvgFor = historical.loc[df["homeTeam"] == ht, "homeScore"].mean()
        homeTeamHomeAvgAgainst = historical.loc[df["homeTeam"] == ht, "awayScore"].mean()

        # divide averages for team by averages for competition to get attack and defence strengths
        homeTeamAttackStrength = homeTeamHomeAvgFor / homeAvg
        homeTeamDefenceStrength = homeTeamHomeAvgAgainst / awayAvg

        # repeat for away team
        awayTeamAwayAvgFor = historical.loc[df["awayTeam"] == at, "awayScore"].mean()
        awayTeamAwayAvgAgainst = historical.loc[df["awayTeam"] == at, "homeScore"].mean()
        awayTeamAttackStrength = awayTeamAwayAvgFor / awayAvg
        awayTeamDefenceStrength = awayTeamAwayAvgAgainst / homeAvg

        # calculated expected goals using attackstrength * defencestrength * average
        homeTeamExpectedGoals = homeTeamAttackStrength * awayTeamDefenceStrength * homeAvg
        awayTeamExpectedGoals = awayTeamAttackStrength * homeTeamDefenceStrength * awayAvg

        # use numpy's poisson distribution to simulate 100000 games between the two teams
        homeTeamPoisson = np.random.poisson(homeTeamExpectedGoals, simulatedgames)
        awayTeamPoisson = np.random.poisson(awayTeamExpectedGoals, simulatedgames)

        # we can now infer some predictions from our simulated games
        # using numpy to count the results and converting to percentage probability
        homeTeamWins = np.sum(homeTeamPoisson > awayTeamPoisson) / simulatedgames * 100
        draws = np.sum(homeTeamPoisson == awayTeamPoisson) / simulatedgames * 100
        awayTeamWins = np.sum(homeTeamPoisson < awayTeamPoisson) / simulatedgames * 100
        totalGoals = np.mean(homeTeamPoisson + awayTeamPoisson)
        threeOrMoreGoals = np.sum((homeTeamPoisson + awayTeamPoisson) > 2) / simulatedgames * 100
        bothTeamsToScore = np.sum((homeTeamPoisson > 0) & (awayTeamPoisson > 0)) / simulatedgames * 100

        # store our prediction into the dataframe
        df.ix[i, "homeWin"] = homeTeamWins
        df.ix[i, "draw"] = draws
        df.ix[i, "awayWin"] = awayTeamWins
        df.ix[i, "totalGoals"] = totalGoals
        df.ix[i, "threeOrMoreGoals"] = threeOrMoreGoals
        df.ix[i, "bothTeamsToScore"] = bothTeamsToScore

        # if probability exceeds our cutoff, print out the game and the expected result
        if (draws > cutoff or homeTeamWins > cutoff or awayTeamWins > cutoff) and cutoff > 0:
            if draws > cutoff:
                result = "Draw"
                probability = draws
                odds = 100 / draws
            elif homeTeamWins > cutoff:
                result = ht + " Win"
                probability = homeTeamWins
                odds = 100 / homeTeamWins
            elif awayTeamWins > cutoff:
                result = at + " Win"
                probability = awayTeamWins
                odds = 100 / awayTeamWins
            print("{0} v {1} : Prediction:{2}, Probability:{3:.2f}, Odds:{4:.2f}".format(ht, at, result, probability,
                                                                                         odds))

    return df
