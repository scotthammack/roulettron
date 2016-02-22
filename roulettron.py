import tweepy, random

from twitter_secrets import CONSUMER_KEY, CONSUMER_SECRET, ACCESS_KEY, ACCESS_SECRET

num_chambers = 6
bot_username = 'roulettron'
player_name = 'You'	# placeholder, should get replaced with username
losers_file = 'losers_list.csv'
high_score_filename = 'high_scores.txt'
score = 0
player_shot = False

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
api = tweepy.API(auth)

class MyStreamListener(tweepy.StreamListener):
	def on_status(self, status):
		encoded_status = status.text.encode('utf-8')
		player = status.author.screen_name
		print "Got a tweet from %s!" % player
		if encoded_status.startswith('@%s' % bot_username):
			play_game(player, status.id, False)
		elif encoded_status.startswith('.@%s' % bot_username):
			play_game(player, status.id, True)
	def on_error(self, status_code):
		print "Error: %s" % status_code
		if status_code == 420:
			print "Rate limited. Womp womp. Bailing out."
			return False

def fire_revolver():
	if random.randint(1, num_chambers) == 1:
		return True
	else:
		return False

def record_loss(player, score):
	losers_list = open(losers_file, 'a')
	losers_list.write("%s,%d\n" % (player, score))
	losers_list.close()

def post_loss(player, score, tweet, public):
	print "Attempting to post: @%s BANG!\n\nFinal score: %d" % (player, score)
	if public == True:
		if score == 0:
			api.update_status(("BANG! @%s lost on their very first try. :(" % player), tweet)
		elif score == 1:
			api.update_status(("BANG! @%s lost after cheating death once." % player), tweet)
		else:
			api.update_status(("BANG! @%s lost after cheating death %d times." % (player, score)), tweet)
	else:
		if score == 0:
			api.update_status(("@%s BANG!\n\nFinal score: %d. Bad luck! :(" % (player, score)), tweet)
		else:
			api.update_status(("@%s BANG!\n\nFinal score: %d" % (player, score)), tweet)

def post_win(player, score, tweet):
	print "Attempting to post: @%s click" % player
	message = "click"
	if score == 3:
		message += "\n\nTriple Combo!"
	elif score == 4:
		message += "\n\nSuper Combo!"
	elif score == 5:
		message += "\n\nHyper Combo!"
	elif score == 6:
		message += "\n\nBrutal Combo!"
	elif score == 7:
		message += "\n\nMaster Combo!"
	elif score == 8:
		message += "\n\nAwesome Combo!"
	elif score == 9:
		message += "\n\nBlaster Combo!"
	elif score == 10:
		message += "\n\nMonster Combo!"
	elif score == 11:
		message += "\n\nKing Combo!"
	elif 12 <= score and score < 20:
		message += "\n\nKiller Combo!"
	elif 20 <= score:
		message += "\n\nULTRAAA COMBOOOO!"
	api.update_status(("@%s %s" % (player, message)), tweet)

def get_score(player):
	score = 0
	scorefilename = ("%s.score.txt" % player)
	try:
		scorefile = open(scorefilename)
	# if score file doesn't exist, score is 0
	except IOError as err:
		print "File doesn't exist. Score is 0."
		return 0
	except ValueError as err:
		print "Score file is most likely empty. Score is 0."
		return 0
	score = int(scorefile.readline())
	print "Read score: %d" % score
	scorefile.close()
	return score

def get_high_score():
	high_score = 0
	try:
		high_score_file = open(high_score_filename)
	except IOError as err:
		print "No high score file found. Guess this is the new high score!"
		return 0
	except ValueError as err:
		print "High score file is empty. Guess this is the new high score!"
		return 0
	high_score = int(high_score_file.readline())
	print "Read high score: %d" % high_score
	high_score_file.close()
	return high_score

def set_high_score(score):
	high_score_file = open(high_score_filename, 'w')
	high_score_file.write(score)
	high_score_file.close()

def increase_score(player, score):
	scorefilename = ("%s.score.txt" % player)
	try:
		scorefile = open(scorefilename, 'r+')
		score = int(scorefile.readline()) + 1
		print "Setting score to %d" % score
	except IOError as err:
		print "Score file can't be read. Attempting to create."
		scorefile = open(scorefilename, 'w')
		score = 1
		print "Score is now %d" % score
	except ValueError as err:
		print "No valid value in score file. So, 0. Increasing to 1."
		scorefile = open(scorefilename, 'w')
		score = 1
		print "Score is now %d" % score
	print "Writing score as a string: %s" % str(score)
	scorefile.seek(0)
	scorefile.truncate(0)
	scorefile.write(str(score))
	scorefile.close()
	
def player_is_dead(player):
	try:
		losers_list = open(losers_file, 'r')
	except IOError as err:
		losers_list = open(losers_file, 'w')
		losers_list.write("")
		losers_list.close()
		losers_list = open(losers_file, 'r')
	loserdata = losers_list.readlines()
	losers_list.close()	
	for line in loserdata:
		if line.startswith(player) == True:
			print "%s tried to play again, but they're dead." % player
			return True
	print "%s does not appear to be dead." % player
	return False

def play_game(player, tweet, public):
	print "Checking whether %s is dead..." % player
	if player_is_dead(player) == True:
		print "Yep!"
		return False
	print "Nope! Firing revolver..."
	score = get_score(player)
	player_shot = fire_revolver()
	print "Checking whether player was shot..."
	if player_shot == True:
		print "Yep! Recording loss..."
		record_loss(player, score)
		print "Posting loss..."
		post_loss(player, score, tweet, public)
		"Resetting..."
		score = 0
		player_shot = False
	else:
		print "Nope! Increasing score..."
		increase_score(player, score)
		print "Posting win..."
		post_win(player, score, tweet)

print "Setting up stream..."
myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)

myStream.filter(track=['@roulettron'], async=True)
